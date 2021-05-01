# TODOs
**todo** is a program to keep track of todos with simple commands.

## Installation
Clone repository:
```
git clone https://github.com/francesco-dorati/todo-app.git
```

Install dependencies:
```
pip3 install -r todo-app/requirements.txt
```

Move the app folder to `/usr/local/bin` (or any other folder in `$PATH`):
```
sudo mv todo-app /usr/local/bin
```

Add symbolic link (to allow: `$ todo` writing instead of `$ todo.py`):
```
sudo ln -s /usr/local/bin/todo-app/todo.py /usr/local/bin/todo
```



## Usage
### Create a TODO list: `todo create`
```
$ todo create

main TODO list successfully created!

Your main TODOs:
    [?] This TODO list is empty

Add one by running: todo add <todo>

$ _
```

## Add a TODO: `todo add <todo>`
```
$ todo add "todo one"

Added "todo one" successfully to main!

Your main TODOs:
    [+] todo one

$ _
```

### Get all TODOs: `todo`
```
$ todo

Your main TODOs:
   [1] todo one
   
$ _

```

### Remove a TODO: `todo remove <index>`
```
$ todo remove 1

Removed "todo one" successfully from main!

Your main TODOs:
   [-] todo one

$ _
```

## Local
When working on a **project**, it's useful to have a **todolist** to help you remember important things.  
With **todo-app** you can create **local todo lists**.  
Local todo lists are stored directly in the **project folder** as `local.todo`, this file can be added to the `git repository` of the project.

### Create a local TODO list: `todo local create`
```
$ todo local create

Local todo-app TODO list successfully created!

Your todo-app TODOs:
    [?] This TODO list is empty

Add one by running: todo local add <todo>

$ _
```

### Get all local TODOs: `todo local`
### Add a local TODO: `todo local add <todo>`
### Remove a TODO: `todo local remove <index>`

## Remote
Usually, using **many devices** it's difficult to **synchronize** todo lists.  
If you have a **raspberry pi** or any other form of server at home, you can **host your todo list** on the home server.

### In the Server
#### [Install the app](#installation)
#### Serve the app: `todo serve`
```
TODO
```
### In your computer
#### Get remote TODOs: `todo remote`
```
TODO
```
#### Add a remote TODO: `todo remote add <todo>`
#### Remove a remote TODO: `todo remote remove <index>`

## Mode
### Show mode: `todo mode`
```
TODO
```
### Change default mode: `todo mode <mode>`
```
TODO

```
