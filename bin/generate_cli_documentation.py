# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import subprocess
import sys

import click

from substra.cli.interface import cli

local_dir = os.path.dirname(os.path.abspath(__file__))


def _click_parse_node(name, command, parent, callback):
    ctx = click.Context(command, info_name=name, parent=parent)
    if not hasattr(ctx.command, 'commands'):
        callback(ctx.command_path)
        return

    # command definitions are sorted in the python script as required for the
    # documentation
    for k, c in ctx.command.commands.items():
        _click_parse_node(c.name, c, ctx, callback)


def click_get_commands(name, command):

    commands = []

    def cb(command_path):
        commands.append(command_path)

    _click_parse_node(name, command, None, cb)
    return commands


def generate_help(commands, fh):
    # TODO use click context to generate help page:
    # https://github.com/click-contrib/click-man/blob/master/click_man/core.py#L20
    fh.write("# Summary\n\n")

    def _create_anchor(command):
        return "#{}".format(command.replace(' ', '-'))

    # XXX order when iterating on commands items must be consistent
    for command in commands:
        anchor = _create_anchor(command)
        fh.write(f"- [{command}]({anchor})\n")

    fh.write("\n\n")
    fh.write("# Commands\n\n")

    for command in commands:
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

    doc_dir = os.path.join(local_dir, '../references')
    default_path = os.path.join(doc_dir, 'cli.md')

    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, default=default_path, required=False)
    parser.set_defaults(func=_cb)

    args = parser.parse_args(sys.argv[1:])
    args.func(args)
