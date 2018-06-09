# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

"""A time tracker for the command line. Utilizing the power of hamster-lib."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import copy
import re
import sys
from datetime import datetime, timedelta
from six import text_type

from hamster_lib import Fact, reports
from hamster_lib.helpers.colored import fg, bg, attr
from hamster_lib.helpers.dated import (
    datetime_from_clock_after,
    datetime_from_clock_prior,
    parse_clock_time,
    parse_relative_minutes,
)
from hamster_lib.helpers.parsing import parse_factoid

from .cmd_common import barf_and_exit, echo_block_header, fact_block_header
from .cmds_list.fact import search_facts
from .create import echo_fact, mend_facts_times, save_facts_maybe
from .interrogate import ask_user_for_edits

__all__ = ['export_facts', 'import_facts']


def export_facts(
    controller,
    to_format,
    start,
    end,
    filename=None,
    deleted=False,
    hidden=False,
    key=None,
    # search_term='',
    activity=None,
    category=None,
    sort_order='desc',
    limit='',
    offset='',
):
    """
    Export all facts in the given timeframe in the format specified.

    Args:
        format (str): Format to export to.
            Valid options are: ``csv``, ``xml`` and ``ical``.
        start (datetime.datetime): Restrict to facts starting at this time or later.
        end (datetime.datetime): Restrict to facts ending no later than this time.

    Returns:
        None: If everything went alright.

    Raises:
        click.Exception: If format is not recognized.
    """

    def _export_facts(start, end):
        must_verify_format(to_format)

        start, end = resolve_start_end(start, end)

        filepath = resolve_filepath(filename, to_format)

        facts = search_facts(
            controller,
            key=key,
            start=start,
            end=end,
            # deleted
            # search_term
            activity=activity,
            category=category,
            # sort_col
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            # **kwarg
        )

        export_formatted(facts, filepath, to_format)

    def must_verify_format(to_format):
        accepted_formats = ['csv', 'tsv', 'ical', 'xml']
        # [TODO]
        # Once hamster_lib has a proper 'export' register available we should be able
        # to streamline this.
        if to_format not in accepted_formats:
            message = _("Unrecocgnized export format received")
            controller.client_logger.info(message)
            raise click.ClickException(message)

    def resolve_start_end(start, end):
        if not start:
            start = None
        if not end:
            end = None
        return start, end

    def resolve_filepath(filename, to_format):
        if filename:
            filepath = filename
        else:
            filepath = controller.client_config['export_path']
            filepath = filepath + '.' + to_format
        return filepath

    def export_formatted(facts, filepath, to_format):
        if to_format == 'csv':
            writer = reports.CSVWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
        elif to_format == 'tsv':
            writer = reports.TSVWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
        elif to_format == 'ical':
            writer = reports.ICALWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
        else:
            assert to_format == 'xml'
            writer = reports.XMLWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))

    # ***

    _export_facts(start, end)

