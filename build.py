#!/usr/bin/env python
from __future__ import print_function
import sys
from os import path

# Add the local Python path
sys.path.append('{0}/python'.format(path.dirname(path.realpath(__file__))))

# Devbuild Modules
from devbuild.git import LenseGitRepo
from devbuild.debuild import LenseDebuild
from devbuild.common import LenseDevBuildCommon

# Make sure Git/Gitpython is available
try:
    import git
except Exception as e:
    print('ERROR: Failed to import module "git". Please make sure Git and Gitpython are installed')
    sys.exit(1)

class LenseDevBuild(LenseDevBuildCommon):
    """
    Build all Lense projects from Github source code.
    """
    def __init__(self):
        super(LenseDevBuild, self).__init__()

    def run(self):
        """
        Public method for starting the build process.
        """
        for project in self.projects:
            self.feedback.block([
                'PROJECT: {0}'.format(project['name']),
                'LOCAL:   {0}'.format(project['git-local']),
                'REMOTE:  {0}'.format(project['git-src']),
                'BRANCH:  {0}'.format(project['git-branch']),
                'VERSION: {0}'.format(project['build-version'])
            ], 'BUILD')

            # Setup the source code repositry
            LenseGitRepo(project['git-local'], project['git-src'], project['name'], project['git-branch']).setup()

            # Setup the build handler
            LenseDebuild(project['name'], project['git-local'], project['build-version']).run()

if __name__ == '__main__':
    build = LenseDevBuild()
    build.run()