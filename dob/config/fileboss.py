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

from configobj import ConfigObj, DuplicateError

from ..helpers import dob_in_user_exit

from .app_dirs import AppDirs

__all__ = (
    'default_config_path',
    'empty_config_obj',
    'load_config_obj',
    'write_config_obj',
)


# ***

def default_config_path():
    config_dir = AppDirs.user_config_dir
    config_filename = 'dob.conf'
    configfile_path = os.path.join(config_dir, config_filename)
    return configfile_path


# ***

def empty_config_obj(configfile_path):
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

def load_config_obj(configfile_path):
    """"""

    def _load_config_obj():
        try:
            config_obj = empty_config_obj(configfile_path)
        except DuplicateError as err:
            # (lb): The original (builtin) configparser would let you
            # choose to error or not on duplicates, but the ConfigObj
            # library (which is awesome in many ways) does not have
            # such a feature (it's got a raise_errors that does not
            # do the trick). Consequently, unless we code a way around
            # this, we gotta die on duplicates. Sorry, User! Seems
            # pretty lame. But also seems pretty unlikely.
            exit_duplicates(str(err))

        return config_obj

    def exit_duplicates(err):
        msg = _(
            'ERROR: Your config file at “{}” has a duplicate setting: “{}”'
        ).format(configfile_path, str(err))
        dob_in_user_exit(msg)

    return _load_config_obj()


# ***

def write_config_obj(config_obj):
    def _write_config_obj():
        if not config_obj.filename:
            raise AttributeError('ConfigObj missing ‘filename’')
        ensure_dirs(config_obj.filename)
        try:
            config_obj.write()
        except UnicodeEncodeError as err:
            die_write_failed(config_obj, err)

    def ensure_dirs(filename):
        # Avoid: FileNotFoundError: [Errno 2] No such file or directory: ....
        configfile_dir = os.path.dirname(filename)
        if configfile_dir and not os.path.lexists(configfile_dir):
            os.makedirs(configfile_dir)

    def die_write_failed(config_obj, err):
        # E.g.,:
        #   UnicodeEncodeError: 'ascii' codec can't encode character
        #     '\u2018' in position 1135: ordinal not in range(128)
        msg = _(
            'ERROR: Failed to write file at “{}”: “{}”\n'
            'Perhaps unknown character(s): {}'
        ).format(
            config_obj.filename,
            str(err),
            err.object[err.start:err.end],
        )
        dob_in_user_exit(msg)

    return _write_config_obj()

