import json
import os
import sys
import datetime
import calendar
import knote_helpers

from knote_editors import Editor

from typing import Dict
from json import JSONEncoder

DAYS_STR = "MTWRFSU"

def get_config_file():
    config_file = os.getenv("KNOTE_CONFIG")
    if config_file is None:
        knote_path = os.getenv("KNOTE_PATH")
        if knote_path is None:
            sys.stderr.write("missing enviroment variable \"KNOTE_PATH\"")
            sys.exit(1)
        default_config = os.path.join("config", "knote_config.json")
        config_file = os.path.join(knote_path, default_config)
    return config_file

def get_config_data():
    config_data = None
    config_file = get_config_file()
    try:
        with open(config_file, "r") as json_file:
            config_data = json.load(json_file)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
    finally:
        return config_data

class TimePeriods:
    def __init__(self, days=[], start=None, end=None):
        self.days = days
        self.start = start
        self.end = end

    def contains(self, active_datetime) -> bool:
        date = active_datetime.date()
        time = active_datetime.time()
        cur_day = DAYS_STR[date.weekday()].lower()
        matches_day = cur_day in [d.lower() for d in self.days]
        matches_time = self.start <= time and time < self.end
        return matches_day and matches_time

    @classmethod
    def from_json(cls, data):
        try:
            timeperiods = TimePeriods()
            timeperiods.__dict__ = data

            start_str = data["start"]
            end_str = data["end"]
            timeperiods.start = knote_helpers.time_parse(start_str)
            timeperiods.end = knote_helpers.time_parse(end_str)

            return timeperiods
        except:
            return None

class Subject:
    def __init__(self, name=None, app=None, periods=[], start_date=None, end_date=None, ext="txt"):
        self.name = name
        self.app = app
        self.periods = periods
        self.start_date = start_date
        self.end_date = end_date
        self.ext = ext

    def is_active(self, active_datetime) -> bool:
        matches = list(filter(lambda period : period.contains(active_datetime), self.periods))
        return len(matches) > 0

    @classmethod
    def from_json(cls, data):
        try:
            subject = Subject()
            subject.__dict__ = data
            subject.app = Editor.from_json(data["app"])
            subject.periods = list(map(TimePeriods.from_json, data["periods"]))
            subject.start_date = knote_helpers.date_parse(data["start_date"])
            subject.end_date = knote_helpers.date_parse(data["end_date"])
            return subject
        except:
            return None

class ConfigEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        return o.__dict__


def config_dict_from_json(data):
    try:
        d = data
        d["subjects"] = list(map(Subject.from_json, data["subjects"]))
        return d
    except:
        return {}

class Config:
    def __init__(self):
        config_data = get_config_data()
        if config_data is None:
            self.subjects = []
        else:
            self.__dict__ = config_dict_from_json(config_data)

    def find_subject(self, classname):
        match = list(filter(lambda existing_subj : classname == existing_subj.name, self.subjects))
        if len(match) > 1:
            print("Corrupt config file")
            sys.exit(1)

        if len(match) == 0:
            match = None
        else:
            match = match[0]
        return match

    def remove_subject(self, classname):
        subject = self.find_subject(classname)
        if(subject is not None):
            self.subjects.remove(subject)

    def add_subject(self, subject) -> bool:
        if subject is None:
            return False
        match = self.find_subject(subject.name)

        if match is not None:
            overwrite = None
            while overwrite not in ("Y","y","N","n"):
                overwrite = input("Subject already exists. Overwrite? (Y/N): ")
            if overwrite.lower() == "y":
                self.subjects.remove(match)
            else:
                return False

        self.subjects.append(subject)
        return True

    def update_subject(self, subject) -> bool:
        for old_subject in self.subjects:
            if old_subject.name == subject.name:
                self.subjects.remove(old_subject)
                self.subjects.append(subject)
                return True
        return False

    def get_active_subject(self, active_datetime) -> Subject:
        matches = list(filter(lambda subject : subject.is_active(active_datetime), self.subjects))
        if len(matches) > 1:
            subject_names = [(lambda subject : subject.name)(subject) for subject in matches]
            active_subject = None
            while active_subject not in subject_names:
                active_subject = input("Multiple subjects are active in is time period:\n\t" + str(subject_names) + "\nSelect one of the above or \'q\' to quit: ")
                if(active_subject.lower() == "q"):
                    sys.exit(0)
            return matches[subject_names.index(active_subject)]
        elif (len(matches) == 1):
            return matches[0]
        else:
            return None

    def get_current_subject(self) -> Subject:
        return self.get_active_subject(datetime.datetime.now())

    def save(self):
        config_file = get_config_file()
        try:
            with open(config_file, "w") as json_file:
                json.dump(self, json_file, indent=4, cls=ConfigEncoder)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
