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
from ..facts_format.factoid import output_factoid_list
from ..facts_format.tabular import output_ascii_table

__all__ = (
    'list_facts',
    'search_facts',
)


def list_facts(
    controller,
    include_id=False,
    match_activity='',
    match_category='',
    match_tagnames=[],
    show_usage=False,
    hide_duration=False,
    chop=False,
    table_type='friendly',
    block_format=None,
    rule='',
    out_file=None,
    term_width=None,
    *args,
    **kwargs
):
    """
    List facts, with filtering and sorting options.

    Returns:
        None: If success.
    """
    def _list_facts():
        activity = hydrate_activity(controller, match_activity)
        category = hydrate_category(controller, match_category)

        kwargs['sort_col'] = sort_col()
        results = search_facts(
            controller,
            *args,
            include_usage=show_usage,
            activity=activity,
            category=category,
            tagnames=match_tagnames,
            **kwargs
        )

        if not results:
            error_exit_no_results(_('facts'))

        if block_format:
            output_factoid_list(controller, results, rule, out_file, term_width)
        else:
            output_ascii_table(
                controller, results, show_usage, hide_duration, chop, table_type,
            )

    def sort_col():
        try:
            return kwargs['sort_col']
        except KeyError:
            if not show_usage:
                return ''
            return 'time'

    _list_facts()


# ***

def search_facts(
    controller,
    key=None,
    *args,
    **kwargs
):
    """
    Search for one or more facts, given a set of search criteria and sort options.

    Args:
        search_term: Term that need to be matched by the fact in order to be
            considered a hit.

        FIXME: Keep documenting...
    """
    if key:
        return [controller.facts.get(pk=key)]
    else:
        return controller.facts.get_all(*args, **kwargs)

