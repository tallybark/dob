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

from . import generate_usage_table

__all__ = ('usage_activities', )


def usage_activities(
    controller,
    hide_usage=False,
    hide_duration=False,
    output_format='table',
    table_style='texttable',
    output_path=None,
    chop=False,
    **kwargs
):
    """
    List all activities. Provide optional filtering by name.

    Args:
        search_term (str): String to match ``Activity.name`` against.

    Returns:
        None: If success.
    """
    def _usage_activities():
        err_context = _('activities')

        results = controller.activities.get_all_by_usage(**kwargs)

        results or error_exit_no_results(err_context)

        generate_usage_table(
            controller,
            results,
            name_header=_("Activity@Category"),
            name_fmttr=name_fmttr,
            hide_usage=hide_usage,
            hide_duration=hide_duration,
            output_format=output_format,
            table_style=table_style,
            output_path=output_path,
            chop=chop,
        )

    def name_fmttr(activity):
        if activity.category:
            category_name = activity.category.name
        else:
            category_name = ''
        actegory = '{}@{}'.format(activity.name, category_name)
        return actegory

    # ***

    _usage_activities()

