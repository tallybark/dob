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
Fixtures available in our tests.

In general fixtures shoudl return a single instance. If a fixture is a factory its name should
reflect that. Fixtures that are parametrized should be suffixed with ``_parametrized`` to indicate
the potentially increased costs to it.
"""

from __future__ import absolute_import, unicode_literals

import codecs
import datetime
import fauxfactory
import os
import pickle as pickle
import pytest
# Once we drop py2 support, we can use the builtin again but unicode support
# under python 2 is practicly non existing and manual encoding is not easily
# possible.
from backports.configparser import SafeConfigParser
from click.testing import CliRunner
from pytest_factoryboy import register
from six import text_type
import freezegun

import nark

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
    dob.AppDirs.user_config_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('config').strpath, 'dob/'))
    dob.AppDirs.user_data_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('data').strpath, 'dob/'))
    dob.AppDirs.user_cache_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('cache').strpath, 'dob/'))
    dob.AppDirs.user_log_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('log').strpath, 'dob/'))
    return dob.AppDirs


@pytest.fixture
def runner(appdirs, get_config_file):
    """Provide a convenient fixture to simulate execution of (sub-) commands."""
    def runner(args=[], **kwargs):
        return CliRunner().invoke(dob.run, args, **kwargs)
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
        'store': 'sqlalchemy',
        'db_engine': 'sqlite',
        'db_path': ':memory:',
        'sql_log_level': 'WARNING',
        'day_start': datetime.time(hour=5, minute=0, second=0),
        #'fact_min_delta': 0,
        'fact_min_delta': 60,
        'tz_aware': False,
        'default_tzinfo': '',  # 'America/Menominee'
    }


@pytest.fixture
def client_config(tmpdir):
    """
    Provide a client config fixture. This can be passed to a controller directly.

    That means this fixture represents the the result of all typechecks and
    type conversions.
    """
    return {
        'log_level': 10,
        'log_console': False,
        # Note that 'log_filename' is what's in the config; logfile_path is made.
        'logfile_path': False,
        #'logfile_path': os.path.join(tmpdir.mkdir('log2').strpath, 'dob.log'),
        'export_path': os.path.join(tmpdir.mkdir('export').strpath, 'export'),
        'term_color': False,
        'term_paging': False,
        'separators': '',  # [,:\n]
        'show_greeting': False,
    }


@pytest.fixture
def config_instance(tmpdir, faker):
    """Provide a (dynamicly generated) SafeConfigParser instance."""
    def generate_config(**kwargs):
            config = SafeConfigParser()
            # Backend
            config.add_section('Backend')
            config.set('Backend', 'store', kwargs.get('store', 'sqlalchemy'))
            config.set('Backend', 'fact_min_delta', kwargs.get('fact_min_delta', '60'))
            #config.set('Backend', 'fact_min_delta', kwargs.get('fact_min_delta', '0'))
            config.set('Backend', 'db_engine', kwargs.get('db_engine', 'sqlite'))
            config.set('Backend', 'db_path', kwargs.get(
                'db_path', os.path.join(tmpdir.strpath, 'hamster_db.sqlite'))
            )
            config.set('Backend', 'db_host', kwargs.get('db_host', ''))
            config.set('Backend', 'db_name', kwargs.get('db_name', ''))
            config.set('Backend', 'db_port', kwargs.get('db_port', ''))
            config.set('Backend', 'db_user', kwargs.get('db_user', '')),
            config.set('Backend', 'db_password', kwargs.get('db_password', ''))
            config.set('Backend', 'day_start', kwargs.get('day_start', '00:00:00'))
            config.set('Backend', 'sql_log_level', kwargs.get('sql_log_level', 'WARNING'))
            config.set('Backend', 'tz_aware', 'False')
            config.set('Backend', 'default_tzinfo', '')  # America/Menominee

            # Client
            config.add_section('Client')
            config.set('Client', 'log_level', kwargs.get('log_level', 'debug'))
            config.set('Client', 'log_console', kwargs.get('log_console', '0'))
            # The log_filename is used to make logfile_path.
            config.set(
                'Client', 'log_filename', kwargs.get('log_filename', faker.file_name())
            )
            config.set('Client', 'export_path', '')
            config.set('Client', 'term_color', 'True')
            config.set('Client', 'term_paging', 'False')
            config.set('Client', 'separators', '')  # [,:\n]
            config.set('Client', 'show_greeting', 'False')
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
def tmp_fact(controller_with_logging, fact):
    """Fixture that ensures there is a ``ongoing fact`` file present at the expected place."""
    fact.end = None
    fact = controller_with_logging.facts.save(fact)
    return fact


@pytest.fixture
def invalid_tmp_fact(tmpdir, client_config):
    """Fixture to provide a *ongoing fact* file that contains an invalid object instance."""
    with open(client_config['tmp_filename'], 'wb') as fobj:
        pickle.dump(None, fobj)


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
        'start': None,
        'end': None,
# NEED?
        'limit': '',
        'offset': '',
        'sort_order': 'desc',
    }),
    ('2015-12-12 18:00', '2015-12-12 19:30', '', {
        'start': datetime.datetime(2015, 12, 12, 18, 0, 0),
        'end': datetime.datetime(2015, 12, 12, 19, 30, 0),
# NEED?
        'limit': '',
        'offset': '',
        'sort_order': 'desc',
    }),
    ('2015-12-12 18:00', '2015-12-12 19:30', '', {
        'start': datetime.datetime(2015, 12, 12, 18, 0, 0),
        'end': datetime.datetime(2015, 12, 12, 19, 30, 0),
# NEED?
        'limit': '',
        'offset': '',
        'sort_order': 'desc',
    }),
    ('2015-12-12 18:00', '', '', {
        'start': freezegun.api.FakeDatetime(2015, 12, 12, 18, 0, 0),
        'end': '',
# NEED?
        'limit': '',
        'offset': '',
        'sort_order': 'desc',
    }),
    ('2015-12-12', '', '', {
        'start': freezegun.api.FakeDate(2015, 12, 12),
        'end': '',
# NEED?
        'limit': '',
        'offset': '',
        'sort_order': 'desc',
    }),
    ('13:00', '', '', {
        'start': datetime.time(13, 0),
        'end': '',
# NEED?
        'limit': '',
        'offset': '',
        'sort_order': 'desc',
    }),
])
def search_parameter_parametrized(request):
    """Provide a parametrized set of arguments for the ``search`` command."""
    return request.param
