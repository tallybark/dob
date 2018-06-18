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

import click
import sys

from nark.helpers.colored import colorize, fg, attr

__all__ = [
    'dob_in_user_exit',
    'dob_in_user_warning',
    'highlight_value',
]


def dob_in_user_exit(msg):
    # (lb): I made two similar error-and-exit funcs. See also: barf_and_exit.
    dob_in_user_warning(msg)
    sys.exit(1)


def dob_in_user_warning(msg):
    click.echo(colorize(msg, 'red_3b'), err=True)


def highlight_value(msg):
    highlight_color = 'medium_spring_green'
    return '{}{}{}'.format(fg(highlight_color), msg, attr('reset'))

