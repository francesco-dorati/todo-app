#!/usr/bin/env python3
import sys
import os
import json
import requests

from termcolor import colored

"""
    TODO
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

file_name = 'todos.json'

# load config
with open('config.json') as file:
    config = json.load(file)

def main():
    todos_color = 'grey'
    attrs = ['bold']

    print()
    # if user wrote only 1 argument
    if len(sys.argv) == 1:
        # get 
        todos = get()
        if len(todos) > 0:
            print(colored('TODO:', attrs=attrs))
            for index, todo in enumerate(todos):
                print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
        else:
            print(colored('TODO list is empty.', 'grey', attrs=attrs))

    # if user wrote 3 arguments
    elif len(sys.argv) == 3:
        option = sys.argv[1]
        
        # add
        if option == 'add':
            added = add(sys.argv[2])
            todos = get()

            print(colored('Added', attrs=attrs), 
                    colored(f'"{added}"', 'green', attrs=attrs), 
                    colored('successfully!', attrs=attrs))
            print(colored('\nTODO:', attrs=attrs))
            for index, todo in enumerate(todos):
                if todo != added:
                    print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
                else:
                    print(colored(f'   [+] {todo}', 'green', attrs=attrs))

        # remove
        elif option == 'remove':
            removed = remove(sys.argv[2])['removed']

            # if removed all
            if isinstance(removed, list):
                print(colored('Removed', attrs=attrs), 
                        colored(f'all', 'red', attrs=attrs), 
                        colored('successfully!', attrs=attrs))
                print(colored('\nTODO:', attrs=attrs))
                # print all removed todos
                for todo in removed:
                    print(colored(f'   [-] {todo["text"]}', 'red', attrs=attrs))

            # if removed one
            else:
                # get all todos
                todos = get()

                print(colored('Removed', attrs=attrs), 
                        colored(f'"{removed["text"]}"', 'red', attrs=attrs), 
                        colored('successfully!', attrs=attrs))
                print(colored('\nTODO:', attrs=attrs))

                # print all todos
                for index, todo in enumerate(todos):
                    if index == removed['index']:
                        # print removed todo
                        print(colored(f'   [-] {removed["text"]}', 'red', attrs=attrs))
                    print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))

        # settings
        elif option == 'settings':
            pass

        else:
            print(f'Illegal option "{sys.argv[1]}".')
        
    else:
        print(f'Invalid number of arguments.')


# GET
def get():
    todos = []

    # if local version
    if not config['remote']:
        # check if file exists
        if not os.path.isfile(file_path):
            open(config['path'] + file_name, 'w').close()

        with open(config['path'] + file_name, 'r') as file:
            for line in file:
                todos.append(line.strip())

    # if remote version
    else:
        # http request
        response = requests.get(config['path'])

        # check response code
        if response.status_code == 200:
            todos = json.loads(response.text)
        else:
            print(response.text)
            exit(2)

    return todos


# ADD
def add(todo):
    # if local version
    if not config['remote']:
        with open(file_path, 'a') as file:
            file.write(todo + '\n')
        added = todo

    # if remote version
    else:
        # http request
        response = requests.post(config['path'], data={'todo': todo})

        # check for status code
        if response.status_code != 200:
            print(response.text)
            exit(2)
        
        added = json.loads(response.text)['added']

    return added


# REMOVE
def remove(index):
    # if local version
    if not config['remote']:
        # read file data
        with open(file_path, 'r') as file:
            infile = file.readlines()

        # check index validity
        index = request.args.get('index') 
        if (not index.isnumeric() and index != 'all') or int(index) > len(infile):
            return "Invalid index", 404
 
        # delete
        if index == 'all':
            deleted = []

            # delete all
            with open(file_name, 'w') as file:
                for line in infile:
                    deleted.append(line.strip())
 
            return jsonify(deleted)
        else:
            # delete the line
            index = int(index) - 1
            with open(file_path, 'w') as file:
                for line_index, line in enumerate(infile):
                    if line_index != index:
                        file.write(line)
                    else:
                        deleted = line.strip()

    # if remote version
    else:
        # http request
        response = requests.delete(config['path'], params={'index': index})

        # check response code
        if response.status_code == 200:
            deleted = json.loads(response.text)
        else:
            print(response.text)
            exit(2)
            
    return deleted

if __name__ == '__main__':
    main()
