from os import path
from git import Repo, Git
from lense_devtools.common import DevToolsCommon

class DevToolsGitRepo(DevToolsCommon):
    """
    Helper class for retrieving a lense project repository.
    """
    def __init__(self, project, attrs):
        """
        :param project: The project name
        :type  project: str
        :param   attrs: Project attributes
        :type    attrs: dict
        """
        super(DevToolsGitRepo, self).__init__()
        
        # Project name
        self.name    = project
        
        # Root / local / remote / branch
        self.root    = self.mkdir('{0}/{1}'.format(self.workspace, attrs.get('git-local', 'src/{0}'.format(project))))
        self.local   = '{0}/{1}'.format(self.root, project)
        self.remote  = attrs.get('git-remote')
        self.branch  = attrs.get('git-branch')

        # Repo / Git objects
        self._repo   = None
        self._git    = None

        # Does the repo exist locally
        self.exists  = False

        # Has the repo been updated / cloned
        self.updated = False
        self.cloned  = False

    def _get_current_branch(self):
        """
        Get the checked out local branch.
        """
        return str(self._repo.active_branch)

    def _checkout(self, branch):
        """
        Checkout the request branch.
        """
        current_branch = self._get_current_branch()

        # Target branch is already checked out
        if current_branch == branch:
            return True

        # Checkout the branch   
        self._git.checkout(branch)
        return self.feedback.success('Switched to branch: {0}'.format(branch))
    
    def _clone(self):
        """
        Clone a remote repository.
        """
        if not self.exists:
            Repo.clone_from(self.remote, self.local)
            self.feedback.success('Cloned repository')
            self.feedback.info('Remote: {0}'.format(self.remote))
            self.feedback.info('Local: {0}'.format(self.local))

            # Store the Repo/Git objects
            self._git  = Git(self.local)
            self._repo = Repo(self.local)

            # Checkout the requested branch
            self._checkout(self.branch)
            self.cloned = True

        # Local repo already exists
        else:
            self.feedback.info('Local repository found: {0}'.format(self.local))

    def _refresh(self):
        """
        Refresh the repository objects.
        """
        self._git  = Git(self.local)
        self._repo = Repo(self.local)

        # Fetch remotes
        self._repo.remotes.origin.fetch()
        self.feedback.info('Fetched changes from remote')

    def _get_local_commit(self):
        """
        Get the latest commit tag from the local branch.
        """
        for o in self._repo.refs:
            if o.name == self.branch:
                return o.commit
            
    def _get_remote_commit(self):
        """
        Get the latest commit tag from the remote branch.
        """
        for o in self._repo.remotes.origin.refs:
            if o.remote_head == self.branch:
                return o.commit

    def _pull(self):
        """
        Pull changes from a remote repository.
        """
        
        # If the repo has just been cloned
        if self.cloned:
            self.feedback.info('Newly cloned repo, skipped pull')
            return True
        
        # Refresh repo objects
        self._refresh()

        # Checkout the branch
        self._checkout(self.branch)

        # Remote / local commits
        remote_commit = self._get_remote_commit()
        local_commit  = self._get_local_commit()

        # Show the local/remote commit info
        self.feedback.info('Local <{0}> is on commit: {1}'.format(self.local, local_commit))
        self.feedback.info('Remote <{0}> is on commit: {1}'.format(self.remote, remote_commit))

        # If local is up to date
        if remote_commit == local_commit:
            return self.feedback.info('Local matches remote, everything up to date'.format(local_commit, remote_commit))

        # Update the local branch
        origin = self._repo.remotes.origin
        origin.pull()

        # Refresh the branches
        self._refresh()

        # Updated success
        self.feedback.success('Local branch updated -> {0}'.format(self._get_local_commit()))
        self.updated = True
        
    def setup(self):
        """
        Construct information about the repository.
        """
        self.exists = False if not path.isdir(self.local) else True

        # Make sure the repo exists locally
        self._clone()

        # Pull any changes from the remote
        self._pull()