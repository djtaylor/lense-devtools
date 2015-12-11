from json import loads as json_loads
from getpass import getuser
from os import path, listdir, unlink
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
        
        # Load arguments
        self.args    = DevToolsArgs()
        
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
        
    def _install(self):
        """
        Install or upgrade all or specific packages in the current builds directory.
        """
        use_projects = self.args.get('projects', None)
        
        # Installing all projects
        if not use_projects:
            code, err = self.shell(['sudo', 'dpkg', '-i', path.expanduser('~/.lense_devtools/build/current/*')])
            
            # Failed to install 
            if not code == 0:
                self.die('Failed to install project packages: {0}'.format(str(err)))
        
        # Install specific projects
        else:
            use_projects = use_projects[0].split(',')
            
            # Make sure project names are valid
            for project in use_projects:
                if not project in self.projects:
                    self.die('Cannot install project <{0}>, not in supported list: {1}'.format(project, ', '.join(self.projects.keys())))
    
            # Build each project
            for project in use_projects:
                code, err =self.shell(['sudo', 'dpkg', '-i', path.expanduser('~/.lense_devtools/build/current/{0}_current_all.deb'.format(project))])
        
                # Failed to install 
                if not code == 0:
                    self.die('Failed to install project <{0}> package: {1}'.format(project, str(err)))
        
    def _build(self):
        """
        Build either all projects or specified projects.
        """
        use_projects = self.args.get('projects', None)
        
        # Building all projects
        if not use_projects:
            for project, attrs in self.projects.iteritems():
                self._build_project(project, attrs)
             
        # Building specific projects   
        else:
            use_projects = use_projects[0].split(',')
            
            # Make sure project names are valid
            for project in use_projects:
                if not project in self.projects:
                    self.die('Cannot build project <{0}>, not in supported list: {1}'.format(project, ', '.join(self.projects.keys())))
    
            # Build each project
            for project in use_projects:
                self._build_project(project, self.projects[project])
    
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