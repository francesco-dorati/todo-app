# import 

def print_help():
  print("""
NAME:
   todo-app - Todo app CLI

USAGE:
   todo [list name] [command] [arguments...]

# VERSION:
#   0.15.0

LISTS:
    all           Main list (todo-app/.todo/all.todo)
    today         Computed today list stored inside list "all" (todo-app/.todo/all.todo)
    tomorrow      Computed tomorrow list stored inside list "all" (todo-app/.todo/all.todo)
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

def print_list(
              list: list, 
              name: str, 
              add: str = None, 
              update: tuple[str, str] = None, 
              remove: str = None, 
              move: tuple[str, int, int] = None,
              ):
  print()

  if add:
    print(f"Added \"{add}\" successfully to {name}.\n")

  elif update:
    print(f"Updated \"{update[0]}\" to \"{update[1]}\" successfully from {name}.\n")

  elif remove:
    print(f"Removed \"{remove}\" successfully from {name}.\n")

  elif move:
    print(f'Moved \"{move[0]}\" from position {move[1]} to position {move[2]}.\n')

  if list:
    print(f"\"{name}\" list:")
    for index, todo in enumerate(list):
      print(f"[{index + 1}] {todo['text']}")
      if todo['children']:
        for child_index, child in enumerate(todo['children']):
          print(f"\t[{index + 1}.{child_index + 1}] {child['text']}")
  else:
    print(f"\"{name}\" list is empty.")
  
  print()

def error(message: str):
  print(f"Error: {message}")
  exit(1)

