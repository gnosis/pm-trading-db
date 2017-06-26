import os
import json

def abi_file_path(file):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), file))


def load_json_file(path):
    return json.load(open(path))
