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

"""Click Group wrapper tweaks usage for the ``dob add --help`` help."""

from __future__ import absolute_import, unicode_literals

from .aliasable_bunchy_plugin import ClickAliasableBunchyPluginGroup
from .bunchy_help import help_header_add_fact

__all__ = (
    'ClickAddFactHelpGroup'
)


class ClickAddFactHelpGroup(ClickAliasableBunchyPluginGroup):

    ADD_FACT_GROUP_NAME = 'add'

    ADD_FACT_GROUP_HELP = 'add --help'

    # SYNC_ME:
    #   dob.run.command(name) ↔ ClickAddFactHelpGroup.ADD_FACT_SKIP_ALIASED=[name,]
    ADD_FACT_SKIP_ALIASED = ['on', 'until', 'next']
    # Here the main names = ['now', 'to', 'after'].
    # FIXME/2019-11-21: (lb): Maybe remove these aliased Add Fact cmds?
    #                        (And be more confident about chosen names.)

    def __init__(self, *args, **kwargs):
        super(ClickAddFactHelpGroup, self).__init__(*args, **kwargs)

    def help_usage_command_path_postfix(self, ctx):
        commands = []
        bunchy_group = ctx.find_root().command.group_bunchies[help_header_add_fact]
        for cmdname in bunchy_group.keys():
            if cmdname in [
                ClickAddFactHelpGroup.ADD_FACT_GROUP_NAME,
                ClickAddFactHelpGroup.ADD_FACT_GROUP_HELP,
                *ClickAddFactHelpGroup.ADD_FACT_SKIP_ALIASED,
            ]:
                continue
            # MEH: (lb): We could weed out hidden commands, too. Seems like work.
            commands.append(cmdname)
        return '|'.join(commands)

    def format_help_text(self, ctx, formatter):
        # (lb): Achoo! Undent (-1, yo!) before click indents (back to 0, we want).
        formatter.dedent()
        super(ClickAddFactHelpGroup, self).format_help_text(ctx, formatter)
        formatter.indent()

