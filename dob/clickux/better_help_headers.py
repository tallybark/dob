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

from .help_header import help_header_format

__all__ = (
    'ClickBetterHeadersGroup'
)


class ClickBetterHeadersGroup(click.Group):

    def __init__(self, *args, **kwargs):
        super(ClickBetterHeadersGroup, self).__init__(*args, **kwargs)

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
        # click.core's behavior: return 'Commands:' (with a colon;
        # but we prefer an underline instead).
        return help_header_format(_('Commands'))

