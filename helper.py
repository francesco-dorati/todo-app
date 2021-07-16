import datetime
import os
import json

def is_today(deadline) -> bool:
    if not deadline:
        return False

    return datetime.date.today() >= datetime.date.fromisoformat(deadline)

def is_tomorrow(deadline) -> bool:
    if not deadline:
        return False

    return datetime.date.today() + datetime.timedelta(days=1) >= datetime.date.fromisoformat(deadline) and not is_today(deadline)

def calculate_date(deadline: str):
    match deadline:
        case 'today':
            return datetime.date.today()
        case 'tomorrow':
            return datetime.date.today() + datetime.timedelta(days=1)

def filter(list: dict, deadline: str):
    def recursive_filter(list: list, validator):
        filtered = []
        for todo in list:
            todo['children'] = recursive_filter(todo['children'], validator)
            if validator(todo['deadline']) or todo['children']:
                filtered.append(todo)
        return filtered

    match deadline:
        case 'today':
            list['name'] = 'today'
            list['todos'] = recursive_filter(list['todos'], is_today)
        case 'tomorrow':
            list['name'] = 'tomrrow'
            list['todos'] = recursive_filter(list['todos'], is_tomorrow)

    return list


def unpack_indexes(index_string: str, list: list) -> list:
    try:
        index_list = [int(i) - 1 for i in index_string.split(".")]
    except ValueError:
        return False

    # validate indexes
    for index in index_list:
        # index out of range
        if index < 0:
            return False

        # index out of range
        if index > len(list):
            return False

        # next child
        list = list[index]['children']

    return index_list 

def load_file(path: str) -> dict | None:
    if not os.path.isfile(path):
        return None

    with open(path, 'r') as file:   
        return json.load(file)

def write_file(path: str, data: dict):
	with open(path, 'w') as file:
		json.dump(data, file)
