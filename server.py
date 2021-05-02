import os
import sys

from flask import Flask, jsonify, request

from todo import get, add, remove

app = Flask(__name__)

"""
    TODOs:
"""

file_name = 'main.todo'

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def todo():
    # GET
    if request.method == 'GET':
        data = get('main')
        data['name'] = 'remote'
        return jsonify(data)

    # POST
    elif request.method == 'POST':
        added = request.form.get('add')
        data = add('main', added)
        data['name'] = 'remote'
        return jsonify(data)

    # DELETE
    else:
        removed = request.args.get('remove')
        data = remove('main', removed)
        data['name'] = 'remote'
        return jsonify(data)

@app.route('/<name>')
def links(name):
    return jsonify(get(name))