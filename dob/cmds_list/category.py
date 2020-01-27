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

from ..clickux.query_assist import error_exit_no_results
from ..helpers.ascii_table import generate_table

__all__ = ('list_categories', )


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

    if not results:
        error_exit_no_results(_('categories'))

    headers = (_("Name"),)
    category_names = []
    for category in results:
        category_names.append((category.name,))

    generate_table(category_names, headers, table_type, truncate, trunccol=0)

