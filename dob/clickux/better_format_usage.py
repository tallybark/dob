# -*- coding: utf-8 -*-

# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

"""Click Group wrapper combines all our custom classes."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
from click.core import Option

from nark.helpers.emphasis import attr

__all__ = (
    'ClickBetterUsageGroup'
)


class ClickBetterUsageGroup(click.Group):

    def __init__(self, *args, **kwargs):
        super(ClickBetterUsageGroup, self).__init__(*args, **kwargs)

    def format_usage(self, ctx, formatter):
        """Writes the usage line into the formatter.

        This is a low-level method called by :meth:`get_usage`.

        Overriden by dob to emphasize with _underline_ and **bold**.
        """
        if self.name == 'run':
            prog = ctx.command_path
        else:
            # command_path is, e.g., "dob init", but we want usage to
            # appear like "dob [--GLOBAL-OPTIONS...] init.
            parts = ctx.command_path.split(' ', 2)
            prog = '{} [--GLOBAL-OPTIONS...] {}'.format(*parts)
        prog = '{bold}{prog}{reset}'.format(
            bold=attr('bold'),
            prog=prog,
            reset=attr('reset'),
        )
        #
        pieces = self.collect_usage_pieces(ctx)
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
        formatter.write_usage(prog, args, prefix=prefix)

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
        if n_opts:
            if self.name == 'run':
                self.options_metavar = '[--GLOBAL-OPTIONS...]'
            else:
                self.options_metavar = '[--COMMAND-OPTIONS...]'
        self.subcommand_metavar = ''
        if self.commands:
            self.subcommand_metavar = 'COMMAND [--COMMAND-OPTIONS...] [ARGS...]'
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
        self.format_prolog(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

