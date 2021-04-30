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
        return jsonify(get('main'))

    # POST
    elif request.method == 'POST':
        added = request.form.get('add')
        return jsonify(add('main', added))

    # DELETE
    else:
        removed = request.args.get('remove')
        return jsonify(remove('main', removed))

@app.route('/<name>')
def links(name):
    return jsonify(get(name))