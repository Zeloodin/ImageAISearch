""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

from json import dumps, load

from core.tools.variables import JSON_FILE_PATH

def save_json_file(json_dict:dict, path = JSON_FILE_PATH, indent = 4):
    # Serializing json
    json_object = dumps(json_dict, indent=indent, ensure_ascii=False)
    # Writing to sample.json
    with open(path, "w", encoding="utf8") as outfile:
        outfile.write(json_object)

def load_json_file(path = JSON_FILE_PATH):
    # Opening JSON file
    with open(path, 'r', encoding="utf8") as openfile:
        # Reading from json file
        json_object = load(openfile)
        return json_object