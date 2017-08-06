import json
import os

class FileOperations:

    def __init__(self, filename):
        self.filename = filename

    def save_setup(self, elements_to_store):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(self.filename, 'w') as outfile:
                json.dump(elements_to_store, outfile)
        except Exception as e:
            print("Exception: " + e)
            pass

    def parse_setup(self):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(location, self.filename)) as config_file:
                return json.load(config_file)
        except Exception as e:
            print("Exception: " + e)
            pass