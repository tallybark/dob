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

__all__ = ('list_activities', )


def list_activities(
    controller,
    output_format='table',
    table_style='texttable',
    output_path=None,
    chop=False,
    # These two --hide flags are ignored but specified to keep out of kwargs.
    hide_usage=False,
    hide_duration=False,
    **kwargs
):
    """
    List activities. Provide optional filtering by name.

    Args:
        search_term (str): String to match ``Activity.name`` against.

    Returns:
        None: If success.
    """
    err_context = _('activities')

    results = controller.activities.get_all(**kwargs)

    results or error_exit_no_results(err_context)

    # This is sorta like `dob usage activity`, except we use
    # separate columns for the Activity name and Category name,
    # rather than combining them as Activity@Category.
    headers = (_("Activity Name"), _("Category Name"))
    actegories = []
    for activity in results:
        try:
            category_name = activity.category.name
        except AttributeError:
            category_name = None

        actegories.append((activity.name, category_name))

    render_results(
        controller,
        results=actegories,
        headers=headers,
        output_format=output_format,
        table_style=table_style,
        output_path=output_path,
        chop=chop,
    )

