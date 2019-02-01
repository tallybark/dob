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

from gettext import gettext as _

import click
import inspect

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'cmd_options_factoid',
    'cmd_options_insert',
    'cmd_options_limit_offset',
    'cmd_options_list_activitied',
    'cmd_options_list_categoried',
    'cmd_options_list_fact',
    'cmd_options_search',
    'cmd_options_table_bunce',
    'cmd_options_usage',
    'cmd_options_edit_item',
    'postprocess_options_list_activitied',
    'postprocess_options_list_categoried',
    'postprocess_options_table_bunce',
    'OptionWithDynamicHelp',
]


# ***
# *** [TIME RANGE] Options.
# ***

_cmd_options_search = [
    click.option(
        '--since', '--after',
        help=_('Show items more recent than a specific date.'),
    ),
    click.option(
        '--until', '--before',
        help=_('Show items older than a specific date.'),
    ),
    click.option(
        '--deleted', is_flag=True, help=_('Show deleted items.'),
    ),
    click.option(
        '--hidden', is_flag=True, help=_('Show hidden items.'),
    ),
    click.option(
        '-k', '--key', help=_('The database key of the item.'),
    ),
    click.argument('search_term', nargs=-1, default=None),
]


def cmd_options_search(func):
    for option in reversed(_cmd_options_search):
        func = option(func)
    return func


# ***
# *** [LIMIT/OFFSET] Options.
# ***

_cmd_options_limit_offset = [
    click.option(
        '-L', '--limit', default=0, show_default=False,
        help=_('Limit the number of records to fetch.'),
    ),
    click.option(
        '-O', '--offset', default=0, show_default=False,
        help=_('Record offset to fetch.'),
    ),
]


def cmd_options_limit_offset(func):
    for option in reversed(_cmd_options_limit_offset):
        func = option(func)
    return func


# ***
# *** [TABLE FANCY] Options.
# ***

_cmd_options_table_bunce = [
    click.option(
        '-t', '--truncate', is_flag=True,
        help=_('Truncate long activity@category names.'),
    ),
    click.option(
        '-T', '--table-type', default='friendly', show_default=True,
        type=click.Choice(['tabulate', 'texttable', 'friendly']),
        help=_('ASCII table formatter.'),
    ),
    click.option(
        '-A', '--asc', is_flag=True, default=None,
        help=_('Sort by ascending column value.'),
    ),
    click.option(
        '-D', '--desc', is_flag=True, default=None,
        help=_('Sort by descending column value.'),
    ),
    click.option(
        '-o', '--order', '--sort', default='',
        type=click.Choice([
            '', 'name', 'activity', 'category', 'tag', 'fact', 'start', 'usage', 'time',
        ]),
        help=_('Order by column (may depend on query).'),
    ),
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
    if not kwargs['sort_col']:
        del kwargs['sort_col']


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
    if not kwargs['sort_order']:
        del kwargs['sort_order']


# ***
# *** [INSERT FACTOID] Options.
# ***

_cmd_options_factoid = [
    click.argument('factoid', nargs=-1, default=None),
]


def cmd_options_factoid(func):
    for option in reversed(_cmd_options_factoid):
        func = option(func)
    return func


# ***
# *** [ADD FACT] Options.
# ***

_cmd_options_insert = [
    click.option(
        '-a', '--ask', is_flag=True,
        help=_('Awesome Prompt for tags, and activity@category.'),
    ),
    click.option(
        '-y', '--yes', is_flag=True,
        help=_('Save conflicts automatically, otherwise ask for confirmation.'),
    ),
    click.option(
        '--dry', is_flag=True,
        help=_('Dry run: do not make changes.'),
    ),
]


def cmd_options_insert(func):
    for option in reversed(_cmd_options_insert):
        func = option(func)
    return func


# ***
# *** [LIST FACT] Options.
# ***

_cmd_options_list_fact = [
    click.option(
        '-w', '--doc', '--document', is_flag=True,
        help='Output Facts in multi-line block document format, not table.',
    ),
    click.option(
        '-r', '--rule', '--sep', nargs=1, default='',
        help=_('Separate facts with a horizontal rule'),
    ),
    click.option(
        '-S', '--span/--no-span', default=True, show_default=True,
        help=_('Show fact elapsed time'),
    ),
]


def cmd_options_list_fact(func):
    for option in reversed(_cmd_options_list_fact):
        func = option(func)
    return func


# ***
# *** [LIST ACTIVITY|LIST TAG] Options.
# ***

_cmd_options_list_categoried = [
    click.option(
        '-c', '--category',
        help=_('Restrict results by matching category name'),
    ),
]


def cmd_options_list_categoried(func):
    for option in reversed(_cmd_options_list_categoried):
        func = option(func)
    return func


def postprocess_options_list_categoried(kwargs):
    # This little dance is so category_name is never None, but '',
    # because get_all() distinguishes between category=None and =''.
    category = kwargs['category'] if kwargs['category'] else ''
    del kwargs['category']
    return category


# ***
# *** [LIST TAG] Options.
# ***

_cmd_options_list_activitied = [
    click.option(
        '-a', '--activity',
        help=_('Restrict results by matching activity name'),
    ),
]


def cmd_options_list_activitied(func):
    for option in reversed(_cmd_options_list_activitied):
        func = option(func)
    return func


def postprocess_options_list_activitied(kwargs):
    activity = kwargs['activity'] if kwargs['activity'] else ''
    del kwargs['activity']
    return activity


# ***
# *** [USAGE] Options.
# ***

_cmd_options_usage = [
    click.option(
        '-u', '--usage', is_flag=True,
        help=_('Include usage (just like usage command!)'),
    ),
]


def cmd_options_usage(func):
    for option in reversed(_cmd_options_usage):
        func = option(func)
    return func


class OptionWithDynamicHelp(click.Option):
    def __init__(self, *args, **kwargs):
        self.temporary_ctx = None
        super(OptionWithDynamicHelp, self).__init__(*args, **kwargs)

    @property
    def default(self):
        if not inspect.isfunction(self._default):
            return self._default
        controller = self.temporary_ctx.obj if self.temporary_ctx else None
        return self._default(controller)

    @default.setter
    def default(self, default):
        self._default = default

    def get_default(self, ctx):
        self.temporary_ctx = ctx
        df = super(OptionWithDynamicHelp, self).get_default(ctx)
        self.temporary_ctx = None
        return df

    def get_help_record(self, ctx):
        # (lb): <Ahhh'ack!> gesundheit
        self.temporary_ctx = ctx
        hr = super(OptionWithDynamicHelp, self).get_help_record(ctx)
        self.temporary_ctx = None
        return hr


# ***
# *** [EDIT ITEM] Options.
# ***

_cmd_options_edit_item = [
    click.argument('key', nargs=-1, type=int),
    click.option(
        '-1', 'latest_1', is_flag=True,
        help=_('Edit most recently saved item.'),
    ),
]


def cmd_options_edit_item(func):
    for option in reversed(_cmd_options_edit_item):
        func = option(func)
    return func

