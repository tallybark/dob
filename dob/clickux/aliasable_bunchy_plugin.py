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

"""Click Group wrapper combines all our custom classes."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from click.core import Argument, Option
from click_alias import ClickAliasedGroup

from nark.helpers.emphasis import attr

from .bunchy_group import ClickBunchyGroup
from .help_header import help_header_format
from .plugin_group import ClickPluginGroup

__all__ = (
    'ClickAliasableBunchyPluginGroup'
)


class ClickAliasableBunchyPluginGroup(
    # ClickBunchyGroup comes first, because
    # its format_commands shadows others'.
    ClickBunchyGroup,
    ClickAliasedGroup,
    ClickPluginGroup,
):

    def __init__(self, *args, **kwargs):
        super(ClickAliasableBunchyPluginGroup, self).__init__(*args, **kwargs)

    def command(self, *args, **kwargs):
        # And awaaaaaay we hack!
        # Ensure that all subcommand classes are also this class.
        kwargs.setdefault('cls', self.__class__)
        return super(ClickAliasableBunchyPluginGroup, self).command(*args, **kwargs)

    @property
    def help_header_options(self):
        return help_header_format(_('Global Options'))

    def format_usage(self, ctx, formatter):
        """Writes the usage line into the formatter.

        This is a low-level method called by :meth:`get_usage`.

        Overriden by dob to emphasize with _underline_ and **bold**.
        """
        prog = '{bold}{prog}{reset}'.format(
            bold=attr('bold'),
            prog=ctx.command_path,
            reset=attr('reset'),
        )
        #
        pieces = self.collect_usage_pieces(ctx)
        args = '{bold}{args}{reset}'.format(
            bold=attr('bold'),
            args=' '.join(pieces),
            reset=attr('reset'),
        )
        #
        prefix = '{underlined}{usage}{reset}: '.format(
            underlined=attr('underlined'),
            usage=_('Usage'),
            reset=attr('reset'),
        )
        #
        formatter.write_usage(prog, args, prefix=prefix)

    def collect_usage_pieces(self, *args, **kwargs):
        """Show '[OPTIONS]' in usage unless command takes none."""
        # MAYBE/2019-11-15: Move this up into Click. Seems legit.
        n_args = 0
        n_opts = 0
        for param in self.params:
            if isinstance(param, Argument):
                n_args += 1
            elif isinstance(param, Option):
                n_opts += 1
        #if n_args:
        #    self.subcommand_metavar = '[ARGS]...'
        #else:
        #    self.subcommand_metavar = ''
        # (lb): I think each argument we add will add its own usage piece.
        self.subcommand_metavar = ''
        if n_opts:
            self.options_metavar = '[OPTIONS]'
        else:
            self.options_metavar = ''
        return super(
            ClickAliasableBunchyPluginGroup, self
        ).collect_usage_pieces(*args, **kwargs)

