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

from dob_bright.termio import dob_in_user_exit

from ..facts_format.tabular import report_table_columns

__all__ = (
    # One decorator is all you need for each list and usage command.
    'cmd_options_any_search_query',
    # Some other commands share use of the ASCII output table feature.
    'cmd_options_table_renderer',
    # Argument parsing helpers, to facilitate **kwargs passing.
    'postprocess_options_normalize_search_args',
    # Private:
    #   '_cmd_options_*',  # Module variables.
    #   '_postprocess_options_formatter',
    #   '_postprocess_options_match_activities',
    #   '_postprocess_options_match_categories',
    #   '_postprocess_options_match_tags',
    #   '_postprocess_options_matching',
    #   '_postprocess_options_grouping',
    #   '_postprocess_options_results_options_order_to_sort_cols',
    #   '_postprocess_options_results_options_asc_desc_to_sort_order',
    #   '_postprocess_options_results_show_hide',
    #   '_postprocess_options_sparkline',
    #   '_postprocess_options_sparkline_float',
    #   '_postprocess_options_sparkline_secs',
    #   '_postprocess_options_sparkline_total',
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
    # FIXME/2020-05-20: Scrub hidden from everywhere.
    # click.option(
    #     '--hidden', is_flag=True, help=_('Show hidden items.'),
    # ),
]


# ***
# *** [SEARCH MATCH] Activity.
# ***

_cmd_options_search_match_activities = [
    click.option(
        '-a', '--activity', multiple=True,
        help=_('Restrict results by matching activity name.'),
    ),
]


def _postprocess_options_match_activities(kwargs):
    if 'activity' not in kwargs:
        return

    activity = kwargs['activity'] if kwargs['activity'] else []
    del kwargs['activity']
    if activity:
        kwargs['match_activities'] = list(activity)


# ***
# *** [SEARCH MATCH] Category.
# ***

_cmd_options_search_match_categories = [
    click.option(
        '-c', '--category', multiple=True,
        help=_('Restrict results by matching category name.'),
    ),
]


def _postprocess_options_match_categories(kwargs):
    if 'category' not in kwargs:
        return

    # This little dance is so category_name is never None, but '',
    # because get_all() distinguishes between category=None and =''.
    category = kwargs['category'] if kwargs['category'] else []
    del kwargs['category']
    if category:
        kwargs['match_categories'] = list(category)


# ***
# *** [SEARCH MATCH] Tag names.
# ***

_cmd_options_search_match_tags = [
    click.option(
        '-t', '--tag', multiple=True,
        help=_('Restrict results by matching tag name(s).'),
    ),
]


def _postprocess_options_match_tags(kwargs):
    if 'tag' not in kwargs:
        return

    tagnames = kwargs['tag'] if kwargs['tag'] else tuple()
    del kwargs['tag']
    if tagnames:
        kwargs['match_tags'] = tagnames


# ***
# *** [RESULTS GROUP] Option.
# ***

def _cmd_options_results_group(item):
    choices = []
    if item != 'activity':
        choices.append('activity')
    if item != 'category':
        choices.append('category')
    if item != 'tags':
        choices.append('tags')
    if item == 'fact':
        choices.append('days')

    return [
        click.option(
            '-g', '--group', multiple=True,
            type=click.Choice(choices),
            help=_('Group results by specified attribute(s).'),
        ),
    ]


def _postprocess_options_grouping(kwargs):
    if 'group' not in kwargs:
        return

    _postprocess_options_grouping_activity(kwargs)
    _postprocess_options_grouping_category(kwargs)
    _postprocess_options_grouping_tags(kwargs)
    _postprocess_options_grouping_days(kwargs)
    del kwargs['group']


def _postprocess_options_grouping_activity(kwargs):
    if 'group_activity' not in kwargs:
        return

    kwargs['group_activity'] = kwargs['group_activity'] or 'activity' in kwargs['group']


def _postprocess_options_grouping_category(kwargs):
    if 'group_category' not in kwargs:
        return

    kwargs['group_category'] = kwargs['group_category'] or 'category' in kwargs['group']


def _postprocess_options_grouping_tags(kwargs):
    if 'group_tags' not in kwargs:
        return

    kwargs['group_tags'] = kwargs['group_tags'] or 'tags' in kwargs['group']


def _postprocess_options_grouping_days(kwargs):
    if 'group_days' not in kwargs:
        return

    kwargs['group_days'] = kwargs['group_days'] or 'days' in kwargs['group']


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

_cmd_options_results_group_tags = [
    click.option(
        '-T', '--group-tags', is_flag=True,
        help=_('Group results by tag names.'),
    ),
]


# ***
# *** [RESULTS GROUP] Days.
# ***

_cmd_options_results_group_days = [
    click.option(
        '-Y', '--group-days', is_flag=True,
        help=_('Group results by day.'),
    ),
]


# ***
# *** [SEARCH RESULTS] Order.
# ***

def _cmd_options_results_sort_order(item, command):
    choices = ['name', 'activity', 'category']
    default_order = ('name',)
    default_direction = ('asc',)
    if item == 'fact' or command == 'usage':
        choices += ['start', 'usage', 'time']
        default_order = ('start',)
        if command == 'usage':
            default_order = ('usage',)
            default_direction = ('desc',)

    if item == 'fact':
        choices.append('day')
    if item in ('tag', 'fact'):
        # Same is --sort name
        choices.append('tag')
    if item == 'fact':
        # Sorts by Fact PK. (lb): Not sure how useful.
        choices.append('fact')

    return [
        click.option(
            '-o', '--order', '--sort',
            default=default_order,
            type=click.Choice(choices),
            # (lb): Not sure how useful to allow multi-col sort, but why not.
            multiple=True,
            help=_('Order by column(s) (specify zero or more).'),
        ),
        click.option(
            '-i', '--direction', '--dir',
            default=default_direction,
            type=click.Choice(['asc', 'desc']),
            multiple=True,
            help=_('Order by direction(s) (one for each --sort).'),
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


def _postprocess_options_results_options_order_to_sort_cols(kwargs):
    if 'order' not in kwargs:
        return

    if kwargs['order']:
        kwargs['sort_cols'] = kwargs['order']
    del kwargs['order']


def _postprocess_options_results_options_asc_desc_to_sort_order(kwargs):
    if 'direction' not in kwargs:
        return

    if kwargs['desc']:
        default_order = 'desc'
    elif kwargs['asc']:
        default_order = 'asc'
    else:
        default_order = ''
    del kwargs['desc']
    del kwargs['asc']

    sort_orders = []
    if 'sort_cols' in kwargs:
        # Ensure sort_orders same length as sort_cols.
        for idx in range(len(kwargs['sort_cols'])):
            try:
                sort_orders.append(kwargs['direction'][idx])
            except IndexError:
                sort_orders.append(default_order)
    del kwargs['direction']

    if sort_orders:
        kwargs['sort_orders'] = sort_orders


# ***
# *** [DOUBLE-SORT] Developer Option.
# ***

_postprocess_options_results_options_sort_double_sort = [
    click.option(
        '--re-sort',
        is_flag=True,
        hidden=True,
        help=_('Resort query after SELECT post-processing.'),
    ),
]


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
# *** [RESULTS HIDE] Description.
# ***

_cmd_options_results_hide_description = [
    click.option(
        '-P', '--hide-description', is_flag=True,
        help=_('Hide Fact description.'),
    ),
]


# ***
# *** [RESULTS SHOW/HIDE] Duration.
# ***

_cmd_options_results_hide_duration = [
    click.option(
        '-N', '--hide-duration', is_flag=True,
        help=_('Omit duration from results.'),
    ),
]


_cmd_options_results_show_duration = [
    click.option(
        '-N', '--show-duration', is_flag=True,
        help=_('Display duration in results.'),
    ),
]


# ***
# *** [RESULTS HIDE/SHOW] Usage.
# ***

_cmd_options_results_hide_usage = [
    click.option(
        '-U', '--hide-usage', is_flag=True,
        help=_('Omit usage count from results.'),
    ),
]


_cmd_options_results_show_usage = [
    click.option(
        '-U', '--show-usage', is_flag=True,
        help=_('Display usage count in results.'),
    ),
]


# ***
# *** [POST PROCESS] Show/Hide.
# ***

def _postprocess_options_results_show_hide(kwargs):
    # The list command have --show-* options; the usage commands
    # have --hide-* options; the export command has neither.
    _postprocess_options_results_show_hide_option(kwargs, 'duration')
    _postprocess_options_results_show_hide_option(kwargs, 'usage')


def _postprocess_options_results_show_hide_option(kwargs, argname):
    hide_item = None
    attr_show = 'show_{}'.format(argname)
    attr_hide = 'hide_{}'.format(argname)
    if attr_show in kwargs:
        hide_item = not kwargs[attr_show]
    elif attr_hide in kwargs:
        hide_item = kwargs[attr_hide]
    if hide_item is not None:
        kwargs[attr_hide] = hide_item
    if attr_show in kwargs:
        del kwargs[attr_show]


# ***
# *** [RESULTS CUSTOM] Columns.
# ***

_cmd_options_results_show_columns = [
    click.option(
        '-l', '--column', multiple=True,
        type=click.Choice(report_table_columns()),
        help=_('Specify custom report columns.'),
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
# *** [REPORT FORMAT] Option.
# ***

_cmd_options_output_format = [
    click.option(
        '-F', '--format', multiple=True,
        type=click.Choice([
            'journal',
            'tabular',
            'factoid',
        ]),
        help=_('Results display format.'),
    ),
]


def _postprocess_options_formatter(kwargs):
    if 'format' not in kwargs:
        return

    kwargs['format_journal'] = kwargs['format_journal'] or 'journal' in kwargs['format']
    kwargs['format_tabular'] = kwargs['format_tabular'] or 'tabular' in kwargs['format']
    kwargs['format_factoid'] = kwargs['format_factoid'] or 'factoid' in kwargs['format']
    del kwargs['format']


# ***
# *** [REPORT FORMAT] Journal.
# ***

_cmd_options_output_format_journal = [
    click.option(
        '-j', '--format-journal', is_flag=True,
        help=_('Output results in Journal format.'),
    ),
]


# ***
# *** [REPORT FORMAT] Tabular.
# ***

_cmd_options_output_format_tabular = [
    click.option(
        '-r', '--format-tabular', is_flag=True,
        help=_('Output results in an ASCII table.'),
    ),
]


# ***
# *** [REPORT FORMAT] Table Type.
# ***


_ascii_table_libs = [
    'texttable',
    'tabulate',
    'friendly',
]


_tabulate_tablefmts = [
    'plain',
    'simple',
    'github',
    'grid',
    'fancy_grid',
    'pipe',
    'orgtbl',
    'jira',
    'presto',
    'psql',
    'rst',
    'mediawiki',
    'moinmoin',
    'youtrack',
    'html',
    'latex',
    'latex_raw',
    'latex_booktabs',
    'textile',
]


_cmd_options_table_renderer = [
    click.option(
        '-E', '--table-type', default='texttable', show_default=True,
        type=click.Choice(
            _ascii_table_libs + _tabulate_tablefmts,
        ),
        help=_('ASCII table formatter.'),
    ),
]


def cmd_options_table_renderer(func):
    for option in reversed(_cmd_options_table_renderer):
        func = option(func)
    return func


def cmd_options_table_renderer(func):
    for option in reversed(_cmd_options_table_renderer):
        func = option(func)
    return func


# ***
# *** [EXPORT FORMAT] Factoid.
# ***

_cmd_options_output_format_factoid = [
    click.option(
        '-f', '--fact', is_flag=True,
        help=_('Output importable Factoid blocks.'),
    ),
]


# ***
# *** [EXPORT FORMAT] Factoid Format.
# ***

_cmd_options_output_factoids_hrule = [
    click.option(
        '-R', '--factoid-rule', '--sep', nargs=1, default='',
        help=_('Separate Factoids with a horizontal rule.'),
    ),
]


# ***
# *** [REPORT/EXPORT/OUTPUT FORMAT] Sparkline Format.
# ***

_cmd_options_output_sparkline_format = [
    click.option(
        '-V', '--spark-total', '--stot', nargs=1,
        default='max', show_default=True,
        metavar='MAX',
        help=_("Secs in full spark: 'max' or 'net' duration, or number."),
    ),
    click.option(
        '-W', '--spark-width', '--swid', type=int, default='12',
        metavar='WIDTH',
        help=_("Number of block (█) characters in full spark."),
    ),
    click.option(
        '-S', '--spark-secs', '--ssec',
        metavar='WIDTH',
        help=_("Secs. per block (█), defaults to total / width."),
    ),
]


# ***
# *** [POST PROCESS] Show/Hide.
# ***

def _postprocess_options_sparkline(kwargs):
    if 'spark_total' not in kwargs:
        return

    _postprocess_options_sparkline_total(kwargs)
    _postprocess_options_sparkline_secs(kwargs)


def _postprocess_options_sparkline_total(kwargs):
    if kwargs['spark_total'] in ('max', 'net'):
        return

    _postprocess_options_sparkline_float(kwargs, 'spark_total')


def _postprocess_options_sparkline_secs(kwargs):
    _postprocess_options_sparkline_float(kwargs, 'spark_secs')


def _postprocess_options_sparkline_float(kwargs, spark_attr):
    try:
        kwargs[spark_attr] = float(kwargs[spark_attr] or 0)
    except ValueError:
        try:
            # Is this a security issue? Ha!
            # - Let user specify math on the command line, e.g., to
            #   specify 8 hours as the full spark width, user'd use:
            #     --spark-total '8 * 60 * 60'
            kwargs[spark_attr] = float(eval(kwargs[spark_attr]))
        except Exception:
            msg = _(
                "Unable to parse --{} value as (eval'able) seconds: {}"
            ).format(spark_attr.replace('_', '-'), kwargs[spark_attr])
            dob_in_user_exit(msg)


# ***
# *** [POST PROCESS] Adjust **kwargs.
# ***

def _postprocess_options_matching(kwargs):
    _postprocess_options_match_activities(kwargs)
    _postprocess_options_match_categories(kwargs)
    _postprocess_options_match_tags(kwargs)


def postprocess_options_normalize_search_args(kwargs):
    _postprocess_options_matching(kwargs)
    _postprocess_options_grouping(kwargs)
    _postprocess_options_results_options_order_to_sort_cols(kwargs)
    _postprocess_options_results_options_asc_desc_to_sort_order(kwargs)
    _postprocess_options_results_show_hide(kwargs)
    _postprocess_options_formatter(kwargs)
    _postprocess_options_sparkline(kwargs)


# ***
# *** [ALL TOGETHER NOW] One @decorator is all you need.
# ***

# *** One @decorator for all your search command option needs.

def cmd_options_any_search_query(command='', item='', match=False, group=False):
    def _cmd_options_any_search_query():
        options = []
        append_cmd_options_search_basics(options)
        append_cmd_options_matching(options)
        append_cmd_options_group_by(options)
        append_cmd_options_results_sort_limit(options)
        append_cmd_options_results_reports(options)

        def _cmd_options_search_query(func):
            for option in reversed(options):
                func = option(func)
            return func

        return _cmd_options_search_query

    def append_cmd_options_search_basics(options):
        options.extend(_cmd_options_search_item_key)
        options.extend(_cmd_options_search_item_name)
        options.extend(_cmd_options_search_time_window)

    def append_cmd_options_matching(options):
        if not match:
            return

        # We could exclude the --activity item from the `dob list activity`
        # and `dob usage activity` commands, but by including it, we allow
        # the user access to a strict text match search, as opposed to using
        # search_term, which is a loose match. E.g., the difference between
        # `dob list activity -a "Must Match Fully"` as compared to
        # `dob list activity fully`, given Activity named "Must Match Fully".
        options.extend(_cmd_options_search_match_activities)
        options.extend(_cmd_options_search_match_categories)
        # MAYBE/2020-05-20: Add a match for tags?
        #  options.extend(_cmd_options_search_match_tags)

    def append_cmd_options_group_by(options):
        if not group:
            return

        if item != 'activity':
            options.extend(_cmd_options_results_group_activity)
        if item != 'category':
            options.extend(_cmd_options_results_group_category)
        if item != 'tags':
            options.extend(_cmd_options_results_group_tags)
        if item == 'fact':
            options.extend(_cmd_options_results_group_days)
        options.extend(_cmd_options_results_group(item))

    def append_cmd_options_results_sort_limit(options):
        options.extend(_cmd_options_results_sort_order(item, command))
        options.extend(_cmd_options_search_limit_offset)
        # (lb): It'd be nice to squelch this option unless config['dev.catch_errors']
        #       but I guess that's what Click 'hidden' option feature is for.
        options.extend(_postprocess_options_results_options_sort_double_sort)

    def append_cmd_options_results_reports(options):
        if command == 'export':
            return

        append_cmd_options_results_basic_usage_hide_show(options)
        append_cmd_options_results_fact_attrs_hide_show(options)
        append_cmd_options_results_chopped(options)
        append_cmd_options_output_formatters(options)
        append_cmd_options_tablular_format(options)
        append_cmd_options_factoids_format(options)
        append_cmd_options_journal_format(options)

    def append_cmd_options_results_basic_usage_hide_show(options):
        # Search results report output column values hide/show options.
        if command == 'usage':
            options.extend(_cmd_options_results_hide_usage)
            options.extend(_cmd_options_results_hide_duration)
        elif command == 'list':
            options.extend(_cmd_options_results_show_usage)
            options.extend(_cmd_options_results_show_duration)

    def append_cmd_options_results_fact_attrs_hide_show(options):
        # Search results report output column values hide/show options.
        if item != 'fact':
            return

        options.extend(_cmd_options_results_hide_description)
        # (lb): I sorta wanna hide final_start and final_end by default.
        # - But then I'm afraid no one would find them.
        # - So instead, supply --column option to fine-tune the output.
        options.extend(_cmd_options_results_show_columns)

    def append_cmd_options_results_chopped(options):
        # A cell value truncate... option.
        if command == 'export':
            return

        options.extend(_cmd_options_results_chop)

    def append_cmd_options_output_formatters(options):
        if item != 'fact':
            return

        options.extend(_cmd_options_output_format_journal)
        options.extend(_cmd_options_output_format_tabular)
        options.extend(_cmd_options_output_format_factoid)
        options.extend(_cmd_options_output_format)

    def append_cmd_options_tablular_format(options):
        options.extend(_cmd_options_table_renderer)

    def append_cmd_options_factoids_format(options):
        if item != 'fact':
            return

        options.extend(_cmd_options_output_factoids_hrule)

    def append_cmd_options_journal_format(options):
        if item != 'fact':
            return

        options.extend(_cmd_options_output_sparkline_format)

    return _cmd_options_any_search_query()

