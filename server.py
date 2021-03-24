import os
import sys

from flask import Flask, jsonify, request

from todo import get, add, remove

app = Flask(__name__)

"""
    TODOs:
"""

file_name = 'main.json'

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def todo():
    # GET
    if request.method == 'GET':
        return jsonify(get(file_name))

    # POST
    elif request.method == 'POST':
        added = request.form.get('add')
        return jsonify(add(file_name, added))

    # DELETE
    else:
        removed = request.args.get('remove')
        return jsonify(remove(file_name, removed))

