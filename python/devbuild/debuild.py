import shutil
import tarfile
from os import chdir, path, unlink
from devbuild.common import LenseDevBuildCommon

class LenseDebuild(LenseDevBuildCommon):
    """
    Helper class for building a debian package from a project.
    """
    def __init__(self, name, root, version):
        super(LenseDebuild, self).__init__()
        
        # Name / root / source / version
        self.name    = name
        self.root    = '{0}/{1}'.format(self.pkgroot, root)
        self.src     = '{0}/{1}'.format(root, name)
        self.version = version

        # Define the source tarball
        self.tarball = '{0}_{1}.orig.tar.gz'.format(self.name, self.version)
        self.tarpath = '{0}/{1}'.format(self.root, self.tarball)

        # Define the output debian package
        self.debpkg  = '{0}_{1}_all.deb'.format(self.name, self.version)
        self.debpath = '{0}/{1}'.format(self.root, self.debpkg)

        # Build output directory
        self.bdir    = self.mkdir('{0}/build/{1}'.format(self.pkgroot, self.version))

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