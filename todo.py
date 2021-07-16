#!/usr/bin/env python3
import sys
import os
import json
import datetime

# import requests

import helper
import logger


BASE_PATH = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
SETTINGS_PATH = BASE_PATH + 'settings.json'

# load settings
settings = None
if os.path.isfile(SETTINGS_PATH):
    settings = helper.load_file(SETTINGS_PATH)
    PATH = {
        'all': settings['path'] + '/all.todo',
        'local': 'local.todo',
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
            create(type, name)

        # rename
        case['rename', list_name, new_list_name]:
            pass

        # help
        case['h' | 'help']:
            logger.print_help()
            exit()

        # add
        case[list_name, 'a' | 'add', text, *args] if list_name in ['all', 'local']:
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
        case[list_name, 'u' | 'update', index, text, *args] if list_name in ['all', 'local']:
            append = False
            if args and len(args) == 2:
                match args[0]:
                    # deadline
                    case 'a' | 'append':
                        append = True 
            update(list_name, index, text.strip(), append)

        # remove
        case[list_name, 'r' | 'remove', index] if list_name in ['all', 'local']:
            remove(list_name, index)

        # move
        case[list_name, 'm' | 'move', index, destination] if list_name in ['all', 'local']:
            move(list_name, int(index), int(destination))

        # get
        case[list_name, *args] if list_name in ['all', 'local']:
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
    list = helper.load_file(PATH[list_name])

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
    list = helper.load_file(PATH[list_name])

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

        if not index_list:
            logger.error('Invalid index.')

        # validate indexes
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
    helper.write_file(PATH[list_name], list)

    # print the list
    logger.print_list(list, add=text)

# UPDATE
def update(list_name: str, index_string: str, text: str, append: bool = False):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # load file
    list = helper.load_file(PATH[list_name])
    
    # check if file exists
    if not list:
        logger.error(
            f'List \'{list["name"]}\' is not set up yet. Initialize it by running \'todo setup\'')
    
    # unpack index
    index_list = helper.unpack_indexes(index_string, list['todos'])

    if not index_list:
        logger.error('Invalid index.')

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
    helper.write_file(PATH[list_name], list)

    # print the list
    logger.print_list(list, update=(old_text, text))

# REMOVE
def remove(list_name: str, index: str):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    # unpack the indexes
    try:
        index_list = [int(i) - 1 for i in index.split(".")]
    except ValueError:
        logger.error("Invalid index.")

    # check if all indexes are positive
    if any(i < 0 for i in index_list):
        logger.error("Index value must be positive.")

    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # load file
            list = helper.load_file(settings['path'] + '/all.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'all\' is not set up yet. Initialize it by running \'todo setup\'')

            # remove the todo
            match list_name:
                case 'all':
                    # check if index is valid
                    if len(list['todos']) <= index_list[0]:
                        logger.error("Index value out of list.")

                case 'today':
                    # check if index is valid
                    if len(helper.filter_today(list['todos'])) <= index_list[0]:
                        logger.error("Index value out of list.")
                    index_list[0] = list['todos'].index(
                        helper.filter_today(list['todos'])[index - 1])

                case 'tomorrow':
                    # check if index is valid
                    if len(helper.filter_tomorrow(list['todos'])) <= index_list[0]:
                        logger.error("Index value out of list.")
                    index_list[0] = list['todos'].index(
                        helper.filter_tomorrow(list['todos'])[index - 1])

            # remove item
            if len(index_list) == 1:
                removed = list['todos'].pop(index_list[0])['text']
            else:
                removed = list['todos'][index_list[0]]['children'].pop(index_list[1])[
                    'text']

            # write to file
            helper.write_file(settings['path'] + '/all.todo', list)

            # print the list
            match list_name:
                case 'all':
                    logger.print_list(
                        list['todos'], name=list_name, remove=removed)

                case 'today':
                    logger.print_list(helper.filter_today(
                        list['todos']), name=list_name, remove=removed)

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(
                        list['todos']), name=list_name, remove=removed)

        case 'local':
            # load file
            list = helper.load_file('local.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'local\' is not set up yet. Initialize it by running \'todo create local\'')

            # check if index is valid
            if len(list['todos']) <= index_list[0]:
                logger.error("Index value out of list.")

            # remove item
            if len(index_list) == 1:
                removed = list['todos'].pop(index_list[0])['text']
            else:
                removed = list['todos'][index_list[0]]['children'].pop(index_list[1])[
                    'text']

            # write to file
            helper.write_file('local.todo', list)

            # print the list
            logger.print_list(list['todos'], name=list_name, remove=removed)

        case _:
            pass

# MOVE
def move(list_name: str, index: int, destination: int):
    if not settings:
        logger.error(
            'Todo list is not set up yet.\n Initialize it by running \'todo setup\'')

    if index < 1 or destination <= 0:
        logger.error("Index value must be positive.")

    match list_name:
        case 'all' | 'today' | 'tomorrow':
            # load file
            list = helper.load_file(settings['path'] + '/all.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'all\' is not set up yet. Initialize it by running \'todo setup\'')

            match list_name:
                case 'all':
                    # check if index is valid
                    if len(list['todos']) < index or len(list['todos']) < destination:
                        logger.error("Index value out of list.")

                    relative_index, relative_destination = index - 1, destination - 1

                case 'today':
                    # check if index is valid
                    if len(list['todos']) < index or len(list['todos']) < destination:
                        logger.error("Index value out of list.")

                    # get real indexes
                    today = helper.filter_today(list['todos'])
                    relative_index = list['todos'].index(today[index - 1])
                    relative_destination = list['todos'].index(
                        today[destination - 1])

                case 'tomorrow':
                    # check if index is valid
                    if len(list['todos']) < index or len(list['todos']) < destination:
                        logger.error("Index value out of list.")

                    # get real indexes
                    tomorrow = helper.filter_tomorrow(list['todos'])
                    relative_index = list['todos'].index(tomorrow[index - 1])
                    relative_destination = list['todos'].index(
                        tomorrow[destination - 1])

            # change position of item
            item = list['todos'].pop(relative_index)
            list['todos'].insert(relative_destination, item)

            # write to file
            helper.write_file(settings['path'] + '/all.todo', list)

            # print the list
            match list_name:
                case 'all':
                    logger.print_list(list['todos'], name=list_name, move=(
                        item['text'], index, destination))

                case 'today':
                    logger.print_list(helper.filter_today(
                        list['todos']), name=list_name, move=(item['text'], index, destination))

                case 'tomorrow':
                    logger.print_list(helper.filter_tomorrow(
                        list['todos']), name=list_name, move=(item['text'], index, destination))

        case 'local':
            # load file
            list = helper.load_file('local.todo')

            # check if file exists
            if not list:
                logger.error(
                    'List \'local\' is not set up yet. Initialize it by running \'todo create local\'')

            # check if index is valid
            if len(list['todos']) < index or len(list['todos']) < destination:
                logger.error("Index value out of list.")

            relative_index, relative_destination = index - 1, destination - 1

            # change position of item
            item = list['todos'].pop(relative_index)
            list['todos'].insert(relative_destination, item)

            # write to file
            helper.write_file('local.todo', list)

            # print the list
            logger.print_list(list['todos'], name=list_name, move=(
                item['text'], index, destination))


if __name__ == '__main__':
    main()

exit()