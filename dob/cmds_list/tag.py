# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
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

from gettext import gettext as _

from ..clickux.query_assist import (
    error_exit_no_results,
    hydrate_activity,
    hydrate_category
)
from ..helpers.ascii_table import generate_table

__all__ = ('list_tags', )


def list_tags(
    controller,
    filter_activity='',
    filter_category='',
    table_type='friendly',
    truncate=False,
    **kwargs
):
    """
    List tags, with filtering and sorting options.

    Returns:
        None: If success.
    """
    activity = hydrate_activity(controller, filter_activity)
    category = hydrate_category(controller, filter_category)
    results = controller.tags.get_all(
        activity=activity, category=category, **kwargs
    )

    if not results:
        error_exit_no_results(_('tags'))

    headers = (_("Name"),)
    tag_names = []
    for tag in results:
        tag_names.append((tag.name,))

    generate_table(tag_names, headers, table_type, truncate, trunccol=0)

