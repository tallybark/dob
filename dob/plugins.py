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

"""A time tracker for the command line. Utilizing the power of hamster! [nark]."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import glob
import os
import shutil
import sys

from click_alias import ClickAliasedGroup

from .cmd_config import get_appdirs_subdir_file_path, AppDirs
from .helpers import dob_in_user_exit, dob_in_user_warning

__all__ = [
    'install_plugin',
    'ClickAliasablePluginGroup',
]


class ClickAliasablePluginGroup(ClickAliasedGroup):

    def __init__(self, *args, **kwargs):
        super(ClickAliasablePluginGroup, self).__init__(*args, **kwargs)
        self.plugins_basepath = os.path.join(
            AppDirs.user_config_dir, 'plugins',
        )

    @property
    def plugin_paths(self):
        py_paths = glob.glob(os.path.join(self.plugins_basepath, '*.py'))
        return py_paths

    def list_commands(self, ctx):
        set_names = set()
        for cmd in self.get_commands_from_plugins(name=None):
            set_names.add(cmd.name)
        cmd_names = super(ClickAliasablePluginGroup, self).list_commands(ctx)
        return cmd_names

    def get_command(self, ctx, name):
        # Call the get-commands func., which really just sources the plugins, so they
        # can tie into Click; then we can just call the base class implementation.
        self.get_commands_from_plugins(name)
        cmd = super(ClickAliasablePluginGroup, self).get_command(ctx, name)
        return cmd

    def get_commands_from_plugins(self, name):
        cmds = set()
        for py_path in self.plugin_paths:
            try:
                files_cmds = self.open_source_eval_and_poke_around(py_path, name)
                # (lb): Use a set, because if different plugins all import the
                # same object, e.g., `from dob.run_cli import run`, we dont'
                # want to return multiple matches.
                cmds |= files_cmds
            except Exception as err:
                msg = _(
                    'ERROR: Could not open plugins file "{}": {}'
                ).format(py_path, str(err))
                dob_in_user_warning(msg)
        return list(cmds)

    def open_source_eval_and_poke_around(self, py_path, name):
        with open(py_path) as py_text:
            cmds = self.eval_source_and_look_for_commands(py_text, py_path, name)
        return cmds

    def eval_source_and_look_for_commands(self, py_text, py_path, name):
        code = self.source_compile(py_text, py_path)
        if code is None:
            return set()
        globcals = {}
        self.eval_source_code(code, globcals, py_path)
        cmds = self.probe_source_for_commands(globcals, name)
        return cmds

    def source_compile(self, py_text, py_path):
        try:
            code = compile(py_text.read(), py_path, 'exec')
        except Exception as err:
            code = None
            msg = _(
                'ERROR: Could not compile plugins file "{}": {}'
            ).format(py_path, str(err))
            dob_in_user_warning(msg)
        return code

    def eval_source_code(self, code, globcals, py_path):
        try:
            # NOTE: This might append to self._aliases!
            eval(code, globcals, globcals)
        except Exception as err:
            msg = _(
                'ERROR: Could not source plugins file "{}": {}'
            ).format(py_path, str(err))
            dob_in_user_warning(msg)

    def probe_source_for_commands(self, globcals, name):
        # Check for alias now, after having sourced the plugin.
        cmd_name = None
        if name:
            cmd_name = self.resolve_alias(name)

        cmds = set()
        for lname, obj in globcals.items():
            if not isinstance(obj, click.Command):
                continue
            if self is obj:
                # This is the 'run' object created in the run_cli module.
                continue
            if not cmd_name or obj.name == cmd_name:
                cmds.add(obj)
        return cmds


# ***
# *** Install-Plugin helper.
# ***

def install_plugin(package_module_path, package_plugin_name):
    """
    Helper function for Dob plugins to use to install themselves.

    For an example, see:

        https://github.com/hotoffthehamster/dob-plugin-example

    and search PyPI for matching "dob-plugin-*" projects.
    """
    def _install_plugin():
        src_plugin = must_src_plugin_path()
        dst_plugin = must_dst_target_path()
        symlink_or_copy_plugin_or_die(src_plugin, dst_plugin)

    def must_src_plugin_path():
        src_plugin = os.path.join(
            os.path.dirname(package_module_path),
            '..',
            'plugins',
            package_plugin_name,
        )
        assert os.path.exists(src_plugin)
        return src_plugin

    def must_dst_target_path():
        dst_plugin = get_appdirs_subdir_file_path(
            file_basename=package_plugin_name,
            dir_dirname='plugins',
            appdirs_dir=AppDirs.user_config_dir,
        )
        if os.path.exists(dst_plugin):
            print("The plugin is already installed!")
            sys.exit(1)
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

