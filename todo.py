#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored

"""
    TODO
    - add git serve to activate server
    - add print function 
    - add settings and make todos.json 
    - settings user change main and local todo file
    - add local todos

    - todo remove multiple elements

    - add other functionality shown in "todo all"
    - idea sector "todo add idea"

    - remove color on created
    
    - fix response on local
    - fix readme
    - add branches
    - add highlight
"""

base_path = "/".join(os.path.realpath(__file__).split('/')[:-1])
file_path = base_path + '/todos.json'

# load config
with open(base_path + '/config.json') as file:
    config = json.load(file)

def main():
    todos_color = 'grey'
    attrs = ['bold']

    print()
    # if user wrote only 1 argument
    if len(sys.argv) == 1:
        # GET
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

    # if user wrote 3 arguments
    elif len(sys.argv) >= 3:
        option = sys.argv[1]
        
        # ADD
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

        # settings
        elif option == 'settings':
            pass

        else:
            print(f'Illegal option "{sys.argv[1]}".')
        
    else:
        print(f'Invalid number of arguments.')


# GET
def get():
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
