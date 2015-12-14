from getpass import getuser
from json import loads as json_loads
from os import path, listdir, unlink, geteuid

# Devtools Libraries
from lense_devtools.dpkg import DevToolsDpkg
from lense_devtools.args import DevToolsArgs
from lense_devtools.common import DevToolsCommon
from lense_devtools.gitrepo import DevToolsGitRepo
from lense_devtools.debuild import DevToolsDebuild

class DevToolsInterface(DevToolsCommon):
    """
    Interface class for handling arguments.
    """
    def __init__(self):
        super(DevToolsInterface, self).__init__()
        
        # Load arguments / dpkg handler
        self.args    = DevToolsArgs()
        self.dpkg    = DevToolsDpkg()
        
        # Main command
        self.command = self.args.get('command')
        
    def _init_config(self, file):
        """
        Load and validate the workspace init config file. This assumes
        that the workspace directory exists and is empty.
        
        :param file: The init config file
        :type  file: str
        """
        
        # Need to create a new init config
        if not path.isfile(file):
            
            # Write out the new config
            with open(file, 'w') as f:
                f.write('[]')
            self.feedback.success('Initialize workspace config: {0}'.format(file))
        
        # Config exists, validate
        else:
            try:
                init_config = json_loads(open(file, 'r').read())
            except Exception as e:
                raise Exception('Failed to parse workspace config <{0}>: {1}'.format(file, self.workspace))
        
    def _init_workspace(self):
        """
        Initialize the workspace.
        """
        init_config = '{0}/.init.json'.format(self.workspace)
        init_new    = False if path.isfile(init_config) else True
        
        # Does the workspace directory exist
        if path.isdir(self.workspace):
            
            # Workspace must be empty if it is new
            if init_new and listdir(self.workspace):
                
                # Look for allowed directories
                allowed = True
                for d in listdir(self.workspace):
                    if not d in ['install']:
                        allowed = False
                
                # Workspace contains unsupported directories (previously existing)
                if not allowed:
                    self.die('Cannot initialize a non-empty workspace: {0}'.format(self.workspace))
        
            # Check if the workspace is writeable by the running user
            try:
                tmp = '{0}/.tmp'.format(self.workspace)
                with open(tmp, 'w') as f:
                    f.write('')
        
                # Workspace is writeable
                unlink(tmp)
            
            # Failed to write to workspace
            except:
                self.die('Workspace <{0}> is not writeable, please check permissions'.format(self.workspace))
        
            # Validate / create the config
            self._init_config(init_config)
        
        # Workspace doesn't exist yet
        else:
            self.die('Workspace <{0}> not found, please create and set appropriate permissions'.format(self.workspace))
        
    def _summarize(self, project, attrs):
        """
        Display a build summary.
        
        :param project: The project name
        :type  project: str
        :param   attrs: Project attributes
        :type    attrs: dict
        """
        self.feedback.block([
            'PROJECT: {0}'.format(project),
            'REMOTE:  {0}'.format(attrs.get('git-remote')),
            'BRANCH:  {0}'.format(attrs.get('git-branch')),
            'LOCAL:   {0}'.format(attrs.get('git-local', '{0}/src/{1}'.format(self.workspace, project))),
            'VERSION: {0}'.format(attrs.get('version'))
        ], 'BUILD')
        
    def _install_pkg(self, project):
        """
        Install a debian package.
        
        :param project: The project name
        :type  project: str
        """
        project_pkg = path.expanduser('~/.lense_devtools/build/current/{0}_current_all.deb'.format(project))
        if path.isfile(project_pkg):
            self.dpkg.installdeb(project_pkg)
        
    def _install(self):
        """
        Install or upgrade all or specific packages in the current builds directory.
        """
        use_projects = self.args.get('projects', None)
        pkg_order    = ['lense-common', 'lense-client', 'lense-engine', 'lense-portal', 'lense-socket']
        
        # Must be superuser
        if not geteuid() == 0:
            self.die('Command <install> must be run as superuser')
        
        # Installing all projects
        if not use_projects:
            for project in pkg_order:
                self._install_pkg(project)
        
        # Install specific projects
        else:
            use_projects = self.validate_projects(use_projects[0].split(','))
    
            # Install projects in order
            for project in pkg_order:
                if project in use_projects:
                    self._install_pkg(project)
        
    def _build_project(self, project, attrs):
        """
        Build a single project.
        
        :param project: The project ID
        :type  project: str
        :param   attrs: Project attributes
        :type    attrs: dict
        """
        self._summarize(project, attrs)
        
        # Setup the source code repositry
        gitrepo = DevToolsGitRepo(project, attrs, automode=self.args.get('auto', False))
        gitrepo.setup()

        # Has the repo been newly cloned or updated
        build = False if not (gitrepo.cloned or gitrepo.updated) else True

        # Setup the build handler
        DevToolsDebuild(project, attrs, build=build, automode=self.args.get('auto', False)).run()
        return True
        
    def _build_status(self, status):
        """
        Show the build status summary.
        
        :param status: A dict of project/status key pairs
        :type  status: dict
        """
        error   = 'Project "{0}" build failed'
        success = 'Project "{0}" build completed'
        for p,s in status.iteritems():
            fb = getattr(self.feedback, 'error' if not s else 'success', 'info')
            fb(error.format(p) if not s else success.format(p))
        
    def _build(self):
        """
        Build either all projects or specified projects.
        """
        use_projects = self.args.get('projects', None)
        
        # Building all projects
        if not self.args.get('projects', None):
            status = {}
            for p,a in self.projects.iteritems():
                status[p] = self._build_project(p,a)
            self._build_status(status)
            return True
             
        # Building specific projects
        targets = self.validate_projects(use_projects[0].split(','))
    
        # Build each project
        self._build_status({p: self._build_project(p, self.projects[p]) for p in targets})
    
    def _run(self):
        """
        Private run method for starting devtools.
        """
        self._init_workspace()
        
        # Command mapper
        mapper = {
            'build': self._build,
            'install': self._install
        }
        
        # Run the command
        mapper[self.command]()
        
    @staticmethod
    def run():
        interface = DevToolsInterface()
        interface._run()