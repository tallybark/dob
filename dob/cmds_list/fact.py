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

import sys

from dob_bright.termio import dob_in_user_exit

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
    # CLI --options.
    show_usage=False,
    hide_description=False,
    hide_duration=False,
    column=None,
    chop=False,
    format_tabular=False,
    format_factoid=False,
    table_type='friendly',
    factoid_rule='',
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
        is_grouped = must_grouping_allowed()

        results = perform_search()
        if not results:
            error_exit_no_results(_('facts'))

        display_results(results, is_grouped)

    def must_grouping_allowed():
        is_grouped = (
            get_kwargs('group_activity')
            or get_kwargs('group_category')
            or get_kwargs('group_tags')
        )
        if is_grouped and format_factoid:
            dob_in_user_exit(_(
                'ERROR: Cannot create Factoid report when grouping.'
            ))
        return is_grouped

    def perform_search():
        activity = hydrate_activity(controller, match_activity)
        category = hydrate_category(controller, match_category)

        kwargs['sort_col'] = sort_col()
        results = search_facts(
            controller,
            *args,
            include_usage=show_usage or column,
            **kwargs
        )

        return results

    def sort_col():
        try:
            return kwargs['sort_col']
        except KeyError:
            if not show_usage:
                return ''
            return 'time'

    def display_results(results, is_grouped):
        row_limit = suss_row_limit()

        if format_factoid:
            output_factoid_list(
                controller,
                results,
                row_limit=row_limit,
                factoid_rule=factoid_rule,
                out_file=out_file,
                term_width=term_width,
            )
        elif format_tabular:
            output_ascii_table(
                controller,
                results,
                row_limit=row_limit,
                is_grouped=is_grouped,
                show_usage=show_usage,
                hide_description=hide_description,
                hide_duration=hide_duration,
                custom_columns=column,
                chop=chop,
                table_type=table_type,
            )

    def suss_row_limit():
        # Limit the number of rows dumped, unless user specified --limit,
        # or if not dumping to the terminal.
        row_limit = None
        if sys.stdin.isatty() and get_kwargs('limit') is None:
            row_limit = controller.config['term.row_limit']
        return row_limit

    def get_kwargs(argname):
        try:
            return kwargs[argname]
        except KeyError:
            return None

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
        try:
            return controller.facts.get_all(*args, **kwargs)
        except NotImplementedError as err:
            # This happens if db.engine != 'sqlite', because get_all
            # uses SQLite-specific aggregate functions.
            dob_in_user_exit(str(err))

