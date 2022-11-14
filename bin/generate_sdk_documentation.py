import argparse
import inspect
import sys
from pathlib import Path

import docstring_parser

from substra import Client
from substra.sdk.utils import retry_on_exception

MODULE_LIST = [Client, retry_on_exception]

KEYWORDS = ["Args", "Returns", "Yields", "Raises", "Example"]


def generate_function_help(fh, asset):
    """Write the description of a function"""
    fh.write(f"# {asset.__name__}\n")
    signature = str(inspect.signature(asset))
    fh.write("```text\n")
    fh.write(f"{asset.__name__}{signature}")
    fh.write("\n```")
    fh.write("\n\n")
    # Write the docstring
    docstring = inspect.getdoc(asset)
    docstring = docstring_parser.parse(inspect.getdoc(asset))
    fh.write(f"{docstring.short_description}\n")
    if docstring.long_description:
        fh.write(f"{docstring.long_description}\n")
    # Write the arguments as a list
    if len(docstring.params) > 0:
        fh.write("\n**Arguments:**\n")
    for param in docstring.params:
        type_and_optional = ""
        if param.type_name or param.is_optional is not None:
            text_optional = "required"
            if param.is_optional:
                text_optional = "optional"
            type_and_optional = f"({param.type_name}, {text_optional})"
        fh.write(f" - `{param.arg_name} {type_and_optional}`: {param.description}\n")
    # Write everything else as is
    for param in [
        meta_param for meta_param in docstring.meta if not isinstance(meta_param, docstring_parser.DocstringParam)
    ]:
        fh.write(f"\n**{param.args[0].title()}:**\n")
        if len(param.args) > 1:
            for extra_param in param.args[1:]:
                fh.write(f"\n - `{extra_param}`: ")
        fh.write(f"{param.description}\n")


def generate_properties_help(fh, public_methods):
    properties = [(f_name, f_method) for f_name, f_method in public_methods if isinstance(f_method, property)]
    for f_name, f_method in properties:
        fh.write(f"## {f_name}\n")
        fh.write("_This is a property._  \n")
        fh.write(f"{f_method.__doc__}\n")


def generate_help(fh):
    for asset in MODULE_LIST:
        if inspect.isclass(asset):  # Class
            public_methods = [
                (f_name, f_method) for f_name, f_method in inspect.getmembers(asset) if not f_name.startswith("_")
            ]
            generate_function_help(fh, asset)
            generate_properties_help(fh, public_methods)
            for _, f_method in public_methods:
                if not isinstance(f_method, property):
                    fh.write("#")  # Title for the methods are one level below
                    generate_function_help(fh, f_method)
        elif callable(asset):
            generate_function_help(fh, asset)


def write_help(path):
    with path.open("w") as fh:
        generate_help(fh)


if __name__ == "__main__":
    default_path = Path(__file__).resolve().parents[1] / "references" / "sdk.md"

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", type=str, default=str(default_path.resolve()), required=False)

    args = parser.parse_args(sys.argv[1:])
    write_help(Path(args.output_path))
