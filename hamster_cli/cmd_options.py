# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True


__all__ = [
    'cmd_options_search',
    'cmd_options_limit_offset',
    'cmd_options_table_bunce',
    'postprocess_options_table_bunce',
    'cmd_options_insert',
]


# ***
# *** [TIME RANGE] Options.
# ***


_cmd_options_search = [
    click.option('-s', '--start',
                 help='The start time string (e.g. "2017-01-01 00:00").'),
    click.option('-e', '--end',
                 help='The end time string (e.g. "2017-02-01 00:00").'),
]

def cmd_options_search(func):
    for option in reversed(_cmd_options_search):
        func = option(func)
    return func


# ***
# *** [LIMIT/OFFSET] Options.
# ***


_cmd_options_limit_offset = [
    click.option('-L', '--limit', default=0, show_default=False,
                 help='Limit the number of records to fetch.'),
    click.option('-O', '--offset', default=0, show_default=False,
                 help='Record offset to fetch.'),
]

def cmd_options_limit_offset(func):
    for option in reversed(_cmd_options_limit_offset):
        func = option(func)
    return func


# ***
# *** [TABLE FANCY] Options.
# ***


_cmd_options_table_bunce = [
    click.option('-t', '--truncate', is_flag=True,
                 help='Truncate long activity@category names.'),
    click.option('-T', '--table-type', default='friendly', show_default=True,
                 type=click.Choice(['tabulate', 'texttable', 'friendly']),
                 help="ASCII table formatter."),
    click.option('-A', '--asc', is_flag=True,
                 help='Sort by ascending column value.'),
    click.option('-D', '--desc', is_flag=True,
                 help='Sort by descending column value.'),
    click.option('-o', '--order', default='',
                 type=click.Choice(['', 'name', 'activity', 'category', 'tag', 'fact', 'start', 'usage']),
                 help='Order by column (may depend on query).'),
]

def cmd_options_table_bunce(func):
    for option in reversed(_cmd_options_table_bunce):
        func = option(func)
    return func


def postprocess_options_table_bunce(kwargs):
    _postprocess_options_table_bunce_order_to_sort_col(kwargs)
    _postprocess_options_table_bunce_asc_desc_to_sort_order(kwargs)


def _postprocess_options_table_bunce_order_to_sort_col(kwargs):
    kwargs['sort_col'] = kwargs['order']
    del kwargs['order']


def _postprocess_options_table_bunce_asc_desc_to_sort_order(kwargs):
    if kwargs['desc']:
        sort_order = 'desc'
    elif kwargs['asc']:
        sort_order = 'asc'
    else:
        sort_order = ''
    del kwargs['desc']
    del kwargs['asc']
    kwargs['sort_order'] = sort_order


# ***
# *** [INSERT FACT] Options.
# ***


_cmd_options_insert = [
    click.argument('factoid', nargs=-1, default=None),
    click.option('-y', '--yes', is_flag=True,
                 help=_('Save conflicts automatically, otherwise ask for confirmation')),
    click.option('-a', '--ask', is_flag=True,
                 help=_(
                     'Ask for tags, and activity@category.'
                     " Useful if tab complete doesn't help because whitespace.")),
]

def cmd_options_insert(func):
    for option in reversed(_cmd_options_insert):
        func = option(func)
    return func

