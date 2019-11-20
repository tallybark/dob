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

from click.core import Option
from click_alias import ClickAliasedGroup

from nark.helpers.emphasis import attr

from .bunchy_group import ClickBunchyGroup
from .help_header import help_header_format
from .plugin_group import ClickPluginGroup

__all__ = (
    'ClickAliasableBunchyPluginGroup'
)


class ClickAliasableBunchyPluginGroup(
    # ClickBunchyGroup comes first, because
    # its format_commands shadows others'.
    ClickBunchyGroup,
    ClickAliasedGroup,
    ClickPluginGroup,
):

    def __init__(self, *args, **kwargs):
        super(ClickAliasableBunchyPluginGroup, self).__init__(*args, **kwargs)

    def command(self, *args, **kwargs):
        # And awaaaaaay we hack!
        # Ensure that all subcommand classes are also this class.
        kwargs.setdefault('cls', self.__class__)
        # So that Click does not complain `Error: Missing command.` when all
        # we want is a little `dob command --help`, always assume
        # invoke_without_command... which is funny, because some commands
        # you can invoke without a command by dropping the option, e.g.,
        # `dob init` works just fine, but `dob init --help` elicits the
        # missing-command complaint from Click. In any case dob.py already
        # wires commands to display help or not as appropriate depending how
        # they're called, e.g., `dob init` runs the init action, but `dob migrate`
        # prints the help for the dob-migrate group of commands.
        kwargs.setdefault('invoke_without_command', True)
        return super(ClickAliasableBunchyPluginGroup, self).command(*args, **kwargs)

    @property
    def help_header_options(self):
        # (lb): Without having the caller pass us the ctx, so we can
        # check ctx.parent is None to know if this is the root command
        # or not, we can use our business knowledge to check the command
        # name, which is 'run', the name of the root callback in run_cli.
        # - I'd rather use ctx.parent is None, and not do a string compare,
        #   but this is dirt cheap and easy squeeze y.
        if self.name == 'run':
            return help_header_format(_('Global Options'))
        return help_header_format(_('Command Options'))

    @property
    def help_header_commands(self):
        # click.core's behavior: return 'Commands:'
        return help_header_format(_('Commands'))

    def format_usage(self, ctx, formatter):
        """Writes the usage line into the formatter.

        This is a low-level method called by :meth:`get_usage`.

        Overriden by dob to emphasize with _underline_ and **bold**.
        """
        prog = '{bold}{prog}{reset}'.format(
            bold=attr('bold'),
            prog=ctx.command_path,
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
            ClickAliasableBunchyPluginGroup, self
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

