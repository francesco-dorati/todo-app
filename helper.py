import datetime
def today():
    return datetime.date.today()

def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def is_today(expiration) -> bool:
    if not expiration:
        return False

    return datetime.date.today() >= datetime.date.fromisoformat(expiration)

def is_tomorrow(expiration) -> bool:
    if not expiration:
        return False

    return datetime.date.today() + datetime.timedelta(days=1) >= datetime.date.fromisoformat(expiration) and not is_today(expiration)


def filter_today(list: list) -> list:
    filtered = []
    for todo in list:
        if is_today(todo["expiration"]):
            filtered.append(todo)
    return filtered


def filter_tomorrow(list: list) -> list:
    filtered = []
    for todo in list:
        if is_tomorrow(todo["expiration"]):
            filtered.append(todo)
    return filtered
