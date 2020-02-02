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

"""Plugin installer plugins call... to install themselves."""

import os
import shutil
import sys

from gettext import gettext as _

from dob_bright.config.app_dirs import AppDirs, get_appdirs_subdir_file_path

from .clickux.plugin_group import PLUGINS_DIRNAME

__all__ = (
    'install_plugin',
)


# ***
# *** Install-Plugin helper.
# ***

def install_plugin(package_module_path, package_plugin_name):
    """
    Helper function for Dob plugins to use to install themselves.

    For an example, see:

        https://github.com/hotoffthehamster/dob-plugin-example

    and search PyPI for matching "dob-plugin-\*" projects.
    """
    def _install_plugin():
        src_plugin = must_src_plugin_path()
        dst_plugin = must_dst_target_path()
        symlink_or_copy_plugin_or_die(src_plugin, dst_plugin)

    def must_src_plugin_path():
        src_plugin = os.path.join(
            os.path.dirname(package_module_path),
            '..',
            PLUGINS_DIRNAME,
            package_plugin_name,
        )
        assert os.path.exists(src_plugin)
        return src_plugin

    def must_dst_target_path():
        dst_plugin = get_appdirs_subdir_file_path(
            file_basename=package_plugin_name,
            dir_dirname=PLUGINS_DIRNAME,
            appdirs_dir=AppDirs.user_config_dir,
        )
        if os.path.exists(dst_plugin):
            print(_("The plugin is already installed!"))
            # Not really an error to already be installed,
            # so return not nonzero.
            sys.exit(0)
        return dst_plugin

    def symlink_or_copy_plugin_or_die(src_plugin, dst_plugin):
        try:
            symlink_or_copy_plugin(src_plugin, dst_plugin)
        except Exception as err:
            exit_error_unknown(err)

    def symlink_or_copy_plugin(src_plugin, dst_plugin):
        try:
            symlink_plugin(src_plugin, dst_plugin)
        except NotImplementedError:
            on_windows_copy_plugin(src_plugin, dst_plugin)

    def symlink_plugin(src_plugin, dst_plugin):
        os.symlink(src_plugin, dst_plugin, target_is_directory=False)
        print(_(
            "Successfully installed plugin (using symlink) to: {}"
        ).format(dst_plugin))

    def on_windows_copy_plugin(src_plugin, dst_plugin):
        shutil.copyfile(src_plugin, dst_plugin)
        print(_(
            "Successfully copied plugin to: {}"
        ).format(dst_plugin))
        print(_(
            "NOTE: To upgrade the plugin after upgrading the package, "
            "run this same command again."
        ))

    def exit_error_unknown(err):
        print(_(
            "OOPS! Something bad happened: {}"
        ).format(str(err)))
        print(_(
            "Please report this bug to the plugin author! Thanks!!"
            " (And for what it's worth, sorry!)"
        ))
        sys.exit(1)

    _install_plugin()

