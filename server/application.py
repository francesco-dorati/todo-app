import os

from flask import Flask, jsonify, request

app = Flask(__name__)

"""
    TODOs:
    - change add remove response ({'todos': [{}, {}], 'added': 1 | [2, 3, 4] | 'all'})
"""

file_name = 'todos.txt'

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def todo():
    # GET
    if request.method == 'GET':
        todos = []

        # check if file exists
        if not os.path.isfile('todos.txt'):
            open(file_name, 'w').close()

        # read the file
        with open(file_name) as file:
            for line in file:
                todos.append(line.strip())

        return jsonify(todos)

    # POST
    elif request.method == 'POST':
        todo = request.form.get('todo') + '\n'

        # append the line
        with open(file_name, 'a') as file:
            file.write(todo)

        return jsonify({'added': todo.strip()}) 

    # DELETE
    else:
        # read file data
        with open(file_name, 'r') as file:
            infile = file.readlines()

        # check index validity
        index = request.args.get('index') 
        if (not index.isnumeric() and index != 'all') or (index.isnumeric() and int(index) > len(infile)):
            return "Invalid index", 404

        # delete
        if index == 'all':
            # delete all
            removed = []
            with open(file_name, 'w') as file:
                for line_index, line in enumerate(infile):
                    removed.append({'text': line.strip(), 'index': line_index})

            return jsonify({'removed': removed})
        else:
            # delete the line
            index = int(index) - 1
            with open(file_name, 'w') as file:
                for line_index, line in enumerate(infile):
                    if line_index != index:
                        file.write(line)
                    else:
                        deleted = line.strip()
    
        return jsonify({'removed': {'text': deleted, 'index': index}})

