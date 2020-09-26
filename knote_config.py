import json
import os
import sys
import datetime
import calendar
import knote_helpers

from typing import Dict
from json import JSONEncoder

def get_config_file():
    config_file = os.getenv('KNOTE_CONFIG')
    if config_file is None:
        knote_path = os.getenv('KNOTE_PATH')
        if knote_path is None:
            sys.stderr.write('missing enviroment variable \"KNOTE_PATH\"')
            sys.exit(1)
        config_file = os.path.join(knote_path, 'knote_config.json')
    return config_file

def get_config_data():
    config_data = None
    config_file = get_config_file()
    try:
        with open(config_file, 'r') as json_file:
            config_data = json.load(json_file)
    except IOError as e:
        print('I/O error({0}): {1}'.format(e.errno, e.strerror))
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
        matches_day = calendar.day_abbr[date.weekday()] in self.days
        matches_time = self.start <= time and time <= self.end
        return matches_day and matches_time

    @classmethod
    def from_json(cls, data):
        try:
            timeperiods = TimePeriods()
            timeperiods.__dict__ = data

            timeperiods.start = knote_helpers.time_parse(data["start"])
            timeperiods.end = knote_helpers.time_parse(data["end"])

            return timeperiods
        except:
            return None

class Subject:
    def __init__(self, name=None, app=None, periods=[], start_date=None, end_date=None):
        self.name = name
        self.app = app
        self.periods = periods
        self.start_date = start_date
        self.end_date = end_date

    def is_active(self, active_datetime) -> bool:
        matches = list(filter(lambda period : period.contains(active_datetime), self.periods))
        return len(matches) > 0

    @classmethod
    def from_json(cls, data):
        try:
            subject = Subject()
            subject.__dict__ = data
            subject.periods = list(map(TimePeriods.from_json, data["periods"]))
            subject.start_date = knote_helpers.day_parse(data["start_date"])
            subject.end_date = knote_helpers.day_parse(data["end_date"])
            return subject
        except:
            return None

class ConfigEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        return o.__dict__


def dict_from_json(data):
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
            self.__dict__ = dict_from_json(config_data)

    def add_subject(self, subject) -> bool:
        if subject is None:
            return False
        match = list(filter(lambda existing_subj : existing_subj.name == subject.name, self.subjects))
        if len(match) > 1:
            print('Corrupt config file')
            sys.exit(1)

        if len(match) == 0:
            match = None
        else:
            match = match[0]

        if match is not None:
            overwrite = None
            while overwrite not in ('Y','y','N','n'):
                overwrite = input('Subject already exists. Overwrite? (Y/N): ')
            if overwrite.lower() == 'y':
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
                active_subject = input('Multiple subjects are active in is time period:\n\t' + str(subject_names) + '\nSelect one of the above: ')
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
            with open(config_file, 'w') as json_file:
                json.dump(self, json_file, indent=4, cls=ConfigEncoder)
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
