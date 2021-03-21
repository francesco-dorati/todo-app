#!/usr/bin/env python

def main():
    pass
    

def get():
    todos = []
    with open('todos.txt', 'r') as file:
        for line in file:
            todos.append(line.strip())
    return todos

def add(todo):
    with open('todos.txt', 'a') as file:
        file.write(todo + '\n')

def remove(index):
    with open('todos.txt', 'r') as file:
        infile = file.readlines()

    if index >= len(infile):
        return False

    with open('todos.txt', 'w') as file:
        for i, line in enumerate(infile):
            if i != index:
                file.write(line)
    return True

if __name__ == '__main__':
    main()
