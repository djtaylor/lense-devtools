from os import path, makedirs
from feedback import Feedback
from json import load as json_load
from subprocess import Popen, PIPE

class LenseDevBuildCommon(object):
    """
    Common class for the development buider modules.
    """
    def __init__(self):
        self.pkgroot  = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))
        
        # Feedback / projects manifest
        self.feedback = Feedback()
        self.projects = json_load(open('{0}/projects.json'.format(self.pkgroot), 'r'))
        
    def mkdir(self, dir_path):
        """
        Make a directory and return the path name.
        """
        if not path.isdir(dir_path):
            makedirs(dir_path)
        return dir_path
        
    def shell_exec(self, cmd, show_stdout=False):
        """
        Run an arbitrary shell command.
        """
        if not isinstance(cmd, list):
            raise Exception('"shell_exec" command argument must be a list')
        
        # Run the command
        proc = Popen(cmd, stderr=PIPE)
        err  = proc.communicate()
        
        # Return the exit code and stderr if any
        return proc.returncode, err
        