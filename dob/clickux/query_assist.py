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

from dob_bright.termio import dob_in_user_exit

__all__ = (
    'error_exit_no_results',
    'hydrate_activity',
    'hydrate_category',
)


# ***

def error_exit_no_results(item_type):
    # MAYBE: (lb): Should we exit on error?
    #              Print message but not error?
    #              Print empty table?
    #              Only print if no facts whatsoever,
    #                as opposed to no facts matching query?
    #        I'd say either print message on stderr and exit, or
    #        print empty table on stdout, so that a tool in the
    #        pipeline would only see empty string or empty table
    #        on stdin, and never a message, so that post-processing
    #        won't die on unexpected error message string.
    msg = _('No {} were found for the specified query.').format(item_type)
    # (lb): I sorta like the message, not table, on no results,
    # because you can tell quicker that nothing was found. I.e.,
    # when I see an empty tell, I spend a nanosecond scanning it
    # for rows, because when I see table headers, I expect to see
    # table rows! So I'm kinda liking printing a message, not table.
    dob_in_user_exit(msg)


# ***

def hydrate_activity(controller, activity_name):
    """Fetch an activity from the back end."""
    activity = False
    if activity_name:
        # FIXME: (lb): This raises KeyError if no exact match found.
        #        We should at least gracefully exit,
        #        if not do a fuzzy search.
        result = controller.activities.get_by_name(activity_name)
        activity = result if result else False
    return activity


# ***

def hydrate_category(controller, category_name):
    """Fetch a category from the backend."""
    category = False
    if category_name:
        # FIXME: (lb): This raises KeyError if no exact match found.
        #        We should at least gracefully exit,
        #        if not do a fuzzy search.
        result = controller.categories.get_by_name(category_name)
        category = result if result else False
    return category

