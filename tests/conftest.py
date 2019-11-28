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
import pytest

import fauxfactory
from click.testing import CliRunner
from configobj import ConfigObj
from pytest_factoryboy import register
from six import text_type

import dob.dob as dob
from dob.controller import Controller

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
def config_root():
    """Provide a generic baseline configuration."""
    config = lib_config.copy()
    config.update(client_config)
    return config


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

        'db.orm': 'sqlalchemy',
        'db.engine': 'sqlite',
        'db.path': ':memory:',
        # MAYBE/2019-02-20: (lb): Support for other DBMS's wired, but not tested.
        #   'db.host': '',
        #   'db.port': '',
        #   'db.name': '',
        #   'db.user': '',
        #   'db.password': '',

        # 2019-02-20: (lb): Note that allow_momentaneous=False probably Bad Idea,
        #                   especially for user upgrading from legacy hamster db.
        'time.allow_momentaneous': True,

        # MAYBE/2019-02-20: (lb): I don't day_start, so probably broke; needs tests.
        #   'day_start': datetime.time(hour=0, minute=0, second=0).isoformat(),
        #   'day_start': datetime.time(hour=5, minute=0, second=0).isoformat(),
        'time.day_start': '',

        # MAYBE/2019-02-20: (lb): Perhaps test min-delta, another feature I !use!
        #   'fact_min_delta': '60',
        'time.fact_min_delta': '0',

        'dev.lib_log_level': 'WARNING',
        'dev.sql_log_level': 'WARNING',

        # FIXME/2019-02-20: (lb): Implement tzawareness/tz_aware/timezone sanity.
        'time.tz_aware': False,
        # FIXME/2019-02-20: (lb): Needs testing, e.g.,
        #   'time.default_tzinfo': 'America/Menominee',
        'time.default_tzinfo': '',
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
        # 'editor.centered': '',
        'editor.centered': 'True',

        'editor.lexer': '',

        # Devmode catch_errors could be deadly under test, as it sets a trace trap.
        'dev.catch_errors': False,

        'term.editor_suffix': '',

        # The default export path is '', i.e., local directory. Use /tmp instead.
        # 'term.export_path': '',  # Default.
        'term.export_path': os.path.join(tmpdir.mkdir('export').strpath, 'export'),

        # Disable color, otherwise tests will have to look for color codes.
        'log.use_color': False,

        # Don't log to console, otherwise tests have to deal with that noise.
        # 'log_console': True,  # Default.
        'log.use_console': False,

        # The default log filename does not need to be changed.
        # 'log_filename': 'dob.log',  # Default.
        # See also:
        #  'logfile_path': '',  # Generated value.

        # 'dev.cli_log_level': 'WARNING',  # Default.
        # 2019-02-20 11:15: I need to see where py.test of Carousel is hanging!
        'dev.cli_log_level': 'DEBUG',

        'fact.separators': '',  # [,:\n]

        'term.show_greeting': False,

        'editor.styling': '',

        'term.use_color': False,
        'term.use_pager': False,
    }


@pytest.fixture
def config_instance(tmpdir, faker):
    """Provide a (dynamicly generated) ConfigObj instance."""

    def generate_config(**kwargs):
        cfg_dict = generate_dict(**kwargs)
        config = ConfigObj(cfg_dict)
        return config

    def generate_dict(**kwargs):
        config = {}

        # ***

        cfg_db = {}
        cfg_dict['db'] = cfg_db

        cfg_db.setdefault('orm', kwargs.get('db.orm', 'sqlalchemy'))
        cfg_db.setdefault('engine', kwargs.get('db.engine', 'sqlite'))
        cfg_db.setdefault('path', kwargs.get(
            # FIXME/2019-11-27: (lb): hamster_db?
            'db_path', os.path.join(tmpdir.strpath, 'hamster_db.sqlite'))
        )
        cfg_db.setdefault('host', kwargs.get('db.host', ''))
        cfg_db.setdefault('port', kwargs.get('db.port', ''))
        cfg_db.setdefault('name', kwargs.get('db.name', ''))
        cfg_db.setdefault('user', kwargs.get('db.user', '')),
        cfg_db.setdefault('password', kwargs.get('db.password', ''))

        # ***

        cfg_dev = {}
        cfg_dict['dev'] = cfg_dev

        cfg_dev.setdefault('lib_log_level',
                           kwargs.get('dev.lib_log_level', 'WARNING'))
        cfg_dev.setdefault('sql_log_level',
                           kwargs.get('dev.sql_log_level', 'WARNING'))

        # ***

        cfg_time = {}
        cfg_dict['time'] = cfg_time

        # (lb): Need to always support momentaneous, because legacy data bugs.
        # cfg_time.setdefault('time.allow_momentaneous', 'False')
        cfg_time.setdefault('time.allow_momentaneous', 'True')

        # cfg_time.setdefault('time.day_start', kwargs.get('time.day_start', ''))
        cfg_time.setdefault('time.day_start', kwargs.get('time.day_start', '00:00:00'))

        cfg_time.setdefault('time.fact_min_delta', kwargs.get('time.fact_min_delta', '60'))
        # cfg_time.setdefault('time.fact_min_delta', kwargs.get('time.fact_min_delta', '0'))

        cfg_time.setdefault('time.tz_aware', 'False')
        cfg_time.setdefault('time.default_tzinfo', '')
        # FIXME/2019-02-20: (lb): Fix timezones. And parameterize, e.g.,
        #  cfg_time.setdefault('time.default_tzinfo', 'America/Menominee')

        # ***

        cfg_editor = {}
        cfg_dict['editor'] = cfg_editor

        cfg_editor.setdefault('centered', False)
        cfg_editor.setdefault('lexer', '')
        cfg_editor.setdefault('styling', '')

        # ***

        cfg_fact = {}
        cfg_dict['fact'] = cfg_fact

        cfg_fact.setdefault('separators', '')  # [,:\n]

        # ***

        assert('dev' in cfg_dict)

        cfg_dev.setdefault('cli_log_level',
                           kwargs.get('dev.cli_log_level', 'warning'))
        cfg_dev.setdefault('catch_errors', 'False')

        # ***

        cfg_log = {}
        cfg_dict['log'] = cfg_log

        cfg_log.setdefault('filename',
                           kwargs.get('dev.log_filename', faker.file_name()))
        # The log_filename is used to make log.filepath, which we don't need to set.
        cfg_log.setdefault('use_color', 'False')
        cfg_log.setdefault('use_console', kwargs.get('dev.log_console', '0'))

        # ***

        cfg_term = {}
        cfg_dict['term'] = cfg_term

        cfg_term.setdefault('export_path', '')
        cfg_term.setdefault('editor_suffix', '')
        cfg_term.setdefault('show_greeting', 'False')
        cfg_term.setdefault('use_color', 'True')
        cfg_term.setdefault('use_pager', 'False')

        # ***

        return config

    return generate_config


@pytest.fixture
def config_file(config_instance, appdirs):
    """Provide a config file store under our fake config dir."""
    conf_path = os.path.join(appdirs.user_config_dir, 'dob.conf')
    with codecs.open(conf_path, 'w', encoding='utf-8') as fobj:
        config_instance().write(fobj)


@pytest.fixture
def get_config_file(config_instance, appdirs):
    """Provide a dynamic config file store under our fake config dir."""
    def generate(**kwargs):
        instance = config_instance(**kwargs)
        conf_path = os.path.join(appdirs.user_config_dir, 'dob.conf')
        with codecs.open(conf_path, 'w', encoding='utf-8') as fobj:
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
    """Fixture tests that ``ongoing fact`` can be saved to data store."""
    fact.end = None
    fact = controller_with_logging.facts.save(fact)
    return fact


def prepare_controller(config_root):
    controller = Controller()
    controller.wire_configience(config_root=config_root)
    return controller


@pytest.yield_fixture
def controller(config_root):
    """Provide a pseudo controller instance."""
    controller = prepare_controller(config_root=config_root)
    controller.standup_store()
    yield controller
    controller.store.cleanup()


@pytest.yield_fixture
def controller_with_logging(config_root):
    """Provide a pseudo controller instance with logging setup."""
    controller = prepare_controller(config_root=config_root)
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

