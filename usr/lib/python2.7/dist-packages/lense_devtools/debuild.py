from re import compile
from socket import getfqdn
from getpass import getuser
from datetime import datetime
from os import chdir, path, unlink, symlink, environ
from lense_devtools.common import DevToolsCommon

class DevToolsDebuild(DevToolsCommon):
    """
    Helper class for building a debian package from a project.
    """
    def __init__(self, project, attrs, build=False, automode=False):
        """
        :param project: The project name
        :type  project: str
        :param   attrs: Project attributes
        :type    attrs: dict
        :param   build: Should we build or not
        :type    build: bool
        """
        super(DevToolsDebuild, self).__init__()
        
        # Should we build or not (repo newly cloned or updated) / auto mode (avoid prompts)
        self.build     = build
        self.automode  = automode

        # Name / root / source / version
        self.name      = project
        self.root      = '{0}/{1}'.format(self.workspace, attrs.get('git-local'))
        self.src       = '{0}/{1}'.format(self.root, project)
        self.version   = attrs.get('version')

    def _preflight(self):
        """
        Run preflight checks prior to building.
        """
        if not self.build:
            self.feedback.info('Source code has not changed, skipping build')
            return False

        # Revisions history / revision / changelog
        self.revisions = '{0}/revisions.txt'.format(self.root)
        self.revision  = self._set_revision()
        self.chlog     = '{0}/debian/changelog'.format(self.src)

        # Define the source tarball
        self.tarball   = '{0}_{1}.orig.tar.gz'.format(self.name, self.version)
        self.tarpath   = '{0}/{1}'.format(self.root, self.tarball)

        # Define the output debian package
        self.debpkg    = '{0}_{1}-{2}_all.deb'.format(self.name, self.version, self.revision)
        self.debpath   = '{0}/{1}'.format(self.root, self.debpkg)

        # Build output directory / current package
        self.bdir      = self.mkdir('{0}/build/{1}-{2}'.format(self.workspace, self.version, self.revision))
        self.current   = '{0}/build/current/{1}_current_all.deb'.format(self.workspace, self.name)

        # Preflight OK
        return True

    def timestamp(self):
        """
        Get a Debian style timestamp.
        
        :rtype: str
        """
        offset = '+0000'
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S {0}'.format(offset))

    def _dpkg_patch(self):
        """
        Run a dpkg-source --commit to generate patches for non-base revisions.
        """
        if not self.revision == 'dev0':
            patch_name = 'patch_{0}'.format(self.revision)
            environ['EDITOR'] = '/bin/true'
            
            # Run dpkg-source
            code, err = self.shell(['dpkg-source', '-q', '--commit', '.', patch_name])
    
            # Make sure the patch was created
            if not code == 0:
                self.die('Failed to generate "{0}": {1}'.format(patch_name, str(err)))
            self.feedback.success('Generated patch file -> {0}'.format(patch_name))

    def _set_changelog(self):
        """
        Set the next changelog entry prior to building.
        """
        release   = '{0} ({1}-{2}) trusty; urgency=low'.format(self.name, self.version, self.revision)
        
        # Get a user message if not automated
        user_msg = ''
        if not self.automode:
            self.feedback.input('Enter an optional changelog message: ', 'changelog_msg', default=None)
            user_rsp = self.feedback.get_response('changelog_msg')
            user_msg = '' if not user_rsp else '\n  * {0}'.format(user_rsp)
        
        # Set the changelog comment
        comment   = '  * Building {0}-{1}{2}'.format(self.version, self.revision, user_msg)
        
        # Set the author line
        author    = ' -- Developer <{0}@{1}>  {2}'.format(getuser(), getfqdn(), self.timestamp())
    
        # Create the file if it doesnt exist
        if not path.isfile(self.chlog):
            chlog_orig = ''
        else:
            # Get the current changelog
            with open(self.chlog, 'r') as f:
                chlog_orig = f.read()
                f.close()
        
        # Write to the changelog
        entry = '{0}\n\n{1}\n\n{2}'.format(release, comment, author)
        with open(self.chlog, 'w') as f:
            f.write('{0}\n\n'.format(entry))
            f.write(chlog_orig)
        self.feedback.info('Appended to "{0}":\n{1}\n{2}\n{3}'.format(self.chlog, '-' * 60, entry, '-' * 60))

    def _set_revision(self):
        """
        Get the next revision number
        """
        revision = None
        if not path.isfile(self.revisions):
            self.feedback.info('Building base revision -> dev0')
            with open(self.revisions, 'w') as f:
                f.write('dev0:: {0}\n'.format(self.timestamp()))
            return 'dev0'
        
        # Read the latest revision
        with open(self.revisions, 'r') as f:
            revision = f.readline().rstrip()
                
        # Extract ID and number
        rev_ex = compile(r'(^[a-zA-Z]*)([0-9]*)::.*$')
        rev_id = rev_ex.sub(r'\g<1>', revision)
        rev_num = rev_ex.sub(r'\g<2>', revision)
                
        # Next revision
        rev_nxt = '{0}{1}'.format(rev_id, int(rev_num) + 1)
        self.feedback.info('Building next revision -> {0}'.format(rev_nxt))
        
        # Read the entire revisions file
        all_revisions = None
        with open(self.revisions, 'r') as f:
            all_revisions = f.read()
        
        # Store the next revision
        with open(self.revisions, 'w') as f:
            f.write('{0}:: {1}\n'.format(rev_nxt, self.timestamp()))
            f.write(all_revisions)
        
        # Return the next revision string
        return rev_nxt

    def _tar_source(self):
        """
        Compress the source directory for the base revision.
        """
        if self.revision == 'dev0':
            return self.targz(self.tarball, self.name, workdir=self.root)
        
        # Next revision, tar file should be present
        if not path.isfile(self.tarpath):
            self.die('Could not locate original source tarball: {0}'.format(self.tarpath))
        self.feedback.info('Found source tarball: {0}'.format(self.tarball))
        
    def _debuild(self):
        """
        Build the debian package from source
        """
        
        # Change to the source directory
        chdir(self.src)
        
        # Generate a patch file if needed
        self._dpkg_patch()
        
        # Start building the package
        code, err = self.shell(['debuild', '-uc', '-us'])

        # Make sure the build was successfull
        if not code == 0:
            self.feedback.error('Failed to build {0}: {1}'.format(self.name, str(err)))
        
        # Change to the project root directory
        chdir(self.root)

        # Move to the builds directory
        latest = '{0}/{1}'.format(self.bdir, self.debpkg)
        self.mvfile(self.debpkg, latest)
        self.feedback.success('Finished building {0}: {1}'.format(self.name, latest))

        # Make sure the current directory exists
        self.mkdir('{0}/build/current'.format(self.workspace))

        # Clear out the old symbolic link
        self.rmfile(self.current)
            
        # Link to the latest DEB
        self.mklink(latest, self.current)
        self.feedback.info('Current build package: {0}'.format(self.current))

    def run(self):
        """
        Public method for starting the build process
        """

        # Preflight checks
        if not self._preflight():
            return None

        # Update the changelog
        self._set_changelog()

        # Create the source tarball and build the debian package
        self._tar_source()
        self._debuild()