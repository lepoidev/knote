import json

from knote.knote_editors import EditorEncoder, EditorsEncoder, Editor, parse_editor_list, get_knote_editors_path

def test_get_knote_editors_path():
    assert get_knote_editors_path() != None

def test_editor_json():
    # create json
    editors = []
    editors.append(Editor("NotePad", "notepad.exe"))
    editors.append(Editor("Vim", "vim.exe"))
    json_out = json.dumps(editors, indent=4, cls=EditorsEncoder)

    # parse json
    editors_data = json.loads(json_out)
    parsed_editors = parse_editor_list(editors_data)

    # compare
    for editor in editors:
        found = False
        for parsed_editor in parsed_editors:
            if editor.__dict__ == parsed_editor.__dict__:
                found = True
                break
        assert found