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
from click_alias import ClickAliasedGroup

from .bunchy_group import ClickBunchyGroup
from .cmd_common import help_header_format
from .plugins import ClickPluginGroup

__all__ = (
    'ClickAliasableBunchyPluginGroup'
)


class ClickAliasableBunchyPluginGroup(
    # ClickBunchyGroup comes first, because its format_commands shadows others'.
    ClickBunchyGroup,
    ClickAliasedGroup,
    ClickPluginGroup,
):

    def __init__(self, *args, **kwargs):
        super(ClickAliasableBunchyPluginGroup, self).__init__(*args, **kwargs)

    @property
    def help_header_options(self):
        return help_header_format(_('Global Options'))

