# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma, © 2015-2016 Eric Goller.  All rights reserved.
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

from gettext import gettext as _

import click_hotoffthehamster as click

__all__ = (
    'cmd_options_limit_offset',
    'cmd_options_list_fact',
    'cmd_options_results_chop',
    'cmd_options_results_group_by',
    'cmd_options_results_group_activity',
    'cmd_options_results_group_category',
    'cmd_options_results_group_tagnames',
    'cmd_options_results_hide_duration',
    'cmd_options_results_show_usage',
    'cmd_options_results_sort_order',
    'cmd_options_search_basics',
    # 'cmd_options_search_deleted_hidden',
    # 'cmd_options_search_item_key',
    # 'cmd_options_search_item_name',
    # 'cmd_options_search_time_window',
    'cmd_options_search_match_activity',
    'cmd_options_search_match_category',
    'cmd_options_search_match_tagnames',
    'cmd_options_table_renderer',
    'postprocess_options_match_activity',
    'postprocess_options_match_category',
    'postprocess_options_match_tagnames',
    'postprocess_options_results_options',
    # Private:
    #   '_cmd_options_*'...,
    #   '_postprocess_options_results_options_order_to_sort_col',
    #   '_postprocess_options_results_options_asc_desc_to_sort_order',
)


# ***
# *** [SEARCH QUERY] Item ID.
# ***

_cmd_options_search_item_key = [
    click.option(
        '-k', '--key',
        metavar='ID',
        help=_('The database key of the item.'),
    ),
]


def cmd_options_search_item_key(func):
    for option in reversed(_cmd_options_search_item_key):
        func = option(func)
    return func


# ***
# *** [SEARCH QUERY] Item Name.
# ***

_cmd_options_search_item_name = [
    click.argument('search_term', nargs=-1, default=None),
]


def cmd_options_search_item_name(func):
    for option in reversed(_cmd_options_search_item_name):
        func = option(func)
    return func


# ***
# *** [SEARCH QUERY] Time Window.
# ***

_cmd_options_search_time_window = [
    click.option(
        '-s', '--since', '--after',
        metavar='TIME',
        help=_('Show items more recent than a specific date.'),
    ),
    click.option(
        '-u', '--until', '--before',
        metavar='TIME',
        help=_('Show items older than a specific date.'),
    ),
]


def cmd_options_search_time_window(func):
    for option in reversed(_cmd_options_search_time_window):
        func = option(func)
    return func


# ***
# *** [SEARCH QUERY] Item ID, Name, and Time Window.
# ***

# *** Combine recent sets of options into one convenient @decorator.

def cmd_options_search_basics(func):
    for option in reversed(
        _cmd_options_search_item_key
        + _cmd_options_search_item_name
        + _cmd_options_search_time_window
    ):
        func = option(func)
    return func


# ***
# *** [SEARCH QUERY] Deleted and Hidden.
# ***

# FIXME/2020-05-16: (lb): Cleanup these options upon broader cleanup.

_cmd_options_search_deleted_hidden = [
    click.option(
        '--deleted', is_flag=True, help=_('Show deleted items.'),
    ),
    click.option(
        '--hidden', is_flag=True, help=_('Show hidden items.'),
    ),
]


def cmd_options_search_deleted_hidden(func):
    for option in reversed(_cmd_options_search_deleted_hidden):
        func = option(func)
    return func


# ***
# *** [SEARCH MATCH] Activity.
# ***

_cmd_options_search_match_activity = [
    click.option(
        '-a', '--activity',
        help=_('Restrict results by matching activity name.'),
    ),
]


def cmd_options_search_match_activity(func):
    for option in reversed(_cmd_options_search_match_activity):
        func = option(func)
    return func


def postprocess_options_match_activity(kwargs):
    activity = kwargs['activity'] if kwargs['activity'] else ''
    del kwargs['activity']
    return activity


# ***
# *** [SEARCH MATCH] Category.
# ***

_cmd_options_search_match_category = [
    click.option(
        '-c', '--category',
        help=_('Restrict results by matching category name.'),
    ),
]


def cmd_options_search_match_category(func):
    for option in reversed(_cmd_options_search_match_category):
        func = option(func)
    return func


def postprocess_options_match_category(kwargs):
    # This little dance is so category_name is never None, but '',
    # because get_all() distinguishes between category=None and =''.
    category = kwargs['category'] if kwargs['category'] else ''
    del kwargs['category']
    return category


# ***
# *** [SEARCH MATCH] Tag names.
# ***

_cmd_options_search_match_tagnames = [
    click.option(
        '-t', '--tag', multiple=True,
        help=_('Restrict results by matching tag name(s).'),
    ),
]


def cmd_options_search_match_tagnames(func):
    for option in reversed(_cmd_options_search_match_tagnames):
        func = option(func)
    return func


def postprocess_options_match_tagnames(kwargs):
    tagnames = kwargs['tag'] if kwargs['tag'] else tuple()
    del kwargs['tag']
    return tagnames


# ***
# *** [RESULTS GROUP] Option.
# ***

_cmd_options_results_group_by = [
    click.option(
        '-g', '--group', multiple=True,
        type=click.Choice([
            'activity', 'category', 'tags',
        ]),
        help=_('Group results by specified attribute(s).'),
    ),
]


def cmd_options_results_group_by(func):
    for option in reversed(_cmd_options_results_group_by):
        func = option(func)
    return func


# ***
# *** [RESULTS GROUP] Activity.
# ***

_cmd_options_results_group_activity = [
    click.option(
        '-A', '--group-activity', is_flag=True,
        help=_('Group results by activity name.'),
    ),
]


def cmd_options_results_group_activity(func):
    for option in reversed(_cmd_options_results_group_activity):
        func = option(func)
    return func


# ***
# *** [RESULTS GROUP] Category.
# ***

_cmd_options_results_group_category = [
    # There's a global -C/--config option, but globals need to be
    # specified before the command name (just how Click works), so
    # this re-usage of the same single -C option is perfectly fine.
    click.option(
        '-C', '--group-category', is_flag=True,
        help=_('Group results by category name.'),
    ),
]


def cmd_options_results_group_category(func):
    for option in reversed(_cmd_options_results_group_category):
        func = option(func)
    return func


# ***
# *** [RESULTS GROUP] Tags.
# ***

_cmd_options_results_group_tagnames = [
    click.option(
        '-T', '--group-tags', is_flag=True,
        help=_('Group results by tag names.'),
    ),
]


def cmd_options_results_group_tagnames(func):
    for option in reversed(_cmd_options_results_group_tagnames):
        func = option(func)
    return func


# ***
# *** [SEARCH RESULTS] Order.
# ***

_cmd_options_results_sort_order = [
    click.option(
        '-o', '--order', '--sort', default='start',
        type=click.Choice([
            'name', 'activity', 'category', 'tag', 'fact', 'start', 'usage', 'time',
        ]),
        help=_('Order by column (may depend on query).'),
    ),
    click.option(
        # (lb): -a/-A are used for matching/grouping by Activity in the query,
        #      and because --asc is the default, the single-char command for
        #      this option just be the "opposite" of the counterpart option,
        #      i.e., given -d/--desc, what's the "opposite"/toggle of -d? -D.
        '-D', '--asc', is_flag=True, default=None,
        help=_('Sort by ascending column value [default].'),
    ),
    click.option(
        '-d', '--desc', is_flag=True, default=None,
        help=_('Sort by descending column value.'),
    ),
]


def cmd_options_results_sort_order(func):
    for option in reversed(_cmd_options_results_sort_order):
        func = option(func)
    return func


# ***
# *** [POST PROCESS] Sort/Order Options.
# ***

def postprocess_options_results_options(kwargs):
    _postprocess_options_results_options_order_to_sort_col(kwargs)
    _postprocess_options_results_options_asc_desc_to_sort_order(kwargs)


def _postprocess_options_results_options_order_to_sort_col(kwargs):
    kwargs['sort_col'] = kwargs['order']
    del kwargs['order']
    if not kwargs['sort_col']:
        del kwargs['sort_col']


def _postprocess_options_results_options_asc_desc_to_sort_order(kwargs):
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
# *** [SEARCH RESULTS] Limit and Offset.
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
# *** [RESULTS HIDE] Duration.
# ***

_cmd_options_results_hide_duration = [
    click.option(
        '-N', '--hide-duration', is_flag=True,
        help=_('Show Fact elapsed time.'),
    ),
]


def cmd_options_results_hide_duration(func):
    for option in reversed(_cmd_options_results_hide_duration):
        func = option(func)
    return func


# ***
# *** [RESULTS SHOW] Usage.
# ***

_cmd_options_results_show_usage = [
    click.option(
        '-U', '--show-usage', is_flag=True,
        help=_('Show usage count (like usage command).'),
    ),
]


def cmd_options_results_show_usage(func):
    for option in reversed(_cmd_options_results_show_usage):
        func = option(func)
    return func


# ***
# *** [SEARCH RESULTS] Chop/Truncate.
# ***

_cmd_options_results_chop = [
    click.option(
        '-p', '--chop', '--truncate', is_flag=True,
        help=_('Truncate long names.'),
    ),
]


def cmd_options_results_chop(func):
    for option in reversed(_cmd_options_results_chop):
        func = option(func)
    return func


# ***
# *** [RESULTS FORMAT] Table Type.
# ***

_cmd_options_table_renderer = [
    click.option(
        '-T', '--table-type', default='texttable', show_default=True,
        type=click.Choice([
            'tabulate',
            'texttable',
            'friendly',
        ]),
        help=_('ASCII table formatter.'),
    ),
]


def cmd_options_table_renderer(func):
    for option in reversed(_cmd_options_table_renderer):
        func = option(func)
    return func


# ***
# *** [RESULTS FORMAT] Factoid Format.
# ***

_cmd_options_list_fact = [
    click.option(
        '-w', '--doc', '--document', is_flag=True,
        help='Format results as importable Factoid blocks.',
    ),
    click.option(
        '-r', '--rule', '--sep', nargs=1, default='',
        help=_('Separate Factoids with a horizontal rule.'),
    ),
]


def cmd_options_list_fact(func):
    for option in reversed(_cmd_options_list_fact):
        func = option(func)
    return func

