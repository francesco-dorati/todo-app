#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored

"""
    TODO
    - add local todos
    - add git serve to activate server

    - todo remove multiple elements

    - add other functionality shown in "todo all"
    - idea sector "todo add idea"

    - remove color on created
    
    - fix response on local
    - fix readme
    - add branches
    - add highlight
"""

base_path = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
file_path = base_path + 'todos.json'

# load config
with open(base_path + 'config.json') as file:
    config = json.load(file)

def main():
    todos_color = 'grey'
    attrs = ['bold']

    print()
    # if user wrote only 1 argument
    if len(sys.argv) == 1:
        # get
        # if local
        if config['mode'] == 'local':
            todos = get()

        # if remote
        else:
            response = requests.get(config['remote'])

            # check for status code
            if response.status_code == 200:
                todos = json.loads(response.text)
            else:
                print(response.text)
                exit(2)

        # print
        if len(todos) > 0:
            print(colored('TODO:', attrs=attrs))
            for index, todo in enumerate(todos):
                print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
        else:
            print(colored('TODO list is empty.', 'grey', attrs=attrs))


    # if user wrote 2 or more2 or more arguments
    elif len(sys.argv) >= 2:
        option = sys.argv[1]
        
        # add
        if option == 'add':
            # if local
            if config['mode'] == 'local':
                todos = add(sys.argv[2])

            # if remote
            else:
                response = requests.post(config['remote'], data={'add': sys.argv[2]})
                
                # check for status code
                if response.status_code == 200:
                    todos = json.loads(response.text)
                else:
                    print(response.text)
                    exit(2)
        
            # print
            print(colored('Added', attrs=attrs), 
                    colored(f'"{todos["todos"][todos["added"] - 1]}"', 'green', attrs=attrs), 
                    colored('successfully!', attrs=attrs))
            print(colored('\nTODO:', attrs=attrs))
            for index, todo in enumerate(todos['todos']):
                if index == todos['added'] - 1:
                    print(colored(f'   [+] {todo}', 'green', attrs=attrs))
                else:
                    print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))

        # remove
        elif option == 'remove':
            # if local
            if config['mode'] == 'local':
                todos = remove(sys.argv[2])

            # if remote
            else: 
                response = requests.delete(config['remote'], params={'remove': sys.argv[2]})

                if response.status_code == 200:
                    todos = json.loads(response.text)
                else:
                    print(response.text)
                    exit(2)

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
                print(colored('Removed', attrs=attrs), 
                        colored(f'"{todos["todos"][todos["removed"] - 1]}"', 'red', attrs=attrs), 
                        colored('successfully!', attrs=attrs))
                print(colored('\nTODO:', attrs=attrs))

                # print all todos
                for index, todo in enumerate(todos["todos"]):
                    if index == todos['removed']:
                        print(colored(f'   [-] {todo}', 'red', attrs=attrs))
                    else:
                        print(colored(f'   [{index + 1 if index < todos["removed"] else index}] {todo}', todos_color, attrs=attrs))

        # local
        elif option == 'local':
            if len(sys.argv) == 2:
                # get
                # change base path
                file_path = 'todos.json'
                todos = get()

                # print
                if len(todos) > 0:
                    print(colored('Local TODOs:', attrs=attrs))
                    for index, todo in enumerate(todos):
                        print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
                else:
                    print(colored('Local TODO list is empty.', 'grey', attrs=attrs))

            # if 4 arguments given
            elif len(sys.argv) == 4:
                local_option = sys.argv[2]

                # add
                if local_option == 'add':
                    file_path = 'todos.json'
                    todos = add(sys.argv[3])

                    # print
                    print(colored('Locally added', attrs=attrs), 
                            colored(f'"{todos["todos"][todos["added"] - 1]}"', 'green', attrs=attrs), 
                            colored('successfully!', attrs=attrs))
                    print(colored('\nLocal TODOs:', attrs=attrs))
                    for index, todo in enumerate(todos['todos']):
                        if index == todos['added'] - 1:
                            print(colored(f'   [+] {todo}', 'green', attrs=attrs))
                        else:
                            print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))

                # remove
                elif local_option == 'remove':
                    file_path = 'todos.json'
                    todos = remove(sys.argv[3])

                    # if removed all
                    if todos['removed'] == 'all':
                        print(colored('Locally removed', attrs=attrs), 
                                colored('all', 'red', attrs=attrs), 
                                colored('successfully!', attrs=attrs))
                        print(colored('\nLocal TODOs:', attrs=attrs))

                        # print all removed todos
                        for todo in todos['todos']:
                            print(colored(f'   [-] {todo}', 'red', attrs=attrs))

                    # if removed one
                    else:
                        print(colored('Locally removed', attrs=attrs), 
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
                print(colored('TODOs settings', attrs=attrs))
                print(colored('\nMode:', attrs=attrs))
                print(colored('[1] Local', 'grey' if config['mode'] == 'remote' else None, attrs=attrs))
                print(colored('[2] Remote', 'grey' if config['mode'] == 'local' else None, attrs=attrs))
                print(colored('\nEdit with', 'grey', attrs=attrs), colored('todo settings mode <number>', attrs=attrs))
            # if 4 arguments given
            elif len(sys.argv) == 4:
                if sys.argv[2] == 'mode':
                    # check invalid mode
                    if sys.argv[3] != '1' and sys.argv[3] != '2':
                        print('Invalid mode.')
                        exit(1)

                    mode = 'local' if sys.argv[3] == '1' else 'remote'

                    # check if mode is already set
                    if mode == config['mode']:
                        print(colored('Mode already set to', attrs=attrs), colored(mode, 'red', attrs=attrs))
                    else:
                        print(colored('Mode set to', attrs=attrs), colored(mode, 'green', attrs=attrs))

                        # write changes to file
                        config['mode'] = mode
                        with open(base_path + 'config.json', 'w') as file:
                            file.write(json.dumps(config))


        else:
            print(f'Illegal option "{sys.argv[1]}".')
            exit(1)
        
    else:
        print(f'Invalid number of arguments.')
        exit(1)


# GET
def get():
    print(file_path)
    # check if file exists
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write(json.dumps([]))
        return []

    # read file
    with open(file_path, 'r') as file:
        todos = json.loads(file.read())

    return todos

# ADD
def add(todo):
    # get and append new todo
    todos = get()
    todos.append(todo)

    # write to file
    with open(file_path, 'w') as file:
        file.write(json.dumps(todos))

    return {'todos': todos, 'added': len(todos)}


# REMOVE
def remove(arg):
    todos = get()

    # check index validity
    if (not arg.isnumeric() and arg != 'all') or (arg.isnumeric() and int(arg) > len(todos)):
        return "Invalid index", 404
 
    # delete all
    if arg == 'all':
        with open(file_path, 'w') as file:
            file.write(json.dumps([]))

        return {'todos': todos, 'removed': 'all'}

    # delete one
    else:
        index = int(arg) - 1
        modified = [*todos]
        modified.pop(index)

        with open(file_path, 'w') as file:
            file.write(json.dumps(modified))

        return {'todos': todos, 'removed': index}
            

if __name__ == '__main__':
    main()
