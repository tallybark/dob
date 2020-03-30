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

"""Click Group wrapper combines all our custom classes."""

from gettext import gettext as _

import click_hotoffthehamster as click
from click_hotoffthehamster.core import Option

from dob_bright.termio.style import attr

from ._ansitextwrap import AnsiTextWrapper

__all__ = (
    'ClickBetterUsageGroup'
)


class ClickBetterUsageGroup(click.Group):

    # (lb): What I originally had but pretty wordy,
    # and tends to force usage to wrap:
    # USAGE_HINT_ALL_OPTS = '--GLOBAL-OPTIONS...'
    # USAGE_HINT_CMD_OPTS = '--COMMAND-OPTIONS...'

    USAGE_HINT_ALL_OPTS = '--GLOBAL...'
    USAGE_HINT_CMD_OPTS = '--OPTION...'
    USAGE_HINT_CMD_ARGS = 'ARGS...'

    def __init__(self, *args, **kwargs):
        super(ClickBetterUsageGroup, self).__init__(*args, **kwargs)

    def help_usage_command_path_postfix(self, ctx):
        if self.name == 'run':
            return ''
        # Return everything but the program name, e.g., if ctx.command_path
        # is "dob config dump", returns "config dump".
        return ctx.command_path.split(' ', 1)[1]

    def format_usage(self, ctx, formatter):
        """Writes the usage line into the formatter.

        This is a low-level method called by :meth:`get_usage`.

        Overriden by dob to emphasize with _underline_ and **bold**.
        """
        # We want usage to appear like "dob [--GLOBAL-OPTIONS...] init...",
        # but default click uses ctx.command_path, which is, e.g., "dob init".
        if self.name == 'run':
            prog = ctx.command_path
        else:
            prog = ctx.command_path.split(' ', 1)[0]
        prog = '{} [{}]'.format(
            prog, ClickBetterUsageGroup.USAGE_HINT_ALL_OPTS,
        )
        commands = self.help_usage_command_path_postfix(ctx)
        if commands:
            prog = '{} {}'.format(prog, commands)
        prog = '{bold}{prog}{reset}'.format(
            bold=attr('bold'),
            prog=prog,
            reset=attr('reset'),
        )
        #
        pieces = self.collect_usage_pieces(ctx)
        args = ''
        if pieces:
            args = '{bold}{args}{reset}'.format(
                bold=attr('bold'),
                args=' '.join(pieces),
                reset=attr('reset'),
            )
        #
        prefix = '{underlined}{usage}{reset}: '.format(
            underlined=attr('underlined'),
            usage=_('Usage'),
            reset=attr('reset'),
        )
        #
        formatter.write_usage(
            prog,
            args,
            prefix=prefix,
            cls=AnsiTextWrapper,
            alt_fmt=True,
        )

    def collect_usage_pieces(self, *args, **kwargs):
        """Show '[OPTIONS]' in usage unless command takes none."""
        # MAYBE/2019-11-15: Move this up into Click. Seems legit.
        n_opts = 0
        for param in self.params:
            if isinstance(param, Option):
                n_opts += 1
            # (lb): Skip click.core.Argument objects, which are
            # added separately to the pieces collection.
        self.options_metavar = ''
        if n_opts and self.name != 'run':
            # E.g., [--COMMAND-OPTIONS...]
            self.options_metavar = '[{}]'.format(
                ClickBetterUsageGroup.USAGE_HINT_CMD_OPTS,
            )
        # else, if n_opts and name == 'run', then --GLOBAL-OPTIONS shown instead.
        self.subcommand_metavar = ''
        if self.commands:
            self.subcommand_metavar = 'COMMAND [{}] [{}]'.format(
                ClickBetterUsageGroup.USAGE_HINT_CMD_OPTS,
                ClickBetterUsageGroup.USAGE_HINT_CMD_ARGS,
            )
        return super(
            ClickBetterUsageGroup, self
        ).collect_usage_pieces(*args, **kwargs)

    def format_help(self, ctx, formatter):
        """Override Click.Command: shorter help for commandless root command action."""
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        if (
            (ctx.command.name == 'run')
            and (ctx.invoked_subcommand is None)
            and (not ctx.help_option_spotted)
        ):
            return
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

