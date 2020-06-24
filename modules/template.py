from helpers import *


class Module:
    """This is an example of how a module should look."""

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6"],
            "Description": "This is an example module."
        }
        self.example_message = None

    def setup(self):
        """This method is called before a module is sent, used to set variables.

        :return True if the setup was successful.
        """
        self.example_message = raw_input(MESSAGE_INPUT + "Message to print: ")
        return True

    def run(self):
        """This is the code which gets executed on the client."""
        return """\
        print "Example message: " + "{0}"
        """.format(self.example_message)

    def process_response(self, response):
        """Optional method which processes the response."""
        print "\n" + response.replace("Example message", "Processed example message")
