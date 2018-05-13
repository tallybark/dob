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

from hamster_lib import reports

__all__ = ['export_facts']

def export_facts(
    controller,
    format,
    start,
    end,
    activity=None,
    category=None,
    tag=None,
    description=None,
    key=None,
    filename=None,
):
    """
    Export all facts in the given timeframe in the format specified.

    Args:
        format (str): Format to export to. Valid options are: ``csv``, ``xml`` and ``ical``.
        start (datetime.datetime): Consider only facts starting at this time or later.
        end (datetime.datetime): Consider only facts starting no later than this time.

    Returns:
        None: If everything went alright.

    Raises:
        click.Exception: If format is not recognized.
    """
    accepted_formats = ['csv', 'tsv', 'ical', 'xml']
    # [TODO]
    # Once hamster_lib has a proper 'export' register available we should be able
    # to streamline this.
    if format not in accepted_formats:
        message = _("Unrecocgnized export format received")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    if not start:
        start = None
    if not end:
        end = None

    if filename:
        filepath = filename
    else:
        filepath = controller.client_config['export_path']
        filepath = filepath + '.' + format

    #facts = controller.facts.get_all(start=start, end=end)
    facts = search_facts(
        controller,
        start=start,
        end=end,
        activity=activity,
        category=category,
        tag=tag,
        description=description,
        key=key,
    )

    if format == 'csv':
        writer = reports.CSVWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
    elif format == 'tsv':
        writer = reports.TSVWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
    elif format == 'ical':
        writer = reports.ICALWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
    else:
        assert format == 'xml'
        writer = reports.XMLWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))

