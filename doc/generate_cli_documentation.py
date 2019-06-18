import os
import subprocess

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
    for command in commands:
        command_args = command.split(' ')
        command_args.append('--help')
        h = subprocess.check_output(command_args)

        fh.write(f"# Command {command}\n\n")
        fh.write("```bash\n")
        fh.write(h.decode('utf-8'))
        fh.write("```\n\n")


if __name__ == '__main__':
    output_path = os.path.join(localdir, 'README.md')
    commands = click_get_commands('substra', cli)
    with open(output_path, 'w') as fh:
        generate_help(commands, fh)
