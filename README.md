# todo
**todo** is a program to keep track of todos with simple commands.

## Installation
Clone repository:
```
git clone https://github.com/francesco-dorati/todo.git
```

Move to /usr/local/bin folder:
```
mv todo /usr/local/bin/todos
```

Add symbolic link:
```
ln -s /usr/local/bin/todo /usr/local/bin/todos/todo.py
```

## Usage
Get all TODOs:
```
todo
```

Add a TODO:
```
todo add [todo]
```
```
example:
todo add "New Todo"
```

Remove a TODO:
```
todo remove [index]
```
```
example:
todo remove 1
```

