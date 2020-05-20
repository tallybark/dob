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
    must_hydrate_category
)

from . import generate_usage_table

__all__ = ('usage_activities', )


def usage_activities(
    controller,
    match_category='',
    hide_usage=False,
    hide_duration=False,
    table_type='friendly',
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

        category = must_hydrate_category(controller, match_category, err_context)

        results = controller.activities.get_all_by_usage(category=category, **kwargs)

        results or error_exit_no_results(err_context)

        generate_usage_table(
            results,
            name_fmttr=name_fmttr,
            table_type=table_type,
            chop=chop,
            name_header=_("Activity@Category"),
            hide_usage=hide_usage,
            hide_duration=hide_duration,
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

