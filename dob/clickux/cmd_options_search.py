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
    # One decorator is all you need for each list and usage command.
    'cmd_options_any_search_query',
    # Some other commands share use of the ASCII output table feature.
    'cmd_options_table_renderer',
    # Argument parsing helpers, to facilitate **kwargs passing.
    'postprocess_options_normalize_search_args',
    # Private:
    #   '_cmd_options_*',  # Module variables.
    #   '_postprocess_options_match_activity',
    #   '_postprocess_options_match_category',
    #   '_postprocess_options_match_tagnames',
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


# ***
# *** [SEARCH QUERY] Item Name.
# ***

_cmd_options_search_item_name = [
    click.argument('search_term', nargs=-1, default=None),
]


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


# ***
# *** [SEARCH MATCH] Activity.
# ***

_cmd_options_search_match_activity = [
    click.option(
        '-a', '--activity',
        help=_('Restrict results by matching activity name.'),
    ),
]


def _postprocess_options_match_activity(kwargs):
    activity = kwargs['activity'] if kwargs['activity'] else ''
    del kwargs['activity']
    if activity:
        kwargs['match_activity'] = activity


# ***
# *** [SEARCH MATCH] Category.
# ***

_cmd_options_search_match_category = [
    click.option(
        '-c', '--category',
        help=_('Restrict results by matching category name.'),
    ),
]


def _postprocess_options_match_category(kwargs):
    # This little dance is so category_name is never None, but '',
    # because get_all() distinguishes between category=None and =''.
    category = kwargs['category'] if kwargs['category'] else ''
    del kwargs['category']
    if category:
        kwargs['match_category'] = category


# ***
# *** [SEARCH MATCH] Tag names.
# ***

_cmd_options_search_match_tagnames = [
    click.option(
        '-t', '--tag', multiple=True,
        help=_('Restrict results by matching tag name(s).'),
    ),
]


def _postprocess_options_match_tagnames(kwargs):
    tagnames = kwargs['tag'] if kwargs['tag'] else tuple()
    del kwargs['tag']
    if tagnames:
        kwargs['match_tagnames'] = tagnames


# ***
# *** [RESULTS GROUP] Option.
# ***

_cmd_options_results_group = [
    click.option(
        '-g', '--group', multiple=True,
        type=click.Choice([
            'activity',
            'category',
            'tags',
        ]),
        help=_('Group results by specified attribute(s).'),
    ),
]


# ***
# *** [RESULTS GROUP] Activity.
# ***

_cmd_options_results_group_activity = [
    click.option(
        '-A', '--group-activity', is_flag=True,
        help=_('Group results by activity name.'),
    ),
]


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


# ***
# *** [RESULTS GROUP] Tags.
# ***

_cmd_options_results_group_tagnames = [
    click.option(
        '-T', '--group-tags', is_flag=True,
        help=_('Group results by tag names.'),
    ),
]


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


# ***
# *** [POST PROCESS] Sort/Order Options.
# ***


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

_cmd_options_search_limit_offset = [
    click.option(
        '-L', '--limit', default=0, show_default=False,
        help=_('Limit the number of records to fetch.'),
    ),
    click.option(
        '-O', '--offset', default=0, show_default=False,
        help=_('Record offset to fetch.'),
    ),
]


# ***
# *** [RESULTS HIDE] Duration.
# ***

_cmd_options_results_hide_duration = [
    click.option(
        '-N', '--hide-duration', is_flag=True,
        help=_('Show Fact elapsed time.'),
    ),
]


# ***
# *** [RESULTS SHOW] Usage.
# ***

_cmd_options_results_show_usage = [
    click.option(
        '-U', '--show-usage', is_flag=True,
        help=_('Show usage count (like usage command).'),
    ),
]


# ***
# *** [SEARCH RESULTS] Chop/Truncate.
# ***

_cmd_options_results_chop = [
    click.option(
        '-p', '--chop', '--truncate', is_flag=True,
        help=_('Truncate long names.'),
    ),
]


# ***
# *** [RESULTS FORMAT] Factoid Format.
# ***

_cmd_options_output_factoids_hrule = [
    click.option(
        '-r', '--rule', '--sep', nargs=1, default='',
        help=_('Separate Factoids with a horizontal rule.'),
    ),
]


# ***
# *** [POST PROCESS] Adjust **kwargs.
# ***

def postprocess_options_normalize_search_args(kwargs):
    _postprocess_options_match_activity(kwargs)
    _postprocess_options_match_category(kwargs)
    _postprocess_options_match_tagnames(kwargs)
    _postprocess_options_results_options_order_to_sort_col(kwargs)
    _postprocess_options_results_options_asc_desc_to_sort_order(kwargs)


# ***
# *** [ALL TOGETHER NOW] One @decorator is all you need.
# ***

# *** One @decorator for all your search command option needs.

def cmd_options_any_search_query(match_target=None, group_target=None):
    def _cmd_options_any_search_query():
        options = []
        append_cmd_options_search_basics(options)
        append_cmd_options_match_target(options)
        append_cmd_options_group_target(options)
        append_cmd_options_results_sort_limit(options)
        if match_target != 'export':
            append_cmd_options_results_adjust_values(options)
            append_cmd_options_tablular_format(options)
            append_cmd_options_factoids_format(options)

        def _cmd_options_search_query(func):
            for option in reversed(options):
                func = option(func)
            return func

        return _cmd_options_search_query

    def append_cmd_options_search_basics(options):
        options.extend(_cmd_options_search_item_key)
        options.extend(_cmd_options_search_item_name)
        options.extend(_cmd_options_search_time_window)

    def append_cmd_options_match_target(options):
        if match_target is None:
            return

        if match_target != 'activity':
            options.extend(_cmd_options_search_match_activity)
        if match_target != 'category':
            options.extend(_cmd_options_search_match_category)
        if match_target != 'tags':
            options.extend(_cmd_options_search_match_tagnames)

    def append_cmd_options_group_target(options):
        if group_target is None:
            return

        if group_target != 'activity':
            options.extend(_cmd_options_results_group_activity)
        if group_target != 'category':
            options.extend(_cmd_options_results_group_category)
        if group_target != 'tags':
            options.extend(_cmd_options_results_group_tagnames)
        options.extend(_cmd_options_results_group)

    def append_cmd_options_results_sort_limit(options):
        options.extend(_cmd_options_results_sort_order)
        options.extend(_cmd_options_search_limit_offset)

    def append_cmd_options_results_adjust_values(options):
        options.extend(_cmd_options_results_show_usage)
    # FIXME/2020-05-16 20:44: This was not revealed for non-Fact, but seems applicable:
        options.extend(_cmd_options_results_hide_duration)
        options.extend(_cmd_options_results_chop)

    def append_cmd_options_tablular_format(options):
        options.extend(_cmd_options_table_renderer)

    def append_cmd_options_factoids_format(options):
        if match_target != 'fact':
            return

        options.extend(_cmd_options_output_factoids_hrule)

    return _cmd_options_any_search_query()

