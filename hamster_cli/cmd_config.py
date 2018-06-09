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
from backports.configparser import SafeConfigParser

import hamster_lib

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'get_config',
    'get_config_instance',
    'get_config_path',
    'write_config_file',
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
# *** Config function: get_config.
# ***


LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
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
        def get_logfile_path():
            log_dir = AppDirs.user_log_dir
            return os.path.join(log_dir, config.get('Client', 'log_filename'))

        def get_log_level():
            try:
                log_level = LOG_LEVELS[config.get('Client', 'log_level').lower()]
            except KeyError:
                raise ValueError(_("Unrecognized log level value in config"))
            return log_level

        def get_log_console():
            return config.getboolean('Client', 'log_console')

        def get_term_color():
            return config.getboolean('Client', 'term_color')

        def get_term_paging():
            return config.getboolean('Client', 'term_paging')

        def get_export_dir():
            """Return path to save exports to. Filenextension will be added by export method."""
            return os.path.join(AppDirs.user_data_dir, 'export')

        # MAYBE/2018-05-05: (lb): Make the config less strict.
        # If a config value is missing, the app crashes, e.g.,
        #
        #   backports.configparser.NoOptionError: No option 'term_color' in section: 'Client'

        return {
            'log_level': get_log_level(),
            'log_console': get_log_console(),
            'logfile_path': get_logfile_path(),
            'export_path': get_export_dir(),
            'term_color': get_term_color(),
            'term_paging': get_term_paging(),
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
        def get_day_start():
            try:
                day_start = datetime.datetime.strptime(config.get('Backend',
                    'daystart'), '%H:%M:%S').time()
            except ValueError:
                raise ValueError(_("We encountered an error when parsing configs"
                            "'day_start' value! Aborting ..."))
            return day_start

        def get_store():
            store = config.get('Backend', 'store')
            if store not in hamster_lib.control.REGISTERED_BACKENDS.keys():
                raise ValueError(_("Unrecognized store option."))
            return store

        def get_db_path():
            return config.get('Backend', 'db_path')

        def get_fact_min_delta():
            return config.get('Backend', 'fact_min_delta')

        def get_tmpfile_path():
            """Return path to file used to store *ongoing fact*."""
            # MAYBE: (lb): The /tmp files are not actually cleaned up.
            #   E.g., look under: /tmp/pytest-of-some_dir/.
            #   Should we cleanup?
            # FIXME/2018-05-06: (lb): The current, ongoing fact is stored
            #   in a temporary file until the user calls hamster-stop.
            #   1. Why is that?
            #   2. Can we fix it so hamster_briefs sees it?
            #      (My hamster tools look for the 1 ongoing fact.)
            return os.path.join(AppDirs.user_data_dir, 'hamster_cli.fact')

        def get_db_config():
            """Provide a dict with db-specifiy key/value to be added to the backend config."""
            result = {}
            engine = config.get('Backend', 'db_engine')
            result = {'db_engine': engine}
            if engine == 'sqlite':
                result.update({'db_path': config.get('Backend', 'db_path')})
            else:
                try:
                    result.update({'db_port': config.get('Backend', 'db_port')})
                except KeyError:
                    pass

                result.update({
                    'db_host': config.get('Backend', 'db_host'),
                    'db_name': config.get('Backend', 'db_name'),
                    'db_user': config.get('Backend', 'db_user'),
                    'db_password': config.get('Backend', 'db_password'),
                })
            return result

        def get_sql_log_level():
            # (lb): A wee bit of a hack! Don't log during the hamster-complete
            #   command, lest yuck!
            if (len(sys.argv) == 2) and (sys.argv[1] == 'complete'):
                # Disable for hamster-complete.
                return logging.CRITICAL + 1
            return config.get('Backend', 'sql_log_level')

        backend_config = {
            'store': get_store(),
            'day_start': get_day_start(),
            'fact_min_delta': get_fact_min_delta(),
            'tmpfile_path': get_tmpfile_path(),
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
        click.echo(_("No valid config file found. Trying to create a new default config"
                     " at: '{}'.".format(configfile_path)))
        config = write_config_file(configfile_path)
        click.echo(_("A new default config file has been successfully created."))
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

    def get_db_path():
        return os.path.join(str(AppDirs.user_data_dir), 'hamster_cli.sqlite')

    def get_tmp_file_path():
        return os.path.join(str(AppDirs.user_data_dir), 'hamster_cli.fact')

    config = SafeConfigParser()

    # Backend
    config.add_section('Backend')
    config.set('Backend', 'store', 'sqlalchemy')
    config.set('Backend', 'daystart', '00:00:00')
    config.set('Backend', 'fact_min_delta', '60')
    config.set('Backend', 'db_engine', 'sqlite')
    config.set('Backend', 'db_host', '')
    config.set('Backend', 'db_port', '')
    config.set('Backend', 'db_name', '')
    config.set('Backend', 'db_path', get_db_path())
    config.set('Backend', 'db_user', '')
    config.set('Backend', 'db_password', '')
    config.set('Backend', 'sql_log_level', 'WARNING')

    # Client
    config.add_section('Client')
    config.set('Client', 'unsorted_localized', 'Unsorted')
    config.set('Client', 'log_level', 'debug')
    config.set('Client', 'log_console', 'False')
    config.set('Client', 'log_filename', 'hamster_cli.log')
    config.set('Client', 'term_color', 'True')
    config.set('Client', 'term_paging', 'False')

    configfile_path = os.path.dirname(file_path)
    if not os.path.lexists(configfile_path):
        os.makedirs(configfile_path)
    with open(file_path, 'w') as fobj:
        config.write(fobj)

    return config

