#!/usr/bin/env python3
import sys

from termcolor import colored

file_path = '/usr/local/bin/todos/todos.txt'

"""
    TODO
    add
    - print message when creating a todo
    remove
    - add remove *
    - when remove preserve index
    - remove with todo name
    
    - add branches
    - add highlight
"""

def main():
    todos_color = 'grey'
    attrs = ['bold']

    print()
    if len(sys.argv) == 1:
        # get 
        todos = get()
        if len(todos) > 0:
            print(colored('TODO:', attrs=attrs))
            for index, todo in enumerate(todos):
                print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
        else:
            print(colored('TODO list is empty.', 'grey', attrs=attrs))

    elif len(sys.argv) == 3:
        option = sys.argv[1]
        
        # add
        if option == 'add':
            added = add(sys.argv[2])
            todos = get()
            print(colored('TODO:', attrs=attrs))
            for index, todo in enumerate(todos):
                if todo != added:
                    print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
                else:
                    print(colored(f'   [+] {todo}', 'green', attrs=attrs))

        # remove
        elif option == 'remove':
            removed = remove(sys.argv[2])
            todos = get()
            print(colored('TODO:', attrs=attrs))
            for index, todo in enumerate(todos):
                print(colored(f'   [{index + 1}] {todo}', todos_color, attrs=attrs))
            print(colored(f'   [-] {removed}', 'red', attrs=attrs))
            
        else:
            print(f'Illegal option "{sys.argv[1]}".')
        
    else:
        print(f'Invalid number of arguments.')

def get():
    todos = []
    with open(file_path, 'r') as file:
        for line in file:
            todos.append(line.strip())
    return todos

def add(todo):
    with open(file_path, 'a') as file:
        file.write(todo + '\n')
    return todo

def remove(index):
    if not index.isnumeric():
        return None

    with open(file_path, 'r') as file:
        infile = file.readlines()

    index = int(index) - 1
    if index >= len(infile):
        return None

    with open(file_path, 'w') as file:
        for i, line in enumerate(infile):
            if i != index:
                file.write(line)
            else:
                deleted = line.strip()
    return deleted

if __name__ == '__main__':
    main()
