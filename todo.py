#!/usr/bin/env python3
import sys
import os
import datetime

import helper
import logger


BASE_PATH = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
SETTINGS_PATH = BASE_PATH + 'settings.json'

# load settings
settings = None
if os.path.isfile(SETTINGS_PATH):
    settings = helper.load_file(SETTINGS_PATH)
    PATH = {
        'a': lambda: settings['path'] + '/all.todo',
        'all': lambda: settings['path'] + '/all.todo',
        'l': lambda: 'local.todo',
        'local': lambda: 'local.todo',
    }

def main():
    match sys.argv[1:]:
        # shell
        case[]:
            shell()

        # setup
        case['setup']:
            setup()

        # create local list
        case['create', 'local']:
            create('local')

        # create list
        case['create', 'list' | 'section' as type, list_name]:
            create(type, list_name)

        # rename
        case['rename', list_name, new_list_name]:
            pass

        # help
        case['h' | 'help']:
            logger.print_help()
            exit()

        # add
        case[list_name, 'a' | 'add', text, *args] if list_name in PATH:
            deadline, position = None, None
            # load args
            if args:
                for index, arg in enumerate(args):
                    match arg:
                        # deadline
                        case 'd' | 'due':
                            deadline = args[index + 1]
                            if not deadline in ['today', 'tomorrow']:
                                logger.error('Deadline not available.')

                        # position
                        case 'p' | 'position':
                            position = args[index + 1]
            add(list_name, text.strip(), deadline, position)

        # update
        case[list_name, 'u' | 'update', index, text, *args] if list_name in PATH:
            append = False
            if args and len(args) == 2:
                match args[0]:
                    # deadline
                    case 'a' | 'append':
                        append = True 
            update(list_name, index, text.strip(), append)

        # remove
        case[list_name, 'r' | 'remove', *index_list] if list_name in PATH:
            if not index_list:
                logger.error('You must provide at least one index.')
            remove(list_name, index_list)

        # move
        case[list_name, 'm' | 'move', starting_index, destination_index] if list_name in PATH:
            move(list_name, starting_index, destination_index)

        # get
        case[list_name, *args] if list_name in PATH:
            deadline = None
            if args and len(args) == 2:
                match args[0]:
                    # deadline
                    case 'd' | 'due':
                        deadline = args[1]
                        if not deadline in ['today', 'tomorrow']:
                            logger.error('Deadline not available.')
            get(list_name, deadline=deadline)

        case _:
            logger.error('Wrong Command')

# todo projects create todo-app
# todo projects todo-app add

# SHELL
def shell():
    current_list = 'all'
    logger.clear_screen()
    get(current_list)

    while True:
        command = input("\n> ").split()
        match command:
            # exit
            case['exit']:
                logger.clear_screen()
                exit()

            # current add
            case['a' | 'add', text]:
                logger.clear_screen()
                add(current_list, text.strip())

            # current update
            case['u' | 'update', index, text]:
                logger.clear_screen()
                update(current_list, int(index), text.strip())

            # current remove
            case['r' | 'remove', index]:
                logger.clear_screen()
                remove(current_list, int(index))

            # list get
            case[list_name]:
                current_list = list_name
                logger.clear_screen()
                get(current_list)

            # list add
            case[list_name, 'a' | 'add', text]:
                current_list = list_name
                logger.clear_screen()
                add(list_name, text.strip())

            # list update
            case[list_name, 'u' | 'update', index, text]:
                current_list = list_name
                logger.clear_screen()
                update(list_name, int(index), text.strip())

            # list remove
            case[list_name, 'r' | 'remove', index]:
                current_list = list_name
                logger.clear_screen()
                remove(list_name, int(index))

# SETUP
def setup():
    # ask for mode
    while True:
        mode = input("Mode (1: local, 2: remote): ")
        if mode == '1':
            mode = 'local'
            break
        elif mode == '2':
            mode = 'remote'
            break

    # local
    if mode == 'local':
        # ask for path
        while True:
            path = input("Path for todo folder (Enter for default): ")
            if path == '':  # default
                path = BASE_PATH
                break
            elif os.path.isdir(path):
                path = path.strip('/') + '/'
                break

        print('Creating files...')

        # create settings file
        helper.write_file(SETTINGS_PATH, {
            'mode': 'local',
            'path': path + '.todo'
        })

        # check if folder already exists
        if os.path.isfile(path + '.todo/all.todo'):
            while True:
                a = input(
                    'A todo folder already exists. Do you want to overwrite it [y/N]? ').lower()
                # overwrite
                if a == 'y' or a == 'yes':
                    print("Overwriting files...")
                    helper.write_file(path + '.todo/all.todo', {
                        'name': 'all',
                        'todos': [],
                    })
                    break

                # do not overwrite
                elif a == 'n' or a == 'no' or a == '':
                    break

        # if does not exist
        else:
            # create todo folder
            os.mkdir(path + '.todo')

            # create list all
            helper.write_file(path + '.todo/all.todo', {
                'name': 'all',
                'todos': [],
            })

        print("Done.")

    # remote
    else:
        # ask for path
        while True:
            path = input("Address for todo server: ")
            print('Connecting to server...')
            if True:    # TODO ping the server and break on response
                print('Connection successful.')
                break
            else:
                print('Server not responding, provide another address.')

        print('Creating files...')

        # create settings file
        helper.write_file(SETTINGS_PATH, {
            'mode': 'remote',
            'path': path,
        })

        print("Done.")

# CREATE
def create(type: str, name: str = None):
    match type:
        case 'list':
            if not name:
                logger.error("List name is required.")
                # todo

        case 'section':
            if not name:
                logger.error("List name is required.")
                # todo

        case 'local':
            if not name:
                name = os.path.basename(os.getcwd())

            # check if local file exists
            if os.path.isfile('local.todo'):
                while True:
                    a = input(
                        'A local todo list already exists. Do you want to overwrite it [y/N]? ').lower()
                    # do not overwrite
                    if a == 'n' or a == 'no' or a == '':
                        exit()

                    # overwrite
                    elif a == 'y' or a == 'yes':
                        break

            # create file
            helper.write_file('local.todo', {
                'name': name,
                'todos': []
            })

            print(f"Created new local list \"{name}\" successfully.")

# GET
def get(list_name: str, deadline: str = None):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # load file
    list = helper.load_file(PATH[list_name]())

    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')

    # filter list by deadline
    helper.filter(list, deadline)

    # print the list
    logger.print_list(list)

# ADD
def add(list_name: str, text: str, deadline: str = None, position: str = None):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # load file
    list = helper.load_file(PATH[list_name]())

    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')

    # build the todo
    todo = {
        'text': text,
        'time': str(datetime.datetime.now()),
        'deadline': str(helper.calculate_date(deadline)) if deadline else None,
        'children': []
    }

    # calculate index
    if position:
        child = False
        if position[-1] == '.':
            child = True
            position = position[:-1]

        # unpack index
        index_list = helper.unpack_indexes(position, list['todos'])

        # traverse the list
        current = list['todos']
        last_index = len(index_list) - 1
        for i, index in enumerate(index_list):
            # if last index
            if i == last_index:
                if child:
                    current[index]['children'].append(todo)
                else:
                    current.insert(index, todo)
            else:
                # next child
                current = current[index]['children']

    # no position
    else:
        # insert the todo
        list['todos'].append(todo)

    # write to file
    helper.write_file(PATH[list_name](), list)

    # print the list
    logger.print_list(list, add=text)

# UPDATE
def update(list_name: str, index_string: str, text: str, append: bool = False):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # load file
    list = helper.load_file(PATH[list_name]())
    
    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')
    
    # unpack index
    index_list = helper.unpack_indexes(index_string, list['todos'])

    current = list['todos']
    last_index = len(index_list) - 1
    for i, index in enumerate(index_list):
        if i == last_index:
            old_text = current[index]['text']
            if append:
               current[index]['text'] = current[index]['text'] + text
            else:
                current[index]['text'] = text
        else:
            # next child
            current = current[index]['children']

    # write to file
    helper.write_file(PATH[list_name](), list)

    # print the list
    logger.print_list(list, update=(old_text, text))

# REMOVE
def remove(list_name: str, index_list: list):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # load file
    list = helper.load_file(PATH[list_name]())

    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')
    
    # get todos to delete (in current index)
    delete_list = []
    for index_string in index_list:
        # unpack index
        destructured_index = helper.unpack_indexes(index_string, list['todos'])
        
        # traverse the list
        current = list['todos']
        last_index = len(destructured_index) - 1
        for i, index in enumerate(destructured_index):
            # if last index
            if i == last_index:
                # add item to delete list
                delete_list.append(current[index])
            else:
                # next child
                current = current[index]['children']
    
    # delete todos
    for i, index_string in enumerate(index_list):
        # unpack index
        destructured_index = helper.unpack_indexes(index_string, list['todos'])
        
        # traverse the list
        current = list['todos']
        last_index = len(destructured_index) - 1
        for ii, index in enumerate(destructured_index):
            # if last index
            if ii == last_index:
                # add item to delete list
                current.remove(delete_list[i])
            else:
                # next child
                current = current[index]['children']

    # write to file
    helper.write_file(PATH[list_name](), list)

    # print the list
    logger.print_list(list, remove=delete_list[0]['text'])

# MOVE
def move(list_name: str, start_string: int, end_string: int):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # load file
    list = helper.load_file(PATH[list_name]())

    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')
    
    # child check
    child = False
    if end_string[-1] == '.':
        child = True
        end_string = end_string[:-1]
    
    # unpack indexes
    start_list = helper.unpack_indexes(start_string, list['todos'])
    end_list = helper.unpack_indexes(end_string, list['todos'])

    # get the todo to be moved
    current1 = list['todos']
    last_index = len(start_list) - 1
    for i, index in enumerate(start_list):
        # if last index
        if i == last_index:
            # store the todo
            todo = current1[index]
            current1[index] = 'DELETED'
        else:
            # next child
            current1 = current1[index]['children']

    # add the new todo
    current2 = list['todos']
    last_index = len(end_list) - 1
    for i, index in enumerate(end_list):
        # if last index
        if i == last_index:
            if child:
                current2[index]['children'].append(todo)
            else:
                current2.insert(index, todo)
        else:
            # next child
            current2 = current2[index]['children'] 

    # delete old todo
    current1.remove('DELETED')

    # write to file
    helper.write_file(PATH[list_name](), list)

    # print the list
    logger.print_list(list, move=(todo['text'], start_string, end_string))


if __name__ == '__main__':
    main()

exit()