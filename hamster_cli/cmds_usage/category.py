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

import click

from ..helpers.ascii_table import generate_table

__all__ = ['usage_categories']

def usage_categories(
    controller,
    table_type='friendly',
    truncate=False,
    **kwargs
):
    """
    List all categories' usage counts, with filtering and sorting options.

    Returns:
        None: If success.
    """
    results = controller.categories.get_all_by_usage(**kwargs)

    headers = (_("Name"), _("Uses"))
    category_name_counts = []
    for category, count in results:
        category_name_counts.append((category.name, count))

    generate_table(category_name_counts, headers, table_type, truncate, trunccol=0)

