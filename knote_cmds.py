import datetime

from datetime import date
from datetime import time
from knote_config import Config, Subject, TimePeriods
from knote_editors import read_editors_from_file

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

def time_parse(time_str):
    try:
        time_str = time_str.upper()
        isAM = "AM" in time_str
        isPM = "PM" in time_str
        if not(isAM or isPM):
            return None

        time_str = time_str.replace("AM", "")
        time_str = time_str.replace("PM", "")

        l = time_str.split(":")
        h = int(l[0])
        m = int(l[1])

        if isPM:
            h += 12

        return datetime.time(h, m)
    except:
        return None

def new_cmd():
    config = Config()

    name = input("Enter Subject name 'q' to quit: ")
    if name.lower() == "q":
        return

    # get start and end dates
    start_date = None
    start_date_str = ""
    while(True):
        start_date_str = input("Enter the start date YYYY-MM-DD 'q' to quit: ")
        if start_date_str.lower() == "q":
            return
        try:
            start_date = date.fromisoformat(start_date_str)
            break
        except:
            print("Invalid string...\n")

    end_date = None
    end_date_str = ""
    while(True):
        end_date_str = input("Enter the end date YYYY-MM-DD 'q' to quit: ")
        if end_date_str.lower() == "q":
            return
        try:
            end_date = date.fromisoformat(end_date_str)
            break
        except:
            print("Invalid string...\n")

    # get time periods
    periods = []

    done_adding = False
    while(not(done_adding)):
        day_str = ""
        period_start_str = ""
        period_end_str = ""

        day_set = set()
        days = []
        period_start = None
        period_end = None

        # get day
        while((len(days) == 0) and not(done_adding)):
            day_str = input("Enter days of period (MTWRFSU) 'q' to quit, 's' to stop adding periods: ")
            if day_str.lower() == "q":
                return
            elif day_str.lower() == 's':
                done_adding = True
                break

            try:
                for day in day_str:
                    if day.upper() in "MTWRFSU":
                        day_set.add(day)
                    else:
                        print("unexpected character: '" + str(day) + "'")
                days = list(day_set)
            except:
                pass

        # get start_time
        while((period_start is None) and not(done_adding)):
            period_start_str = input("Enter start of period HH:MM(AM|PM) 'q' to quit, 's' to stop adding periods: ")
            if period_start_str.lower() == "q":
                return
            elif period_start_str.lower() == 's':
                done_adding = True
                break

            period_start = time_parse(period_start_str)

        # get end time
        while((period_end is None) and not(done_adding)):
            period_end_str = input("Enter end of period HH:MM(AM|PM) 'q' to quit, 's' to stop adding periods: ")
            if period_end_str.lower() == "q":
                return
            elif period_end_str.lower() == 's':
                done_adding = True
                break

            period_end = time_parse(period_end_str)

        if not(done_adding):
            periods.append(TimePeriods(days, period_start, period_end))


    # choose app to open with
    editors = read_editors_from_file()
    print("Editors:")
    for editor in editors:
        print("\t" + editor.name)
    chosen = None
    while(chosen is None):
        chosen_str = input("Choose an editor from above 'q' to quit, 's' to stop adding periods: ")
        if period_start_str.lower() == "q":
            return
        elif period_start_str.lower() == 's':
            done_adding = True
        chosen = next((editor for editor in editors if editor.name.lower() == chosen_str.lower()), None)


    subject = Subject(name, chosen, periods, start_date, end_date)
    config.add_subject(subject)
    config.save()

def open_current_cmd():
    config = Config()
    current_subject = config.get_current_subject()
    open_cmd(current_subject.name)