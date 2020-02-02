# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
#
# 'dob' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'dob' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

from gettext import gettext as _

from dob_bright.termio import attr, fg, click_echo, echo_exit

from ..run_cli import run


def help_command_help(ctx, command=None):
    cmd = run
    if not command:
        # A simple `dob help`.
        cmd = run
        # The context is the 'help' command, which, if passed to
        # cmd.get_help, shows usage a bit incorrectly, as:
        #
        #   Usage: dob help [OPTIONS] COMMAND [ARGS]...
        #
        # (note the "help"), so specify the parent (the root 'dob'
        # command), so that usage gets printed more accurately as:
        #
        #   Usage: dob [OPTIONS] COMMAND [ARGS]...
        cmd_ctx = ctx.parent
    else:
        # For help on a subcommand, i.e., `dob help command`,
        # use the 'help' command to find the subcommand.
        cmd_ctx = ctx.parent
        parts = []
        for part in command:
            if part.startswith('-'):
                continue
            parts.append(part)
            cmd = cmd.get_command(cmd_ctx, part)
            if cmd is None:
                echo_exit(ctx, _(
                    """
For detailed help, try:
  {codehi}{helpcmd}{reset}

ERROR: No such command: “{command}”
                    """
                ).format(
                    command=' '.join(parts),
                    helpcmd=' '.join([ctx.command_path] + parts[:-1]),
                    codehi=(fg('turquoise_2') or ''),
                    reset=(attr('reset') or ''),
                ).strip(), exitcode=1)
            if isinstance(cmd, tuple):
                cmd = cmd[1]
            # Make a temporary Context to print the help.
            # (lb): This couples dob to Click more tightly than I'd
            # like, but it also means I don't have to sell a lot of
            # little design tweaks to the Click team.
            args = []
            cmd_ctx = cmd.make_context(cmd.name, args, parent=cmd_ctx)

    click_echo(cmd.get_help(cmd_ctx))

