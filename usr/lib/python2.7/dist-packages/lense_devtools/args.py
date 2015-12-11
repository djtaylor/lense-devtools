from sys import argv, exit
from argparse import ArgumentParser, RawDescriptionHelpFormatter

class DevToolsArgs(object):
    """
    Class object for handling command line arguments.
    """
    def __init__(self):
        self.parser = None
        self._args  = None
        
        # Construct arguments and validate
        self._construct()
        self._validate()
        
    def list(self):
        """
        Return a list of argument keys.
        
        lense-devtools build {package} (optional) # Defaults to build all
        
        """
        return self._args.keys()
        
    def _command_help(self):
        return ("build: Build all or specific project in the current workspace")
        
    def _desc(self):
         return ("Lense DevTools\n\n"
                 "Tools to assist developers in developing and contributing\n"
                 "to Lense projects.")
        
    def _validate(self):
        """
        Perform argument validation.
        """
        commands = ['build']
        
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
        
        # Parse arguments
        argv.pop(0)
        self._args = vars(self.parser.parse_args(argv))
        
    def set(self, k, v):
        """
        Set a new argument or change the value.
        """
        self._args[k] = v
        
    def get(self, k, default=None):
        """
        Retrieve an argument passed via the command line.
        """
        return self._args.get(k, default)