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

from helpers.ascii_table import generate_table

__all__ = ['list_activities']

def list_activities(
    controller,
    search_term='',
    category_name='',
    sort_by_category=False,
):
    """
    List all activities. Provide optional filtering by name.

    Args:
        search_term (str): String to match ``Activity.name`` against.

    Returns:
        None: If success.
    """
    category = False
    if category_name:
        # FIXME: (lb): This raises KeyError if no exact match found.
        #        We should at least gracefully exit,
        #        if not do a fuzzy search.
        result = controller.categories.get_by_name(category_name)
        category = result if result else False
    result = controller.activities.get_all(
        search_term=search_term, category=category, sort_by_category=sort_by_category,
    )
    table = []
    headers = (_("Activity"), _("Category"))
    for activity in result:
        if activity.category:
            category = activity.category.name
        else:
            category = None
        table.append((activity.name, category))

    click.echo(generate_table(table, headers=headers))

