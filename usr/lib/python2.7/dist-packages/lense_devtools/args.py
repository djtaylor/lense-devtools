from sys import argv, exit
from argparse import ArgumentParser, RawTextHelpFormatter

class DevToolsArgs(object):
    """
    Class object for handling command line arguments.
    """
    def __init__(self):
        
        # Argument parser / storage
        self.parser  = None
        self.storage = None
        
        # Construct arguments and validate
        self._construct()
        self._validate()
        
    def list(self):
        """
        Return a list of argument keys.
        
        :rtype: list
        """
        return self.storage.keys()
        
    def _command_help(self):
        """
        :rtype: str
        """
        return ("build:   Build all or specific project in the current workspace\n"
                "install: Install or upgrade all/specific projects in the current builds directory")
        
    def _desc(self):
        """
        :rtype: str
        """
        return ("Lense DevTools\n\n"
                 "Tools to assist developers in developing and contributing\n"
                 "to Lense projects.")
        
    def _validate(self):
        """
        Perform argument validation.
        """
        commands = ['build', 'install']
        
        # Make sure the command is valid
        if not self.get('command') in commands:
            self.parser.print_help()
            exit(1)
        
    def _construct(self):
        """
        Construct the argument parser.
        
        lense-devtools build {package} (optional) # Defaults to build all
        """
        self.parser = ArgumentParser(description=self._desc(), formatter_class=RawTextHelpFormatter)
        
        # Main argument
        self.parser.add_argument('command', help=self._command_help())
        
        # Argument flags
        self.parser.add_argument('-p', '--projects', help='A single project or comma seperated list of projects', action='append')
        self.parser.add_argument('-a', '--auto', help='Run in automated mode (avoid prompts)', action='store_true')
        
        # Parse arguments
        argv.pop(0)
        self.storage = vars(self.parser.parse_args(argv))
        
    def set(self, k, v):
        """
        Set a new argument or change the value.
        """
        self.storage[k] = v
        
    def get(self, k, default=None):
        """
        Retrieve an argument passed via the command line.
        """
        return self.storage.get(k, default)