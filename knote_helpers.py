import datetime

def day_parse(day_str):
    try:
        ymd = day_str.split("-")
        return datetime.date(int(ymd[0]), int(ymd[1]), int(ymd[2]))
    except:
        return None

def time_parse(time_str):
    try:
        time_str = time_str.upper()
        isPM = "PM" in time_str

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
