import json
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

KNOTE_EDITORS = "knote_editors.json"

def create_default_editors():
    try:
        with open(KNOTE_EDITORS, "w") as json_file:
            editors = []
            editors.append(Editor("NotePad", "notepad.exe"))
            editors.append(Editor("Vim", "vim.exe"))
            json.dump(editors, json_file, indent=4, cls=EditorsEncoder)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

def read_editors_from_file(json_file=KNOTE_EDITORS):
    editors = []
    try:
        with open(json_file, "r") as json_file:
            editors_data = json.load(json_file)
            for editor_data in editors_data:
                editor = Editor()
                editor.__dict__ = editor_data
                editors.append(editor)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
    finally:
        return editors