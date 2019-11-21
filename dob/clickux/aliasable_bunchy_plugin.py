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

from click_alias import ClickAliasedGroup

from .better_format_usage import ClickBetterUsageGroup
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
    # General click.Group overrides (to clean up help output).
    ClickBetterUsageGroup,
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

