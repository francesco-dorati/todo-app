import helper 

def print_help():
  pass

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
              order: tuple[str, int, int] = None,
              add_child: tuple[str, str] = None,
              remove_child: tuple[str, str] = None,
              ):
  print()

  if add:
    print(f"Added \"{add}\" successfully to {name}.\n")

  elif update:
    print(f"Updated \"{update[0]}\" to \"{update[1]}\" successfully from {name}.\n")

  elif remove:
    print(f"Removed \"{remove}\" successfully from {name}.\n")

  elif order:
    print(f'Moved \"{order[0]}\" from position {order[1]} to position {order[2]}.\n')

  elif add_child:
    print(f'Added \"{add_child[0]}\" successfully as a child of {add_child[1]} to {name}.\n')

  elif remove_child:
    print(f'Removed \"{remove_child[0]}\" successfully from \"{remove_child[1]}\" in {name}.\n')
  
  if list:
    print(f"{name} list:")
    for index, todo in enumerate(list):
      print(f"[{index + 1}] {todo['text']}")
      if todo['children']:
        for child_index, child in enumerate(todo['children']):
          print(f"\t[{index + 1}.{child_index + 1}] {child['text']}")
      #print(f"{todo['expiration']} {helper.is_today(todo['expiration'])}")
  else:
    print(f"{name} list is empty.")
  
  print()

def error(message: str):
  print(f"Error: {message}")
  exit(1)

