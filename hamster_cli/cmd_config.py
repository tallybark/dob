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

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import appdirs
import click
import datetime
import logging
import os
import sys
# Once we drop Py2 support, we can use the builtin again, but Unicode support
# under Python 2 is practically non existing and manual encoding is not easily
# possible.
from backports.configparser import NoOptionError, SafeConfigParser

import hamster_lib
from hamster_lib.helpers.colored import colorize

from .helpers import click_echo_and_exit

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'get_config',
    'get_config_instance',
    'get_config_path',
    'write_config_file',
    'get_history_path',
]


# ***
# *** Hamster AppDirs.
# ***

class HamsterAppDirs(appdirs.AppDirs):
    """Custom class that ensure appdirs exist."""

    def __init__(self, *args, **kwargs):
        """Add create flag value to instance."""
        super(HamsterAppDirs, self).__init__(*args, **kwargs)
        self.create = True

    @property
    def user_data_dir(self):
        """Return ``user_data_dir``."""
        directory = appdirs.user_data_dir(
            self.appname,
            self.appauthor,
            version=self.version,
            roaming=self.roaming,
        )
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def site_data_dir(self):
        """Return ``site_data_dir``."""
        directory = appdirs.site_data_dir(
            self.appname,
            self.appauthor,
            version=self.version,
            multipath=self.multipath,
        )
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def user_config_dir(self):
        """Return ``user_config_dir``."""
        directory = appdirs.user_config_dir(
            self.appname,
            self.appauthor,
            version=self.version,
            roaming=self.roaming,
        )
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def site_config_dir(self):
        """Return ``site_config_dir``."""
        directory = appdirs.site_config_dir(
            self.appname,
            self.appauthor,
            version=self.version,
            multipath=self.multipath,
        )
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def user_cache_dir(self):
        """Return ``user_cache_dir``."""
        directory = appdirs.user_cache_dir(
            self.appname, self.appauthor, version=self.version,
        )
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def user_log_dir(self):
        """Return ``user_log_dir``."""
        directory = appdirs.user_log_dir(
            self.appname, self.appauthor, version=self.version,
        )
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    def _ensure_directory_exists(self, directory):
        """Ensure that the passed path exists."""
        if not os.path.lexists(directory):
            os.makedirs(directory)
        return directory


AppDirs = HamsterAppDirs('hamster_cli')


# ***
# *** Config defaults.
# ***


class BackendDefaults(object):
    """"""
    def __init__(self):
        pass

    @property
    def store(self):
        return 'sqlalchemy'

    @property
    def daystart(self):
        return '00:00:00'

    @property
    def fact_min_delta(self):
        return '60'

    @property
    def db_engine(self):
        return 'sqlite'

    @property
    def db_host(self):
        return ''

    @property
    def db_port(self):
        return ''

    @property
    def db_name(self):
        return ''

    @property
    def db_path(self):
        return os.path.join(
            str(AppDirs.user_data_dir),
            'hamster_cli.sqlite',
        )

    @property
    def db_user(self):
        return ''

    @property
    def db_password(self):
        return ''

    @property
    def sql_log_level(self):
        return 'CRITICAL'


class ClientDefaults(object):
    """"""
    def __init__(self):
        pass

    @property
    def log_level(self):
        return 'CRITICAL'

    @property
    def log_console(self):
        return False

    @property
    def log_filename(self):
        return 'hamster_cli.log'

    @property
    def export_path(self):
        return ''

    @property
    def term_color(self):
        return True

    @property
    def term_paging(self):
        return False

    @property
    def separators(self):
        return ''

    @property
    def show_greeting(self):
        return False


# ***
# *** Config function: get_config.
# ***


LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


def get_config(config_instance):
    """
    Rertrieve config dictionaries for backend and client setup.

    Raises:
        ValueError: Raised if we fail to process the user supplied config information.
            Please note that there will be no log entry as at this point, logging has not
            been set up yet.

    Returns:
        tuple: ``backend_config, client_config)`` tuple, where each element is a
            dictionary storing relevant config data.
    """
    # [TODO]
    # We propably can make better use of configparsers default config optionn,
    # but for now this will do.

    def get_client_config(config):
        """
        Read and translate config file client section into dictionary.

        Make sure config values are of proper type and provide basic
        sanity checks (e.g. make sure we got a filename if we want to log to
        file and such..).

        Not all key/values returned here need to be user configurable!

        It is worth noting that this is where we turn our user provided config
        information into the actual dictionaries to be consumed by our backend
        and client objects. A particular consequence is that the division
        of "Client/Backend" in the config file is purely cosmetic. Another
        consequence is that not all user provided config information has to be
        processed at all. We just take what we need and can safely ignore the
        rest. That way we can improve the config file layout without having to
        adjust our code all the time. It also means our main code does not have
        to deal with turning ``path`` plus ``name`` into a full location and
        such.
        """
        def client_config_or_default(keyname):
            try:
                return config.get('Client', keyname)
            except NoOptionError:
                return getattr(ClientDefaults(), keyname)

        def client_config_or_default_boolean(keyname):
            try:
                return config.getboolean('Client', keyname)
            except NoOptionError:
                return getattr(ClientDefaults(), keyname)

        def get_log_level():
            log_level_name = client_config_or_default('log_level')
            try:
                log_level = LOG_LEVELS[log_level_name.lower()]
            except KeyError:
                msg = _(
                    "Unrecognized log level value in config: “{}”. Try one of: {}."
                ).format(log_level_name, ', '.join(LOG_LEVELS))
                click_echo_and_exit(msg)
            return log_level

        def get_log_console():
            return client_config_or_default_boolean('log_console')

        def get_logfile_path():
            log_dir = AppDirs.user_log_dir
            log_filename = client_config_or_default('log_filename')
            return os.path.join(log_dir, log_filename)

        def get_export_dir():
            """
            Return path to save exports to.
            File extension will be added by export method.
            """
            return os.path.join(AppDirs.user_data_dir, 'export')

        def get_term_color():
            return client_config_or_default_boolean('term_color')

        def get_term_paging():
            return client_config_or_default_boolean('term_paging')

        def get_separators():
            return client_config_or_default('separators')

        def get_show_greeting():
            return client_config_or_default('show_greeting')

        return {
            'log_level': get_log_level(),
            'log_console': get_log_console(),
            'logfile_path': get_logfile_path(),
            'export_path': get_export_dir(),
            'term_color': get_term_color(),
            'term_paging': get_term_paging(),
            'separators': get_separators(),
            'show_greeting': get_show_greeting(),
        }

    def get_backend_config(config):
        """
        Return properly populated config dictionaries for consumption by our
        application.

        Make sure config values are of proper type and provide basic sanity
        checks (e.g. make sure we got a filename if we want to log to file and
        such..).

        Setting of config values that are not actually derived from our config
        file but by inspecting our runtime environment (e.g. path information)
        happens here as well.

        Note:
            At least the validation code/sanity checks may be relevant to other
            clients as well. So mabe this qualifies for inclusion into
            hammsterlib?
        """
        def backend_config_or_default(keyname):
            try:
                return config.get('Backend', keyname)
            except NoOptionError:
                return getattr(BackendDefaults(), keyname)

        def get_day_start():
            day_start_text = backend_config_or_default('daystart')
            if not day_start_text:
                return ''
            try:
                day_start = datetime.datetime.strptime(
                    day_start_text, '%H:%M:%S',
                ).time()
            except ValueError as err:
                raise ValueError(_(
                    'Failed to parse "day_start" from config: {}'
                ).format(day_start_text))
            return day_start

        def get_store():
            store = backend_config_or_default('store')
            if store not in hamster_lib.control.REGISTERED_BACKENDS.keys():
                raise ValueError(_("Unrecognized store option."))
            return store

        def get_db_path():
            return backend_config_or_default('db_path')

        def get_fact_min_delta():
            return backend_config_or_default('fact_min_delta')

        def get_db_config():
            """
            Provide a dict with db-specifiy key/value to be added to the backend config.
            """
            result = {
                'db_engine': backend_config_or_default('db_engine'),
            }
            if result['db_engine'] == 'sqlite':
                result.update({
                    'db_path': backend_config_or_default('db_path'),
                })
            else:
                result.update({
                    'db_host': backend_config_or_default('db_host'),
                    'db_port': backend_config_or_default('db_port'),
                    'db_name': backend_config_or_default('db_name'),
                    'db_user': backend_config_or_default('db_user'),
                    'db_password': backend_config_or_default('db_password'),
                })
            return result

        def get_sql_log_level():
            # (lb): A wee bit of a hack! Don't log during the hamster-complete
            #   command, lest yuck!
            if (len(sys.argv) == 2) and (sys.argv[1] == 'complete'):
                # Disable for hamster-complete.
                return logging.CRITICAL + 1
            sql_log_level = backend_config_or_default('sql_log_level')
            return sql_log_level

        backend_config = {
            'store': get_store(),
            'day_start': get_day_start(),
            'fact_min_delta': get_fact_min_delta(),
            'sql_log_level': get_sql_log_level(),
        }
        backend_config.update(get_db_config())
        return backend_config

    return (get_backend_config(config_instance), get_client_config(config_instance))


# ***
# *** Config function: get_config_instance.
# ***


def get_config_instance():
    """
    Return a SafeConfigParser instance.

    If we cannot find an existing config file, create a new one.

    Returns:
        SafeConfigParser: Either the config loaded from an existing file, or
            default config from a new config file that this function creates.
    """
    config = SafeConfigParser()
    configfile_path = get_config_path()
    if not config.read(configfile_path):
        click.echo('{}: {}'.format(
            _('Config file not found. Creating a new config file at'),
            configfile_path,
        ))
        config = write_config_file(configfile_path)
        click.echo(_('A new default config file was successfully created.'))
    return config


# ***
# *** Config function: get_config_path.
# ***


def get_config_path():
    """Show general information upon client launch."""
    config_dir = AppDirs.user_config_dir
    config_filename = 'hamster_cli.conf'
    return os.path.join(config_dir, config_filename)


# ***
# *** Config helper functions.
# ***


def write_config_file(file_path):
    """
    Write a default config file to the specified location.

    Returns:
        SafeConfigParser: Instace written to file.
    """
    # [FIXME]
    # This may be usefull to turn into a proper command, so users can restore to
    # factory settings easily.
    def _write_config_file():
        config = SafeConfigParser()
        set_defaults_backend(config)
        set_defaults_client(config)
        makedirs_and_write(config)
        return config

    def makedirs_and_write(config):
        configfile_path = os.path.dirname(file_path)
        if not os.path.lexists(configfile_path):
            os.makedirs(configfile_path)
        with open(file_path, 'w') as fobj:
            config.write(fobj)

    def set_defaults_backend(config):
        backend = BackendDefaults()
        config.add_section('Backend')
        config.set('Backend', 'store', backend.store)
        config.set('Backend', 'daystart', backend.daystart)
        config.set('Backend', 'fact_min_delta', backend.fact_min_delta)
        config.set('Backend', 'db_engine', backend.db_engine)
        config.set('Backend', 'db_host', backend.db_host)
        config.set('Backend', 'db_port', backend.db_port)
        config.set('Backend', 'db_name', backend.db_name)
        config.set('Backend', 'db_path', backend.db_path)
        config.set('Backend', 'db_user', backend.db_user)
        config.set('Backend', 'db_password', backend.db_password)
        config.set('Backend', 'sql_log_level', backend.sql_log_level)
        config.set('Backend', 'tz_aware', backend.tz_aware)
        config.set('Backend', 'default_tzinfo', backend.default_tzinfo)

    def set_defaults_client(config):
        client = ClientDefaults()
        config.add_section('Client')
        config.set('Client', 'log_level', client.log_level)
        config.set('Client', 'log_console', client.log_console)
        config.set('Client', 'log_filename', client.log_filename)
        config.set('Client', 'export_path', client.export_path)
        config.set('Client', 'term_color', client.term_color)
        config.set('Client', 'term_paging', client.term_paging)
        config.set('Client', 'separators', client.separators)
        config.set('Client', 'show_greeting', client.show_greeting)

    return _write_config_file()

# ***
# *** Shim function: get_history_path.
# ***


DEFAULT_HIST_PATH_DIR = 'history'

DEFAULT_HIST_NAME_FMT = '{}'


# (lb): This doesn't quite belong in this package, but we need AppDirs.
def get_history_path(
    topic,
    hist_dir=DEFAULT_HIST_PATH_DIR,
    file_fmt=DEFAULT_HIST_NAME_FMT,
):
    """
    Return the path to the history file for a specific topic.

    Args:
        topic (text_type): Topic name, to distinguish different histories.

    Returns:
        str: Fully qualified path to history file for specified topic.
    """
    hist_path = AppDirs.user_cache_dir
    if hist_dir:
        hist_path = os.path.join(hist_path, hist_dir)
    # (lb): So disrespectful! Totally accessing "hidden" method.
    AppDirs._ensure_directory_exists(hist_path)
    hist_path = os.path.join(hist_path, file_fmt.format(topic))
    if os.path.exists(hist_path) and not os.path.isfile(hist_path):
        click.echo(
            '{} At:\n  {}'.format(
                colorize(_(
                    'UNEXPECTED: history cache exists but not a file!',
                    'red_3b',
                )),
                hist_path,
            ),
            err=True,
        )
        hist_path = None
    return hist_path

