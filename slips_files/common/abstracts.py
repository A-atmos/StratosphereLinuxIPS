from abc import ABC, abstractmethod
# This is the abstract Module class to check against. Do not modify
class Module(ABC):
    name = ''
    description = 'Template abstract module'
    authors = ['Template abstract Author']

    def __init__(self, outputqueue):
        self.outputqueue = outputqueue

    def print(self, text, verbose=1, debug=0):
        """
        Function to use to print text using the outputqueue of slips.
        Slips then decides how, when and where to print this text by taking all the processes into account
        :param verbose:
            0 - don't print
            1 - basic operation/proof of work
            2 - log I/O operations and filenames
            3 - log database/profile/timewindow changes
        :param debug:
            0 - don't print
            1 - print exceptions
            2 - unsupported and unhandled types (cases that may cause errors)
            3 - red warnings that needs examination - developer warnings
        :param text: text to print. Can include format like 'Test {}'.format('here')
        """

        levels = f'{verbose}{debug}'
        self.outputqueue.put(f'{levels}|{self.name}|{text}')

    @abstractmethod
    def shutdown_gracefully(self):
        """
        Tells slips.py that this module is
        done processing and does necessary cleanup
        """

    @abstractmethod
    def run(self):
        """ Main function """