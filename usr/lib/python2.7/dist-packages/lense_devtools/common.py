import tarfile
from sys import exit
from feedback import Feedback
from subprocess import Popen, PIPE
from json import loads as json_loads
from shutil import move as move_file
from os import path, makedirs, unlink, symlink, chdir, getcwd

class DevToolsCommon(object):
    """
    Common class for the development buider modules.
    """
    def __init__(self):
        self.feedback  = Feedback()
        
        # Configuration / workspace / projects / disabled projects
        self.config    = self._get_config()
        self.workspace = self._get_workspace()
        self.projects  = self._get_projects()
        self.disabled  = self._get_disabled()
        
    def _get_config(self):
        """
        Look for a configuration at: /etc/lense_devtools/config.json
        
        :rtype: dict
        """
        config = '/etc/lense_devtools/config.json'
        if not path.isfile(config):
            raise Exception('Configuration file missing: <{0}> not found'.format(config))
        
        try:
            return json_loads(open(config, 'r').read())
        except Exception as e:
            self.die('Failed to parse <{0}>: {1}'.format(config, str(e.message)))
        
    def _get_disabled(self):
        """
        Return a list of disable projects.
        """
        return {} if not 'DISABLED' in self.config else self.config['DISABLED']
        
    def _get_projects(self):
        """
        Retrieve a dict of configured projects.
        
        :rtype: dict
        """
        if not 'PROJECTS' in self.config:
            self.die('Missing required <PROJECTS> key in: {0}'.format(self.config))
        
        # Projects must be a dict
        if not isinstance(self.config['PROJECTS'], dict):
            self.die('Required key <PROJECTS> must be a dict'.format(self.config))
        
        # Project validation manifest
        vattrs = '/usr/share/lense_devtools/project.json'
        
        # Try to load the validation manifest
        if not path.isfile(vattrs):
            self.die('Could not locate project attributes manifest: {0}'.format(vattrs))
        vattrs = json_loads(open(vattrs, 'r').read())
        
        # Validate projects
        for pk,pa in self.config['PROJECTS'].iteritems():
            if not pk in vattrs['supported']:
                self.die('Unsupported project: {0}'.format(pk))
                
            # Make sure required attributes are set
            for k in vattrs['attributes']['required']:
                if not k in pa:
                    self.die('Missing required project attribute <{0}> for <{1}>'.format(k, pk))
        
        # Return projects
        return self.config['PROJECTS']
        
    def _get_workspace(self):
        """
        Retrieve the devtools workspace path.
        
        :rtype: str
        """
        if not 'WORKSPACE' in self.config:
            self.die('Missing required <WORKSPACE> key in: {0}'.format(self.config))
        return self.mkdir(path.expanduser('~/{0}'.format(self.config['WORKSPACE'])))
        
    def die(self, message='An error ocurred', code=1):
        """
        Print error and quit.
        
        :param message: The error message
        :type  message: str
        """
        self.feedback.error(message)
        exit(code)
        
    def targz(self, tarfile, source, workdir=None):
        """
        Make a new Gzip tar file.
        
        :param tarfile: The destination tarfile to create
        :type  tarfile: str
        :param  source: The source folder to compress
        :type   source: str
        :param workdir: Change to a new working directory
        :type  workdir: str
        """
        
        # Get the current working directory
        cwd = getcwd()
        
        # If changing working directories prior to compressing
        if workdir:
            if not path.isdir(workdir):
                self.die('Cannot change to working directory <{0}>, not found'.format(workdir))
        
            # Change working directories
            chdir(workdir)
        
        # Create the tarfile
        with tarfile.open(tarfile, 'w:gz') as tar:
            tar.add(source)
        self.feedback.info('Created tarball: {0}'.format(tarfile))
            
        # Revert directory
        chdir(cwd)
        
    def rmfile(self, file):
        """
        Remove a file/symlink if it exists.
        
        :param file: The target file
        :type  file: str
        """
        if path.isfile(file) or path.islink(file):
            unlink(file)
        
    def mvfile(self, src, dst):
        """
        Move a file from one place to another.
        
        :param src: The source file
        :type  src: str
        :param dst: The destination file
        :type  dst: str
        """
        move_file(src, dst)
        
    def mklink(self, target, link):
        """
        Make a symbolic link.
        
        :param target: The target file
        :type  target: str
        :param   link: The target link
        :type    link: str
        """
        symlink(target, link)
        self.feedback.info('Created symlink: {0} -> {1}'.format(target, link))
        
    def mkdir(self, dir_path):
        """
        Make a directory and return the path name.
        
        :rtype: str
        """
        if not path.isdir(dir_path):
            makedirs(dir_path)
        return dir_path
        
    def shell(self, cmd, stdout=False):
        """
        Run an arbitrary shell command.
        
        :param stdout: Capture stdout or not
        :type  stdout: bool
        :rtype: str|None
        """
        if not isinstance(cmd, list):
            raise Exception('<DevToolsCommon.shell> command argument must be a list')
        
        # Start the process
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE) if stdout else Popen(cmd, stderr=PIPE)
        
        # Call the command
        if stdout:
            out, err = proc.communicate()
            return proc.returncode, out, err
        else:
            err = proc.communicate()
            return proc.returncode, err
        