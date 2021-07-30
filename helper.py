import datetime
import os
import json

from logger import error

def load_lists(path: str) -> dict:
    res = {
        'all': path + '/all.todo',  'a': path + '/all.todo',
        'local': 'local.todo',      'l': 'local.todo',
    }

    # loop for files in todo folder
    for filename in os.listdir(path):
        if filename == 'all.todo':
            continue
        
        if filename[-5:] == '.todo':
            res[filename[:-5]] = path + '/' + filename
    
    return res


# DATE
# date to str
def compute_date(date) -> str:
    if not date:
        return ''

    # today
    elif datetime.date.today() >= datetime.date.fromisoformat(date):
        return 'today'
    
    # tomorrow
    elif datetime.date.today() + datetime.timedelta(days=1) >= datetime.date.fromisoformat(date):
        return 'tomorrow' 
    
    else:
        return date
# str to date
def calculate_date(deadline: str) -> datetime:
    match deadline:
        case 'today':
            return datetime.date.today()
        case 'tomorrow':
            return datetime.date.today() + datetime.timedelta(days=1)


def filter(list: dict, deadline: str) -> list:
    def recursive_filter(list: list, deadline: str = None):
        filtered = []
        for todo in list:
            todo['children'] = recursive_filter(todo['children'], deadline)
            # filter by deadline
            if deadline:
                if compute_date(todo['deadline']) == deadline or todo['children']:
                    filtered.append(todo)
        return filtered

    if deadline:
        list['todos'] = recursive_filter(list['todos'], deadline)

    return list

def unpack_indexes(index_string: str, list: list = None) -> list:
    try:
        index_list = [int(i) - 1 for i in index_string.split(".")]
    except ValueError:
        error('Invalid index.')

    # validate indexes
    for index in index_list:
        # index out of range
        if index < 0:
            error('Invalid index.')

        # index out of range
        if list: 
            if index >= len(list):
                error('Invalid index.')

            # next child
            list = list[index]['children']

    return index_list 


# FILE
# load
def load_file(path: str) -> dict | None:
    if not os.path.isfile(path):
        return None

    with open(path, 'r') as file:   
        return json.load(file)

# write
def write_file(path: str, data: dict) -> None:
	with open(path, 'w') as file:
		json.dump(data, file)

# delete
def delete_file(path: str):
    if os.path.isfile(path):
        os.remove(path)
    else:
        error('Invalid path.')