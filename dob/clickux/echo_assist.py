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

import sys
from functools import update_wrapper

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
    'flush_pager',
    # PRIVATE:
    # 'fact_block_header',
)


# ***

this = sys.modules[__name__]

this.PAGER_ON = False

# (lb): This module-scope global makes me feel somewhat icky.
this.PAGER_CACHE = []


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

def click_echo(message=None, **kwargs):
    if coloring():
        kwargs['color'] = True
    if not paging():
        click.echo(message, **kwargs)
    else:
        # Collect echoes and show at end, otherwise every call
        # to echo_via_pager results in one pager session, and
        # user has to click 'q' to see each line of output!
        this.PAGER_CACHE.append(message or '')


# ***

def flush_pager(func):
    def flush_echo(*args, **kwargs):
        func(*args, **kwargs)
        if paging() and this.PAGER_CACHE:
            click.echo_via_pager(u'\n'.join(this.PAGER_CACHE))
            this.PAGER_CACHE = []

    return update_wrapper(flush_echo, func)


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


# ***

def echo_exit(ctx, message, exitcode=0):
    def _echo_exit(message):
        click_echo(message)
        _flush_pager()
        ctx.exit(exitcode)

    def _flush_pager():
        # To get at the PAGER_CACHE, gotta go through the decorator.
        # So this is quite roundabout.
        @flush_pager
        def __flush_pager():
            pass
        __flush_pager()

    _echo_exit(message)

