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

