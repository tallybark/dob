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

import os

from click_hotoffthehamster import ClickException

import fauxfactory
import pytest

import nark

from dob.facts.export_facts import export_facts

from .. import truncate_to_whole_seconds


class TestExport(object):
    """Unittests related to data export."""
    @pytest.mark.parametrize('format', ['html', fauxfactory.gen_latin1()])
    def test_invalid_format(self, controller_with_logging, format, mocker):
        """Make sure that passing an invalid format exits prematurely."""
        controller = controller_with_logging
        with pytest.raises(ClickException):
            export_facts(controller, format)

    def test_csv(self, controller, controller_with_logging, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        nark.reports.CSVWriter = mocker.MagicMock()
        export_facts(controller, 'csv')
        assert nark.reports.CSVWriter.called

    def test_tsv(self, controller, controller_with_logging, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        nark.reports.TSVWriter = mocker.MagicMock()
        export_facts(controller, 'tsv')
        assert nark.reports.TSVWriter.called

    def test_ical(self, controller, controller_with_logging, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        nark.reports.ICALWriter = mocker.MagicMock()
        export_facts(controller, 'ical')
        assert nark.reports.ICALWriter.called

    def test_xml(self, controller, controller_with_logging, mocker):
        """Ensure passing 'xml' as format returns appropriate writer class."""
        nark.reports.XMLWriter = mocker.MagicMock()
        export_facts(controller, 'xml')
        assert nark.reports.XMLWriter.called

    def test_with_since(self, controller, controller_with_logging, tmpdir, mocker):
        """Make sure that passing a end date is passed to the fact gathering method."""
        controller.facts.gather = mocker.MagicMock()
        path = os.path.join(tmpdir.mkdir('report').strpath, 'report.csv')
        nark.reports.CSVWriter = mocker.MagicMock(
            return_value=nark.reports.CSVWriter(path),
        )
        since = fauxfactory.gen_datetime()
        # Get rid of fractions of a second.
        since = truncate_to_whole_seconds(since)
        export_facts(controller, 'csv', since=since.strftime('%Y-%m-%d %H:%M'))
        args, kwargs = controller.facts.gather.call_args
        assert kwargs['since'] == since

    def test_with_until(self, controller, controller_with_logging, tmpdir, mocker):
        """Make sure that passing a until date is passed to the fact gathering method."""
        controller.facts.gather = mocker.MagicMock()
        path = os.path.join(tmpdir.mkdir('report').strpath, 'report.csv')
        nark.reports.CSVWriter = mocker.MagicMock(
            return_value=nark.reports.CSVWriter(path),
        )
        until = fauxfactory.gen_datetime()
        until = truncate_to_whole_seconds(until)
        export_facts(controller, 'csv', until=until.strftime('%Y-%m-%d %H:%M'))
        args, kwargs = controller.facts.gather.call_args
        assert kwargs['until'] == until

    def test_with_filename(self, controller, controller_with_logging, tmpdir, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        path = os.path.join(tmpdir.ensure_dir('export').strpath, 'export.csv')
        nark.reports.CSVWriter = mocker.MagicMock()
        export_facts(controller, 'csv', file_out=path)
        assert nark.reports.CSVWriter.called

