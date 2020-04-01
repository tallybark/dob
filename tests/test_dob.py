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

import datetime
import os

from click_hotoffthehamster import ClickException

import fauxfactory
from freezegun import freeze_time
import pytest

import nark

from dob import (
    __package_name__,
    get_version,
    cmds_list,
    details,
    dob
)
from dob.cmds_list.fact import search_facts
from dob.facts.add_fact import add_fact
from dob.facts.cancel_fact import cancel_fact
from dob.facts.echo_fact import echo_ongoing_fact
from dob.facts.export_facts import export_facts
from dob.helpers import ascii_table


from . import truncate_to_whole_seconds


class TestSearchTerm(object):
    """Unit tests for search command."""

    @freeze_time('2015-12-12 18:00')
    def test_search(self, controller, mocker, fact, search_parameter_parametrized):
        """Ensure that search parameters are passed to appropriate backend function."""
        since, until, description, expectation = search_parameter_parametrized
        controller.facts.get_all = mocker.MagicMock(return_value=[fact])
        # F841 local variable '_facts' is assigned to but never used
        _facts = search_facts(controller, since=since, until=until)  # noqa: F841
        controller.facts.get_all.assert_called_with(**expectation)
        # See: nark's test_get_all_various_since_and_until_times
        assert controller.facts.get_all.called
        assert controller.facts.get_all.call_args[1] == {
            'since': expectation['since'],
            'until': expectation['until'],
        }


class TestAddFact(object):
    """Unit test related to starting a new fact."""

    @freeze_time('2015-12-25 18:00')
    @pytest.mark.parametrize(
        ('raw_fact', 'time_hint', 'expectation'),
        [
            # Use clock-to-clock format, the date inferred from now; with actegory.
            ('13:00 to 16:30: foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 25, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 25, 16, 30, 0),
                'tags': [],
            }),
            # Use datetime-to-datetime format, with actegory.
            ('2015-12-12 13:00 to 2015-12-12 16:30: foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 12, 16, 30, 0),
                'tags': [],
            }),
            # The end date is inferred from start date.
            ('2015-12-12 13:00 - 18:00 foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 12, 18, 00, 0),
                'tags': [],
            }),
            # actegory spanning day (straddles) midnight) and spanning multiple days.
            ('2015-12-12 13:00 - 2015-12-25 18:00 foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 25, 18, 00, 0),
                'tags': [],
            }),
            # Create open/ongoing/un-ended fact.
            ('2015-12-12 13:00 foo@bar', 'verify_start', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': None,
                'tags': [],
            }),
            # Create ongoing fact starting at right now.
            ('foo@bar', 'verify_none', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 25, 18, 0, 0),
                'end': None,
                'tags': [],
            }),
            # Tags.
            (
                '2015-12-12 13:00 foo@bar: #precious #hashish, i like ike',
                'verify_start',
                {
                    'activity': 'foo',
                    'category': 'bar',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['precious', 'hashish'],
                    'description': 'i like ike',
                },
            ),
            # Multiple Tags are identified by a clean leading delimiter character.
            (
                '2015-12-12 13:00 foo@bar, #just walk away "#not a tag", blah',
                'verify_start',
                {
                    'activity': 'foo',
                    'category': 'bar',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['just walk away "#not a tag"'],
                    'description': 'blah',
                },
            ),
            # Alternative tag delimiter; and quotes are just consumed as part of tag.
            (
                '2015-12-12 13:00 foo@bar, #just walk away @"totes a tag", blah',
                'verify_start',
                {
                    'activity': 'foo',
                    'category': 'bar',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['just walk away', '"totes a tag"'],
                    'description': 'blah',
                },
            ),
            # Test '#' in description, elsewhere, after command, etc.
            (
                '2015-12-12 13:00 baz@bat",'
                ' #tag1, #tag2 tags cannot come #too late, aha!'
                ' Time is also ignored at end: 12:59',
                'verify_start',
                {
                    'activity': 'baz',
                    'category': 'bat"',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['tag1'],
                    'description': '#tag2 tags cannot come #too late, aha!'
                                   ' Time is also ignored at end: 12:59',
                },
            ),
        ],
    )
    def test_add_new_fact(
        self,
        controller_with_logging,
        mocker,
        raw_fact,
        time_hint,
        expectation,
    ):
        """
        Test that input validation and assignment of start/end time(s) works as expected.

        To test just this function -- and the parametrize, above -- try:

          workon dob
          cdproject
          py.test --pdb -vv -k test_add_new_fact tests/

        """
        controller = controller_with_logging
        controller.facts.save = mocker.MagicMock()
        add_fact(controller, raw_fact, time_hint=time_hint, use_carousel=False)
        assert controller.facts.save.called
        args, kwargs = controller.facts.save.call_args
        fact = args[0]
        assert fact.start == expectation['start']
        assert fact.end == expectation['end']
        assert fact.activity.name == expectation['activity']
        assert fact.category.name == expectation['category']
        expecting_tags = ''
        tagnames = list(expectation['tags'])
        if tagnames:
            tagnames.sort()
            expecting_tags = ['#{}'.format(name) for name in tagnames]
            expecting_tags = '{}'.format(' '.join(expecting_tags))
        assert fact.tagnames() == expecting_tags
        expect_description = expectation.get('description', None)
        assert fact.description == expect_description


class TestStop(object):
    """Unit test concerning the stop command."""

    def test_stop_existing_ongoing_fact(
        self,
        ongoing_fact,
        controller_with_logging,
        mocker,
    ):
        """Make sure stopping an ongoing fact works as intended."""
        mockfact = mocker.MagicMock()
        mockfact.activity.name = 'foo'
        mockfact.category.name = 'bar'
        mocktime = mocker.MagicMock(return_value="%Y-%m-%d %H:%M")
        mockfact.start.strftime = mocktime
        mockfact.end.strftime = mocktime
        current_fact = mocker.MagicMock(return_value=mockfact)
        # While nark still has stop_current_fact, dob replaced stop_fact
        # with add_fact, so it can use all the same CLI magic that the
        # other add-fact commands use. So while we're testing stop-fact
        # here, we're really testing add-fact with a verify-end time-hint.
        controller_with_logging.facts.save = current_fact
        # 2019-12-06: stop_fact was deleted, replaced with add_fact + time_hint.
        add_fact(
            controller_with_logging,
            factoid='',
            time_hint='verify_end',
            use_carousel=False,
        )
        assert controller_with_logging.facts.save.called

    def test_stop_no_existing_ongoing_fact(self, controller_with_logging, capsys):
        """Make sure that stop without actually an ongoing fact leads to an error."""
        with pytest.raises(SystemExit):
            # 2019-12-06: stop_fact was deleted, replaced with add_fact + time_hint.
            add_fact(
                controller_with_logging,
                factoid='',
                time_hint='verify_end',
                use_carousel=False,
            )


class TestCancel(object):
    """Unit tests related to cancelation of an ongoing fact."""

    def test_cancel_existing_ongoing_fact(
        self, ongoing_fact, controller_with_logging, mocker, capsys,
    ):
        """Test cancelation in case there is an ongoing fact."""
        controller = controller_with_logging
        current_fact = mocker.MagicMock(return_value=ongoing_fact)
        controller.facts.cancel_current_fact = current_fact
        cancel_fact(controller)
        out, err = capsys.readouterr()
        assert controller.facts.cancel_current_fact.called
        assert out.startswith('Cancelled: ')

    def test_cancel_no_existing_ongoing_fact(self, controller_with_logging, capsys):
        """Test cancelation in case there is no actual ongoing fact."""
        with pytest.raises(ClickException):
            cancel_fact(controller_with_logging)
            assert False  # Unreachable.


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
        controller.facts.get_all = mocker.MagicMock()
        path = os.path.join(tmpdir.mkdir('report').strpath, 'report.csv')
        nark.reports.CSVWriter = mocker.MagicMock(
            return_value=nark.reports.CSVWriter(path),
        )
        since = fauxfactory.gen_datetime()
        # Get rid of fractions of a second.
        since = truncate_to_whole_seconds(since)
        export_facts(controller, 'csv', since=since.strftime('%Y-%m-%d %H:%M'))
        args, kwargs = controller.facts.get_all.call_args
        assert kwargs['since'] == since

    def test_with_until(self, controller, controller_with_logging, tmpdir, mocker):
        """Make sure that passing a until date is passed to the fact gathering method."""
        controller.facts.get_all = mocker.MagicMock()
        path = os.path.join(tmpdir.mkdir('report').strpath, 'report.csv')
        nark.reports.CSVWriter = mocker.MagicMock(
            return_value=nark.reports.CSVWriter(path),
        )
        until = fauxfactory.gen_datetime()
        until = truncate_to_whole_seconds(until)
        export_facts(controller, 'csv', until=until.strftime('%Y-%m-%d %H:%M'))
        args, kwargs = controller.facts.get_all.call_args
        assert kwargs['until'] == until

    def test_with_filename(self, controller, controller_with_logging, tmpdir, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        path = os.path.join(tmpdir.ensure_dir('export').strpath, 'export.csv')
        nark.reports.CSVWriter = mocker.MagicMock()
        export_facts(controller, 'csv', file_out=path)
        assert nark.reports.CSVWriter.called


class TestCategories(object):
    """Unittest related to category listings."""

    def test_categories(self, controller_with_logging, category, mocker, capsys):
        """Make sure the categories get displayed to the user."""
        controller = controller_with_logging
        controller.categories.get_all = mocker.MagicMock(return_value=[category])
        cmds_list.category.list_categories(controller)
        out, err = capsys.readouterr()
        assert category.name in out
        assert controller.categories.get_all.called


class TestCurrent(object):
    """Unittest for dealing with 'ongoing facts'."""

    def test_no_ongoing_fact(self, controller_with_logging, capsys):
        """Make sure we display proper feedback if there is no current 'ongoing fact."""
        controller = controller_with_logging
        with pytest.raises(SystemExit):
            echo_ongoing_fact(controller)
            assert False  # Unreachable.


class TestActivities(object):
    """Unit tests for the ``activities`` command."""

    def test_list_activities_no_category(self, controller, activity, mocker, capsys):
        """Make sure command works if activities do not have a category associated."""
        activity.category = None
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        ascii_table.tabulate.tabulate = mocker.MagicMock(
            return_value='{}, {}'.format(activity.name, None),
        )
        cmds_list.activity.list_activities(controller, table_type='tabulate')
        out, err = capsys.readouterr()
        assert out.startswith(activity.name)
        assert ascii_table.tabulate.tabulate.call_args[0] == ([[activity.name, None]],)

    def test_list_activities_no_filter(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure activity name and category are displayed if present."""
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        cmds_list.activity.list_activities(controller, '')
        out, err = capsys.readouterr()
        assert activity.name in out
        assert activity.category.name in out

    def test_list_activities_using_category(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure the search term is passed on."""
        controller.categories.get_by_name = mocker.MagicMock(
            return_value=activity.category,
        )
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        cmds_list.activity.list_activities(
            controller, filter_category=activity.category.name,
        )
        out, err = capsys.readouterr()
        assert controller.activities.get_all.called
        controller.activities.get_all.assert_called_with(
            category=activity.category,
        )
        assert activity.name in out
        assert activity.category.name in out

    def test_list_activities_with_search_term(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure the search term is passed on."""
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        cmds_list.activity.list_activities(
            controller, search_term=activity.category.name,
        )
        out, err = capsys.readouterr()
        assert controller.activities.get_all.called
        controller.activities.get_all.assert_called_with(
            category=False, search_term=activity.category.name,
        )
        assert activity.name in out
        assert activity.category.name in out

    def test_list_activities_with_category_miss(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure the search term is passed on."""
        category_miss = activity.category.name + '_test'
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        with pytest.raises(KeyError):
            cmds_list.activity.list_activities(
                controller, filter_category=category_miss,
            )
            assert False  # Unreachable.
        out, err = capsys.readouterr()
        assert not controller.activities.get_all.called


class TestDetails(object):
    """Unittests for the ``details`` command."""

    def test_details_general_data_is_shown(self, controller, capsys):
        """Make sure user recieves the desired output."""
        controller.setup_tty_color(use_color=False)
        details.echo_app_details(controller)
        out, err = capsys.readouterr()
        startswiths = (
            'You are running {} version {}'.format(
                __package_name__, get_version(),
            ),
            'Configuration file at: ',
            'Plugins directory at: ',
            'Logfile stored at: ',
            'Reports exported to: ',
            'Using sqlite on database: :memory:',
        )
        for idx, line in enumerate(out.splitlines()):
            assert line.startswith(startswiths[idx])

    def test_details_sqlite(self, controller, appdirs, mocker, capsys):
        """Make sure database details for sqlite are shown properly."""
        controller._get_store = mocker.MagicMock()
        engine, path = 'sqlite', appdirs.user_data_dir
        controller.config['db.engine'] = engine
        controller.config['db.path'] = path
        details.echo_app_details(controller)
        out, err = capsys.readouterr()
        for item in (engine, path):
            assert item in out
        assert out.splitlines()[-1] == 'Using {} on database: {}'.format(engine, path)

    def test_details_non_sqlite(
        self,
        controller,
        capsys,
        db_port,
        db_host,
        db_name,
        db_user,
        db_password,
        mocker,
    ):
        """
        Make sure database details for non-sqlite are shown properly.

        We need to mock the backend Controller because it would try to setup a
        database connection right away otherwise.
        """
        controller._get_store = mocker.MagicMock()
        controller.config['db.engine'] = 'postgres'
        controller.config['db.name'] = db_name
        controller.config['db.host'] = db_host
        controller.config['db.user'] = db_user
        controller.config['db.password'] = db_password
        controller.config['db.port'] = db_port
        details.echo_app_details(controller)
        out, err = capsys.readouterr()
        for item in ('postgres', db_host, db_name, db_user):
            assert item in out
        if db_port:
            assert db_port in out
        assert db_password not in out


class TestLicense(object):
    """Unittests for ``license`` command."""

    def test_license_is_shown(self, capsys):
        """Make sure the license text is actually displayed."""
        dob._license()
        out, err = capsys.readouterr()
        assert out.startswith("GNU GENERAL PUBLIC LICENSE")
        assert "Version 3, 29 June 2007" in out


class TestGenerateTable(object):
    def test_generate_table(self, controller, fact):
        """Make sure the table contains all expected fact data."""
        table, header = cmds_list.fact.generate_facts_table(controller, [fact])
        assert table[0].start == fact.start.strftime('%Y-%m-%d %H:%M')
        assert table[0].activity == fact.activity.name

    def test_header(self, controller):
        """Make sure the tables header matches our expectation."""
        table, header = cmds_list.fact.generate_facts_table(controller, [])
        assert len(header) == 8


class TestShowGreeting(object):
    """Make shure our greeting function behaves as expected."""

    def test_shows_copyright(self, capsys):
        """Make sure we show basic copyright information."""
        dob.echo_copyright()
        out, err = capsys.readouterr()
        assert "Copyright" in out

    def test_shows_license(self, capsys):
        """Make sure we display a brief reference to the license."""
        dob.echo_license()
        out, err = capsys.readouterr()
        assert 'GNU GENERAL PUBLIC LICENSE' in out
        assert 'Version 3' in out

