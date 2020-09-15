from knote_config import Config

def list_cmd():
    config = Config()
    config.save()

def configure_cmd():
    pass

def open_cmd(classname):
    pass

def edit_cmd(classname):
    pass

def remove_cmd(classname):
    pass

def new_cmd():
    pass

def open_current_cmd():
    config = Config()
    current_subject = config.get_current_subject()
    open_cmd(current_subject.name)