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

from click_hotoffthehamster_alias import ClickAliasedGroup

from .better_format_usage import ClickBetterUsageGroup
from .better_help_headers import ClickBetterHeadersGroup
from .bunchy_group import ClickBunchyGroup
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
    ClickBetterHeadersGroup,
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

