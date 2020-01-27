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

from gettext import gettext as _

from ..clickux.echo_assist import click_echo
from ..helpers import dob_in_user_exit, highlight_value

from . import ConfigRoot

from .fileboss import (
    default_config_path,
    empty_config_obj,
    load_config_obj,
    write_config_obj
)

__all__ = (
    'ConfigUrable',
)


class ConfigUrable(object):
    """"""

    DOB_CONFIGFILE_ENVKEY = 'DOB_CONFIGFILE'

    def __init__(self):
        super(ConfigUrable, self).__init__()
        self.configfile_path = None
        # The ConfigRoot is a module-level Singleton. Deal.
        self.config_root = ConfigRoot

    # ***

    @property
    def config_path(self):
        return self.configfile_path

    # ***

    def find_all(self, parts):
        return self.config_root.find_all(parts)

    # ***

    def create_config(self, force):
        cfgfile_exists = os.path.exists(self.config_path)
        if cfgfile_exists and not force:
            dob_in_user_exit(_('Config file exists'))

        self.reset_config()
        click_echo(
            _('Initialized default Dob configuration at {}').format(
                highlight_value(self.config_path),
            )
        )

    # ***

    def load_config(self, configfile_path):
        def _load_config():
            self.configfile_path = _resolve_configfile_path(configfile_path)
            cfgfile_exists = os.path.exists(self.config_path)
            config_obj = load_config_obj(self.config_path)
            self.config_root.forget_config_values()
            self.config_root.update_known(config_obj)
            self.cfgfile_exists = cfgfile_exists
            self.cfgfile_sanity = not self.cfgfile_exists or _is_config_like()

        def _resolve_configfile_path(commandline_value):
            if commandline_value is not None:
                return commandline_value

            if ConfigUrable.DOB_CONFIGFILE_ENVKEY in os.environ:
                return os.environ[ConfigUrable.DOB_CONFIGFILE_ENVKEY]

            return default_config_path()

        def _is_config_like():
            # What's a reasonable expectation to see if the config file
            # legitimately exists? Check that the file exists? Or parse it
            # and verify one or more settings therein? Let's do the latter,
            # seems more robust. We can check the `store` settings, seems
            # like the most obvious setting to check. In any case, we do
            # this just to tell the user if they need to create a config;
            # the app will run just fine without a config file, because
            # defaults!
            try:
                self.config_root.asobj.db.orm.value_from_config
                return True
            except AttributeError:
                return False

        _load_config()

    def inject_from_cli(self, *keyvals):
        def _inject_cli_settings():
            for keyval in keyvals:
                process_option(keyval)

        def process_option(keyval):
            key, value = keyval.split('=', 2)
            parts = key.split('.')
            setting = self.config_root.find_setting(parts)
            if setting is None:
                dob_in_user_exit(
                    _('ERROR: Unknown config option: “{}”').format(key)
                )
            setting.value_from_cliarg = value

        return _inject_cli_settings()

    # ***

    def round_out_config(self):
        self.write_config(skip_unset=False)

    # ***

    def reset_config(self):
        config_obj = empty_config_obj(self.config_path)
        # Fill in dict object using Config defaults.
        self.config_root.forget_config_values()
        self.config_root.apply_items(config_obj, use_defaults=True)
        write_config_obj(config_obj)
        self.cfgfile_exists = True  # If anything, we just created it!
        self.cfgfile_sanity = True  # If anything, we just created it!

    # ***

    def write_config(self, skip_unset=False):
        config_obj = empty_config_obj(self.config_path)
        # Fill in dict object using values previously set from config or newly set.
        self.config_root.apply_items(config_obj, skip_unset=skip_unset)
        write_config_obj(config_obj)
        self.cfgfile_exists = True
        self.cfgfile_sanity = True

