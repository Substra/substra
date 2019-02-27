import os
import json


def load_json_from_args(args):
    if os.path.isfile(args):
        with open(args, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise Exception(f'File "{args}" is not a valid JSON file: {e}')
    else:
        try:
            data = json.loads(args)
        except json.JSONDecodeError as e:
            if args[0] in ['[', '{']:
                raise Exception(f'String "{args}" is not valid JSON: {e}')
            else:
                raise Exception(f'String "{args}" is neither a path to a JSON file nor valid JSON: {e}')
    return data


