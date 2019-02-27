import os
import json


class InvalidJSONArgsException(Exception):
    msg = 'String "{args}" is neither a path to a JSON file nor valid JSON: {json_error}'

    def __init__(self, args, json_error):
        super().__init__(self.msg.format(args=args, json_error=json_error))


class InvalidJSONFileException(InvalidJSONArgsException):
    msg = 'File "{args}" is not a valid JSON file: {json_error}'


class InvalidJSONStringException(InvalidJSONArgsException):
    msg = 'String "{args}" is not valid JSON: {json_error}'


def load_json_from_args(args):
    if os.path.isfile(args):
        with open(args, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise InvalidJSONFileException(args, e)
    else:
        try:
            data = json.loads(args)
        except json.JSONDecodeError as e:
            # testing whether args is json-like
            if args[0] in ['[', '{']:
                raise InvalidJSONStringException(args, e)
            else:
                raise InvalidJSONArgsException(args, e)
    return data


