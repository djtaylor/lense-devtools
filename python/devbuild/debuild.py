import shutil
import tarfile
from re import compile
from getpass import getuser
from datetime import datetime
from socket import gethostname
from os import chdir, path, unlink, symlink
from devbuild.common import LenseDBCommon

class LenseDebuild(LenseDBCommon):
    """
    Helper class for building a debian package from a project.
    """
    def __init__(self, name, root, version, build=False):
        """
        :param    name: The project name (i.e., lense-engine)
        :type     name: str
        :param    root: The project build root
        :type     root: str
        :param version: The version to build (without revision)
        :type  version: str
        :param   build: Should we build or not
        :type    build: bool
        """
        super(LenseDebuild, self).__init__()
        
        # Should we build or not (repo newly cloned or updated)
        self.build     = build

        # Name / root / source / version
        self.name      = name
        self.root      = '{0}/{1}'.format(self.pkgroot, root)
        self.src       = '{0}/{1}'.format(self.root, name)
        self.version   = version

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
        self.bdir      = self.mkdir('{0}/build/{1}-{2}'.format(self.pkgroot, self.version, self.revision))
        self.current   = '{0}/build/current/{1}_current_all.deb'.format(self.pkgroot, self.debpkg)

        # Preflight OK
        return True

    def timestamp(self):
        """
        Get a Debian style timestamp.
        
        :rtype: str
        """
        offset = '+0000'
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S {0}'.format(offset))

    def _set_changelog(self):
        """
        Set the next changelog entry prior to building.
        """
        release   = '{0} ({1}-{2}) trusty; urgency=low'.format(self.name, self.version, self.revision)
        
        # Get a user message
        self.feedback.input('Enter an optional changelog message: ', 'changelog_msg', default=None)
        user_rsp = self.feedback.get_response('changelog_msg')
        user_msg = '' if not user_rsp else '\n  * {0}'.format(user_rsp)
        
        # Set the changelog comment
        comment   = '  * Building {0}-{1}{2}'.format(self.version, self.revision, user_msg)
        
        # Set the author line
        author    = ' -- Developer <{0}@{1}>  {2}'.format(getuser(), gethostname(), self.timestamp())
    
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
                f.write('dev0:: {0}'.format(self.timestamp()))
            return 'dev0'
        
        # Open the revisions file
        with open(self.revisions, 'r') as f:
            revision = f.readline().rstrip()
                
        # Extract ID and number
        rev_ex = compile(r'(^[a-zA-Z]*)([0-9]*::.*$)')
        rev_id = rev_ex.sub(r'\g<1>', revision)
        rev_num = rev_ex.sub(r'\<2>', revision)
                
        # Next revision
        rev_nxt = '{0}{1}'.format(rev_id, int(rev_num) + 1)
        self.feedback.info('Building next revision -> {0}'.format(rev_nxt))
        return rev_nxt

    def _tar_source(self):
        """
        Compress the source directory for the base revision.
        """
        if self.revision == 'dev0':
            chdir(self.root)
            with tarfile.open(self.tarball, 'w:gz') as tar:
                tar.add(self.name)
            return self.feedback.info('Created source tarball: {0}'.format(self.tarball))
        self.feedback.info('Found source tarball: {0}'.format(self.tarball))
        
    def _debuild(self):
        """
        Build the debian package from source
        """
        
        # Change to the source directory
        chdir(self.src)
        
        # Start building the package
        code, err = self.shell_exec(['debuild', '-uc', '-us'])

        # Make sure the build was successfull
        if not code == 0:
            self.feedback.error('Failed to build {0}: {1}'.format(self.name, str(err)))
        
        # Change to the project root directory
        chdir(self.root)

        # Move to the builds directory
        latest = '{0}/{1}'.format(self.bdir, self.debpkg)
        shutil.move(self.debpkg, latest)
        self.feedback.success('Finished building {0}: {1}'.format(self.name, latest))

        # Make sure the current directory exists
        self.mkdir('{0}/build/current'.format(self.pkgroot))

        print 'LATEST: {0}'.format(latest)
        print 'CURRENT: {0}'.format(self.current)

        # Clear out the old symbolic link
        if path.islink(self.current):
            unlink(self.current)
            
        # Link to the latest DEB
        symlink(latest, self.current)
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