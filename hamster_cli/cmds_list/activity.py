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

from ..cmd_common import hydrate_category
from ..helpers.ascii_table import generate_table

__all__ = ['list_activities']

def list_activities(
    controller,
    filter_category='',
    table_type='friendly',
    truncate=False,
    **kwargs
):
    """
    List all activities. Provide optional filtering by name.

    Args:
        search_term (str): String to match ``Activity.name`` against.

    Returns:
        None: If success.
    """
    category = hydrate_category(controller, filter_category)

    results = controller.activities.get_all(
        category=category, **kwargs
    )

    # This is sorta like `hamster usage activity`, except we use
    # separate columns for the activity name and category name,
    # rather than combining as activity@category.
    headers = (_("Activity"), _("Category"))
    actegories = []
    for activity in results:
        if activity.category:
            category_name = activity.category.name
        else:
            category_name = None
        actegories.append((activity.name, category_name))

    generate_table(actegories, headers, table_type, truncate, trunccol=0)

