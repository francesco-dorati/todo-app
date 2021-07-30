import sys
import helper

def print_help():
  print("""
NAME:
   todo-app - Todo app CLI

USAGE:
   todo [list name] [command] [arguments...]

VERSION:
   1.0.0

LISTS:
    all           Main list (todo-app/.todo/all.todo)
    local         Local todo list stored in local folder (./local.todo)

COMMANDS: 
    todo                                  Open todo terminal
    todo setup                            Setup list
    todo [list]                           Print list
    ... a, add [text]                     Add todo
    ... [index] a, add [text]             Add todo as a child of another
    ... u, update [index] [text]          Update todo to a new text
    ... m, move [index] [destination]     Move todo
    ... r, remove [index]                 Remove todo
    ... h, help                           Show help
  """)

def clear_screen():
    import os
    
    if os.name == 'nt': 
        _ = os.system('cls') # windows
    else:        
        _ = os.system('clear') # unix

"""
Added ""[ at position 1.2][ due tomorrow].
Removed "" from position  list.
Removed "" from list.

All list[ filtered by {filter}]:
  [1] ciao

"""
def print_list(
  list_name: str,
  list: list, 
  filter: str = None, 
  add: dict = None, # {'text', 'index'}
  update: dict = None, # {'index', 'new'} 
  move: dict = None, # {'text', 'old', 'new'}
  remove: dict | list = None, # {'text', 'index'} | ['1.2', '4.3.1]
):
  print()

  colors = {
    'black': "\033[0;30m",
    'red': "\033[0;31m",
    'green': "\033[0;32m", 
    'yellow': "\033[0;33m",
    'blue': "\033[0;34m",
    'purple': "\033[0;35m",
    'cyan': "\033[0;36m", 
    'white': "\033[0;37m"
  }

  background = {
    'on_black': "\033[0;40m",
    'on_red': "\033[0;41m",
    'on_green': "\033[0;42m", 
    'on_yellow': "\033[0;43m",
    'on_blue': "\033[0;44m",
    'on_purple': "\033[0;45m",
    'on_cyan': "\033[0;46m", 
    'on_white': "\033[0;47m", 
  }

  attributes = {
    'bold': "\033[1m",
    'dark': "\033[2m",
    'italic': "\033[3m",
    'underline': "\033[4m",
    'negative': "\033[7m",
    'crossed': "\033[9m",
    'end': "\033[0m"
  }

  # colored
  def colored(text, color=None, background=None, attrs=[]):
    s = ''

    if color:
      s += colors[color]
    if background:
      s += background[background]
    if attrs:
      for a in attrs:
        s += attributes[a]

    s += text + attributes['end']

    return s

  # recursive function
  def recursive_print(list: list, parent_index: str = None):
    for index, todo in enumerate(list):
      index += 1

      if parent_index:
        tabs_number = len(parent_index.split('.')) + 1
        index = f'{parent_index}.{index}'
      else:
        tabs_number = 1
        index = str(index)

      print('    ' * tabs_number +
        f"[{colored(index)}]"+
        f" {todo['text']}" +
        (colored(f' [{helper.compute_date(todo["deadline"])}]', 'blue') if todo["deadline"] and not filter else ''))
    
      if todo['children']:
        recursive_print(todo['children'], index if parent_index else str(index))

  # notifications
  if add:
    print(f"Added \"{add['text']}\" at {add['index']} in {list_name}.\n")
  elif update:
    print(f"Updated {update['index']} to \"{update['new']}\" in {list_name}.\n")
  elif move:
    print(f"Moved \"{move['text']}\" from {move['old']} to {move['new']} in {list_name}.\n")
  elif remove:
    if 'text' in remove:
      print(f"Removed \"{remove['text']}\" at {remove['index']} from {list_name}.\n")
    else:
      print(colored("Removed", 'red') + ' items ', end='')
      print(*[colored(index, 'blue') for index in remove], sep=', ', end='')
      print(f" from {colored(list_name, attrs=['bold'])}\n")

  # title
  print(f"{colored(list_name, attrs=['bold'])} list" +
   (f" filtered by {colored(filter, 'blue')}" if filter else '') +
   ":")

  # list
  if list:
    recursive_print(list)
  else:
    print(colored(f"   list is empty.", attrs=['dark'])) # grey
  
  print()

"""
Your lists:
  - all [10]
  - local [4]
  - projects [5]

"""
def print_available_lists(available_lists):
  print('\nYour lists:')
  for list in available_lists:
    if list in ['a', 'l']:
      continue

    length = len(helper.load_file(available_lists[list])['todos'])
    print(f'  - {list} [{length}]')

def error(message: str):
  sys.stderr.write(f"Error: {message}\n")
  exit(1)
