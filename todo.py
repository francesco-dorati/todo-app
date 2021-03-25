#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored, cprint

"""
    TODO
    - todo local remove all print nothin
    - local change color
    - create prints todolist

    - in get dont check for file
    - allow only one todofile
    - store in local.todo
    - use rename to rename file

    commands
        - todo rename
        - todo remove
        - todo link

    - rethink local (store files in name.todo)
    - add todo create/init
    - todo create name
        - todo link name
        - modify get

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

        # print
        print_list('get', todos)

    # if user wrote 2 or more arguments
    elif len(sys.argv) >= 2:
        option = sys.argv[1]
        
        # create
        if option == 'create':
            # check if file exists
            if os.path.isfile(paths['main']):
                print(colored(f'\nFile {colored(paths["main"], "red")} already exists.', attrs=attrs)) 
                exit(3)

            # create file
            with open(paths['main'], 'w') as file:
                file.write(json.dumps({'name': 'main', 'todos': [], 'links': {}}))
                print(colored(f'\nTODO list created successfully!', attrs=attrs)) 
        
        # add
        elif option == 'add':
            # if local
            todolist = add(paths[config['mode']], sys.argv[2])
        
            # print
            print_list('add', todolist)

        # remove
        elif option == 'remove':
            todolist = remove(paths[config['mode']], sys.argv[2])
            
            # print
            print_list('remove', todolist)

        # local
        elif option == 'local':
            # if 2 arguments given
            if len(sys.argv) == 2:
                # get
                # check if file exists
                if not os.path.isfile(paths['local']):
                    print(colored(f'\nNo local TODO found.', attrs=attrs)) 
                    print(colored(f'\nCreate one by running: todo local create <name>', 'grey', attrs=attrs)) 
                    exit(3)

                todolist = get(paths['local'])

                # print
                print_list('get', todolist)

            # if more than two arguments given
            elif len(sys.argv) > 2:
                local_option = sys.argv[2]
                
                # create
                if local_option == 'create':
                    # get name
                    name = os.path.basename(os.getcwd()) if len(sys.argv) == 3 else sys.argv[3]

                    # check if file exists
                    if os.path.isfile(paths['local']):
                        print(colored(f'\nLocal TODO already exists.', attrs=attrs))
                        exit(3)

                    # create file
                    with open(paths['local'], 'w') as file:
                        file.write(json.dumps({'name': name, 'todos': []}))

                    # print
                    print(colored(f'\nLocal TODO list', attrs=attrs), 
                            colored(name, "green", attrs=attrs),
                            colored('successfully created!', attrs=attrs))    

                # add
                elif local_option == 'add':
                    todolist = add(paths['local'], sys.argv[3])

                    # print
                    print_list('add', todolist)

                # remove
                elif local_option == 'remove':
                    todolist = remove(paths['local'], sys.argv[3])

                    print_list('removed', todolist)

        # settings
        elif option == 'settings':
            # if 2 arguments given
            if len(sys.argv) == 2:
                print(colored('\nTODOs settings', attrs=attrs))
                print(colored('\nMode:', attrs=attrs))
                print(colored('[1] Main', 'grey' if config['mode'] == 'remote' else None, attrs=attrs))
                print(colored('[2] Remote', 'grey' if config['mode'] == 'main' else None, attrs=attrs))
                print(colored('\nEdit with: todo settings mode <number>', 'grey', attrs=attrs))

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

        elif option in get(paths['main'])['links']:
            if len(argv) == 2:
                # get
                pass
            else:
                # add and remove
                pass
            pass

        else:
            print(f'Illegal option "{sys.argv[1]}".')
            exit(1)
        
    else:
        print(f'Invalid number of arguments.')
        exit(1)


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
        # get and append new todo
        todos = get(path)
        todos['todos'].append(added)

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(todos))

        return {
            'name': todos['name'],
            'todos': todos['todos'],
            'added': {
                'index': len(todos['todos']) - 1, 
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
        todolist = get(path)
        todolist['removed'] = []

        # check index validity
        if (not removed.isnumeric() and removed != 'all') or (removed.isnumeric() and int(removed) > len(todolist['todos'])):
            return "Invalid index", 404
 
        # delete all
        if removed == 'all':
            for index, todo in enumerate(todolist['todos']):
                todolist['removed'].append({'index': index, 'text': todo})
            todolist['todos'] = []

        # delete one
        elif removed.isnumeric():
            index = int(removed) - 1
            todolist['removed'].append({'index': index, 'text': todolist['todos'].pop(int(index) - 1)})

        with open(path, 'w') as file:
            file.write(json.dumps(todolist))

        return todolist
            

def print_list(action, todolist):
    print_bold = lambda x, y=None: cprint(x, y, attrs=['bold'], end='')

    if todolist['name'] == 'remote':
        name_color = 'blue'
    elif todolist['name'] == 'main':
        name_color = 'yellow'
    else:
        name_color = 'green'

    # get add remove
    if action in ['get', 'add', 'remove']:
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


        print_bold('\nYour ')
        print_bold(todolist['name'], name_color)
        print_bold(' TODOs:\n')

        # get
        if action == 'get':
            # todos present
            if len(todolist['todos']) > 0:
                for index, todo in enumerate(todolist['todos']):
                    print_bold(f'   [{index + 1}] {todo}\n', 'grey')

            # no todos
            else:
                print_bold('    [?] This TODO list is empty\n', 'grey')
                print_bold('\nAdd one by running: todo add <todo>\n', 'grey')

        # add
        elif action == 'add':
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

                print_bold(f'   [{index + 1}] {todo}\n', 'grey')

            if any(removed['index'] == len(todolist['todos']) for removed in todolist['removed']):
                print_bold(f'   [-] {todolist["removed"][len(todolist["todos"])]["text"]}\n', 'red')

            

    elif action == 'settings':
        print_bold('\nTODOs settings\n')
        print_bold('\nDefaults:\n')
        print_bold('[1] Main', 'grey' if config['mode'] == 'remote' else None)
        print_bold('[2] Remote', 'grey' if config['mode'] == 'main' else None)
        print_bold('\nEdit with: todo settings mode <number>', 'grey')

    # nel remoed dai il vecchio index e nella todo ritorna quella attuale, inseriscine dui in un loop 
    # all ritorna tutti gli elementi

if __name__ == '__main__':
    main()
