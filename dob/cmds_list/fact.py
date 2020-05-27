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

from nark.managers.query_terms import QueryTerms

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
    # - Save for controller, all parameters are CLI --options.
    # - The named keyword arguments listed first are used for output
    #   formatting and not for the query.
    hide_usage=False,
    hide_duration=False,
    hide_description=False,
    column=None,
    format_journal=False,
    format_tabular=False,
    format_factoid=False,
    table_type='friendly',
    chop=False,
    factoid_rule='',
    spark_total=None,
    spark_width=None,
    spark_secs=None,
    out_file=None,
    row_limit=None,
    term_width=None,
    # - Any unnamed arguments are used as search terms in the query.
    *args,
    # - All remaining keyword arguments correspond to nark.QueryTerms.
    **kwargs
):
    """
    Finds and lists facts according to specified filtering, sorting and display options.

    Writes to stdout, or to the specified ``out_file``.

    Arguments:
        Most of the arguments are documented elsewhere.

    Returns:
        None: If success.
    """
    def _list_facts():
        qt = prepare_query_terms()
        results = search_facts(controller, query_terms=qt)
        if not results:
            error_exit_no_results(_('facts'))
        display_results(results, qt)

    # ***

    def prepare_query_terms():
        qt = QueryTerms(*args, **kwargs)
        must_grouping_allowed(qt)
        qt.include_stats = should_include_stats(qt)
        qt.sort_cols = decide_sort_cols(qt)
        return qt

    def must_grouping_allowed(qt):
        if not qt.is_grouped or not format_factoid:
            return

        dob_in_user_exit(_(
            'ERROR: Cannot create Factoid report when grouping.'
        ))

    # Note that the two complementary commands, dob-list and dob-usage,
    # have complementary options, --show-usage and --hide-usage options,
    # and --show-duration and --hide-duration, that dictate if we need
    # the query to include the aggregate columns or not.
    def should_include_stats(qt):
        # If prepare a Factoid export, the output_factoid_list expects
        # list of items, and nothing more.
        if format_factoid:
            return False

        # If a group-by is specified, the report will show the aggregated names,
        # such as showing 'Activities' instead of 'Activity'. Include the extra
        # aggregate columns.
        if qt.is_grouped:
            return True

        # Also include the aggregate columns if the user wants to include the
        # 'Duration' in the output. (Note that we we could compute this after
        # the query, from Fact.end - Fact.start, but currently the SQL query
        # does it with julianday() - julianday() math.)
        if (
            # Ignore `not hide_usage` -- the 'uses' column can be deduced as 1
            # because not qt.is_grouped.
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

    def decide_sort_cols(qt):
        if qt.sort_cols is not None:
            return qt.sort_cols

        # If request includes the 'duration' column, might as well use it.
        if not qt.include_stats or hide_usage:
            # No 'duration' column, or user is asking to hide the 'uses'
            # column. Fall back to default, order-by 'start'.
            return ('start',)  # The get_all default.
        return ('time',)  # Aka, sort-by 'duration'.

    # ***

    def display_results(results, qt):
        _row_limit = suss_row_limit(qt)

        if format_factoid:
            output_factoid_list(
                controller,
                results,
                row_limit=_row_limit,
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
                row_limit=_row_limit,
                query_terms=qt,
                hide_usage=hide_usage,
                hide_duration=hide_duration,
                hide_description=hide_description,
                custom_columns=column,
                table_type='journal' if format_journal else table_type,
                chop=chop,
                spark_total=spark_total,
                spark_width=spark_width,
                spark_secs=spark_secs,
            )

    def suss_row_limit(qt):
        # Limit the number of rows dumped, unless user specified --limit,
        # or if not dumping to the terminal.
        _row_limit = row_limit
        # Note: Not caring about qt.limit here, as the query limit is
        # a separate concern from the row limit.
        if _row_limit is None and out_file is None and sys.stdout.isatty():
            _row_limit = controller.config['term.row_limit']
        return _row_limit

    _list_facts()


# ***

def search_facts(controller, **kwargs):
    """
    Search for one or more facts, given a set of search criteria and sort options.

    Args:
        query_terms: A QueryTerms object that defines the query.

        **kwargs: Alternatively, pass any or all of the QueryTerms attributes.

    Returns:
        A list of matching Facts, or matching (Fact, *statistics) tuples,
        depending on the QueryTerms.
    """
    try:
        return controller.facts.get_all(**kwargs)
    except NotImplementedError as err:
        # This happens if db.engine != 'sqlite', because get_all
        # uses SQLite-specific aggregate functions.
        dob_in_user_exit(str(err))

