import argparse
import os
import subprocess
import sys

import click

from substra.cli.interface import cli

localdir = os.path.dirname(os.path.abspath(__file__))


def _click_parse_node(name, command, parent, callback):
    ctx = click.Context(command, info_name=name, parent=parent)
    if not hasattr(ctx.command, 'commands'):
        callback(ctx.command_path)
        return

    for c in sorted(ctx.command.commands.values(), key=lambda x: x.name):
        _click_parse_node(c.name, c, ctx, callback)


def click_get_commands(name, command):

    commands = []

    def cb(command_path):
        commands.append(command_path)

    _click_parse_node(name, command, None, cb)
    return commands


def generate_help(commands, fh):
    fh.write(f"# Summary\n\n")

    def _create_anchor(command):
        return "#{}".format(command.replace(' ', '-'))

    for command in sorted(commands):
        anchor = _create_anchor(command)
        fh.write(f"- [{command}]({anchor})\n")

    fh.write("\n\n")
    fh.write(f"# Commands\n\n")

    for command in sorted(commands):
        anchor = _create_anchor(command)
        command_args = command.split(' ')
        command_args.append('--help')
        command_helper = subprocess.check_output(command_args)
        command_helper = command_helper.decode('utf-8')

        fh.write(f"## {command}\n\n")
        fh.write("```bash\n")
        fh.write(command_helper)
        fh.write("```\n\n")


def write_help(path):
    commands = click_get_commands('substra', cli)
    with open(path, 'w') as fh:
        generate_help(commands, fh)


if __name__ == '__main__':

    def _cb(args):
        write_help(args.output_path)

    default_path = os.path.join(localdir, 'README.md')

    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, default=default_path, required=False)
    parser.set_defaults(func=_cb)

    args = parser.parse_args(sys.argv[1:])
    args.func(args)
