import os
import json


def load(path: str) -> dict | None:
	if not os.path.isfile(path):
		return None

	with open(path, 'r') as file:
		return json.load(file)


def write(path: str, data: dict):
	with open(path, 'w') as file:
		json.dump(data, file)
