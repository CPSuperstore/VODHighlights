import datetime


def display_time(seconds: float) -> str:
    return str(datetime.timedelta(seconds=float(seconds))).split(".")[0]
