#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored, cprint

"""
    TODO
    - load external links 
        - if remote load also remote links
    - remote compernde solo il main
    - pero ideas lo voglio nel server
    - controlla prima in locale e poi nel server

    - aggiungere help
    
    - aggiungere possibilita si annullare il remove con undo (per tempo)

    commands
        - todo rename
        - todo remove
            - "todo remove" print todos and prompts for dalete until -1 given 
            - "todo remove" multiple elements
        - todo serve
        - todo branch
        - todo all

    - fix readme
"""

names = {
    'main': 'main.todo',
    'local': 'local.todo',
    'config': 'config.json'
}

base = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'

# load config
with open(base + names['config']) as file:
    config = json.load(file)

paths = {
    'main': base + names['main'],
    'local': names['local'],
    'remote': config['remote'],
    'config': base + names['config']
}

# load links
if os.path.isfile(paths['main']):
    with open(paths['main'], 'r') as file:
        links = json.load(file)['links']

        for name in links:
            paths[name] = links[name]

# load remote links
if config['mode'] == 'remote':
    response = requests.get(paths['remote'])

    # check for status code
    if response.status_code == 200:
        for name in json.loads(response.text)['links']:
            paths[name] = paths['remote'] + name
    else:
        print(response.text)
        exit(2)


def main():
    todos_color = 'grey'
    attrs = ['bold']

    # if user wrote only 1 argument
    if len(sys.argv) == 1:
        # get
        data = get(config['mode'])
        print_list('get', data)

    # if user wrote 2 or more arguments
    elif len(sys.argv) >= 2:
        option = sys.argv[1]

        # create
        if option == 'create':
            data = create('main')
            print_list('create', data)

        # add
        elif option == 'add':
            # if local
            data = add(config['mode'], sys.argv[2])
            print_list('add', data)

        # remove
        elif option == 'remove':
            data = remove(config['mode'], sys.argv[2])
            print_list('remove', data)

        # modes
        elif option in paths:
            # get
            if len(sys.argv) == 2:
                data = get(option)
                print_list('get', data)

            else:
                local_option = sys.argv[2]

                # create
                if local_option == 'create':
                    data = create(option)

                # add
                elif local_option == 'add':
                    data = add(option, sys.argv[3])

                # remove
                elif local_option == 'remove':
                    data = remove(option, sys.argv[3])

                print_list(local_option, data)

        # mode
        elif option == 'mode':
            # if 2 arguments given
            if len(sys.argv) == 2:
                print_list('mode')

            elif sys.argv[2] in ['remote', 'main']:
                mode = sys.argv[2]
                # check if mode is already set
                if mode == config['mode']:
                    print_list('mode', {
                        'error': 2,
                        'message': 'Mode already set.',
                        'mode': mode
                    })
                else:
                    # write changes to file
                    config['mode'] = mode
                    with open(paths['config'], 'w') as file:
                        file.write(json.dumps(config))

                    print_list('mode', {
                        'mode': mode
                    })

            else:
                print_list('settings', {
                    'error': 1,
                    'message': 'Inalid mode.',
                })

        else:
            print(f'Illegal option "{sys.argv[1]}".')
            exit(1)

    else:
        print(f'Invalid number of arguments.')
        exit(1)

# create
def create(mode, name=None):
    path = paths[mode]

    if mode == 'remote':
        exit(1)

    # check if file exists
    if os.path.isfile(path):
        return {'error': 1, 'message': 'file already exists.', 'path': path}

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
            file.write(json.dumps(main))

    else:
        data = {
            'name': 'main',
            'todos': [],
            'links': {}
        }

    # write to file
    with open(path, 'w') as file:
        file.write(json.dumps(data))

    return data


# GET
def get(mode):
    path = paths[mode]

    # if remote
    if 'http://' in path or 'https://' in path:
        response = requests.get(path)

        # check for status code
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.text)
            exit(2)

    # if local
    else:
        if not os.path.isfile(path):
            return {'error': 1, 'message': 'file not found', 'path': path}

        # read file
        with open(path, 'r') as file:
            return json.loads(file.read())

# ADD
def add(mode, added):
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
            return {'error': 1, 'message': 'file not found', 'path': path}

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
def remove(mode, removed):
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
            return {'error': 1, 'message': 'file not found', 'path': path}

        # get todos
        data = get(mode)
        removed_list = []

        # check index validity
        if ((not removed.isnumeric() and removed != 'all') or
                (removed.isnumeric() and (int(removed) > len(data['todos']) or int(removed) <= 0))):
            return {'error': 2, 'message': 'invalid index.', 'path': path}

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


def print_list(action, data={}):
    def print_bold(x, y=None): return cprint(x, y, attrs=['bold'], end='')
    mode_color = {
        'remote': 'blue',
        'main': 'yellow',
        'local': 'magenta'
    }

    # if no error
    if not 'error' in data:
        # get add remove
        if action in ['get', 'add', 'remove', 'create']:
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
                            f'   [-] {data["removed"][index]["text"]}\n', 'red')
                        data['removed'].pop(index)

                    print_bold(f'   [{index + 1}] {todo}\n', 'grey')

                # print remaining removed todos
                for todo in data['removed']:
                    print_bold(f'   [-] {todo["text"]}\n', 'red')

            # get
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

            if data:
                print_bold('\nNow you can access ', 'grey')
                print_bold(data['mode'], 'grey')
                print_bold(' just by running: todo\n', 'grey')
            else:
                print_bold('\nEdit with: todo mode <mode>\n', 'grey')

    # if error
    else:
        print_bold('\nError: ', 'red')
        if action in ['get', 'add', 'remove']:
            # file not found
            if data['error'] == 1:
                if data['path'] == paths['local']:
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
