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

"""Hamter CLI Nonbusiness Helper modules."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import sys

from nark.helpers.colored import coloring, colorize, fg, attr

__all__ = [
    'dob_in_user_exit',
    'dob_in_user_warning',
    'highlight_value',
    'prepare_log_msg',
]


def click_echo(*args, **kwargs):
    if coloring():
        kwargs['color'] = True
    click.echo(*args, **kwargs)


def dob_in_user_exit(msg):
    # (lb): I made two similar error-and-exit funcs. See also: barf_and_exit.
    dob_in_user_warning(msg)
    sys.exit(1)


def dob_in_user_warning(msg):
    click.echo(colorize(msg, 'red_3b'), err=True)


def highlight_value(msg):
    highlight_color = 'medium_spring_green'
    return '{}{}{}'.format(fg(highlight_color), msg, attr('reset'))


# ***

def prepare_log_msg(fact_or_dict, msg_content):
    try:
        line_num = fact_or_dict['line_num']
        raw_meta = fact_or_dict['raw_meta']
    except TypeError:
        try:
            line_num = fact_or_dict.ephemeral['line_num']
            raw_meta = fact_or_dict.ephemeral['raw_meta']
        except Exception:
            line_num = 0
            raw_meta = ''
    # NOTE: Using colors overrides logger's coloring, which is great!
    return _(
        '{}At line: {}{} / {}\n  {}“{}”{}\n  {}{}{}'
        .format(
            attr('bold'),
            line_num,
            attr('reset'),

            msg_content,

            fg('hot_pink_2'),
            raw_meta.strip(),
            attr('reset'),

            fg('grey_78'),
            fact_or_dict,
            attr('reset'),
        )
    )

