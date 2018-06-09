# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from ..helpers.ascii_table import generate_table

__all__ = ['list_categories']


def list_categories(
    controller,
    table_type='friendly',
    truncate=False,
    **kwargs
):
    """
    List all existing categories, ordered by name.

    Returns:
        None: If success.
    """
    results = controller.categories.get_all(**kwargs)

    headers = (_("Name"),)
    category_names = []
    for category in results:
        category_names.append((category.name,))

    generate_table(category_names, headers, table_type, truncate, trunccol=0)

