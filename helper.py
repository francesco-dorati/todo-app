import os
import datetime

def clear():
  
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


def today():
    return datetime.date.today()

def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)