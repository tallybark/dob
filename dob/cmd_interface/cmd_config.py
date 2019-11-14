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
import sys

from gettext import gettext as _

import click
import lazy_import
import nark
from nark.helpers.app_dirs import NarkAppDirs

from ..helpers import dob_in_user_exit, dob_in_user_warning

# Profiling: load backports: ~ 0.006 secs.
# LATER: Drop Py2 support, then switch from backports to builtin configparser.
# (lb): Py2 uses backports for Unicode support [if I understand correctly].
# (lb): This lazy-load is probably pointless, as config is always loaded.
configparser = lazy_import.lazy_module('backports.configparser')

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = (
    'furnish_config',
    'get_appdirs_subdir_file_path',
    'get_config_path',
    'replenish_config',
    # Private:
    #  'fresh_config',
    #  'get_config_instance',
    #  'get_separate_configs',
    #  'store_config',
)


# ***
# *** `dob` AppDirs.
# ***

class DobAppDirs(NarkAppDirs):
    """Custom class that ensure appdirs exist."""
    def __init__(self, *args, **kwargs):
        """Add create flag value to instance."""
        super(DobAppDirs, self).__init__(*args, **kwargs)


AppDirs = DobAppDirs('dob')


# ***
# *** Config defaults: `nark` back end.
# ***

# FIXME: (lb): DRY this. nark duplicates a lot of this.
#   See also/SYNC: nark.helpers.app_config.get_default_backend_config()
#   (We can make a single, layered config manager
#    that'll support arbitrary plugin config, too.)
class BackendDefaults(object):
    """"""
    def __init__(self):
        pass

    @property
    def store(self):
        return 'sqlalchemy'

    @property
    def db_engine(self):
        return 'sqlite'

    @property
    def db_path(self):
        return os.path.join(
            AppDirs.user_data_dir,
            # MAYBE: Rename? 'nark.sqlite'?? or 'hamster.sqlite'??
            # FIXME: Make this a package const rather than inline literal.
            #        (Maybe on Config refactor how to do so will be evident.)
            'dob.sqlite',
        )

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
    def db_user(self):
        return ''

    @property
    def db_password(self):
        return ''

    @property
    def allow_momentaneous(self):
        return False

    @property
    def day_start(self):
        # (lb): Disable this by default; I've never liked this logic!
        #   In Legacy Hamster: '00:00:00'
        return ''

    @property
    def fact_min_delta(self):
        # (lb): Disable this by default; I've never liked this logic!
        #   In Legacy Hamster: 60, i.e., facts must be 1 minute apart!
        #   In Modern Hamster (nark), you can make facts every seconds,
        #     or every millisecond, we don't care, so long as they do
        #     not overlap!
        return '0'

    @property
    def lib_log_level(self):
        return 'WARNING'

    @property
    def sql_log_level(self):
        return 'WARNING'

    @property
    def tz_aware(self):
        # FIXME/2018-06-09: (lb): Implement tzawareness!
        #   Then maybe this should be default True?
        return False

    @property
    def default_tzinfo(self):
        return ''


# ***
# *** Config defaults: `dob` front end.
# ***

class ClientDefaults(object):
    """"""
    def __init__(self):
        pass

    @property
    def carousel_centered(self):
        return False

    @property
    def carousel_lexer(self):
        return ''

    @property
    def devmode(self):
        return False

    @property
    def editor_suffix(self):
        return ''

    @property
    def export_path(self):
        return ''

    @property
    def fifo_dir(self):
        return ''

    @property
    def log_color(self):
        return False

    @property
    def log_console(self):
        return True

    @property
    def log_filename(self):
        return 'dob.log'

    @property
    def cli_log_level(self):
        return 'WARNING'

    @property
    def separators(self):
        return ''

    @property
    def styling(self):
        return ''

    @property
    def show_greeting(self):
        return False

    @property
    def term_color(self):
        return True

    @property
    def term_paging(self):
        return False


# ***
# *** Config function: log level helpers.
# ***

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


# MEH/2019-01-17: Deal with this when refactoring config:
#   If cli_log_level is wrong, app just logs a warning.
#   But for some reason, here, if sql_log_level is wrong,
#   app dies. Should probably just warning instead and
#   get on with life... print colorful stderr message,
#   but live.
#     See also: nark/nark/control.py and nark/nark/helpers/logging.py
#     have log_level functions, should probably consolidate this!
def must_verify_log_level(log_level_name):
    try:
        log_level = LOG_LEVELS[log_level_name.lower()]
    except KeyError:
        msg = _(
            "Unrecognized log level value in config: “{}”. Try one of: {}."
        ).format(log_level_name, ', '.join(LOG_LEVELS))
        dob_in_user_exit(msg)
    return log_level


# ***
# *** Config function: furnish_config.
# ***

def furnish_config(nark_preset=None, dob_preset=None):
    config, preexists = get_config_instance()
    configs = get_separate_configs(config, nark_preset, dob_preset)
    return (*configs), preexists


def replenish_config():
    new_config = fresh_config()
    file_path = get_config_path()
    store_config(new_config, file_path)
    configs = get_separate_configs(new_config)
    return (*configs), file_path


# ***
# *** Config helpers.
# ***

def from_config_or_default(config, tests_preset, cls_defaults, section, keyname):
    default_value = getattr(cls_defaults(), keyname)
    if isinstance(tests_preset, dict):
        return tests_preset.get(keyname, default_value)
    try:
        return config.get(section, keyname)
    except configparser.NoOptionError:
        return default_value


def from_config_or_default_boolean(config, tests_preset, cls_defaults, section, keyname):
    default_value = getattr(cls_defaults(), keyname)
    if isinstance(tests_preset, dict):
        return tests_preset.get(keyname, default_value)
    try:
        return config.getboolean(section, keyname)
    except configparser.NoOptionError:
        return default_value


# ***
# *** Config helper: get_separate_configs.
# ***

def get_separate_configs(config, nark_preset=None, dob_preset=None):
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
    def _get_separate_configs(config):
        return (
            get_backend_config(config, nark_preset),
            get_client_config(config, dob_preset),
        )

    def get_client_config(config, dob_preset=None):
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
            return from_config_or_default(
                config, dob_preset, ClientDefaults, 'Client', keyname,
            )

        def client_config_or_default_boolean(keyname):
            return from_config_or_default_boolean(
                config, dob_preset, ClientDefaults, 'Client', keyname,
            )

        def get_carousel_centered():
            return client_config_or_default_boolean('carousel_centered')

        def get_carousel_lexer():
            return client_config_or_default('carousel_lexer')

        def get_devmode():
            return client_config_or_default_boolean('devmode')

        def get_editor_suffix():
            return client_config_or_default('editor_suffix')

        def get_export_path():
            """
            Return path to save exports to.
            File extension will be added by export method.
            """
            return os.path.join(AppDirs.user_data_dir, 'export')

        def get_fifo_dir():
            return client_config_or_default('fifo_dir')

        def get_log_color():
            return client_config_or_default_boolean('log_color')

        def get_log_console():
            return client_config_or_default_boolean('log_console')

        def get_logfile_path():
            log_dir = AppDirs.user_log_dir
            log_filename = client_config_or_default('log_filename')
            return os.path.join(log_dir, log_filename)

        def get_cli_log_level():
            cli_log_level_name = client_config_or_default('cli_log_level')
            # MEH/2019-01-17: We should warn, not die; see: resolve_log_level.
            cli_log_level = must_verify_log_level(cli_log_level_name)
            return cli_log_level

        def get_separators():
            return client_config_or_default('separators')

        def get_styling():
            return client_config_or_default('styling')

        def get_show_greeting():
            return client_config_or_default_boolean('show_greeting')

        def get_term_color():
            return client_config_or_default_boolean('term_color')

        def get_term_paging():
            return client_config_or_default_boolean('term_paging')

        return {
            'carousel_centered': get_carousel_centered(),
            'carousel_lexer': get_carousel_lexer(),
            'devmode': get_devmode(),
            'editor_suffix': get_editor_suffix(),
            'export_path': get_export_path(),
            'fifo_dir': get_fifo_dir(),
            'log_color': get_log_color(),
            'log_console': get_log_console(),
            'logfile_path': get_logfile_path(),
            'cli_log_level': get_cli_log_level(),
            'separators': get_separators(),
            'styling': get_styling(),
            'show_greeting': get_show_greeting(),
            'term_color': get_term_color(),
            'term_paging': get_term_paging(),
        }

    def get_backend_config(config, nark_preset=None):
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
            return from_config_or_default(
                config, nark_preset, BackendDefaults, 'Backend', keyname,
            )

        def backend_config_or_default_boolean(keyname):
            return from_config_or_default_boolean(
                config, nark_preset, BackendDefaults, 'Backend', keyname,
            )

        def get_store():
            store = backend_config_or_default('store')
            if store not in nark.control.REGISTERED_BACKENDS.keys():
                raise ValueError(_("Unrecognized store option."))
            return store

        def get_db_path():
            # 2019-01-11: Not called.
            return backend_config_or_default('db_path')

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

        def get_allow_momentaneous():
            return backend_config_or_default_boolean('allow_momentaneous')

        def get_day_start():
            def _get_day_start():
                day_start = None
                day_start_text = backend_config_or_default('day_start')
                if day_start_text:
                    try:
                        day_start = datetime.datetime.strptime(
                            day_start_text, '%H:%M:%S',
                        ).time()
                    except ValueError:
                        warn_invalid(day_start_text)
                if not day_start:
                    day_start = datetime.time(0, 0, 0)
                return day_start

            def warn_invalid(day_start_text):
                msg = _(
                    'WARNING: Invalid "day_start" from config: {}'
                ).format(str(day_start_text))
                dob_in_user_warning(msg)

            return _get_day_start()

        def get_fact_min_delta():
            return backend_config_or_default('fact_min_delta')

        def get_log_level_safe(keyname):
            # FIXME/EXPLAIN/2019-01-17: What only do this for nark,
            #   and not also for cli_log_level ?
            #   TEST: Per comment, test ``dob complete`` and see if dob logs
            #     anything (and if so, apply this logic to cli_log_level).

            # (lb): A wee bit of a hack! Don't log during the dob-complete
            #   command, lest yuck!
            if (len(sys.argv) == 2) and (sys.argv[1] == 'complete'):
                # Disable for dob-complete.
                return logging.CRITICAL + 1
            sql_log_level = backend_config_or_default(keyname)
            return sql_log_level

        def get_lib_log_level():
            lib_log_level = get_log_level_safe('lib_log_level')
            return lib_log_level

        def get_sql_log_level():
            sql_log_level = get_log_level_safe('sql_log_level')
            return sql_log_level

        def get_tz_aware():
            return backend_config_or_default_boolean('tz_aware')

        def get_default_tzinfo():
            return backend_config_or_default('default_tzinfo')

        backend_config = {
            'store': get_store(),
            # db_engine, etc., will be added next.
            'allow_momentaneous': get_allow_momentaneous(),
            'day_start': get_day_start(),
            'fact_min_delta': get_fact_min_delta(),
            'lib_log_level': get_lib_log_level(),
            'sql_log_level': get_sql_log_level(),
            'tz_aware': get_tz_aware(),
            'default_tzinfo': get_default_tzinfo(),
        }
        backend_config.update(get_db_config())
        return backend_config

    return _get_separate_configs(config)


# ***
# *** Config helper: get_config_instance.
# ***

def get_config_instance():
    """
    Return a ConfigParser instance.

    If we cannot find an existing config file, create a new one.

    Returns:
        ConfigParser: Either the config loaded from an existing file, or
            default config from a new config file that this function creates.
    """
    def _get_config_instance():
        try:
            return unpack_config()
        except configparser.DuplicateOptionError as err:
            return suffer_config(err)

    def unpack_config():
        return prepare_config(duplicates_ok=False)

    def suffer_config(err):
        warn_duplicates(err)
        return prepare_config(duplicates_ok=True)

    def prepare_config(duplicates_ok):
        config = configparser.ConfigParser(strict=not duplicates_ok)
        configfile_path = get_config_path()
        if config.read(configfile_path):
            return config, True
        new_config = fresh_config()
        return new_config, False

    def warn_duplicates(err):
        msg = _(
            'BEWARE: Your config file has duplicate key-values: {}'
        ).format(str(err))
        dob_in_user_warning(msg)

    return _get_config_instance()


# ***
# *** Config function: get_config_path.
# ***

def get_config_path():
    """Show general information upon client launch."""
    config_dir = AppDirs.user_config_dir
    config_filename = 'dob.conf'
    return os.path.join(config_dir, config_filename)


# ***
# *** Config helper: fresh_config.
# ***

def fresh_config():
    """
    Create a default config. Caller is responsible for saving config file.

    Returns:
        ConfigParser: Fresh config configured with default,
            not yet written to file.
    """
    # [FIXME]
    # This may be useful to turn into a proper command, so users can restore to
    # factory settings easily.
    def _fresh_config():
        config = configparser.ConfigParser()
        set_defaults_backend(config)
        set_defaults_client(config)
        return config

    def set_defaults_backend(config):
        backend = BackendDefaults()
        config.add_section('Backend')
        config.set('Backend', 'store', backend.store)
        config.set('Backend', 'db_engine', backend.db_engine)
        config.set('Backend', 'db_path', backend.db_path)
        config.set('Backend', 'db_host', backend.db_host)
        config.set('Backend', 'db_port', backend.db_port)
        config.set('Backend', 'db_name', backend.db_name)
        config.set('Backend', 'db_user', backend.db_user)
        config.set('Backend', 'db_password', backend.db_password)
        config.set('Backend', 'allow_momentaneous', str(backend.allow_momentaneous))
        config.set('Backend', 'day_start', backend.day_start)
        config.set('Backend', 'fact_min_delta', backend.fact_min_delta)
        config.set('Backend', 'lib_log_level', backend.lib_log_level)
        config.set('Backend', 'sql_log_level', backend.sql_log_level)
        config.set('Backend', 'tz_aware', str(backend.tz_aware))
        config.set('Backend', 'default_tzinfo', backend.default_tzinfo)

    def set_defaults_client(config):
        client = ClientDefaults()
        config.add_section('Client')
        config.set('Client', 'carousel_centered', str(client.carousel_centered))
        config.set('Client', 'carousel_lexer', client.carousel_lexer)
        config.set('Client', 'devmode', str(client.devmode))
        config.set('Client', 'editor_suffix', client.editor_suffix)
        config.set('Client', 'export_path', client.export_path)
        config.set('Client', 'fifo_dir', client.fifo_dir)
        config.set('Client', 'log_color', str(client.log_color))
        config.set('Client', 'log_console', str(client.log_console))
        config.set('Client', 'log_filename', client.log_filename)
        config.set('Client', 'cli_log_level', client.cli_log_level)
        config.set('Client', 'separators', client.separators)
        config.set('Client', 'styling', client.styling)
        config.set('Client', 'show_greeting', str(client.show_greeting))
        config.set('Client', 'term_color', str(client.term_color))
        config.set('Client', 'term_paging', str(client.term_paging))

    return _fresh_config()


# ***
# *** Config function: store_config.
# ***

def store_config(config, file_path):
    configfile_path = os.path.dirname(file_path)
    if not os.path.lexists(configfile_path):
        os.makedirs(configfile_path)
    with open(file_path, 'w') as fobj:
        config.write(fobj)


# ***
# *** Shim function: get_appdirs_subdir_file_path.
# ***

DEFAULT_APPDIRS_FILE_BASENAME_FMT = '{}'


def get_appdirs_subdir_file_path(
    file_basename,
    dir_dirname,
    appdirs_dir=AppDirs.user_cache_dir,
    basename_fmt=DEFAULT_APPDIRS_FILE_BASENAME_FMT,
):
    """
    Return the path to a file stored in a subdirectory of an AppDirs directory.
    """
    subdir_path = os.path.join(appdirs_dir, dir_dirname)
    # (lb): So disrespectful! Totally accessing "hidden" method.
    AppDirs._ensure_directory_exists(subdir_path)
    full_path = os.path.join(subdir_path, basename_fmt.format(file_basename))
    if os.path.exists(full_path) and not os.path.isfile(full_path):
        msg = _(
            '{} At:\n  {}'
        ).format(
            _('UNEXPECTED: target path exists but not a file!'),
            full_path,
        )
        dob_in_user_warning(msg)
        full_path = None
    return full_path

