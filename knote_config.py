import json
import os
import sys
import datetime
import calendar

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
    def __init__(self):
        self.days = []
        self.start = None
        self.end = None

    def contains(self, active_datetime) -> bool:
        date = active_datetime.date()
        time = active_datetime.time()
        matches_day = calendar.day_abbr[date.weekday()] in self.days
        matches_time = self.start <= time and time <= self.end
        return matches_day and matches_time

class Subject:
    def __init__(self):
        self.name = None
        self.app = None
        self.periods = []
        self.start_date = None
        self.end_date = None

    def is_active(self, active_datetime) -> bool:
        matches = filter(lambda period : period.contains(active_datetime), self.periods)
        return len(matches) > 0

class ConfigEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Config:
    def __init__(self):
        config_data = get_config_data()
        if config_data is None:
            self.subjects = []
        else:
            self.__dict__ = config_data

    def add_subject(self, subject):
        match = list(filter(lambda existing_subj : existing_subj.name == subject.name, self.subjects))
        if len(match) > 1:
            print('Corrupt config file')
            sys.exit(1)

        match = match[0]
        if match is not None:
            overwrite = None
            while overwrite not in ('Y','y','N','n'):
                overwrite = input('Subject already exists. Overwrite? (Y/N): ')
            if overwrite.lower() == 'y':
                self.subjects.remove(match)
            else:
                return

        self.subjects.append(subject)

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
        else:
            return matches[0]

    def get_current_subject(self) -> Subject:
        return self.get_active_subject(datetime.datetime.now())

    def save(self):
        config_file = get_config_file()
        try:
            with open(config_file, 'w') as json_file:
                json.dump(self, json_file, indent=4, cls=ConfigEncoder)
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
