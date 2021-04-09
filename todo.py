#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored, cprint

"""
    TODO
    - todo switch mode -> changes mode

    - load external links 
        - if remote load also remote links
    - remote compernde solo il main
    - pero ideas lo voglio nel server
    - controlla prima in locale e poi nel server
    
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

def main():
    todos_color = 'grey'
    attrs = ['bold']

    # if user wrote only 1 argument
    if len(sys.argv) == 1:
        # get
        todolist = get(config['mode'])
        print_list('get', todolist)

    # if user wrote 2 or more arguments
    elif len(sys.argv) >= 2:
        option = sys.argv[1]
        
        # create
        if option == 'create':
            todolist = create('main')
            print_list('create', todolist)
        
        # add
        elif option == 'add':
            # if local
            todolist = add(config['mode'], sys.argv[2])
            print_list('add', todolist)

        # remove
        elif option == 'remove':
            todolist = remove(config['mode'], sys.argv[2])
            print_list('remove', todolist)

        # modes
        elif option in paths:
            # get
            if len(sys.argv) == 2:
                todolist = get(option)
                print_list('get', todolist)

            else:
                local_option = sys.argv[2]

                # create
                if local_option == 'create':
                    todolist = create(option)

                # add
                elif local_option == 'add':
                    todolist = add(option, sys.argv[3])

                # remove
                elif local_option == 'remove':
                    todolist = remove(option, sys.argv[3])

                print_list(local_option, todolist)

        # settings
        elif option == 'settings':
            # if 2 arguments given
            if len(sys.argv) == 2:
                print_list('settings')

            # if 4 arguments given
            elif len(sys.argv) == 4:
                if sys.argv[2] == 'mode':
                    # check invalid mode
                    if sys.argv[3] != '1' and sys.argv[3] != '2':
                        print_list('settings', {
                            'error': 1,
                            'message': 'Inalid mode.',
                        })

                    mode = 'main' if sys.argv[3] == '1' else 'remote'

                    # check if mode is already set
                    if mode == config['mode']:
                        print_list('settings', {
                            'error': 2,
                            'message': 'Mode already set.',
                            'mode': mode
                        })

                    else:
                        # write changes to file
                        config['mode'] = mode
                        with open(paths['config'], 'w') as file:
                            file.write(json.dumps(config))

                        print_list('settings', {
                            'mode': mode
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
            
    # create todolist
    if mode == 'local':
        todolist = {
            'name': name if name else os.path.basename(os.getcwd()),
            'todos': []
        }

        # add to links
        with open(paths['main'], 'r') as file:
            main = json.loads(file.read())
            main['links'][todolist['name']] = os.getcwd() + '/' + paths['local']

        with open(paths['main'], 'w') as file:
            file.write(json.dumps(main))

    else:
        todolist = {
            'name': 'main',
            'todos': [],
            'links': {}
        }

    # write to file
    with open(path, 'w') as file:
        file.write(json.dumps(todolist))

    return todolist
                    

# GET
def get(mode):
    path = paths[mode]
    
    # if remote
    if mode == 'remote':
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
    if mode == 'remote':
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
        todolist = get(mode)
        todolist['todos'].append(added)

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(todolist))

        return {
            'name': todolist['name'],
            'todos': todolist['todos'],
            'added': {
                'index': len(todolist['todos']) - 1, 
                'text': added
            }
        }


# REMOVE
def remove(mode, removed):
    path = paths[mode]

    # if remote
    if mode == 'remote':
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
        todolist = get(mode)
        removed_list = []

        # check index validity
        if ((not removed.isnumeric() and removed != 'all') or
            (removed.isnumeric() and (int(removed) > len(todolist['todos']) or int(removed) <= 0))):
            return {'error': 2, 'message': 'invalid index.', 'path': path} 
 
        # delete all
        if removed == 'all':
            for index, todo in enumerate(todolist['todos']):
                removed_list.append({'index': index, 'text': todo})
            todolist['todos'] = []

        # delete one
        elif removed.isnumeric():
            index = int(removed) - 1
            removed_list.append({'index': index, 'text': todolist['todos'].pop(index)})

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(todolist))

        return {
            'name': todolist['name'],
            'todos': todolist['todos'],
            'removed': removed_list 
        }
            

def print_list(action, todolist={}):
    print_bold = lambda x, y=None: cprint(x, y, attrs=['bold'], end='')
    remote_color = 'blue'
    main_color = 'yellow'
    local_color = 'magenta'

    # if no error
    if not 'error' in todolist:
        # get add remove
        if action in ['get', 'add', 'remove', 'create']:
            # name color
            if todolist['name'] == 'remote':
                name_color = remote_color 
            elif todolist['name'] == 'main':
                name_color = main_color 
            else:
                name_color = local_color 

            # feedback
            if action == 'add':
                print_bold('\nAdded '), 
                print_bold(f'"{todolist["added"]["text"]}" ', 'green') 
                print_bold('successfully to ')
                print_bold(todolist['name'], name_color)
                print_bold('!\n')

            elif action == 'remove':
                print_bold('\nRemoved '), 
                if len(todolist['todos']) == 0 and len(todolist['removed']) != 1:
                    print_bold('all ', 'red') 
                elif len(todolist['removed']) == 1:
                    print_bold(f'"{todolist["removed"][0]["text"]}" ', 'red') 
                print_bold('successfully from ')
                print_bold(todolist['name'], name_color)
                print_bold('!\n')
    
            elif action == 'create':
                if todolist['name'] == 'main':
                    print_bold('\n')
                    print_bold(todolist['name'], name_color)
                    print_bold(' TODO list successfully created!\n')
                else:
                    print_bold('\nLocal ')
                    print_bold(todolist['name'], name_color)
                    print_bold(' TODO list successfully created!\n')
    
            print_bold('\nYour ')
            print_bold(todolist['name'], name_color)
            print_bold(' TODOs:\n')
    
            # add
            if action == 'add':
                for index, todo in enumerate(todolist['todos']):
                    if index == todolist['added']['index']:
                        print_bold(f'    [+] {todo}\n', 'grey')
                    else:
                        print_bold(f'    [{index + 1}] {todo}\n', 'grey')
    
            # remove
            elif action == 'remove':
                for index, todo in enumerate(todolist['todos']):
                    if any(removed['index'] == index for removed in todolist['removed']):
                        print_bold(f'   [-] {todolist["removed"][index]["text"]}\n', 'red')
                        todolist['removed'].pop(index)
    
                    print_bold(f'   [{index + 1}] {todo}\n', 'grey')
    
                # print remaining removed todos
                for todo in todolist['removed']:
                    print_bold(f'   [-] {todo["text"]}\n', 'red')
    
            # get
            else:
                # todos present
                if len(todolist['todos']) > 0:
                    for index, todo in enumerate(todolist['todos']):
                        print_bold(f'   [{index + 1}] {todo}\n', 'grey')
    
                # no todos
                else:
                    print_bold('    [?] This TODO list is empty\n', 'grey')
                    print_bold(f'\nAdd one by running: ', 'grey')
                    print_bold(f'todo {"local " if not todolist["name"] == "main" else ""}add <todo>\n', 'grey')
    
    
        # settings
        elif action == 'settings':
            if todolist:
                print_bold('\nMode set to ')
                print_bold(todolist['mode'], 'green')
                print_bold('\n')

            print_bold('\nTODOs settings\n')
            print_bold('\nMode:\n')
            print_bold('[1] Main\n', 'grey' if config['mode'] == 'remote' else None)
            print_bold('[2] Remote\n', 'grey' if config['mode'] == 'main' else None)
            
            if todolist:
                print_bold('\nNow you can access ', 'grey')
                print_bold(todolist['mode'], 'grey')
                print_bold(' just by running: todo\n', 'grey')
            else:
                print_bold('\nEdit with: todo settings mode <number>\n', 'grey')
                

    # if error
    else:
        print_bold('\nError: ', 'red')
        if action in ['get','add', 'remove']:
            # file not found
            if todolist['error'] == 1:
                if todolist['path'] == paths['local']:
                    print_bold('No ')
                    print_bold('local', local_color)
                    print_bold(' TODO list found.\n')
                    print_bold('\nCreate one by running: todo local create [<name>]\n', 'grey')
                else:
                    print_bold('No ')
                    print_bold('main', main_color)
                    print_bold(' TODO list found.\n')
                    print_bold('\nCreate by running: todo create\n', 'grey')
            if action == 'remove' and todolist['error'] == 2:
                print_bold('Invalid index.\n')

        elif action == 'create':
            if todolist['error'] == 1:
                if todolist['path'] == paths['local']:
                    name = get(paths['local'])['name']
                    print_bold('local', local_color)
                    print_bold(' TODO list already exists as ')
                    print_bold(name, local_color)
                    print_bold('.\n')
                else:
                    print_bold('main', main_color)
                    print_bold(' TODO list already exists in ')
                    print_bold(todolist['path'], main_color)
                    print_bold('.\n')

        elif action == 'settings':
            if todolist['error'] == 1:
                print_bold('Wrong index.\n')

            elif todolist['error'] == 2:
                print_bold('Mode already set to ')                    
                print_bold(todolist['mode'], 'red')
                print_bold('.\n')
                    
        # exit
        exit(todolist['error'])

    
if __name__ == '__main__':
    main()
