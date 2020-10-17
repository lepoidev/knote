import json
import os
import sys
from json import JSONEncoder

class EditorEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class EditorsEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Editor:
    def __init__(self, name=None, command=None):
        self.name = name
        self.command = command

    @classmethod
    def from_json(cls, data):
        editor = Editor()
        editor.__dict__ = data
        return editor

def get_knote_editors_path():
    knote_path = os.getenv("KNOTE_PATH")
    if knote_path is None:
        sys.stderr.write("missing enviroment variable \"KNOTE_PATH\"")
        sys.exit(1)

    knote_editors = os.path.join(knote_path, "knote_editors.json")
    return knote_editors

def create_default_editors():
    try:
        knote_editors = get_knote_editors_path()
        with open(knote_editors, "w") as json_file:
            editors = []
            editors.append(Editor("NotePad", "notepad"))
            editors.append(Editor("Vim", "vim"))
            json.dump(editors, json_file, indent=4, cls=EditorsEncoder)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

def parse_editor_list(editors_data):
    editors = []
    for editor_data in editors_data:
        try:
            editor = Editor()
            editor.__dict__ = editor_data
            editors.append(editor)
        finally:
            pass
    return editors

def read_editors_from_file(json_file=get_knote_editors_path()):
    editors = []
    try:
        with open(json_file, "r") as json_file:
            editors_data = json.load(json_file)
            editors = parse_editor_list(editors_data)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        return []

    return editors