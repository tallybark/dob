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

"""A time tracker for the command line. Utilizing the power of nark."""

from gettext import gettext as _

import click_hotoffthehamster as click

from nark import reports

from dob_bright.termio import click_echo, highlight_value

from ..cmds_list.fact import search_facts

__all__ = (
    'export_facts',
    'CMD_EXPORT_OPT_FORMAT_CHOICES',
    'CMD_EXPORT_OPT_FORMAT_DEFAULT',
)


# MAYBE/2020-05-20: Have export formats register with this module,
# to make easier to add/remove formats...
CMD_EXPORT_OPT_FORMAT_CHOICES = ['csv', 'tsv', 'xml', 'ical']


CMD_EXPORT_OPT_FORMAT_DEFAULT = 'csv'


def export_facts(
    controller,
    to_format='csv',
    file_out=None,

    # The remaining arguments are a subset of QueryTerms options.

    key=None,

    since=None,
    until=None,
    deleted=False,
    # hidden=False,
    search_term=None,

    match_activities=[],
    match_categories=[],

    # Not supported for export (b/c exports Facts, not aggregates;
    # use reporting for aggregate values, e.g., `dob list`)):
    #  group_activity=False,
    #  group_category=False,
    #  group_tags=False,

    sort_orders=('desc',),

    limit='',
    offset='',
):
    """
    Export all facts in the given timeframe in the format specified.

    Args:
        format (str): Format to export to.
            Valid options are: ``csv``, ``xml`` and ``ical``.
        since (datetime.datetime): Restrict to facts starting at this time or later.
        until (datetime.datetime): Restrict to facts ending no later than this time.

    Returns:
        None: If everything went alright.

    Raises:
        click.Exception: If format is not recognized.
    """

    def _export_facts(since, until):
        must_verify_format(to_format)

        since, until = resolve_since_until(since, until)

        filepath = resolve_filepath(file_out, to_format)

        facts = search_facts(
            controller,

            # The remaining arguments are all the QueryTerms options.
            # The complete list included here as an educational reminder
            # of how the export command is simply a more restrictive list
            # command with different output options.

            raw=False,
            named_tuples=False,
            include_stats=False,

            count_results=False,

            key=key,
            since=since,
            until=until,
            endless=False,
            exclude_ongoing=False,
            partial=False,
            # deleted=deleted,
            deleted=False,

            search_term=search_term,

            activity=False,
            match_activities=match_activities,
            category=False,
            match_categories=match_categories,

            group_activity=False,
            group_category=False,
            group_tags=False,
            group_days=False,

            # sort_cols=sort_cols,
            sort_cols=None,
            sort_orders=sort_orders,

            limit=limit,
            offset=offset,
        )

        # The list and usage commands call error_exit_no_results()
        # if no results. This command does not.

        export_formatted(facts, filepath, to_format)

    def must_verify_format(to_format):
        if to_format in CMD_EXPORT_OPT_FORMAT_CHOICES:
            return

        message = _("Unrecocgnized export format received: {}").format(to_format)
        controller.client_logger.info(message)
        raise click.ClickException(message)

    def resolve_since_until(since, until):
        # EXPLAIN/2020-05-20: (lb): What's the point of this?
        # To convert '' to None... except I think I fixed function
        # that uses since and until to do a truthy check first, so
        # this function probably unnecessary.
        if not since:
            since = None
        if not until:
            until = None
        return since, until

    def resolve_filepath(file_out, to_format):
        if file_out:
            filepath = file_out.format(format=to_format)
        else:
            filepath = ''  # Tell ReportWriter to use sys.stdout.
        return filepath

    def export_formatted(facts, filepath, to_format):
        writer = fetch_export_writer(filepath, to_format)
        writer.write_report(facts)
        writer_report_path(filepath, facts)

    def fetch_export_writer(filepath, to_format):
        if to_format == 'csv':
            writer = reports.CSVWriter(filepath)
        elif to_format == 'tsv':
            writer = reports.TSVWriter(filepath)
        elif to_format == 'ical':
            writer = reports.ICALWriter(filepath)
        else:
            assert to_format == 'xml'
            writer = reports.XMLWriter(filepath)
        return writer

    def writer_report_path(filepath, facts):
        if file_out == filepath:
            # If supplied filename is same as filepath, no need to
            # tell user. Otherwise, filepath was formed from, e.g.,
            # "export.{format}", so spit out formatted filename.
            return

        click_echo(_(
            "{n_facts} Facts were exported to {path}"
        ).format(
            n_facts=highlight_value(len(facts)),
            path=highlight_value(filepath),
        ))

    # ***

    _export_facts(since, until)

