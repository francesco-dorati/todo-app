#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored, cprint

"""
    TODO
    commands
        - todo rename
        - todo remove

    - todo welcome
    - main file is linked to other local.todo stored in links
    - an title to and other data to todofile 
    - store todos in different files which are sections
    - local is a reserved keyword which refers to loal file, add possibility to add common keywords which refer to files
    - link todos to mainfiles (maybe fetch data from local)

    - todo branch
    
    - add order
    - add git serve to activate server

    - "todo remove" print todos and prompts for dalete until -1 given 
    - "todo remove" multiple elements

    - add other functionality shown in "todo all"
    - idea sector "todo add idea"

    - remove color on created
    
    - fix readme
    - add branches
    - add highlight
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

def main():
    todos_color = 'grey'
    attrs = ['bold']

    # if user wrote only 1 argument
    if len(sys.argv) == 1:
        # get
        todos = get(paths[config['mode']])
        print_list('get', todos)

    # if user wrote 2 or more arguments
    elif len(sys.argv) >= 2:
        option = sys.argv[1]
        
        # create
        if option == 'create':
            todolist = create(paths['main'])
            print_list('create', todolist)
        
        # add
        elif option == 'add':
            # if local
            todolist = add(paths[config['mode']], sys.argv[2])
            print_list('add', todolist)

        # remove
        elif option == 'remove':
            todolist = remove(paths[config['mode']], sys.argv[2])
            print_list('remove', todolist)

        # local
        elif option == 'local':
            # if 2 arguments given
            if len(sys.argv) == 2:
                # get
                todolist = get(paths['local'])
                print_list('get', todolist)

            # if more than two arguments given
            elif len(sys.argv) > 2:
                local_option = sys.argv[2]
                
                # create
                if local_option == 'create':
                    name = sys.argv[3] if len(sys.arv) == 4 else None
                    todolist = create(paths['local'], name)

                # add
                elif local_option == 'add':
                    todolist = add(paths['local'], sys.argv[3])

                # remove
                elif local_option == 'remove':
                    todolist = remove(paths['local'], sys.argv[3])

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
                        print('Invalid mode.')
                        exit(1)

                    mode = 'main' if sys.argv[3] == '1' else 'remote'

                    # check if mode is already set
                    if mode == config['mode']:
                        print(colored('\nMode already set to', attrs=attrs), colored(mode, 'red', attrs=attrs))
                    else:
                        print(colored('\nMode set to', attrs=attrs), colored(mode, 'green', attrs=attrs))

                        # write changes to file
                        config['mode'] = mode
                        with open(paths['config'], 'w') as file:
                            file.write(json.dumps(config))

        else:
            print(f'Illegal option "{sys.argv[1]}".')
            exit(1)
        
    else:
        print(f'Invalid number of arguments.')
        exit(1)

# create
def create(path, name=None):
    # check if file exists
    if os.path.isfile(path):
        """main TODO already exists in <path red>"""
        """local TODO already exists as <name red>"""
        exit(3)
            
    # create todolist
    if path == paths['local']:
        todolist = {
            'name': name if name else os.path.basename(os.getcwd()),
            'todos': []
        }
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
def get(path):
    # if remote
    if "http://" in path or "https://" in path:
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
def add(path, added):
    # if remote
    if "http://" in path or "https://" in path:
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
        todolist = get(path)
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
def remove(path, removed):
    # if remote
    if "http://" in path or "https://" in path:
        response = requests.delete(config['remote'], params={'remove': sys.argv[2]})

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
        todolist = get(path)
        removed_list = []

        # check index validity
        if ((not removed.isnumeric() and removed != 'all') or
            (removed.isnumeric() and int(removed) > len(todolist['todos']))):
            return "Invalid index", 404
 
        # delete all
        if removed == 'all':
            for index, todo in enumerate(todolist['todos']):
                removed_list.append({'index': index, 'text': todo})
            todolist['todos'] = []

        # delete one
        elif removed.isnumeric():
            index = int(removed) - 1
            removed_list.append({'index': index, 'text': todolist['todos'].pop(int(index) - 1)})

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(todolist))

        return {
            'name': todolist['name'],
            'todos': todolist['todos'],
            'removed': removed_list 
        }
            

def print_list(action, todolist=None):
    print_bold = lambda x, y=None: cprint(x, y, attrs=['bold'], end='')


    # if no error
    if not 'error' in todolist:
        # get add remove
        if action in ['get', 'add', 'remove', 'create']:
            # name color
            if todolist['name'] == 'remote':
                name_color = 'blue'
            elif todolist['name'] == 'main':
                name_color = 'yellow'
            else:
                name_color = 'magenta'

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
            print_bold('\nTODOs settings\n')
            print_bold('\nDefaults:\n')
            print_bold('[1] Main\n', 'grey' if config['mode'] == 'remote' else None)
            print_bold('[2] Remote\n', 'grey' if config['mode'] == 'main' else None)
            print_bold('\nEdit with: todo settings mode <number>\n', 'grey')

    # if error
    else:
        print_bold('\nError: ', 'red')
        if action in ['get','add', 'remove']:
            # file not found
            if todolist['error'] == 1:
                if todolist['path'] == paths['local']:
                    print_bold('No ')
                    print_bold('local', 'magenta')
                    print_bold(' TODO list found.\n')
                    print_bold('\nCreate one by running: todo local create [<name>]\n', 'grey')
                else:
                    print_bold('No ')
                    print_bold('main', 'yellow')
                    print_bold(' TODO list found.\n')
                    print_bold('\nCreate by running: todo create\n', 'grey')

        # exit
        exit(todolist['error'])


    
if __name__ == '__main__':
    main()
