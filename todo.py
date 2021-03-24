#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored

"""
    TODO
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
        # todos present
        if len(todos) > 0:
            print(colored('\nYour TODOs:', attrs=attrs))
            for index, todo in enumerate(todos):
                print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))

        # no todos
        else:
            print(colored('\nYour TODOs:', attrs=attrs))
            print(colored('    [?] This TODO list is empty', 'grey', attrs=attrs))
            print(colored('\nAdd one by running: todo add <todo>', 'grey', attrs=attrs))

    # if user wrote 2 or more arguments
    elif len(sys.argv) >= 2:
        option = sys.argv[1]
        
        # init
        if option == 'init':
            # check if file exists
            if os.path.isfile(paths['main']):
                print(colored(f'\nFile {colored(paths["main"], "red")} already exists.', attrs=attrs)) 
                exit(3)

            # create file
            with open(paths['main'], 'w') as file:
                file.write(json.dumps({'name': 'main', 'todos': [], 'links': {}}))
                print(colored(f'\nTODO list initialized successfully!', attrs=attrs)) 
        
        # add
        elif option == 'add':
            # if local
            todos = add(paths[config['mode']], sys.argv[2])
        
            # print
            print(colored('\nAdded', attrs=attrs), 
                    colored(f'"{todos["todos"][todos["added"] - 1]}"', 'green', attrs=attrs), 
                    colored('successfully!', attrs=attrs))
            print(colored('\nTODO:', attrs=attrs))
            for index, todo in enumerate(todos['todos']):
                if index == todos['added'] - 1:
                    print(colored(f'   [+] {todo}', todos_color, attrs=attrs))
                else:
                    print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
        # remove
        elif option == 'remove':
            todos = remove(paths[config['mode']], sys.argv[2])


            # if removed all
            if todos['removed'] == 'all':
                print(colored('Removed', attrs=attrs), 
                        colored('all', 'red', attrs=attrs), 
                        colored('successfully!', attrs=attrs))
                print(colored('\nTODO:', attrs=attrs))

                # print all removed todos
                for todo in todos['todos']:
                    print(colored(f'   [-] {todo}', 'red', attrs=attrs))

            # if removed one
            else:
                print(colored('\nRemoved', attrs=attrs), 
                        colored(f'"{todos["todos"][todos["removed"] - 1]}"', 'red', attrs=attrs), 
                        colored('successfully!', attrs=attrs))
                print(colored('\nTODO:', attrs=attrs))

                # print all todos
                for index, todo in enumerate(todos["todos"]):
                    if index == todos['removed']:
                        print(colored(f'   [-] {todo}', 'red', attrs=attrs))
                    else:
                        print(colored(f'   [{index + 1 if index < todos["removed"] else index}] {todo}', todos_color, attrs=attrs))

        # create
        elif option == 'create':
            # get name
            name = os.path.basename(os.getcwd()) if len(sys.argv) == 2 else sys.argv[2]

            # check if file exists
            if os.path.isfile(name + '.todo'):
                print(colored(f'\nFile {colored(name, "red")} already exists.', attrs=attrs)) 
                exit(3)
                
            # create file
            with open(name + '.todo', 'w') as file:
                file.write(json.dumps({'name': name, 'todos': []}))

            # print
            print(colored(f'\nLocal TODO list', attrs=attrs), 
                    colored(name, "green", attrs=attrs),
                    colored('successfully created!', attrs=attrs))


        # link
        elif option == 'link':
            # get name
            name = os.path.basename(os.getcwd()) if len(sys.argv) == 2 else sys.argv[2]

            # get todos and add link
            todos = get(paths['main'])
            todos['links'][name] = os.getcwd() + '/' + name + '.todo'

            # write changes
            with open(paths['main'], 'w') as file:
                file.write(json.dumps(todos))

            print(colored('\n' + name, 'green', attrs=attrs), colored('linked successfully!', attrs=attrs))

        # local
        elif option == 'local':
            if len(sys.argv) == 2:
                # get
                # change base path
                todos = get(paths['local'])

                # print
                if len(todos) > 0:
                    print(colored('\nYour Local TODOs:', attrs=attrs))
                    for index, todo in enumerate(todos):
                        print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
                else:
                    print(colored('\nYour Local TODOs:', attrs=attrs))
                    print(colored('    [?] This TODO list is empty', 'grey', attrs=attrs))
                    print(colored('\nAdd one by running: todo local add <todo>', 'grey', attrs=attrs))

            # if 4 arguments given
            elif len(sys.argv) == 4:
                local_option = sys.argv[2]

                # add
                if local_option == 'add':
                    todos = add(paths['local'], sys.argv[3])

                    # print
                    print(colored('\nLocally added', attrs=attrs), 
                            colored(f'"{todos["todos"][todos["added"] - 1]}"', 'green', attrs=attrs), 
                            colored('successfully!', attrs=attrs))
                    print(colored('\nYour Local TODOs:', attrs=attrs))
                    for index, todo in enumerate(todos['todos']):
                        if index == todos['added'] - 1:
                            print(colored(f'   [+] {todo}', 'green', attrs=attrs))
                        else:
                            print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))

                # remove
                elif local_option == 'remove':
                    todos = remove(paths['local'], sys.argv[3])

                    # if removed all
                    if todos['removed'] == 'all':
                        print(colored('\nLocally removed', attrs=attrs), 
                                colored('all', 'red', attrs=attrs), 
                                colored('successfully!', attrs=attrs))
                        print(colored('\nLocal TODOs:', attrs=attrs))

                        # print all removed todos
                        for todo in todos['todos']:
                            print(colored(f'   [-] {todo}', 'red', attrs=attrs))

                    # if removed one
                    else:
                        print(colored('\nLocally removed', attrs=attrs), 
                                colored(f'"{todos["todos"][todos["removed"] - 1]}"', 'red', attrs=attrs), 
                                colored('successfully!', attrs=attrs))
                        print(colored('\nLocal TODOs:', attrs=attrs))

                        # print all todos
                        for index, todo in enumerate(todos["todos"]):
                            if index == todos['removed']:
                                print(colored(f'   [-] {todo}', 'red', attrs=attrs))
                            else:
                                print(colored(f'   [{index + 1 if index < todos["removed"] else index}] {todo}', todos_color, attrs=attrs))


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
        # check if file exists
        if not os.path.isfile(path):
            print('\nMain file not found.')
            print('\nCreate it with: todo init')
            exit(3)


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
        todos.append(added)

        # write to file
        with open(path, 'w') as file:
            file.write(json.dumps(todos))

        return {'todos': todos, 'added': len(todos)}


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
        todos = get(path)

        # check index validity
        if (not removed.isnumeric() and removed != 'all') or (removed.isnumeric() and int(removed) > len(todos)):
            return "Invalid index", 404
 
        # delete all
        if removed == 'all':
            with open(path, 'w') as file:
                file.write(json.dumps([]))

            return {'todos': todos, 'removed': 'all'}

        # delete one
        else:
            index = int(removed) - 1
            modified = [*todos]
            modified.pop(index)

            with open(path, 'w') as file:
                file.write(json.dumps(modified))

            return {'todos': todos, 'removed': index}
            

if __name__ == '__main__':
    main()
