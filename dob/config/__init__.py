# -*- coding: utf-8 -*-

# This file is part of 'nark'.
#
# 'nark' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'nark' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'nark'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import datetime
import os

from gettext import gettext as _

# FIXME: move Backend half back to nark (and fix this import path)
from nark.control import REGISTERED_BACKENDS

from ..helpers import dob_in_user_warning

from .app_dirs import AppDirs
from .inify import section
from .log_levels import get_log_level_safe, must_verify_log_level
from .subscriptable import Subscriptable

__all__ = (
    'ConfigRoot',
    # PRIVATE:
    # 'NarkConfigurable',
    # 'DobConfigurable',
)


# ***
# *** Top-level, root config object.
# ***

@section(None)
class ConfigRoot(object):
    pass


# ***
# *** Backend (nark) Config.
# ***

# FIXME: (lb): DRY: See what up in nark. Or maybe defer, could be non-ROI work,
#        especially because nark config is not tied to actual file, or cares
#        about command line overrides or environs, like dob does. So probably
#        make INERT note and forget! -2019-11-16 22:48
#        Old note says:
#           See also/SYNC:
#               nark.helpers.app_config.get_default_backend_config()
#               (We can make a single, layered config manager
#                that'll support arbitrary plugin config, too.)
# MAYBE/2019-11-16 22:49: That note about plugin config is interesting...
# - How would we support plugin configuration, eh?

@ConfigRoot.section('backend')
class NarkConfigurable(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        # Cannot super because @section decorator makes NarkConfigurable an
        # object instance of a different class type, so there is really no
        # NarkConfigurable class, it's been replaced/monkey patched into
        # an object instance of the decorator class. As such, calling super
        # super here, without the correct class, would raise.
        # DEATH: super(NarkConfigurable, self).__init__(*args, **kwargs)
        pass

    @property
    @ConfigRoot.setting(
        # Just showing off: How to deliberately specify the setting name,
        # otherwise it defaults to the function name.
        name='store',  # I.e., instead if `def store(self)`.
        choices=REGISTERED_BACKENDS,
    )
    def store_default(self):
        # HINT: The doc string here can be used in lieu of specifying in @setting.
        """ORM used by dob to interface with the DBMS. Most likely ‘sqlalchemy’."""
        # HINT: The property return value is the default for the setting.
        # HINT: The type of this value determines the setting type, too.
        return 'sqlalchemy'

    @property
    @ConfigRoot.setting(
        _("Database management system used to manage your data."
            " Most likely ‘sqlite’."),
    )
    def db_engine(self):
        return 'sqlite'

    @property
    @ConfigRoot.setting(
        _("Path to SQLite database file"
            " (for ‘sqlite’ db_engine)."),
        # The db_path only applies for 'sqlite' DBMS.
        # But we won't set ephemeral or hidden, because user should still see in
        # config, so they more easily understand how to change DBMS settings.
    )
    def db_path(self):
        # 2019-01-11: Not called.
        return os.path.join(
            AppDirs.user_data_dir,
            # MAYBE: Rename? 'nark.sqlite'?? or 'hamster.sqlite'??
            # FIXME: Make this a package const rather than inline literal.
            #        (Maybe on Config refactor how to do so will be evident.)
            'dob.sqlite',
        )

    # The 5 settings -- db_host, db_port, db_name, db_user, and db_password --
    # apply when db_engine != 'sqlite'. Otherwise, if sqlite, only db_path used.

    @property
    @ConfigRoot.setting(
        _("Host name of the database server"
            " (for non-‘sqlite’ db_engine)."),
    )
    def db_host(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("Port number on which the server is listening"
            " (for non-‘sqlite’ db_engine)."),
    )
    def db_port(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("The database name (for non-‘sqlite’ db_engine)."),
    )
    def db_name(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("The database user (for non-‘sqlite’ db_engine)."),
    )
    def db_user(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("The database password (non-‘sqlite’)."
            " WARNING: This setting is potentially unsafe!"),
    )
    def db_password(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("If True, lets you save Facts that start and end"
            " at the exact same time, i.e., zero-length Facts."),
        # FIXME/2019-11-18: (lb): Hidden for now. Still testing.
        # ! - Might be better to default True.
        hidden=True,
    )
    def allow_momentaneous(self):
        return False

    # (lb): Seems like an abuse: Not a class method (no self),
    # but not a staticmethod either, so what is?
    def validate_day_start(day_start_text):
        def _get_day_start():
            day_start = None
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

    @property
    @ConfigRoot.setting(
        # FIXME/2019-11-18: Explain this option better.
        _("The time at which the day is considered started."),
        validate=validate_day_start,
    )
    def day_start(self):
        # (lb): Disable this by default; I've never liked this logic!
        #   In Legacy Hamster: '00:00:00'
        return ''

    @property
    @ConfigRoot.setting(
        _("If nonzero, dob will not let you save a Fact"
            " with a duration less than this number of seconds."),
    )
    def fact_min_delta(self):
        # (lb): Disable this by default; I've never liked this logic!
        #   In Legacy Hamster: 60, i.e., facts must be 1 minute apart!
        #   In Modern Hamster (nark), you can make facts every seconds,
        #     or every millisecond, we don't care, so long as they do
        #     not overlap!
        return '0'

    @property
    @ConfigRoot.setting(
        _("The log level setting for backend (Hamster) squaller"
            " (using Python logging library levels)"),
        validate=get_log_level_safe,
    )
    def lib_log_level(self):
        return 'WARNING'

    @property
    @ConfigRoot.setting(
        _("The log level setting for database (SQL) squaller"
            " (using Python logging library levels)"),
        validate=get_log_level_safe,
    )
    def sql_log_level(self):
        return 'WARNING'

    @property
    @ConfigRoot.setting(
        _("If True, makes it easier to travel across timezones"
            " and daylight savings with dob!"),
    )
    def tz_aware(self):
        # FIXME/2018-06-09: (lb): Implement tzawareness!
        #   Then maybe this should be default True?
        return False

    @property
    @ConfigRoot.setting(
        _("Default TimeZone when tz_aware is in effect."),
    )
    def default_tzinfo(self):
        return ''


# ***
# *** Client (dob) Config.
# ***

@ConfigRoot.section('client')
class DobConfigurable(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        # See comment in NarkConfigurable:
        #   Cannot super because decorator shenanigans.
        # DEATH: super(DobConfigurable, self).__init__(*args, **kwargs)
        pass

    @property
    @ConfigRoot.setting(
        _("If True, center the Carousel in the terminal (on `dob edit`)"),
    )
    def carousel_centered(self):
        return False

    @property
    @ConfigRoot.setting(
        # FIXME/2019-11-18: Confirm Pygments lexer, does it work, is it wired?
        _("Fact lexer. Defaults to Pygments lexer."),
        # FIXME/2019-11-16 22:45: Confirm hidden option!
        hidden=True,
    )
    def carousel_lexer(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("If True, enables features for developing dob"
            " (e.g., print stack trace on affirm faults"),
    )
    def devmode(self):
        return False

    @property
    @ConfigRoot.setting(
        _("The filename suffix to tell EDITOR so it can determine highlighting"),
    )
    def editor_suffix(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("Path to directory where export files are created"),

        # FIXME/2019-11-17 00:56: Nothing uses export_path.
        #   So hidden for now. Delete later, or implement.
        hidden=True,
    )
    def export_path(self):
        """
        Return path to save exports to.
        File extension will be added by export method.
        """
        # FIXME: Not sure who this'll be used... maybe two separate config
        #        values, one editable and one generated, like log_filename
        #        and logfile_path. But first, we need a feature that exports!
        #        Until then... either keep this setting hidden, or delete it!
        return os.path.join(AppDirs.user_data_dir, 'export')

    @property
    @ConfigRoot.setting(
        _("FIXME: fifo_dir not implemented, and I cannot remember what it was for"),
    )
    def fifo_dir(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("If True, use color in log files (useful if tailing logs in terminal)"),
    )
    def log_color(self):
        return False

    @property
    @ConfigRoot.setting(
        _("If True, send logs to the console, not the file"),
    )
    def log_console(self):
        return True

    @property
    @ConfigRoot.setting(
        _("Filename of dob log under AppDirs.user_log_dir"),
    )
    def log_filename(self):
        return 'dob.log'

    # User should not set logfile_path in config, because it's
    # generated, but we make it a pseudo-setting so the code can
    # access just the same as other settings (and the value depends
    # on another config value, the log_filename, so it sorta is a
    # config value, just a derived one).
    @property
    @ConfigRoot.setting(
        _('Generate value.'),
        ephemeral=True,
    )
    def logfile_path(self):
        log_dir = AppDirs.user_log_dir
        # Note that self is the root ConfigDecorator, not the DobConfigurable...
        log_filename = self['log_filename']
        return os.path.join(log_dir, log_filename)

    @property
    @ConfigRoot.setting(
        _("The log level setting for frontend (dob) squaller"
            " (using Python logging library levels)"),
        # MEH/2019-01-17: We should warn, not die; see: resolve_log_level.
        validate=must_verify_log_level,
    )
    def cli_log_level(self):
        return 'WARNING'

    @property
    @ConfigRoot.setting(
        _("Separator character(s) using to indicate datetime start to end."),
    )  # noqa: E501
    def separators(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("Interface style to use."),
    )
    def styling(self):
        return ''

    @property
    @ConfigRoot.setting(
        _("If True, show copyright greeting before every command."),
    )
    def show_greeting(self):
        return False

    @property
    @ConfigRoot.setting(
        _("If True, use color and font ornamentation in output."),
    )
    def term_color(self):
        return True

    @property
    @ConfigRoot.setting(
        _("If True, send application output to terminal pager."),
    )
    def term_paging(self):
        return False

