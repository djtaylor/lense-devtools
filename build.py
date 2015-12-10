#!/usr/bin/env python
from __future__ import print_function
import sys
from os import path

# Add the local Python path
sys.path.append('{0}/python'.format(path.dirname(path.realpath(__file__))))

# Devbuild Modules
from devbuild.gitrepo import LenseGitRepo
from devbuild.debuild import LenseDebuild
from devbuild.common import LenseDBCommon

class LenseDB(LenseDBCommon):
    """
    Build all Lense projects from Github source code.
    """
    def __init__(self):
        super(LenseDB, self).__init__()

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
            gitrepo = LenseGitRepo(project['git-local'], project['git-src'], project['name'], project['git-branch'])
            gitrepo.setup()

            # Has the repo been newly cloned or updated
            build = False if not (gitrepo.cloned or gitrepo.updated) else True

            # Setup the build handler
            LenseDebuild(project['name'], project['git-local'], project['build-version'], build=build).run()

if __name__ == '__main__':
    build = LenseDB()
    build.run()