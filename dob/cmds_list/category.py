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

from dob_bright.reports.render_results import render_results

from ..clickux.query_assist import error_exit_no_results

__all__ = ('list_categories', )


def list_categories(
    controller,
    output_format='table',
    table_type='texttable',
    max_width=-1,
    output_path=None,
    # These two --hide flags are ignored but specified to keep out of kwargs.
    hide_usage=False,
    hide_duration=False,
    **kwargs
):
    """
    List category names, optionally filtered and formatted specially.

    Writes to stdout, or to the file specified by ``output_path``.
    """
    err_context = _('categories')

    results = controller.categories.get_all(**kwargs)

    results or error_exit_no_results(err_context)

    headers = (_("Category Name"),)
    category_names = []
    for category in results:
        category_name = category.name if category else '<NULL>'
        category_names.append((category_name,))

    render_results(
        controller,
        results=category_names,
        headers=headers,
        output_format=output_format,
        table_type=table_type,
        max_width=max_width,
        output_path=output_path,
    )

