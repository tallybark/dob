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
from inflector import English, Inflector

from nark.managers.query_terms import QueryTerms

from dob_bright.reports.render_results import render_results
from dob_bright.termio import (
    click_echo,
    dob_in_user_exit,
    dob_in_user_warning,
    highlight_value
)

from ..clickux.cmd_options_search import cmd_options_output_format_facts_only
from ..clickux.query_assist import error_exit_no_results

__all__ = (
    'list_facts',
)


def list_facts(
    controller,
    # - Save for controller, all parameters are CLI --options.
    # - The named keyword arguments listed first are used for output
    #   formatting and not for the query.
    # - Args: Select columns to output.
    hide_usage=False,
    hide_duration=False,
    hide_description=False,
    column=None,
    # - Args: Output formatter processor writer.
    output_format='csv',
    # - Args: Format- and Row-specific arguments.
    table_type='texttable',  # Applies when output_format == 'table'.
    max_width=-1,
    row_limit=None,
    factoid_rule='',
    # - Args: Output constraints.
    output_path=None,
    # - Args: Cell-specific arguments.
    spark_total=None,
    spark_width=None,
    spark_secs=None,
    # - Args: Total reporting arguments.
    show_totals=False,
    hide_totals=False,
    # - Developer controls.
    re_sort=False,
    # - Any unnamed arguments are used as search terms in the query.
    *args,
    # - All remaining keyword arguments correspond to nark.QueryTerms.
    **kwargs
):
    """
    Finds and lists facts according to specified filtering, sorting and display options.

    Writes to stdout, or to the file specified by ``output_path``.

    Arguments:
        Most of the arguments are documented elsewhere.

    Returns:
        None: If success.
    """
    format_restricted = output_format in cmd_options_output_format_facts_only()

    def _list_facts():
        qt = prepare_query_terms(*args, **kwargs)
        results = find_facts(controller, query_terms=qt)
        if not results:
            error_exit_no_results(_('facts'))
        n_total = len(results)
        n_written = display_results(results, qt, output_path)
        report_report_written(controller, output_path, n_total, n_written)

    # ***

    def prepare_query_terms(*args, **kwargs):
        qt = QueryTerms(*args, **kwargs)
        must_grouping_allowed(qt)
        qt.include_stats = should_include_stats(qt)
        qt.sort_cols = decide_sort_cols(qt)
        return qt

    def must_grouping_allowed(qt):
        if not qt.is_grouped or not format_restricted:
            return

        dob_in_user_exit(_(
            'ERROR: Specified format type does not support grouping results.'
        ))

    # Note that the two complementary commands, dob-list and dob-usage,
    # have complementary options, --show-usage and --hide-usage options,
    # and --show-duration and --hide-duration, that dictate if we need
    # the query to include the aggregate columns or not.
    def should_include_stats(qt):
        # If preparing a Factoid export, the FactoidWriter
        # expects a list of items, and not prepared tuples.
        if format_restricted:
            return False

        # If a group-by is specified, the report will show the aggregated names,
        # such as showing 'Activities' instead of 'Activity'. Include the extra
        # aggregate columns.
        if qt.is_grouped:
            return True

        # Not grouping results, so each result is a Fact, but check if the user
        # wants the 'Duration'. (It's an either-or with the SQL code, either you
        # retrieve just item columns, or you retrieve item columns and all extra
        # columns, whether or not you want them all.)
        # - The 'duration' is a simple julianday() - julianday() value, which
        #   the tabulate_results.prepare_duration may or may not use (it might
        #   call fact.delta instead) so really adding stats just to get the
        #   'Duration' is about as unnecessary as this comment.
        # - Ignore `not hide_usage` -- 'uses' obviously 1 because not qt.is_grouped.
        # - Check for 'sparkline' output, which is calculated from 'duration'.
        #   - Again, we could just do this during post-processing in tabulate_results.
        if (
            not hide_duration
            and (not column or (
                True
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

    def find_facts(controller, **kwargs):
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
        except Exception as err:
            # - NotImplementedError happens if db.engine != 'sqlite', because
            #   get_all uses SQLite-specific aggregate functions.
            # - ParserInvalidDatetimeException happens on bad since or until.
            dob_in_user_exit(str(err))

    # ***

    def display_results(results, qt, output_path):
        row_limit = suss_row_limit(qt)
        n_written = render_results(
            controller,
            results,
            query_terms=qt,
            hide_usage=hide_usage,
            hide_duration=hide_duration,
            hide_description=hide_description,
            custom_columns=column,
            output_format=output_format,
            table_type=table_type,
            max_width=max_width,
            row_limit=row_limit,
            factoid_rule=factoid_rule,
            output_path=output_path,
            spark_total=spark_total,
            spark_width=spark_width,
            spark_secs=spark_secs,
            show_totals=show_totals,
            hide_totals=hide_totals,
            re_sort=re_sort,
        )
        return n_written

    def suss_row_limit(qt):
        # Limit the number of rows dumped, unless user specified --limit,
        # or if not dumping to the terminal.
        _row_limit = row_limit
        # Note: Not caring about qt.limit here, as the query limit is
        # a separate concern from the row limit.
        if _row_limit is None and not output_path and sys.stdout.isatty():
            _row_limit = controller.config['term.row_limit']
        return _row_limit

    # ***

    def report_report_written(controller, output_path, n_total, n_written):
        if (
            not output_path
            or not sys.stdout.isatty()
            # (lb): I don't quite like this coupling, but it works:
            #       - Don't click_echo if carousel_active.
            or controller.ctx.command.name == 'edit'
        ):
            # If writ to stdout or pager, skip count and path report.
            return
        # Otherwise, path was formed from, e.g., "export.{format}", so display actual.

        if n_written < n_total:
            echo_warn_if_truncated(controller, n_written, n_total)

        click_echo(_(
            "Wrote {n_written} {facts} to {output_path}"
        ).format(
            n_written=highlight_value(n_written),
            facts=Inflector(English).conditional_plural(n_written, _('Fact')),
            output_path=highlight_value(output_path),
        ))

    def echo_warn_if_truncated(controller, n_results, n_rows):
        if n_results <= n_rows:
            return

        dob_in_user_warning(_(
            'Showed only {} of {} results. Use `-C term.row_limit=0` to see all results.'
        ).format(format(n_results, ','), format(n_rows, ',')))

    # ***

    _list_facts()

