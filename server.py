import os
import sys

from flask import Flask, jsonify, request

from todo import get, add, remove

app = Flask(__name__)

"""
    TODOs:
"""

file_name = 'todos.txt'

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def todo():
    # GET
    if request.method == 'GET':
        return jsonify(get())

    # POST
    elif request.method == 'POST':
        todo = request.form.get('add')
        print(todo)
        return jsonify(add(todo))

    # DELETE
    else:
        arg = request.args.get('remove')
        return jsonify(remove(arg))

