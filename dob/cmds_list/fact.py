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
    # CLI --options.
    hide_usage=False,
    hide_duration=False,
    hide_description=False,
    column=None,
    chop=False,
    format_journal=False,
    format_tabular=False,
    format_factoid=False,
    table_type='friendly',
    factoid_rule='',
    out_file=None,
    term_width=None,
    # 2020-05-20: (lb): include_id is not (currently) used (and not CLI --option).
    include_id=False,
    # args is search term(s), if any.
    *args,
    # kwargs is pass-through CLI --options for get_all, including:
    #   group_activity, group_category, group_tags, group_days;
    #   as wells as sort_cols, sort_orders, limit, and offset,
    #   and since, and until.
    **kwargs
):
    """
    List facts, with filtering and sorting options.

    Returns:
        None: If success.
    """
    def _list_facts():
        is_grouped = must_grouping_allowed()
        include_extras = includes_extras(is_grouped)

        results = perform_search(include_extras)
        if not results:
            error_exit_no_results(_('facts'))

        display_results(results, is_grouped, include_extras)

    def must_grouping_allowed():
        is_grouped = (
            get_kwargs('group_activity')
            or get_kwargs('group_category')
            or get_kwargs('group_tags')
            or get_kwargs('group_days')
        )
        if is_grouped and format_factoid:
            dob_in_user_exit(_(
                'ERROR: Cannot create Factoid report when grouping.'
            ))
        return is_grouped

    # Note that the two complementary commands, dob-list and dob-usage,
    # have complementary options, --show-usage and --hide-usage options,
    # and --show-duration and --hide-duration, that dictate if we need
    # the query to include the aggregate columns or not.
    def includes_extras(is_grouped):
        # If a group-by is specified, the report will show the aggregated names,
        # such as showing 'Activities' instead of 'Activity'. Include the extra
        # aggregate columns.
        if is_grouped:
            return True

        # Also include the aggregate columns if the user wants to include the
        # 'Duration' in the output. (Note that we we could compute this after
        # the query, from Fact.end - Fact.start, but currently the SQL query
        # does it with julianday() - julianday() math.)
        if (
            # Ignore `not hide_usage` -- the 'uses' column can be deduced as 1
            # because not is_grouped.
            not hide_duration
            and (not column or (
                True
                # The duration and sparkline could be computed from just the Fact,
                # but currently, get_all does (sqlite) julianday math in SELECT.
                # Tell get_all to return the aggregate columns with each Fact result.
                and 'duration' not in column
                and 'sparkline' not in column
                ))
            ):
            return True

        return False

    def perform_search(include_extras):
        kwargs['sort_cols'] = sort_cols(include_extras)
        results = search_facts(
            controller,
            *args,
            include_extras=include_extras,
            **kwargs
        )

        return results

    def sort_cols(include_extras):
        try:
            return kwargs['sort_cols']
        except KeyError:
            # If request includes the 'duration' column, might as well use it.
            if not include_extras or hide_usage:
                # No 'duration' column, or user is asking to hide the 'uses'
                # column. Fall back to default, order-by 'start'.
                return ('start',)  # The get_all default.
            return ('time',)  # Aka, sort-by 'duration'.

    def display_results(results, is_grouped, includes_extras):
        row_limit = suss_row_limit()

        if format_factoid:
            output_factoid_list(
                controller,
                results,
                row_limit=row_limit,
                include_id=include_id,
                hide_duration=hide_duration,
                chop=chop,
                factoid_rule=factoid_rule,
                out_file=out_file,
                term_width=term_width,
            )
        else:
            # else, either format_tabular or format_journal.
            output_ascii_table(
                controller,
                results,
                row_limit=row_limit,
                is_grouped=is_grouped,
                includes_extras=includes_extras,
                hide_usage=hide_usage,
                hide_duration=hide_duration,
                hide_description=hide_description,
                custom_columns=column,
                chop=chop,
                table_type='journal' if format_journal else table_type,
                sort_cols=get_kwargs('sort_cols'),
                sort_orders=get_kwargs('sort_orders'),
                group_days=get_kwargs('group_days'),
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

