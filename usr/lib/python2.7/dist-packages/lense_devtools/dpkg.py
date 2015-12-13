from os.path import basename
from feedback import Feedback
from apt.cache import Cache
from apt.debfile import DebPackage, VERSION_NONE, VERSION_OUTDATED, VERSION_SAME, VERSION_NEWER

class DevToolsDpkg(DebPackage):
    """
    Class for managing packages via 'dpkg'
    """
    def __init__(self):
        
        # Get the apt cache
        self.cache = Cache()
        
        # Feedback module
        self.feedback = Feedback()
        
    def installdeb(self, pkg):
        """
        Install the Debian package.
        
        :param pkg: The path to the package to install
        :type  pkg: str
        """
        
        # Get the DebPackage object and the filename
        dpkg     = DebPackage(filename=pkg, cache=self.cache)
        pkg_name = basename(pkg)
        
        # Make sure the package is installable
        if not dpkg.check():
            self.feedback.error('Cannot install package <{0}>'.format(pkg_name))
            return False
            
        # Look for package conflicts
        if not dpkg.check_conflicts():
            self.feedback.block(dpkg.conflicts, 'CONFLICT')
            self.feedback.error('Cannot install package <{0}>, conflicts with:'.format(pkg_name))
            return False
        
        # Get any version in cache
        cache_version = dpkg.compare_to_version_in_cache()
        action        = 'Installed'
        
        # Not installed
        if cache_version == VERSION_NONE:
            self.feedback.info('Package <{0}> not installed'.format(pkg_name))
            
        # Upgrading
        if cache_version == VERSION_OUTDATED:
            self.feedback.info('Package <{0}> outdated, upgrading'.format(pkg_name))
            action = 'Updated'
            
        # Same version
        if cache_version == VERSION_SAME:
            return self.feedback.info('Package <{0}> already installed'.format(pkg_name))
        
        # Installed is newer
        if cache_version == VERSION_NEWER:
            return self.feedback.info('Package <{0}> has newer version installed'.format(pkg_name))
            
        # Install the package
        dpkg.install()
        self.feedback.success('{0}: {0}'.format(action, pkg_name))