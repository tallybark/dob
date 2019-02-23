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

"""
Fixtures available to the tests/.

- In general, fixtures should return a single instance.

- If a fixture is a factory, its name should reflect that.

- A fixture that is parametrized should be suffixed with
  ``_parametrized`` to imply it has increased complexity.
"""

from __future__ import absolute_import, unicode_literals

import codecs
import datetime
import os

import dob.dob as dob
from dob.controller import Controller

import fauxfactory
import pytest
# Once we drop py2 support, we can use the builtin again but unicode support
# under python 2 is practicly non existing and manual encoding is not easily
# possible.
from backports.configparser import ConfigParser
from click.testing import CliRunner
from pytest_factoryboy import register
from six import text_type

from . import factories

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)


@pytest.fixture
def filename():
    """Provide a filename string."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def filepath(tmpdir, filename):
    """Provide a fully qualified pathame within our tmp-dir."""
    return os.path.join(tmpdir.strpath, filename)


@pytest.fixture
def appdirs(mocker, tmpdir):
    """Provide mocked version specific user dirs using a tmpdir."""
    def ensure_directory_exists(directory):
        if not os.path.lexists(directory):
            os.makedirs(directory)
        return directory

    dob.AppDirs = mocker.MagicMock()
    dob.AppDirs.user_config_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('config').strpath, 'dob/'),
    )
    dob.AppDirs.user_data_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('data').strpath, 'dob/'),
    )
    dob.AppDirs.user_cache_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('cache').strpath, 'dob/'),
    )
    dob.AppDirs.user_log_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('log').strpath, 'dob/'),
    )
    return dob.AppDirs


@pytest.fixture
def runner(appdirs, get_config_file, tmpdir):
    """Provide a convenient fixture to simulate execution of (sub-) commands."""
    def runner(args=[], keep_paths=False, **kwargs):
        # Override environments that AppDirs (thankfully) hooks. Ref:
        #   ~/.virtualenvs/dob/lib/python3.6/site-packages/appdirs.py

        # Override paths: (1) if caller running multiple command test
        # (keep_paths=True); or (2) if user wants theirs (DOB_KEEP_PATHS).
        if keep_paths or os.environ.get('DOB_KEEP_PATHS', False):
            XDG_CONFIG_HOME = os.environ['XDG_CONFIG_HOME']
            XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
        else:
            path = tmpdir.strpath
            XDG_CONFIG_HOME = '{}/.config'.format(path)
            XDG_DATA_HOME = '{}/.local/share'.format(path)
        os.environ['XDG_CONFIG_HOME'] = XDG_CONFIG_HOME
        os.environ['XDG_DATA_HOME'] = XDG_DATA_HOME

        env = {
            'XDG_CONFIG_HOME': XDG_CONFIG_HOME,
            'XDG_DATA_HOME': XDG_DATA_HOME,
            # Do not overwrite ~/.cache/dob path, where dob.log lives,
            # so DEV tail sees test output, too:
            #   'XDG_CACHE_HOME': '{}/.cache'.format(path),
            # It should not be necessary to set the state directory:
            #   'XDG_STATE_HOME': '{}/.local/state'.format(path),
            # AppDirs also checks 2 other environs, generally set
            # to system paths, and also you'll find already existing
            # for your user, probably:
            #   'XDG_DATA_DIRS': '/usr/local/share' or '/usr/share',
            #   'XDG_CONFIG_DIRS': '/etc/xdg',
        }
        return CliRunner().invoke(dob.run, args, env=env, **kwargs)
    return runner


@pytest.fixture
def base_config():
    """Provide a generic baseline configuration."""
    return lib_config, client_config


@pytest.fixture
def lib_config(tmpdir):
    """
    Provide a backend config fixture. This can be passed to a controller directly.

    That means this fixture represents the the result of all typechecks and
    type conversions.
    """
    return {
        # FIXME/2019-02-20: (lb): Test with missing config values; I know, bugs!
        # E.g., unset store, and I think dob topples.

        'store': 'sqlalchemy',
        'db_engine': 'sqlite',
        'db_path': ':memory:',
        # MAYBE/2019-02-20: (lb): Support for other DBMS's wired, but not tested.
        #   'db_host': '',
        #   'db_port': '',
        #   'db_name': '',
        #   'db_user': '',
        #   'db_password': '',

        # 2019-02-20: (lb): Note that allow_momentaneous=False probably Bad Idea,
        #                   especially for user upgrading from legacy hamster db.
        'allow_momentaneous': True,

        # MAYBE/2019-02-20: (lb): I don't day_start, so probably broke; needs tests.
        #   'day_start': datetime.time(hour=0, minute=0, second=0).isoformat(),
        #   'day_start': datetime.time(hour=5, minute=0, second=0).isoformat(),
        'day_start': '',

        # MAYBE/2019-02-20: (lb): Perhaps test min-delta, another feature I !use!
        #   'fact_min_delta': '60',
        'fact_min_delta': '0',

        'lib_log_level': 'WARNING',
        'sql_log_level': 'WARNING',

        # FIXME/2019-02-20: (lb): Implement tzawareness/tz_aware/timezone sanity.
        'tz_aware': False,
        # FIXME/2019-02-20: (lb): Needs testing, e.g.,
        #   'default_tzinfo': 'America/Menominee',
        'default_tzinfo': '',
    }


@pytest.fixture
def client_config(tmpdir):
    """
    Provide a client config fixture. This can be passed to a controller directly.

    That means this fixture represents the the result of all typechecks and
    type conversions.
    """
    return {
        # FIXME/2019-02-20: (lb): Test with missing config values; I know, bugs!

        # FIXME/2019-02-20: (lb): Clarify: Use bool, or string? True, or 'True'?
        # 'carousel_centered': '',
        'carousel_centered': 'True',

        'carousel_lexer': '',

        # Devmode would probably be deadly under test, as it sets a trace trap.
        'devmode': False,

        'editor_suffix': '',

        # The default export path is '', i.e., local directory. Use /tmp instead.
        # 'export_path': '',  # Default.
        'export_path': os.path.join(tmpdir.mkdir('export').strpath, 'export'),

        'fifo_dir': '',

        # Disable color, otherwise tests will have to look for color codes.
        'log_color': False,

        # Don't log to console, otherwise tests have to deal with that noise.
        # 'log_console': True,  # Default.
        'log_console': False,

        # The default log filename does not need to be changed.
        # 'log_filename': 'dob.log',  # Default.
        # See also:
        #  'logfile_path': '',  # Generated value.

        # 'cli_log_level': 'WARNING',  # Default.
        # 2019-02-20 11:15: I need to see where py.test of Carousel is hanging!
        'cli_log_level': 'DEBUG',  # Default.

        'separators': '',  # [,:\n]

        'show_greeting': False,

        'styling': '',

        'term_color': False,
        'term_paging': False,
    }


@pytest.fixture
def config_instance(tmpdir, faker):
    """Provide a (dynamicly generated) ConfigParser instance."""
    def generate_config(**kwargs):
            config = ConfigParser()
            # Backend
            config.add_section('Backend')

            config.set('Backend', 'store', kwargs.get('store', 'sqlalchemy'))
            config.set('Backend', 'db_engine', kwargs.get('db_engine', 'sqlite'))
            config.set('Backend', 'db_path', kwargs.get(
                'db_path', os.path.join(tmpdir.strpath, 'hamster_db.sqlite'))
            )
            config.set('Backend', 'db_host', kwargs.get('db_host', ''))
            config.set('Backend', 'db_port', kwargs.get('db_port', ''))
            config.set('Backend', 'db_name', kwargs.get('db_name', ''))
            config.set('Backend', 'db_user', kwargs.get('db_user', '')),
            config.set('Backend', 'db_password', kwargs.get('db_password', ''))

            # (lb): Need to always support momentaneous, because legacy data bugs.
            # config.set('Backend', 'allow_momentaneous', 'False')
            config.set('Backend', 'allow_momentaneous', 'True')

            # config.set('Backend', 'day_start', kwargs.get('day_start', ''))
            config.set('Backend', 'day_start', kwargs.get('day_start', '00:00:00'))

            config.set('Backend', 'fact_min_delta', kwargs.get('fact_min_delta', '60'))
            # config.set('Backend', 'fact_min_delta', kwargs.get('fact_min_delta', '0'))

            config.set('Backend', 'lib_log_level', kwargs.get('lib_log_level', 'WARNING'))
            config.set('Backend', 'sql_log_level', kwargs.get('sql_log_level', 'WARNING'))

            config.set('Backend', 'tz_aware', 'False')
            config.set('Backend', 'default_tzinfo', '')
            # FIXME/2019-02-20: (lb): Fix timezones. And parameterize, e.g.,
            #  config.set('Backend', 'default_tzinfo', 'America/Menominee')

            # Client
            config.add_section('Client')
            # config.set('Client', 'carousel_centered', '')
            # config.set('Client', 'carousel_lexer', '')
            # config.set('Client', 'devmode', '')
            # config.set('Client', 'editor_suffix', '')
            config.set('Client', 'export_path', '')
            # config.set('Client', 'fifo_dir', '')
            # config.set('Client', 'log_color', 'False')
            config.set('Client', 'log_console', kwargs.get('log_console', '0'))
            # The log_filename is used to make logfile_path, which we don't need to set.
            config.set(
                'Client', 'log_filename', kwargs.get('log_filename', faker.file_name())
            )
            config.set('Client', 'cli_log_level', kwargs.get('cli_log_level', 'debug'))
            config.set('Client', 'separators', '')  # [,:\n]
            config.set('Client', 'show_greeting', 'False')
            # config.set('Client', 'styling', '')
            config.set('Client', 'term_color', 'True')
            config.set('Client', 'term_paging', 'False')
            return config

    return generate_config


@pytest.fixture
def config_file(config_instance, appdirs):
    """Provide a config file store under our fake config dir."""
    with codecs.open(os.path.join(appdirs.user_config_dir, 'dob.conf'),
            'w', encoding='utf-8') as fobj:
        config_instance().write(fobj)


@pytest.fixture
def get_config_file(config_instance, appdirs):
    """Provide a dynamic config file store under our fake config dir."""
    def generate(**kwargs):
        instance = config_instance(**kwargs)
        with codecs.open(os.path.join(appdirs.user_config_dir, 'dob.conf'),
                'w', encoding='utf-8') as fobj:
            instance.write(fobj)
        return instance
    return generate


# Various config settings
@pytest.fixture
def db_name(request):
    """Return a randomized database name."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def db_user(request):
    """Return a randomized database username."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def db_password(request):
    """Return a randomized database password."""
    return fauxfactory.gen_utf8()


@pytest.fixture(params=(fauxfactory.gen_latin1(), fauxfactory.gen_ipaddr()))
def db_host(request):
    """Return a randomized database username."""
    return request.param


@pytest.fixture
def db_port(request):
    """Return a randomized database port."""
    return text_type(fauxfactory.gen_integer(min_value=0, max_value=65535))


@pytest.fixture
def ongoing_fact(controller_with_logging, fact):
    """Fixture that ensures there is a ``ongoing fact`` file present at the expected place."""
    fact.end = None
    fact = controller_with_logging.facts.save(fact)
    return fact


def prepare_controller(lib_config, client_config):
    controller = Controller(lib_config, client_config)
    return controller


@pytest.yield_fixture
def controller(lib_config, client_config):
    """Provide a pseudo controller instance."""
    controller = prepare_controller(lib_config, client_config)
    controller.standup_store()
    yield controller
    controller.store.cleanup()


@pytest.yield_fixture
def controller_with_logging(lib_config, client_config):
    """Provide a pseudo controller instance with logging setup."""
    controller = prepare_controller(lib_config, client_config)
    controller.setup_logging()
    controller.standup_store()
    yield controller
    controller.store.cleanup()


@pytest.fixture(params=[
    # 2018-05-05: (lb): I'm so confused. Why is datetime.datetime returned
    # in one test, but freezegun.api.FakeDatetime returned in another?
    # And then for today's date, you use datetime.time! So strange!!
    #
    # I thought it might be because @freezegun.freeze_time only freezes
    # now(), so all other times are not mocked, but note how the frozen
    # 18:00 time, '2015-12-12 18:00', is not mocked in the first two tests,
    # but then it is in the third test!! So confused!
    (None, None, '', {
        'since': None,
        'until': None,
    }),
    ('2015-12-12 18:00', '2015-12-12 19:30', '', {
        'since': datetime.datetime(2015, 12, 12, 18, 0, 0),
        'until': datetime.datetime(2015, 12, 12, 19, 30, 0),
    }),
    ('2015-12-12 18:00', '2015-12-12 19:30', '', {
        'since': datetime.datetime(2015, 12, 12, 18, 0, 0),
        'until': datetime.datetime(2015, 12, 12, 19, 30, 0),
    }),
    ('2015-12-12 18:00', '', '', {
        # (lb): Note sure diff btw. FakeDatetime and datetime.
        # 'since': freezegun.api.FakeDatetime(2015, 12, 12, 18, 0, 0),
        'since': datetime.datetime(2015, 12, 12, 18, 0, 0),
        'until': None,  # `not until` becomes None, so '' => None.
    }),
    ('2015-12-12', '', '', {
        # 'since': freezegun.api.FakeDatetime(2015, 12, 12, 0, 0, 0),
        'since': datetime.datetime(2015, 12, 12, 0, 0, 0),
        'until': None,  # `not until` becomes None, so '' => None.
    }),
    ('13:00', '', '', {
        'since': datetime.datetime(2015, 12, 12, 13, 0, 0),
        'until': None,  # `not until` becomes None, so '' => None.
    }),
])
def search_parameter_parametrized(request):
    """Provide a parametrized set of arguments for the ``search`` command."""
    return request.param

