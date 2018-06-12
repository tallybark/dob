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

from . import generate_usage_table
from ..cmd_common import hydrate_activity, hydrate_category

__all__ = ['usage_tags']


def usage_tags(
    controller,
    filter_activity='',
    filter_category='',
    table_type='friendly',
    truncate=False,
    **kwargs
):
    """
    List all tags' usage counts, with filtering and sorting options.

    Returns:
        None: If success.
    """
    activity = hydrate_activity(controller, filter_activity)
    category = hydrate_category(controller, filter_category)
    results = controller.tags.get_all_by_usage(
        activity=activity, category=category, **kwargs
    )
    generate_usage_table(results, table_type=table_type, truncate=truncate)

