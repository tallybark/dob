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

"""Click Group wrapper adds plugin support."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import os

import click
from click._compat import term_len

__all__ = (
    'ClickBunchyGroup',
)


class ClickBunchyGroup(click.Group):

    def __init__(self, *args, **kwargs):
        super(ClickBunchyGroup, self).__init__(*args, **kwargs)
        self.group_bunchies = { None: set(), }
        self.order_sortkeys = { None: 0, }

    def add_command(self, cmd, name=None):
        self.group_bunchies[None].add(cmd.name)
        return super(ClickBunchyGroup, self).add_command(cmd, name)

    def add_to_bunch(self, cmd, bunchy_name, sort_key=0):
        self.bunchies_regroup(cmd, bunchy_name)
        self.sortkeys_update(cmd, bunchy_name, sort_key)

    def bunchies_regroup(self, cmd, bunchy_name):
        self.group_bunchies.setdefault(bunchy_name, set())
        self.group_bunchies[bunchy_name].add(cmd.name)
        self.group_bunchies[None].remove(cmd.name)

    def sortkeys_update(self, cmd, bunchy_name, sort_key):
        self.order_sortkeys[bunchy_name] = sort_key

    # SYNC_ME: (lb): This is nasty...
    # Override Click's MultiCommand implementation.
    def format_commands(self, ctx, formatter):
        # Avoid list mutation when iterating and call list_commands now, so that
        # the plugins are sourced. (I.e., if a plugin calls add_to_bunch, it edits
        # group_bunchies, which should not (cannot) happen while under iteration.)
        _ignored = self.list_commands(ctx)

        for tup in sorted(self.order_sortkeys.items(), key=lambda tup: tup[1]):
            commands, col_max = self.format_commands_fetch(ctx, tup[0])
            section_header = callable(tup[0]) and tup[0]() or tup[0]
            self.format_commands_write(
                commands, ctx, formatter, section_header, col_min=col_max
            )

    # Override Click's MultiCommand implementation.
    def format_commands_fetch(self, ctx, bunchy_name):
        commands = []
        col_max = 0
        _commands = super(ClickBunchyGroup, self).format_commands_fetch(ctx)
        for subcommand, cmd in _commands:
            # GROUP-BUNCH: (lb): A little wonky. Seems least disruptive to code, though,
            # i.e., this is a lazy approach to solving group command bunching.
            if subcommand in self._commands:
                #aliases = ','.join(sorted(self._commands[subcommand]))
                aliases = '|'.join(sorted(self._commands[subcommand]))
                #aliases = ', '.join(sorted(self._commands[subcommand]))
                subcommand = '{0} ({1})'.format(subcommand, aliases)
                #subcommand = '{0}|{1}'.format(subcommand, aliases)
            col_max = max(col_max, term_len(subcommand))
            # Note that this width does not account for color (ANSI codes).
            if cmd.name not in self.group_bunchies[bunchy_name]:
                continue
            commands.append((subcommand, cmd))
        return commands, col_max

