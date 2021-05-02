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
        data = jsonify(get('main'))
        data['name'] = 'remote'
        return data

    # POST
    elif request.method == 'POST':
        added = request.form.get('add')
        data = jsonify(add('main', added))
        data['name'] = 'remote'
        return data

    # DELETE
    else:
        removed = request.args.get('remove')
        data = jsonify(remove('main', removed))
        data['name'] = 'remote'
        return data

@app.route('/<name>')
def links(name):
    return jsonify(get(name))