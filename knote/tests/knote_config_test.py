import datetime
import json

# fix for 'double import'
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from knote_config import TimePeriods, Subject, Config, ConfigEncoder, config_dict_from_json, get_config_file, DAYS_STR
from knote_editors import Editor

# some testing constants
today = datetime.datetime.now().date()
now = datetime.datetime.combine(today, datetime.time(8,30,00))
cur_day = DAYS_STR[today.weekday()].lower()
next_day = DAYS_STR[(today.weekday() + 1) % len(DAYS_STR)].lower()
prev_day = DAYS_STR[(today.weekday() - 1) % len(DAYS_STR)].lower()
start_time = datetime.time(00,00,00)
end_time = datetime.time(23,59,59)
start_date = today - datetime.timedelta(days=1)
end_date = today + datetime.timedelta(days=1)
tp_cur = TimePeriods(days=[cur_day], start=start_time, end=end_time)
tp_prev = TimePeriods(days=[prev_day], start=start_time, end=end_time)
tp_next = TimePeriods(days=[next_day], start=start_time, end=end_time)
start_datetime = datetime.datetime.combine(start_date, start_time)
end_datetime = datetime.datetime.combine(end_date, end_time)
notepad = Editor("NotePad", "notepad.exe")
vim = Editor("Vim", "vim.exe")

# do not call save ever on the return value
def create_empty_config():
    config = Config()
    config.subjects = []
    return config

# tests ability to construct the path
def test_get_config_file():
    assert get_config_file() != None

def test_time_period():
    not_now = now + datetime.timedelta(days=2)

    tp = TimePeriods(days=[cur_day], start=start_time, end=end_time)

    # fail
    assert not tp.contains(not_now)

    # single day
    assert tp.contains(now)

    # multiple days match
    tp.days.append(prev_day)
    tp.days.append(next_day)
    assert tp.contains(now)

    # multiple days no-match
    assert not tp.contains(not_now)

def test_subject():
    subject = Subject("test", None, [tp_cur, tp_next, tp_prev], start_date, end_date)

    # test contains
    assert subject.is_active(now)

    # test start
    assert subject.is_active(start_datetime)

    # test end
    assert not subject.is_active(end_datetime)

    # test out of start/end date
    assert not subject.is_active(now - datetime.timedelta(days=3))

def create_test_config():
    config = create_empty_config()
    s1 = Subject("s1", notepad, [tp_cur, tp_next], start_date, end_date, "out")
    s2 = Subject("s2", vim, [tp_prev], start_date, end_date)
    config.add_subject(s1)
    config.add_subject(s2)
    return config

def test_config_add():
    config = create_test_config()
    assert len(config.subjects) == 2

def test_config_delete():
    config = create_test_config()

    subjects_to_delete = [subject.name for subject in config.subjects]
    for subject_name in subjects_to_delete:
        config.remove_subject(subject_name)

    assert len(config.subjects) == 0

def test_config_update():
    config = create_test_config()
    
    s_new = config.subjects[0]
    s_new.periods = s_new.periods[1:]

    assert config.update_subject(s_new)

def test_config_get_active_subject():
    config = create_test_config()
    active = config.get_active_subject(now)
    assert active.name == "s1"

def test_config_json_ops():
    config = create_test_config()

    config_str = json.dumps(config, indent=4, cls=ConfigEncoder)

    config_data = json.loads(config_str)

    config_dict = config_dict_from_json(config_data)

    parsed_config = create_test_config()
    parsed_config.__dict__ = config_dict

    assert isinstance(parsed_config, Config)
    assert len(parsed_config.subjects) == 2

    for subject in parsed_config.subjects:
        assert isinstance(subject, Subject)
        assert len(subject.periods) > 0
        assert isinstance(subject.start_date, datetime.date)
        assert isinstance(subject.end_date, datetime.date)
        for tp in subject.periods:
            assert isinstance(tp, TimePeriods)
            assert tp.days is not None
            assert tp.start is not None
            assert tp.end is not None
            assert isinstance(tp.start, datetime.time)
            assert isinstance(tp.end, datetime.time)