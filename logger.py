import helper 

def print_help():
  pass

def clear_screen():
    import os
    
    if os.name == 'nt': 
        _ = os.system('cls') # windows
    else:        
        _ = os.system('clear') # unix

def print_list(list: list, add: str = None, update: str = None, remove: str = None):
  if add:
    print(f"Added \"{add}\" successfully to the list.\n")

  elif update:
    print(f"Updated \"{update}\" successfully.\n")

  elif remove:
    print(f"Removed \"{remove}\" successfully.\n")
  
  if list:
    for index, todo in enumerate(list):
      print(f"[{index + 1}] {todo['text']}")
      #print(f"{todo['expiration']} {helper.is_today(todo['expiration'])}")
  else:
    print("No todos yet.")

def error(message: str):
  print(f"Error: {message}")
  exit(1)

