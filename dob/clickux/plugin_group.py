# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

"""Click Group wrapper adds plugin support."""

from functools import update_wrapper
import glob
import os

from gettext import gettext as _

import click_hotoffthehamster as click

from dob_bright.config.app_dirs import AppDirs
from dob_bright.termio import dob_in_user_warning

from ..helpers.path import compile_and_eval_source

__all__ = (
    'ensure_plugged_in',
    'ClickPluginGroup',
    'PLUGINS_DIRNAME',
)


PLUGINS_DIRNAME = 'plugins'


class ClickPluginGroup(click.Group):

    def __init__(self, *args, **kwargs):
        super(ClickPluginGroup, self).__init__(*args, **kwargs)
        self.plugins_basepath = os.path.join(
            AppDirs.user_config_dir, PLUGINS_DIRNAME,
        )
        self.has_loaded = False

    @property
    def plugin_paths(self):
        py_paths = glob.glob(os.path.join(self.plugins_basepath, '*.py'))
        return py_paths

    def list_commands(self, ctx):
        """Return list of commands."""
        set_names = set()
        for cmd in self.get_commands_from_plugins(name=None):
            set_names.add(cmd.name)
        cmd_names = super(ClickPluginGroup, self).list_commands(ctx)
        return cmd_names

    def get_command(self, ctx, name):
        # Aha!:
        #   assert ctx.command is self  # So True.
        # NOTE: get_command is called via self.resolve_command, from
        #       click.MultiCommand.invoke. Just FYI. -(lb)
        # Call the get-commands func., which really just sources the plugins, so they
        # can tie into Click; then we can just call the base class implementation.
        cmd = super(ClickPluginGroup, self).get_command(ctx, name)
        if cmd is None:
            # (lb): Profiling: Loading plugins [2018-07-15: I have 3]: 0.139 secs.
            #       So only call if necessary.
            self.get_commands_from_plugins(name)
            cmd = super(ClickPluginGroup, self).get_command(ctx, name)
        return cmd

    def ensure_plugged_in(self, controller):
        if self.has_loaded:
            return
        self.get_commands_from_plugins(name=None)
        # Redo the config now that the plugins are loaded (because when we
        # first read the config, the plugins had not added their definitions
        # yet, so any user plugin config was previously ignored).
        controller.replay_config()

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
        self.has_loaded = True
        return list(cmds)

    def open_source_eval_and_poke_around(self, py_path, name):
        # NOTE: The code that's eval()ed might append to self._aliases!
        #       (Or anything else!)
        # NOTE: This source *should* be trusted -- the user had to run
        #       `dob plugin install` to wire it. At least I think so. -lb.
        eval_globals = compile_and_eval_source(py_path)
        cmds = self.probe_source_for_commands(eval_globals, name)
        return cmds

    def probe_source_for_commands(self, eval_globals, name):
        # Check for alias now, after having sourced the plugin.
        cmd_name = None
        if name:
            cmd_name = self.resolve_alias(name)

        cmds = set()
        for lname, obj in eval_globals.items():
            if not isinstance(obj, click.Command):
                continue
            if self is obj:
                # This is the 'run' object created in the run_cli module.
                continue
            if not cmd_name or obj.name == cmd_name:
                cmds.add(obj)
        return cmds


# ***

def ensure_plugged_in(func):
    """
    """

    def wrapper(ctx, controller, *args, **kwargs):
        # Ensure plugins are loaded for Click functions decorated like:
        #   @pass_controller
        #   @click.pass_context
        #   @ensure_plugged_in
        # - ctx.parent is a click_hotoffthehamster.core.Context, and
        #   ctx.parent.command is <ClickAliasableBunchyPluginGroup run>.
        ctx.parent.command.ensure_plugged_in(controller)
        func(ctx, controller, *args, **kwargs)

    return update_wrapper(wrapper, func)

