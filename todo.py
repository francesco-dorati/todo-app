#!/usr/bin/env python3
import sys
import os
import json
import requests
import datetime

from termcolor import cprint

import helper
import logger

"""
lists/sections:
- today
- tomorrow
- this week
- next week

- local
- <other>
"""

base_path = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
settings_path = base_path + 'settings.json'


# load settings
settings = None
if os.path.isfile(settings_path):
    with open(settings_path, 'r') as file:
        settings = json.load(file)


def main():
    match sys.argv[1:]:
        # shell
        case []:
            shell()
        
        # setup
        case ['setup']:
            setup()

        # create list
        case ['create', 'list' | 'section' as type, list_name]:
            create(type, name)

        # create local list
        case ['create', 'local']:
            create('local')

        # rename
        case ['rename', list_name, new_list_name]:
            pass

        # help
        case ['help']:
            pass

        # get
        case [list_name]:
            get(list_name)

        # add
        case [list_name, 'a' | 'add', text]:
            add(list_name, text.strip())

        # update
        case [list_name, 'u' | 'update', index, text]:

            update(list_name, int(index), text.strip())

        # remove
        case [list_name, 'r' | 'remove', index]:
            remove(list_name, int(index))


# todo projects create todo-app
# todo projects todo-app add


def shell():
    current_list = 'all'
    logger.clear_screen()
    get(current_list)

    while True:
        command = input("\n> ").split()
        match command:
            # exit
            case ['exit']:
                logger.clear_screen()
                exit()

            # current add
            case ['a' | 'add', text]:
                logger.clear_screen()
                add(current_list, text.strip())

            # current update
            case ['u' | 'update', index, text]:
                logger.clear_screen()
                update(current_list, int(index), text.strip())

            # current remove
            case ['r' | 'remove', index]:
                logger.clear_screen()
                remove(current_list, int(index))
            
            # list get
            case [list_name]:
                current_list = list_name
                logger.clear_screen()
                get(current_list)

            # list add
            case [list_name, 'a' | 'add', text]:
                current_list = list_name
                logger.clear_screen()
                add(list_name, text.strip())

            # list update
            case [list_name, 'u' | 'update', index, text]:
                current_list = list_name
                logger.clear_screen()
                update(list_name, int(index), text.strip())

            # list remove
            case [list_name, 'r' | 'remove', index]:
                current_list = list_name
                logger.clear_screen()
                remove(list_name, int(index))
            


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
            if path == '': # default
                path = base_path
                break
            elif os.path.isdir(path):
                path = path.strip('/') + '/'
                break
        
        print('Creating files...')

        # create settings file
        with open(settings_path, 'w') as file:
            json.dump({
                'mode': 'local',
                'path': path + '.todo'
            }, file)


        # check if folder already exists
        if os.path.isfile(path + '.todo/all.todo'):
            while True:
                a = input('A todo folder already exists. Do you want to overwrite it [y/N]? ').lower()
                # overwrite
                if a == 'y' or a == 'yes':
                    print("Overwriting files...")
                    with open(path + '.todo/all.todo', 'w') as file:
                        json.dump({
                            'name': 'all',
                            'todos': [],
                        }, file)
                    break

                # do not overwrite
                elif a == 'n' or a == 'no' or a == '':
                    break

        # if does not exist
        else:
            # create todo folder
            os.mkdir(path + '.todo')

            # create list all
            with open(path + '.todo/all.todo', 'w') as file:
                json.dump({
                    'name': 'all',
                    'todos': [],
                }, file)
        
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
        with open(settings_path, 'w') as file:
            json.dump({
                'mode': 'remote',
                'path': path,
            }, file)
        
        print("Done.")

# CREATE
def create(type: str, name: str = None):
    match type:
        case 'list':
            if not name:
                logger.error("List name is required.")

        case 'section':
            if not name:
                logger.error("List name is required.")

        case 'local':
            if not name:
                name = os.path.basename(os.getcwd())

            # check if local file exists
            if os.path.isfile('local.todo'):
                logger.error("Local list already exists.")
            
            # create file
            with open('local.todo', 'w') as file:
                json.dump({
                    'name': name,
                    'todos': []
                }, file)
            
            print(f"Created new local list \"{name}\" successfully.")

            


# GET
def get(list_name: str):
    if not settings:
        logger.error('Todo list is not set up yet.\n Initialize it by running \'todo setup\'')
    
    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # check if file exists
            if not os.path.isfile(settings['path'] + '/all.todo'):
                print('List \'all\' is not set up yet.')
                print('Initialize it by running \'todo setup\'')
                return

            # load list from file
            with open(settings['path'] + '/all.todo') as file:
                list = json.load(file)
            
            # print the list
            match list_name:
                case 'all':
                    logger.print_list(list['todos'], name=list_name)

                case 'today':
                    logger.print_list(helper.filter_today(list['todos']), name=list_name)

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(list['todos']), name=list_name)

        case 'local':
            # check if file exists
            if not os.path.isfile('local.todo'):
                logger.error('Local list is not set up yet. \nCreate it by running \'todo create local\'')

            # load list from file
            with open('local.todo') as file:
                list = json.load(file)
            
            # print the list
            logger.print_list(list['todos'], name=list_name)

        case name if name in []:
            # add to list_name without expiration
            pass


        case _:
            # wrong list name
            pass

# ADD
def add(list_name: str, text: str):
    if not settings:
        logger.error('Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    match list_name:
        # all, today and tomorrow
        case 'all' | 'today' | 'tomorrow':
            # check if file exists
            if not os.path.isfile(settings['path'] + '/all.todo'):
                logger.error('List \'all\' is not set up yet. Initialize it by running \'todo setup\'')

            # read from file
            with open(settings['path'] + '/all.todo', 'r') as file:
                list = json.load(file)

            # calculate expiration
            match list_name:
                case 'all':
                    expiration = None
                case 'today':
                    expiration = str(helper.today())
                case 'tomorrow':
                    expiration = str(helper.tomorrow())

            # add to all with expiration tomorrow
            list['todos'].append({
                'text': text,
                'time': str(datetime.datetime.now()),
                'expiration': expiration
            })

            # write to file
            with open(settings['path'] + '/all.todo', 'w') as file:
                json.dump(list, file)
            
            # print the list
            match list_name:
                case 'all':
                    logger.print_list(list['todos'], name=list_name, add=text)

                case 'today':
                    logger.print_list(helper.filter_today(list['todos']), name=list_name, add=text)

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(list['todos']), name=list_name, add=text)


        case 'local':
            # check if file exists
            if not os.path.isfile('local.todo'):
                logger.error('Local list is not set up yet. \nCreate it by running \'todo create local\'')

            # read from file
            with open('local.todo', 'r') as file:
                list = json.load(file)

            # add to all with expiration tomorrow
            list['todos'].append({
                'text': text,
                'time': str(datetime.datetime.now()),
            })

            # write to file
            with open('local.todo', 'w') as file:
                json.dump(list, file)
            
            # print the list
            logger.print_list(list['todos'], name=list_name, add=text)

        case name if name in []:
            # add to list_name without expiration
            pass

        case _:
            # wrong list name
            pass

# UPDATE
def update(list_name: str, index: int, text: str):
    if not settings:
        logger.error('Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # check if file exists
            if not os.path.isfile(settings['path'] + '/all.todo'):
                logger.error('List \'all\' is not set up yet. \nInitialize it by running \'todo setup\'')

            # read from file
            with open(settings['path'] + '/all.todo', 'r') as file:
                list = json.load(file)

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
            with open(settings['path'] + '/all.todo', 'w') as file:
                json.dump(list, file)
                                    
            # print the list
            match list_name:
                case 'all':
                    logger.print_list(list['todos'], name=list_name, update=(old_text, text))

                case 'today':
                    logger.print_list(helper.filter_today(list['todos']), name=list_name, update=(old_text, text))

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(list['todos']), name=list_name, update=(old_text, text))

        case 'local':
            # check if file exists
            if not os.path.isfile('local.todo'):
                logger.error('Local list is not set up yet. \nCreate it by running \'todo create local\'')

            # read from file
            with open('local.todo', 'r') as file:
                list = json.load(file)

            # update the todo
            old_text = list['todos'][index - 1]['text']
            list['todos'][index - 1]['text'] = text

            # write to file
            with open('local.todo', 'w') as file:
                json.dump(list, file)
                                    
            # print the list
            logger.print_list(list['todos'], name=list_name, update=(old_text, text))

        case _:
            pass

# REMOVE
def remove(list_name: str, index: int):
    if not settings:
        logger.error('Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    if index <= 0:
        logger.error("Index value must be positive.")
    
    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # check if file exists
            if not os.path.isfile(settings['path'] + '/all.todo'):
                logger.error('List \'all\' is not set up yet. \nInitialize it by running \'todo setup\'')

            # read from file
            with open(settings['path'] + '/all.todo', 'r') as file:
                list = json.load(file)

            # remove the todo
            match list_name:
                case 'all':
                    # check if index is valid
                    if len(list['todos']) < index:
                        logger.error("Index value out of list.")
                    index = index - 1

                case 'today':
                    # check if index is valid
                    if len(helper.filter_today(list['todos'])) < index: 
                        logger.error("Index value out of list.")
                    index = list['todos'].index(helper.filter_today(list['todos'])[index - 1])

                case 'tomorrow':
                    # check if index is valid
                    if len(helper.filter_tomorrow(list['todos'])) < index: 
                        logger.error("Index value out of list.")
                    index = list['todos'].index(helper.filter_tomorrow(list['todos'])[index - 1])

            # remove item
            removed = list['todos'].pop(index)['text']

            # write to file
            with open(settings['path'] + '/all.todo', 'w') as file:
                json.dump(list, file)

            # print the list
            match list_name:
                case 'all':
                    logger.print_list(list['todos'], name=list_name, remove=removed)

                case 'today':
                    logger.print_list(helper.filter_today(list['todos']), name=list_name, remove=removed)

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(list['todos']), name=list_name, remove=removed)

        case 'local':
            # check if file exists
            if not os.path.isfile('local.todo'):
                logger.error('List \'all\' is not set up yet. \nInitialize it by running \'todo setup\'')

            # read from file
            with open('local.todo', 'r') as file:
                list = json.load(file)

            # check if index is valid
            if len(list['todos']) < index:
                logger.error("Index value out of list.")

            # remove item
            removed = list['todos'].pop(index - 1)['text']

            # write to file
            with open('local.todo', 'w') as file:
                json.dump(list, file)

            # print the list
            logger.print_list(list['todos'], name=list_name, remove=removed)


        case _:
            pass

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
        case []:
            data = get(config['mode'])
            print_list('get', data)
        
        # create
        case ['create']:
            data = create('main')
            print_list('create', data)

        # add
        case ['add', element]:
            data = add(config['mode'], element)
            print_list('add', data) 
        
        # remove
        case ['remove', index]:
            data = remove(config['mode'], index)
            print_list('remove', data)
        
        # all
        case ['all']:
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
        case ['mode']:
            print_list('mode')
        
        # mode set
        case ['mode', mode] if mode in ['remote', 'main', 'local']:
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
        case ['serve']:
            from server import app
            app.run(host='0.0.0.0', port='5000', debug=True)

        # help
        case ['help']:
            print_list('help')

        # create branch
        case ['branch', name]:

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

        case [*command]:
            print(f"Illegal command {command}")
            exit(1)

# create
def old_create(mode, name=None):
    path = paths[mode]

    if mode == 'remote':
        exit(1)

    # check if file exists
    if os.path.isfile(path):
        print_error('create', {'error': 1, 'message': 'file already exists.', 'path': path})

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
            print_error('get', {'error': 1, 'message': 'server not found', 'path': path})

        # check for status code
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.text)
            exit(2)

    # if local
    else:
        if not os.path.isfile(path):
            print_error('get', {'error': 1, 'message': 'file not found', 'path': path})

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
            print_error('add', {'error': 1, 'message': 'file not found', 'path': path})

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
            print_error('remove', {'error': 1, 'message': 'file not found', 'path': path})

        # get todos
        data = get(mode)
        removed_list = []

        # check index validity
        if ((not removed.isnumeric() and removed != 'all') or
                (removed.isnumeric() and (int(removed) > len(data['todos']) or int(removed) <= 0))):
            print_error('remove', {'error': 2, 'message': 'invalid index.', 'path': path})

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
            print_bold('main\n', mode_color['main']) if config['mode'] != 'main' and os.path.isfile(paths['main']) else None 

            # remote
            # try:
            #     print_bold('remote\n', mode_color['remote']) if config['mode'] != 'remote' and requests.get(paths['remote']) else None
            # except requests.exceptions.RequestException:
            #     pass 

            # local 
            print_bold('local\n', mode_color['local']) if config['mode'] != 'local' and os.path.isfile(paths['local']) else None

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
        print_bold('[✓]', 'green') if config['mode'] == 'main' else print_bold('[ ]')
        print_bold(' main\n', mode_color['main'])
        print_bold('[✓]', 'green') if config['mode'] == 'remote' else print_bold('[ ]')
        print_bold(' remote\n', mode_color['remote'])
        print_bold('[✓]', 'green') if config['mode'] == 'local' else print_bold('[ ]')
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
        print_bold('  create                               -   creates a new main list\n', color)
        print_bold('  add <todo>                           -   adds a new todo to the default list\n', color)
        print_bold('  remove <index>                       -   removes a new todo to the default list\n', color)
        print_bold('  all                                  -   prints all todolists\n', color)
        print_bold('  local [create | add | remove]        -   work with local todolist\n', color)
        print_bold('  <listname> [create | add | remove]   -   work with specific todolist\n', color)
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
