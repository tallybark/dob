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

import sys

from gettext import gettext as _

import click
from nark.helpers.emphasis import attr, coloring, colorize, fg

from ..helpers import ascii_art

__all__ = (
    'disable_paging',
    'enable_paging',
    'paging',
    'set_paging',
    #
    'barf_and_exit',
    'click_echo',
    'echo_block_header',
    # PRIVATE:
    # 'fact_block_header',
)


# ***

this = sys.modules[__name__]

this.PAGER_ON = False


def disable_paging():
    this.PAGER_ON = False


def enable_paging():
    this.PAGER_ON = True


def paging():
    return this.PAGER_ON


def set_paging(new_paging):
    was_paging = this.PAGER_ON
    this.PAGER_ON = new_paging
    return was_paging


# ***

def click_echo(*args, **kwargs):
    if coloring():
        kwargs['color'] = True
    if not paging():
        click.echo(*args, **kwargs)
    else:
        click.echo_via_pager(*args, **kwargs)


# ***

def barf_and_exit(msg, crude=True):
    # (lb): I made two similar error-and-exit funcs. See also: dob_in_user_exit.
    if crude:
        click_echo()
        click_echo(ascii_art.lifeless().rstrip())
        click_echo(ascii_art.infection_notice().rstrip())
        # click.pause(info='')
    click_echo()
    click_echo(colorize(msg, 'red'))
    sys.exit(1)


# ***

def echo_block_header(title, **kwargs):
    click_echo()
    click_echo(fact_block_header(title, **kwargs))


def fact_block_header(title, sep='━', full_width=False):
    """"""
    def _fact_block_header():
        header = []
        append_highlighted(header, title)
        append_highlighted(header, hr_rule())
        return '\n'.join(header)

    def append_highlighted(header, text):
        highlight_col = 'red_1'
        header.append('{}{}{}'.format(
            fg(highlight_col),
            text,
            attr('reset'),
        ))

    def hr_rule():
        if not full_width:
            horiz_rule = sep * len(title)
        else:
            # NOTE: When piping (i.e., no tty), width defaults to 80.
            term_width = click.get_terminal_size()[0]
            horiz_rule = '─' * term_width
        return horiz_rule

    return _fact_block_header()

