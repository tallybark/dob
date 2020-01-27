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

from nark.helpers.app_dirs import NarkAppDirs

from ..helpers import dob_in_user_warning

__all__ = (
    'AppDirs',
    'get_appdirs_subdir_file_path',
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

