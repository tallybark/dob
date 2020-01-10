# -*- coding: utf-8 -*-

# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import datetime
import logging
import os
from unittest import mock

from dob import (
    __package_name__,
    __resolve_vers__,
    cmds_list,
    create,
    details,
    dob,
    transcode
)
from dob.config import decorate_config, app_dirs, fileboss
from dob.config.app_dirs import DobAppDirs
from dob.config.fileboss import load_config_obj, write_config_obj
from dob.config.urable import ConfigUrable
from dob.cmds_list.fact import search_facts
from dob.helpers import ascii_table

import fauxfactory
import nark
import pytest
from click import ClickException
from freezegun import freeze_time
from nark.helpers import logging as logging_helpers

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

        create.add_fact(controller, raw_fact, time_hint=time_hint, use_carousel=False)
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


# FIXME/2020-01-09: (lb): Perhaps delete this test and related code, or repair
# or rewire it, but first go from dob.py and see what current stop command does.
class TestStop(object):
    """Unit test concerning the stop command."""

    def test_stop_existing_ongoing_fact(
        self,
        ongoing_fact,
        controller_with_logging,
        mocker,
    ):
        """Make sure stoping an ongoing fact works as intended."""
        # 2018-05-05: (lb): How long have these tests been broken?
        #
        #   I forked a zombie project! Works, Not Works!
        #
        #   In any case, there's a u''.format() in create.stop_fact
        #   that complains if you pass it MagicMock objects instead
        #   of strings. So here we mock all the methods and members
        #   that stop_fact uses. (And I'm not super familiar with
        #   py.test and mocking, so I can only hope I'm doing this
        #   correctly!)
        #
        # Here's the original code (w/ stop_current_fact renamed from stop_ongoing_fact):
        #
        #   controller_with_logging.facts.stop_current_fact = mocker.MagicMock()
        #
        # And here's what I changed to make this test succeed:
        mockfact = mocker.MagicMock()
        mockfact.activity.name = 'foo'
        mockfact.category.name = 'bar'
        mocktime = mocker.MagicMock(return_value="%Y-%m-%d %H:%M")
        mockfact.start.strftime = mocktime
        mockfact.end.strftime = mocktime
        current_fact = mocker.MagicMock(return_value=mockfact)
        controller_with_logging.facts.stop_current_fact = current_fact
        # FIXME/2019-12-06: stop_fact was deleted...
        #create.stop_fact(controller_with_logging)
        assert controller_with_logging.facts.stop_current_fact.called

    def test_stop_no_existing_ongoing_fact(self, controller_with_logging, capsys):
        """Make sure that stop without actually an ongoing fact leads to an error."""
        controller = controller_with_logging
        with pytest.raises(SystemExit):
            # FIXME/2019-12-06: stop_fact was deleted...
            #create.stop_fact(controller)
            assert False  # Unreachable.


class TestCancel(object):
    """Unit tests related to cancelation of an ongoing fact."""

    def test_cancel_existing_ongoing_fact(
        self, ongoing_fact, controller_with_logging, mocker, capsys,
    ):
        """Test cancelation in case there is an ongoing fact."""
        controller = controller_with_logging
        current_fact = mocker.MagicMock(return_value=ongoing_fact)
        controller.facts.cancel_current_fact = current_fact
        create.cancel_fact(controller)
        out, err = capsys.readouterr()
        assert controller.facts.cancel_current_fact.called
        assert out.startswith('Cancelled: ')

    def test_cancel_no_existing_ongoing_fact(self, controller_with_logging, capsys):
        """Test cancelation in case there is no actual ongoing fact."""
        with pytest.raises(ClickException):
            create.cancel_fact(controller_with_logging)
            assert False  # Unreachable.


class TestExport(object):
    """Unittests related to data export."""
    @pytest.mark.parametrize('format', ['html', fauxfactory.gen_latin1()])
    def test_invalid_format(self, controller_with_logging, format, mocker):
        """Make sure that passing an invalid format exits prematurely."""
        controller = controller_with_logging
        with pytest.raises(ClickException):
            transcode.export_facts(controller, format)

    def test_csv(self, controller, controller_with_logging, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        nark.reports.CSVWriter = mocker.MagicMock()
        transcode.export_facts(controller, 'csv')
        assert nark.reports.CSVWriter.called

    def test_tsv(self, controller, controller_with_logging, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        nark.reports.TSVWriter = mocker.MagicMock()
        transcode.export_facts(controller, 'tsv')
        assert nark.reports.TSVWriter.called

    def test_ical(self, controller, controller_with_logging, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        nark.reports.ICALWriter = mocker.MagicMock()
        transcode.export_facts(controller, 'ical')
        assert nark.reports.ICALWriter.called

    def test_xml(self, controller, controller_with_logging, mocker):
        """Ensure passing 'xml' as format returns appropriate writer class."""
        nark.reports.XMLWriter = mocker.MagicMock()
        transcode.export_facts(controller, 'xml')
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
        transcode.export_facts(controller, 'csv', since=since.strftime('%Y-%m-%d %H:%M'))
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
        transcode.export_facts(controller, 'csv', until=until.strftime('%Y-%m-%d %H:%M'))
        args, kwargs = controller.facts.get_all.call_args
        assert kwargs['until'] == until

    def test_with_filename(self, controller, controller_with_logging, tmpdir, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        path = os.path.join(tmpdir.ensure_dir('export').strpath, 'export.csv')
        nark.reports.CSVWriter = mocker.MagicMock()
        transcode.export_facts(controller, 'csv', file_out=path)
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
            cmds_list.fact.echo_ongoing_fact(controller)
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
                __package_name__, __resolve_vers__(),
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


class TestSetupLogging(object):
    """Make sure that our logging setup is executed as expected."""

    def test_setup_logging_and_log_level(self, controller):
        """
        Test that library and client logger have log level set according to config.
        """
        controller.setup_logging()
        assert controller.lib_logger.level == (
            logging_helpers.resolve_log_level(
                controller.config['dev.lib_log_level']
            )[0]
        )
        assert controller.client_logger.level == (
            logging_helpers.resolve_log_level(
                controller.config['dev.cli_log_level']
            )[0]
        )

    def test_setup_logging_log_console_true(self, controller):
        """Ensure if console logging, lib and client have streamhandlers."""
        controller.config['log.use_console'] = True
        controller.setup_logging()
        assert isinstance(
            controller.client_logger.handlers[0],
            logging.StreamHandler,
        )
        assert isinstance(
            controller.client_logger.handlers[1],
            logging.FileHandler,
        )
        assert isinstance(
            controller.lib_logger.handlers[0],
            logging.StreamHandler,
        )
        assert isinstance(
            controller.lib_logger.handlers[1],
            logging.FileHandler,
        )
        assert len(controller.client_logger.handlers) == 2
        assert len(controller.lib_logger.handlers) == 2
        assert controller.client_logger.handlers[0].formatter

    def test_setup_logging_no_logging(self, controller):
        """Make sure that if no logging enabled, our loggers don't have any handlers."""
        controller.setup_logging()
        # Default loggers are set up in ~/.cache/<app>/log/<app>.log
        assert len(controller.lib_logger.handlers) == 1
        assert len(controller.client_logger.handlers) == 1

    def test_setup_logging_log_file_true(self, controller, appdirs):
        """
        Make sure that if we enable logfile_path, both loggers receive ``FileHandler``.
        """
        controller.config['log.filepath'] = os.path.join(
            appdirs.user_log_dir, 'foobar.log',
        )
        controller.setup_logging()
        assert isinstance(
            controller.lib_logger.handlers[0],
            logging.FileHandler,
        )
        assert isinstance(
            controller.client_logger.handlers[0],
            logging.FileHandler,
        )


class TestGetConfig(object):
    """Make sure that turning a config instance into proper config dictionaries works."""

    @pytest.mark.parametrize('cli_log_level', ['debug'])
    def test_log_levels_valid(self, cli_log_level, config_instance):
        """
        Make sure *string loglevels* translates to their respective integers properly.
        """
        config_obj = config_instance(cli_log_level=cli_log_level)
        assert config_obj['dev']['cli_log_level'] == cli_log_level
        config = decorate_config(config_obj)
        assert config['dev']['cli_log_level'] == 10
        assert config['dev.cli_log_level'] == 10
        assert config.asobj.dev.cli_log_level.value == 10

    @pytest.mark.parametrize('cli_log_level', ['foobar'])
    def test_log_levels_invalid(self, cli_log_level, config_instance, capsys):
        """Test that invalid *string loglevels* raise ``ValueError``."""
        config_obj = config_instance(cli_log_level=cli_log_level)
        with pytest.raises(
            ValueError,
            match=r"^Unrecognized value for setting ‘cli_log_level’: “foobar”.*"
        ):
            config = decorate_config(config_obj)
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''

    def test_invalid_store(self, config_instance):
        """Make sure that passing an ORM other than 'sqlalchemy' raises an exception."""
        config_obj = config_instance(orm='foobar')
        with pytest.raises(
            ValueError,
            match=r"^Unrecognized value for setting ‘orm’: “foobar” \(Choose from: ‘sqlalchemy’\)$"
        ):
            config = decorate_config(config_obj)

    def test_non_sqlite(self, config_instance):
        """Make sure that passing a postgres config works.

        Albeit actual postgres connections not tested."""
        confnstnc = config_instance(engine='postgres')
        config = decorate_config(confnstnc)
        assert config['db.host'] == confnstnc['db']['host']
        assert config['db.port'] == confnstnc['db']['port']
        assert config['db.name'] == confnstnc['db']['name']
        assert config['db.user'] == confnstnc['db']['user']
        assert config['db.password'] == confnstnc['db']['password']


class TestGetConfigInstance(object):
    def test_no_file_present(self, appdirs, mocker):
        # In lieu of testing from completely vanilla account, ensure config file does
        # not exist (which probably exists for your user at ~/.config/dob/dob.conf).
        # NOTE: AppDirs is a module-scope object with immutable attributes, so we
        # need to mock the entire object (i.e., cannot just patch attribute itself).
        app_dirs_mock = mock.Mock()
        app_dirs_mock.configure_mock(user_config_dir='/XXX')
        # Mock other attributes so that we do not have to mock other fcns, e.g.,
        #   mocker.patch('dob.app_config.fresh_config')
        # i.e., go for more coverage!
        app_dirs_mock.configure_mock(user_data_dir='/XXX')
        mocker.patch.object(fileboss, 'AppDirs', app_dirs_mock)
        self.configurable = ConfigUrable()
        self.configurable.load_config(configfile_path=None)
        assert len(list(self.configurable.config_root.items())) > 0
        assert self.configurable.cfgfile_exists is False

    def test_file_present(self, config_instance):
        """Make sure we try parsing a found config file."""
        self.configurable = ConfigUrable()
        self.configurable.load_config(configfile_path=None)
        cfg_val = self.configurable.config_root['db']['orm']
        assert cfg_val == config_instance()['db']['orm']
        assert config_instance() is not self.configurable.config_root

    def test_config_path_getter(self, appdirs, mocker):
        """Make sure the config target path is constructed to our expectations."""
        mocker.patch('dob.config.fileboss.load_config_obj')
        # DRY?/2020-01-09: (lb): Perhaps move repeated ConfigUrable code to fixture.
        self.configurable = ConfigUrable()
        self.configurable.load_config(configfile_path=None)
        # 'dob.conf' defined and used in dob.config.fileboss.default_config_path.
        expectation = os.path.join(appdirs.user_config_dir, 'dob.conf')
        assert fileboss.load_config_obj.called_with(expectation)


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


# FIXME/2020-01-09: (lb): Could probably move this to dob/tests/test_config or test_fileboss.
class TestWriteConfigFile(object):
    def test_file_is_written(self, filepath, config_instance):
        """Ensure file is written. Content not checked; that's ConfigObj's job."""
        config_obj = config_instance()
        write_config_obj(config_obj)
        assert os.path.lexists(config_obj.filename)

    def test_non_existing_path(self, tmpdir, filename, config_instance):
        """Make sure that the path-parents are created if not present."""
        filepath = os.path.join(tmpdir.strpath, filename)
        assert os.path.lexists(filepath) is False
        config_obj = config_instance()
        config_obj.filename = filepath
        write_config_obj(config_obj)
        assert os.path.lexists(config_obj.filename)


class TestDobAppDirs(object):
    """AppDirs tests."""

    def _test_app_dir_returns_directoy(self, app_dirname, tmpdir, **kwargs):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        with mock.patch(
            'appdirs.{}'.format(app_dirname),
            new_callable=mock.PropertyMock,
        ) as mock_app_dir:
            mock_app_dir.return_value = path
            appdir = app_dirs.DobAppDirs('dob')
            assert getattr(appdir, app_dirname) == path
            # (lb): Guh. After py3.5 dropped, we could simplify this to:
            #   mock_app_dir.assert_called_once()
            # Until then, gotta specify args and kwargs.
            kwargs['version'] = None
            mock_app_dir.assert_called_once_with('dob', None, **kwargs)

    def _test_app_dir_creates_file(self, app_dirname, create, tmpdir, faker, **kwargs):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        # We want NarkAppDirs's call to appdirs.XXX_dir to return our /tmp path.
        # (lb): Note that mocker (from pytest-mock) merely takes care of teardown,
        #   which is also accomplished with your simply use with-mock, as follows.
        with mock.patch(
            'appdirs.{}'.format(app_dirname),
            new_callable=mock.PropertyMock,
            return_value=path,
        ) as mock_app_dir:
            appdir = app_dirs.DobAppDirs('dob')
            appdir.create = create
            # DEVS: Weird: If this assert fires and you're running `py.test --pdb`,
            # entering e.g., `appdir.user_data_dir` at the pdb prompt shows the
            # non-mocked value! But if you capture the value first and print it,
            # it's correct! So in code you'd have:
            #   show_actual = appdir.user_data_dir
            # And in pdb you'd type:
            #   (pdb) show_actual
            #   '/tmp/pytest-of-user/pytest-1142/test_user_data_dir_creates_fil0/relationship/'
            #   (pdb) appdir.user_data_dir
            #   '/home/user/.local/share/dob'
            assert os.path.exists(getattr(appdir, app_dirname)) is create
            # Were not for supporting py3.5, we could simply call:
            #   mock_app_dir.assert_called_once()
            # but have to do it the hard way.
            kwargs['version'] = None
            mock_app_dir.assert_called_once_with('dob', None, **kwargs)

    # ***

    def test_user_data_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'user_data_dir', tmpdir, roaming=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_user_data_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'user_data_dir', create, tmpdir, faker, roaming=False,
        )

    # ---

    def test_site_data_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'site_data_dir', tmpdir, multipath=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_site_data_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'site_data_dir', create, tmpdir, faker, multipath=False,
        )

    # ---

    def test_user_config_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'user_config_dir', tmpdir, roaming=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_user_config_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'user_config_dir', create, tmpdir, faker, roaming=False,
        )

    # ---

    def test_site_config_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'site_config_dir', tmpdir, multipath=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_site_config_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'site_config_dir', create, tmpdir, faker, multipath=False,
        )

    # ---

    def test_user_cache_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy('user_cache_dir', tmpdir)

    @pytest.mark.parametrize('create', [True, False])
    def test_user_cache_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file('user_cache_dir', create, tmpdir, faker)

    # ---

    def test_user_log_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy('user_log_dir', tmpdir)

    @pytest.mark.parametrize('create', [True, False])
    def test_user_log_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file('user_log_dir', create, tmpdir, faker)


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

