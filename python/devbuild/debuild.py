import shutil
import tarfile
from re import compile
from os import chdir, path, unlink
from devbuild.common import LenseDevBuildCommon

class LenseDebuild(LenseDevBuildCommon):
    """
    Helper class for building a debian package from a project.
    """
    def __init__(self, name, root, version):
        super(LenseDebuild, self).__init__()
        
        # Name / root / source / version / revision
        self.name     = name
        self.root     = '{0}/{1}'.format(self.pkgroot, root)
        self.src      = '{0}/{1}'.format(self.root, name)
        self.version  = version
        self.revision = self._next_revision()

        # History file
        self.history  = '{0}/build_history.txt'.format(self.root)

        # Define the source tarball
        self.tarball  = '{0}_{1}.orig.tar.gz'.format(self.name, self.version)
        self.tarpath  = '{0}/{1}'.format(self.root, self.tarball)

        # Define the output debian package
        self.debpkg   = '{0}_{1}_{2}_all.deb'.format(self.name, self.version, self.revision)
        self.debpath  = '{0}/{1}'.format(self.root, self.debpkg)

        # Build output directory
        self.bdir     = self.mkdir('{0}/build/{1}'.format(self.pkgroot, self.version))

    def _next_revision(self):
        """
        Get the next revision number
        """
        
        # No history file present (revision 1)
        if not path.isfile(self.history):
            return '1'
        
        # Get the latest revision
        last = None
        with open(self.history, 'r') as f:
            for l in f.readlines():
                last = l
        
        # Extract the last revision
        return compile(r'^[^_]_[^_]*_(.*$)'.format(self.name)).sub(r'\g<1>', last)

    def _set_history(self, entry):
        """
        Set a build history entry for the project.
        
        <package>-<version>-<revision>
        
        :param entry: The history entry for this package
        :type  entry: str
        """
        
        # New history file
        if not path.isfile(self.history):
            open(history_file, 'w').close()
            self.feedback.info('Initializing build history: {0}'.format(self.history))

        # Write the new history entry
        with open(self.history, 'a') as f:
            f.write(entry)
            self.feedback.info('Build history now at: {0}'.format(entry))

    def _tar_src(self):
        """
        Compress the source directory.
        """
        chdir(self.root)
        with tarfile.open(self.tarball, 'w:gz') as tar:
            tar.add(self.name)
        self.feedback.info('Created source tarball: {0}'.format(self.tarball))
        
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
        build_file = '{0}/{1}'.format(self.bdir, self.debpkg)
        shutil.move(self.debpkg, build_file)
        self.feedback.success('Finished building {0}: {1}'.format(self.name, build_file))

        # Add to the build history
        self._set_history('{0}_{1}_{2}'.format(self.name, self.version, self.revision))

    def run(self):
        """
        Public method for starting the build process
        """
        if path.isfile(self.tarpath):
            self.feedback.info('Clearing old source archive...')
            unlink(self.tarpath)

        # Create the source tarball and build the debian package
        self._tar_src()
        self._debuild()