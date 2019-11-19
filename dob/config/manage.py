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

import os

from gettext import gettext as _

from configobj import ConfigObj, DuplicateError

from . import ConfigRoot
from .app_dirs import AppDirs
from ..helpers import dob_in_user_exit

__all__ = (
    'get_config_path',
    'load_config',
    'reset_config',
    'write_config',
    # Private:
    #  'default_config_obj',
    #  'empty_config_obj',
)


# ***

def get_config_path():
    """Show general information upon client launch."""
    config_dir = AppDirs.user_config_dir
    config_filename = 'dob.conf'
    return os.path.join(config_dir, config_filename)


# ***

def load_config():
    """"""

    def _load_config():
        try:
            config_obj = empty_config_obj()
        except DuplicateError as err:
            # (lb): The original (builtin) configparser would let you
            # choose to error or not on duplicates, but the ConfigObj
            # library (which is awesome in many ways) does not have
            # such a feature (it's got a raise_errors that does not
            # do the trick). Consequently, unless we code a way around
            # this, we gotta die on duplicates. Sorry, User! Seems
            # pretty lame. But also seems pretty unlikely.
            exit_duplicates(str(err))

        config_root = ConfigRoot.update_from_dict(config_obj)
        # What's a reasonable expectation to see if the config file
        # legitimately exists? Check that the file exists? Or parse it
        # and verify one or more settings therein? Let's do the latter,
        # seems more robust. We can check the `store` settings, seems
        # like the most obvious setting to check. In any case, we do
        # this just to tell the user if they need to create a config;
        # the app will run just fine without a config file, because
        # defaults!
        try:
            config_root.backend.store.value_from_config
            preexists = True
        except AttributeError:
            preexists = False
        return config_root, preexists

    def exit_duplicates(err):
        msg = _(
            'ERROR: Your config file at “{}” has a duplicate setting: “{}”'
        ).format(get_config_path(), str(err))
        dob_in_user_exit(msg)

    return _load_config()


# ***

def reset_config():
    config_obj = default_config_obj()

    # FIXME/2019-11-16 23:26: need to ensure path? not sure... TEST THIS
    configfile_path = os.path.dirname(config_obj.filename)
    if not os.path.lexists(configfile_path):
        os.makedirs(configfile_path)

    config_obj.write()

    # Return path to caller so that can report it to user.
    return config_obj, configfile_path


# ***

def write_config(setting):
    config_obj = empty_config_obj()
    # Fill in dict object using values previously set from config or newly set.
    config_root = setting._find_root()
    config_root.download_to_dict(config_obj, skip_unset=True)
    config_obj.write()


# ***
# ***
# ***

# ***

def empty_config_obj():
    configfile_path = get_config_path()
    config_obj = ConfigObj(
        configfile_path,
        write_empty_values=False,
        # Note that ConfigObj has a raise_errors param, but if False, it
        # just defers the error, if any; it'll still get raised, just at
        # the end. So what's the point? -(lb)
        #   raise_errors=False,
    )
    return config_obj


# ***

def default_config_obj():
    config_obj = empty_config_obj()
    # Fill in dict object using Config defaults.
    ConfigRoot.download_to_dict(config_obj, use_defaults=True)
    return config_obj

