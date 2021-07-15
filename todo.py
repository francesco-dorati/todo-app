#!/usr/bin/env python3
import sys
import os
import json
import datetime

# import requests

import helper
import logger
import storage


BASE_PATH = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
SETTINGS_PATH = BASE_PATH + 'settings.json'

# load settings
settings = None
if os.path.isfile(SETTINGS_PATH):
    settings = storage.load(SETTINGS_PATH)


def main():
    match sys.argv[1:]:
        # shell
        case[]:
            shell()

        # setup
        case['setup']:
            setup()

        # create local list
        case['create', 'local']:
            create('local')

        # create list
        case['create', 'list' | 'section' as type, list_name]:
            create(type, name)

        # rename
        case['rename', list_name, new_list_name]:
            pass

        # help
        case['h' | 'help']:
            logger.print_help()
            exit()

        # add
        case[list_name, 'a' | 'add', text, *args] if list_name in ['all', 'local']:
            deadline, position = None, None
            # load args
            if args:
                for index, arg in enumerate(args):
                    match arg:
                        # deadline
                        case 'd' | 'due':
                            deadline = args[index + 1]
                            if not deadline in ['today', 'tomorrow']:
                                logger.error('Deadline not available.')

                        # position
                        case 'p' | 'position':
                            position = args[index + 1]
            add(list_name, text.strip(), deadline, position)

        # update
        case[list_name, 'u' | 'update', index, text] if list_name in ['all', 'local']:
            update(list_name, index, text.strip())

        # remove
        case[list_name, 'r' | 'remove', index] if list_name in ['all', 'local']:
            remove(list_name, index)

        # move
        case[list_name, 'm' | 'move', index, destination] if list_name in ['all', 'local']:
            move(list_name, int(index), int(destination))

        # get
        case[list_name, *args] if list_name in ['all', 'local']:
            deadline = None
            if args and len(args) == 2:
                match args[0]:
                    # deadline
                    case 'd' | 'due':
                        deadline = args[1]
                        if not deadline in ['today', 'tomorrow']:
                            logger.error('Deadline not available.')
            get(list_name, deadline=deadline)

        case _:
            logger.error('Wrong Command')

# todo projects create todo-app
# todo projects todo-app add

# SHELL
def shell():
    current_list = 'all'
    logger.clear_screen()
    get(current_list)

    while True:
        command = input("\n> ").split()
        match command:
            # exit
            case['exit']:
                logger.clear_screen()
                exit()

            # current add
            case['a' | 'add', text]:
                logger.clear_screen()
                add(current_list, text.strip())

            # current update
            case['u' | 'update', index, text]:
                logger.clear_screen()
                update(current_list, int(index), text.strip())

            # current remove
            case['r' | 'remove', index]:
                logger.clear_screen()
                remove(current_list, int(index))

            # list get
            case[list_name]:
                current_list = list_name
                logger.clear_screen()
                get(current_list)

            # list add
            case[list_name, 'a' | 'add', text]:
                current_list = list_name
                logger.clear_screen()
                add(list_name, text.strip())

            # list update
            case[list_name, 'u' | 'update', index, text]:
                current_list = list_name
                logger.clear_screen()
                update(list_name, int(index), text.strip())

            # list remove
            case[list_name, 'r' | 'remove', index]:
                current_list = list_name
                logger.clear_screen()
                remove(list_name, int(index))

# SETUP
def setup():
    # ask for mode
    while True:
        mode = input("Mode (1: local, 2: remote): ")
        if mode == '1':
            mode = 'local'
            break
        elif mode == '2':
            mode = 'remote'
            break

    # local
    if mode == 'local':
        # ask for path
        while True:
            path = input("Path for todo folder (Enter for default): ")
            if path == '':  # default
                path = BASE_PATH
                break
            elif os.path.isdir(path):
                path = path.strip('/') + '/'
                break

        print('Creating files...')

        # create settings file
        storage.write(SETTINGS_PATH, {
            'mode': 'local',
            'path': path + '.todo'
        })

        # check if folder already exists
        if os.path.isfile(path + '.todo/all.todo'):
            while True:
                a = input(
                    'A todo folder already exists. Do you want to overwrite it [y/N]? ').lower()
                # overwrite
                if a == 'y' or a == 'yes':
                    print("Overwriting files...")
                    storage.write(path + '.todo/all.todo', {
                        'name': 'all',
                        'todos': [],
                    })
                    break

                # do not overwrite
                elif a == 'n' or a == 'no' or a == '':
                    break

        # if does not exist
        else:
            # create todo folder
            os.mkdir(path + '.todo')

            # create list all
            storage.write(path + '.todo/all.todo', {
                'name': 'all',
                'todos': [],
            })

        print("Done.")

    # remote
    else:
        # ask for path
        while True:
            path = input("Address for todo server: ")
            print('Connecting to server...')
            if True:    # TODO ping the server and break on response
                print('Connection successful.')
                break
            else:
                print('Server not responding, provide another address.')

        print('Creating files...')

        # create settings file
        storage.write(SETTINGS_PATH, {
            'mode': 'remote',
            'path': path,
        })

        print("Done.")

# CREATE
def create(type: str, name: str = None):
    match type:
        case 'list':
            if not name:
                logger.error("List name is required.")
                # todo

        case 'section':
            if not name:
                logger.error("List name is required.")
                # todo

        case 'local':
            if not name:
                name = os.path.basename(os.getcwd())

            # check if local file exists
            if os.path.isfile('local.todo'):
                while True:
                    a = input(
                        'A local todo list already exists. Do you want to overwrite it [y/N]? ').lower()
                    # do not overwrite
                    if a == 'n' or a == 'no' or a == '':
                        exit()

                    # overwrite
                    elif a == 'y' or a == 'yes':
                        break

            # create file
            storage.write('local.todo', {
                'name': name,
                'todos': []
            })

            print(f"Created new local list \"{name}\" successfully.")

# GET
def get(list_name: str, deadline: str = None):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # calculate list path
    match list_name:
        case 'all':
            path = settings['path'] + '/all.todo'
        case 'local':
            path = 'local.todo'
        case name if name in []:
            path = ''
        case _:
            logger.error("Inexisent list name.")

    # load file
    list = storage.load(path)

    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')

    # filter list by deadline
    helper.filter(list, deadline)

    # print the list
    logger.print_list(list)

# ADD
def add(list_name: str, text: str, deadline: str = None, position: str = None):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # calculate list path
    match list_name:
        case 'all':
            path = settings['path'] + '/all.todo'
        case 'local':
            path = 'local.todo'
        case name if name in []:
            path = ''
        case _:
            logger.error("Inexisent list name.")

    # load file
    list = storage.load(path)

    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')

    # build the todo
    todo = {
        'text': text,
        'time': str(datetime.datetime.now()),
        'deadline': str(helper.calculate_date(deadline)) if deadline else None,
        'children': []
    }

    # calculate index
    if position:
        # unpack indexes
        try:
            index_list = [int(i) - 1 for i in position.split(".")]
        except ValueError:
            logger.error("Invalid index.")

        # validate indexes
        current = list['todos']
        last_index = len(index_list) - 1
        for i, index in enumerate(index_list):
            # index out of range
            if index < 0:
                logger.error("Invalid index.")

            # index out of range
            if index >= len(current) and i != last_index:
                    logger.error("Invalid index.")
            
            # if last index
            if i == last_index:
                current.insert(index, todo)
                break

            # next child
            current = current[index]['children']

    # no position
    else:
        # insert the todo
        list['todos'].append(todo)

    # write to file
    storage.write(path, list)

    # print the list
    logger.print_list(list, add=text)

# UPDATE
def update(list_name: str, index: str, text: str):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # calculate list path
    match list_name:
        case 'all':
            path = settings['path'] + '/all.todo'
        case 'local':
            path = 'local.todo'
        case name if name in []:
            path = ''
        case _:
            logger.error("Inexisent list name.")

    # load file
    list = storage.load(path)
    
    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')

###########
    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # load file
            list = storage.load(settings['path'] + '/all.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'all\' is not set up yet. Initialize it by running \'todo setup\'')

            match list_name:
                case 'all':
                    # check if index is valid
                    if len(list['todos']) < index:
                        logger.error("Index value out of list.")

                    # update the todo
                    old_text = list['todos'][index - 1]['text']
                    list['todos'][index - 1]['text'] = text

                case 'today':
                    # check if index is valid
                    if len(helper.filter_today(list['todos'])) < index:
                        logger.error("Index value out of list.")

                    # filter todos
                    old = helper.filter_today(list['todos'])[index - 1]
                    old_text = old['text']
                    list['todos'][list['todos'].index(old)]['text'] = text

                case 'tomorrow':
                    # check if index is valid
                    if len(helper.filter_tomorrow(list['todos'])) < index:
                        logger.error("Index value out of list.")

                    # filter todos
                    old = helper.filter_tomorrow(list['todos'])[index - 1]
                    old_text = old['text']
                    list['todos'][list['todos'].index(old)]['text'] = text

            # write to file
            storage.write(settings['path'] + '/all.todo', list)

            # print the list
            match list_name:
                case 'all':
                    logger.print_list(
                        list['todos'], name=list_name, update=(old_text, text))

                case 'today':
                    logger.print_list(helper.filter_today(
                        list['todos']), name=list_name, update=(old_text, text))

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(
                        list['todos']), name=list_name, update=(old_text, text))

        case 'local':
            # load file
            list = storage.load('local.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'local\' is not set up yet. Initialize it by running \'todo create local\'')

            # update the todo
            old_text = list['todos'][index - 1]['text']
            list['todos'][index - 1]['text'] = text

            # write to file
            storage.write('local.todo', list)

            # print the list
            logger.print_list(
                list['todos'], name=list_name, update=(old_text, text))

        case _:
            pass

# REMOVE
def remove(list_name: str, index: str):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # unpack the indexes
    try:
        index_list = [int(i) - 1 for i in index.split(".")]
    except ValueError:
        logger.error("Invalid index.")

    # check if all indexes are positive
    if any(i < 0 for i in index_list):
        logger.error("Index value must be positive.")

    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # load file
            list = storage.load(settings['path'] + '/all.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'all\' is not set up yet. Initialize it by running \'todo setup\'')

            # remove the todo
            match list_name:
                case 'all':
                    # check if index is valid
                    if len(list['todos']) <= index_list[0]:
                        logger.error("Index value out of list.")

                case 'today':
                    # check if index is valid
                    if len(helper.filter_today(list['todos'])) <= index_list[0]:
                        logger.error("Index value out of list.")
                    index_list[0] = list['todos'].index(
                        helper.filter_today(list['todos'])[index - 1])

                case 'tomorrow':
                    # check if index is valid
                    if len(helper.filter_tomorrow(list['todos'])) <= index_list[0]:
                        logger.error("Index value out of list.")
                    index_list[0] = list['todos'].index(
                        helper.filter_tomorrow(list['todos'])[index - 1])

            # remove item
            if len(index_list) == 1:
                removed = list['todos'].pop(index_list[0])['text']
            else:
                removed = list['todos'][index_list[0]]['children'].pop(index_list[1])[
                    'text']

            # write to file
            storage.write(settings['path'] + '/all.todo', list)

            # print the list
            match list_name:
                case 'all':
                    logger.print_list(
                        list['todos'], name=list_name, remove=removed)

                case 'today':
                    logger.print_list(helper.filter_today(
                        list['todos']), name=list_name, remove=removed)

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(
                        list['todos']), name=list_name, remove=removed)

        case 'local':
            # load file
            list = storage.load('local.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'local\' is not set up yet. Initialize it by running \'todo create local\'')

            # check if index is valid
            if len(list['todos']) <= index_list[0]:
                logger.error("Index value out of list.")

            # remove item
            if len(index_list) == 1:
                removed = list['todos'].pop(index_list[0])['text']
            else:
                removed = list['todos'][index_list[0]]['children'].pop(index_list[1])[
                    'text']

            # write to file
            storage.write('local.todo', list)

            # print the list
            logger.print_list(list['todos'], name=list_name, remove=removed)

        case _:
            pass

# MOVE
def move(list_name: str, index: int, destination: int):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    if index < 1 or destination <= 0:
        logger.error("Index value must be positive.")

    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # load file
            list = storage.load(settings['path'] + '/all.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'all\' is not set up yet. Initialize it by running \'todo setup\'')

            match list_name:
                case 'all':
                    # check if index is valid
                    if len(list['todos']) < index or len(list['todos']) < destination:
                        logger.error("Index value out of list.")

                    relative_index, relative_destination = index - 1, destination - 1

                case 'today':
                    # check if index is valid
                    if len(list['todos']) < index or len(list['todos']) < destination:
                        logger.error("Index value out of list.")

                    # get real indexes
                    today = helper.filter_today(list['todos'])
                    relative_index = list['todos'].index(today[index - 1])
                    relative_destination = list['todos'].index(
                        today[destination - 1])

                case 'tomorrow':
                    # check if index is valid
                    if len(list['todos']) < index or len(list['todos']) < destination:
                        logger.error("Index value out of list.")

                    # get real indexes
                    tomorrow = helper.filter_tomorrow(list['todos'])
                    relative_index = list['todos'].index(tomorrow[index - 1])
                    relative_destination = list['todos'].index(
                        tomorrow[destination - 1])

            # change position of item
            item = list['todos'].pop(relative_index)
            list['todos'].insert(relative_destination, item)

            # write to file
            storage.write(settings['path'] + '/all.todo', list)

            # print the list
            match list_name:
                case 'all':
                    logger.print_list(list['todos'], name=list_name, move=(
                        item['text'], index, destination))

                case 'today':
                    logger.print_list(helper.filter_today(
                        list['todos']), name=list_name, move=(item['text'], index, destination))

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(
                        list['todos']), name=list_name, move=(item['text'], index, destination))

        case 'local':
            # load file
            list = storage.load('local.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'local\' is not set up yet. Initialize it by running \'todo create local\'')

            # check if index is valid
            if len(list['todos']) < index or len(list['todos']) < destination:
                logger.error("Index value out of list.")

            relative_index, relative_destination = index - 1, destination - 1

            # change position of item
            item = list['todos'].pop(relative_index)
            list['todos'].insert(relative_destination, item)

            # write to file
            storage.write('local.todo', list)

            # print the list
            logger.print_list(list['todos'], name=list_name, move=(
                item['text'], index, destination))


if __name__ == '__main__':
    main()

exit()
# ---

"""
    TODO
    - aggiungere possibilita si annullare il remove con undo (solo nella shell)

    commands
        - todo remove
            - "todo remove" multiple elements

    - fix readme
"""

names = {
    'main': 'main.todo',
    'local': 'local.todo',
    'config': 'config.json',
    'server': 'server.py'
}

base = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'

# load config
with open(base + names['config']) as file:
    config = json.load(file)

paths = {
    'main': base + names['main'],
    'local': names['local'],
    'remote': config['remote'],
    'config': base + names['config'],
    'server': base + names['server']
}

# load links
if os.path.isfile(paths['main']):
    with open(paths['main'], 'r') as file:
        links = json.load(file)['links']

        for name in links:
            paths[name] = links[name]

# add if remote
# # load remote links
# try:
#     response = requests.get(paths['remote'])
#     # check for status code
#     if response.status_code == 200:
#         for name in json.loads(response.text)['links']:
#             paths[name] = paths['remote'] + name
#     else:
#         print(response.text)
#         exit(2)
# except requests.exceptions.RequestException:
#     pass


def old_main():
    match sys.argv[1:]:
        # get
        case[]:
            data = get(config['mode'])
            print_list('get', data)

        # create
        case['create']:
            data = create('main')
            print_list('create', data)

        # add
        case['add', element]:
            data = add(config['mode'], element)
            print_list('add', data)

        # remove
        case['remove', index]:
            data = remove(config['mode'], index)
            print_list('remove', data)

        # all
        case['all']:
            data = get(config['mode'])
            # try:
            #     response = requests.get(paths['remote'])
            #     # check for status code
            #     if response.status_code == 200:
            #         for name in json.loads(response.text)['links']:
            #             data['links'][name] = paths['remote'] + name
            #     else:
            #         print(response.text)
            #         exit(2)
            # except requests.exceptions.RequestException:
            #     pass
            print_list('all', data)

        # mode get
        case['mode']:
            print_list('mode')

        # mode set
        case['mode', mode] if mode in ['remote', 'main', 'local']:
            # check if mode is already set
            if mode == config['mode']:
                print_error('mode', {
                    'error': 2,
                    'message': 'Mode already set.',
                    'mode': mode
                })

            # write changes to file
            else:
                config['mode'] = mode
                with open(paths['config'], 'w') as file:
                    json.dump(config, file)

                print_list('mode', {
                    'mode': mode
                })

        # serve
        case['serve']:
            from server import app
            app.run(host='0.0.0.0', port='5000', debug=True)

        # help
        case['help']:
            print_list('help')

        # create branch
        case['branch', name]:

            pass

        # # paths get
        # case [path] if path in paths:
        #     data = get(path)
        #     print_list('get', data)

        # # path create
        # case [path, 'create']:
        #     data = create(path)
        #     print_list('create', data)

        # # path add
        # case [path, 'add', element]:
        #     data = add(path, element)
        #     print_list('add', data)

        # # path remove
        # case [path, 'remove', index]:
        #     data = remove(path, index)
        #     print_list('remove', data)

        case[*command]:
            print(f"Illegal command {command}")
            exit(1)

# create


def old_create(mode, name=None):
    path = paths[mode]

    if mode == 'remote':
        exit(1)

    # check if file exists
    if os.path.isfile(path):
        print_error(
            'create', {'error': 1, 'message': 'file already exists.', 'path': path})

    # create data
    if mode == 'local':
        data = {
            'name': name if name else os.path.basename(os.getcwd()),
            'todos': []
        }

        # add to links
        with open(paths['main'], 'r') as file:
            main = json.loads(file.read())
            main['links'][data['name']] = os.getcwd() + '/' + \
                paths['local']

        with open(paths['main'], 'w') as file:
            json.dumps(main, file)

    else:
        data = {
            'name': 'main',
            'todos': [],
            'links': {}
        }

    # write to file
    with open(path, 'w') as file:
        json.dumps(data, file)

    return data


# GET
def old_get(mode):
    path = paths[mode]

    # if remote
    if 'http://' in path or 'https://' in path:
        try:
            response = requests.get(path)
        except requests.exceptions.RequestException:
            print_error(
                'get', {'error': 1, 'message': 'server not found', 'path': path})

        # check for status code
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.text)
            exit(2)

    # if local
    else:
        if not os.path.isfile(path):
            print_error(
                'get', {'error': 1, 'message': 'file not found', 'path': path})

        # read file
        with open(path, 'r') as file:
            return json.loads(file.read())

# ADD


def old_add(mode, added):
    path = paths[mode]

    # if remote
    if 'http://' in mode or 'https://' in mode:
        response = requests.post(path, data={'add': added})

        # check for status code
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.text)
            exit(2)

    # if local
    else:
        # check for file
        if not os.path.isfile(path):
            print_error(
                'add', {'error': 1, 'message': 'file not found', 'path': path})

        # get and append new todo
        data = get(mode)
        data['todos'].append(added)

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(data))

        return {
            'name': data['name'],
            'todos': data['todos'],
            'added': {
                'index': len(data['todos']) - 1,
                'text': added
            }
        }


# REMOVE
def old_remove(mode, removed):
    path = paths[mode]

    # if remote
    if 'http://' in mode or 'https://' in mode:
        response = requests.delete(path, params={'remove': sys.argv[2]})

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.text)
            exit(2)

    # if local
    else:
        # check for file
        if not os.path.isfile(path):
            print_error(
                'remove', {'error': 1, 'message': 'file not found', 'path': path})

        # get todos
        data = get(mode)
        removed_list = []

        # check index validity
        if ((not removed.isnumeric() and removed != 'all') or
                (removed.isnumeric() and (int(removed) > len(data['todos']) or int(removed) <= 0))):
            print_error(
                'remove', {'error': 2, 'message': 'invalid index.', 'path': path})

        # delete all
        if removed == 'all':
            for index, todo in enumerate(data['todos']):
                removed_list.append({'index': index, 'text': todo})
            data['todos'] = []

        # delete one
        elif removed.isnumeric():
            index = int(removed) - 1
            removed_list.append(
                {'index': index, 'text': data['todos'].pop(index)})

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(data))

        return {
            'name': data['name'],
            'todos': data['todos'],
            'removed': removed_list
        }


def print_bold(x, y=None): return cprint(x, y, attrs=['bold'], end='')


mode_color = {
    'remote': 'blue',
    'main': 'yellow',
    'local': 'magenta'
}


def print_list(action, data={}):
    # get add remove
    if action in ['get', 'add', 'remove', 'create', 'all']:
        # name color
        if data['name'] in mode_color:
            name_color = mode_color[data['name']]
        else:
            name_color = mode_color['local']

        # feedback
        if action == 'add':
            print_bold('\nAdded '),
            print_bold(f'"{data["added"]["text"]}" ', 'green')
            print_bold('successfully to ')
            print_bold(data['name'], name_color)
            print_bold('!\n')

        elif action == 'remove':
            print_bold('\nRemoved '),
            if len(data['todos']) == 0 and len(data['removed']) != 1:
                print_bold('all ', 'red')
            elif len(data['removed']) == 1:
                print_bold(f'"{data["removed"][0]["text"]}" ', 'red')
            print_bold('successfully from ')
            print_bold(data['name'], name_color)
            print_bold('!\n')

        elif action == 'create':
            if data['name'] == 'main':
                print_bold('\n')
                print_bold(data['name'], name_color)
                print_bold(' TODO list successfully created!\n')
            else:
                print_bold('\nLocal ')
                print_bold(data['name'], name_color)
                print_bold(' TODO list successfully created!\n')

        print_bold('\nYour ')
        print_bold(data['name'], name_color)
        print_bold(' TODOs:\n')

        # add
        if action == 'add':
            for index, todo in enumerate(data['todos']):
                if index == data['added']['index']:
                    print_bold(f'    [+] {todo}\n', 'grey')
                else:
                    print_bold(f'    [{index + 1}] {todo}\n', 'grey')

        # remove
        elif action == 'remove':
            for index, todo in enumerate(data['todos']):
                if any(removed['index'] == index for removed in data['removed']):
                    print_bold(
                        f'   [-] {data["removed"][0]["text"]}\n', 'red')
                    data['removed'].pop(0)

                print_bold(f'   [{index + 1}] {todo}\n', 'grey')

            # print remaining removed todos
            for todo in data['removed']:
                print_bold(f'   [-] {todo["text"]}\n', 'red')

        # get and all
        else:
            # todos present
            if len(data['todos']) > 0:
                for index, todo in enumerate(data['todos']):
                    print_bold(f'   [{index + 1}] {todo}\n', 'grey')

            # no todos
            else:
                print_bold('    [?] This TODO list is empty\n', 'grey')
                print_bold(f'\nAdd one by running: ', 'grey')
                print_bold(
                    f'todo {"local " if not data["name"] == "main" else ""}add <todo>\n', 'grey')

        if action == 'all':

            print_bold('\nOther lists:\n')

            # main
            print_bold('main\n', mode_color['main']) if config['mode'] != 'main' and os.path.isfile(
                paths['main']) else None

            # remote
            # try:
            #     print_bold('remote\n', mode_color['remote']) if config['mode'] != 'remote' and requests.get(paths['remote']) else None
            # except requests.exceptions.RequestException:
            #     pass

            # local
            print_bold('local\n', mode_color['local']) if config['mode'] != 'local' and os.path.isfile(
                paths['local']) else None

            for list in data['links']:
                if 'http://' in data['links'][list] or 'https://' in data['links'][list]:
                    color = mode_color['remote']
                else:
                    color = mode_color['local']

                if not list in ['main', 'remote', 'local', 'config', 'server']:
                    print_bold(list, color)
                    print_bold('\t(' + data['links'][list] + ')\n', 'grey')

    # settings
    elif action == 'mode':
        if data:
            print_bold('\nMode set to ')
            print_bold(data['mode'], mode_color[data['mode']])
            print_bold('\n')

        print_bold('\nMode:\n')
        print_bold(
            '[✓]', 'green') if config['mode'] == 'main' else print_bold('[ ]')
        print_bold(' main\n', mode_color['main'])
        print_bold(
            '[✓]', 'green') if config['mode'] == 'remote' else print_bold('[ ]')
        print_bold(' remote\n', mode_color['remote'])
        print_bold(
            '[✓]', 'green') if config['mode'] == 'local' else print_bold('[ ]')
        print_bold(' local\n', mode_color['local'])

        if data:
            print_bold('\nNow you can access ', 'grey')
            print_bold(data['mode'], 'grey')
            print_bold(' just by running: todo\n', 'grey')
        else:
            print_bold('\nEdit with: todo mode <mode>\n', 'grey')

    elif action == 'help':
        title = None
        color = 'grey'
        print_bold('\nUsage: todo [options]\n', title)
        print_bold('\nOptions:\n', title)
        print_bold(
            '  create                               -   creates a new main list\n', color)
        print_bold(
            '  add <todo>                           -   adds a new todo to the default list\n', color)
        print_bold(
            '  remove <index>                       -   removes a new todo to the default list\n', color)
        print_bold(
            '  all                                  -   prints all todolists\n', color)
        print_bold(
            '  local [create | add | remove]        -   work with local todolist\n', color)
        print_bold(
            '  <listname> [create | add | remove]   -   work with specific todolist\n', color)
        print_bold('\nColors:\n', title)
        print_bold('yellow', 'yellow')
        print_bold('\t- main list\n', color)
        print_bold('blue', 'blue')
        print_bold('\t- remote list\n', color)
        print_bold('purple', 'magenta')
        print_bold('\t- local list\n', color)


def print_error(action, data={}):
    print_bold('\nError: ', 'red')
    if action in ['get', 'add', 'remove']:
        # file not found
        if data['error'] == 1:
            if 'http://' in data['path'] or 'https://' in data['path']:
                print_bold('No ')
                print_bold('remote', mode_color['remote'])
                print_bold(' TODO list found.\n')
                print_bold('\nCheck the URL in the config file.\n', 'grey')
            elif data['path'] == paths['local']:
                print_bold('No ')
                print_bold('local', mode_color['local'])
                print_bold(' TODO list found.\n')
                print_bold(
                    '\nCreate one by running: todo local create [<name>]\n', 'grey')
            else:
                print_bold('No ')
                print_bold('main', mode_color['main'])
                print_bold(' TODO list found.\n')
                print_bold('\nCreate by running: todo create\n', 'grey')
        if action == 'remove' and data['error'] == 2:
            print_bold('Invalid index.\n')

    elif action == 'create':
        if data['error'] == 1:
            if data['path'] == paths['local']:
                name = get(paths['local'])['name']
                print_bold('local', mode_color['local'])
                print_bold(' TODO list already exists as ')
                print_bold(name, mode_color['local'])
                print_bold('.\n')
            else:
                print_bold('main', mode_color['main'])
                print_bold(' TODO list already exists in ')
                print_bold(data['path'], mode_color['main'])
                print_bold('.\n')

    elif action == 'mode':
        if data['error'] == 1:
            print_bold('Wrong index.\n')

        elif data['error'] == 2:
            print_bold('Mode already set to ')
            print_bold(data['mode'], mode_color[data['mode']])
            print_bold('.\n')

    # exit
    exit(data['error'])


if __name__ == '__main__':
    main()
