from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def todo():
    if request.method == 'GET':
        todos = []
        with open('todos.txt') as file:
            for line in file:
                todos.append(line.strip())
        print(todos)
        return jsonify(todos)

    elif request.method == 'POST':
        todo = request.get_json().get('todo') + '\n'
        print(request.data)
        with open('todos.txt', 'a') as file:
            file.write(todo)
        return todo
