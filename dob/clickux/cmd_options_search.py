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

from dob_bright.reports.tabulate_results import report_table_columns
from dob_bright.termio import dob_in_user_exit, dob_in_user_warning

__all__ = (
    # One decorator is all you need for each list and usage command.
    'cmd_options_any_search_query',
    # Some other commands share use of the ASCII output table feature.
    'cmd_options_output_format_any_input',
    'cmd_options_output_format_facts_only',
    # Argument parsing helpers, to facilitate **kwargs passing.
    'postprocess_options_normalize_search_args',
    'postprocess_options_output_format_any_input',
    # Private module variables:
    #   '_cmd_options_*',
    # Private module functions:
    #   '_cmd_options_output_format_choices',
    #   '_cmd_options_output_format_multiple_choices_option',
    #   '_cmd_options_output_format_singular_options_any',
    #   '_cmd_options_output_format_singular_options_fact',
    #   '_cmd_options_output_format_tabling',
    #   '_cmd_options_output_formats_basic',
    #   '_cmd_options_output_formats_table',
    #   '_cmd_options_results_group',
    #   '_cmd_options_results_output_path',
    #   '_cmd_options_results_sort_order',
    #   '_cmd_options_search_time_window',
    #   '_postprocess_options_grouping',
    #   '_postprocess_options_match_activities',
    #   '_postprocess_options_match_categories',
    #   '_postprocess_options_matching',
    #   '_postprocess_options_results_options_direction_to_sort_order',
    #   '_postprocess_options_results_options_sort_to_sort_cols',
    #   '_postprocess_options_results_show_hide',
    #   '_postprocess_options_results_show_hide_option',
    #   '_postprocess_options_search_term',
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
# *** [SEARCH QUERY] Search Terms.
# ***

_cmd_options_search_search_term = [
    click.argument(
        'search_term',
        nargs=-1,
        default=None,
    ),
]


def _postprocess_options_search_term(kwargs):
    if 'search_term' not in kwargs:
        return

    # (lb): Me, the pedant.
    kwargs['search_terms'] = kwargs['search_term']
    del kwargs['search_term']


# ***
# *** [SEARCH QUERY] Time Window.
# ***

def _cmd_options_search_time_window(command=''):
    since_default_value = ''
    since_show_default = False
    if command == 'journal':
        since_default_value = 'last week'
        since_show_default = True
    cmd_options = [
        click.option(
            '-s', '--since', '--after',
            metavar='TIME',
            default=since_default_value,
            show_default=since_show_default,
            help=_('Show items newer than a specific date.'),
        ),
        click.option(
            '-u', '--until', '--before',
            metavar='TIME',
            help=_('Show items older than a specific date.'),
        ),
    ]
    return cmd_options


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
        help=_('Restrict results by exact activity name(s).'),
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
        help=_('Restrict results by exact category name(s).'),
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
# *** [SEARCH MATCH] Fuzzy terms.
# ***

_cmd_options_search_fuzzy_terms = [
    click.option(
        '--fuzzy-terms', '--fuzzy',
        is_flag=True,
        help=_(
            'Try SEARCH_TERM matching on activity, category, and tag names'
            ' (otherwise SEARCH_TERM only matches description).'
        ),
    ),
]


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
            help=_('Alias of `--group-<attribute>` options (multiple allowed).'),
        ),
    ]


def _postprocess_options_grouping(kwargs, cmd_journal=False):
    def __postprocess_options_grouping():
        if 'group' not in kwargs:
            return

        process_grouping_option('activity')
        process_grouping_option('category')
        process_grouping_option('tags')
        process_grouping_option('days')
        del kwargs['group']

        ensure_default_grouping()

    def process_grouping_option(type_name):
        # Form the group name, e.g., group_activity, group_category, etc.
        group_name = 'group_{}'.format(type_name)
        if group_name not in kwargs:
            return

        kwargs[group_name] = kwargs[group_name] or type_name in kwargs['group']

    def ensure_default_grouping():
        if not cmd_journal:
            return

        if not (
            kwargs['group_activity']
            or kwargs['group_category']
            or kwargs['group_tags']
            or kwargs['group_days']
        ):
            kwargs['group_activity'] = True
            kwargs['group_category'] = True

    __postprocess_options_grouping()


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

def _cmd_options_results_sort_order(item, command, group):
    choices = ['name', 'activity', 'category']
    default_sort_cols = ['name']
    default_sort_orders = ['asc']
    if item == 'fact' or command == 'usage':
        choices += ['start', 'time']
        default_sort_cols = ['start']
        if group:
            choices += ['usage']
            if command == 'usage' or command == 'journal':
                default_sort_cols = ['usage']
                default_sort_orders = ['desc']

    if group and item == 'fact':
        choices.append('day')
    if item in ('tag', 'fact'):
        # For item == 'tag', this option same as --sort 'name'.
        choices.append('tag')
    if item == 'fact':
        # Sorts by Fact PK. (lb): Not sure how useful.
        # - Because Momentaneous Facts, potentially useful.
        choices.append('fact')

    return [
        click.option(
            '-S', '--sort', '--order',
            default=default_sort_cols,
            show_default=True,
            type=click.Choice(choices),
            multiple=True,
            help=_('Order by column(s) (multiple allowed).'),
        ),
        click.option(
            '-D', '--direction', '--dir',
            default=default_sort_orders,
            type=click.Choice(['asc', 'desc']),
            multiple=True,
            help=_('Order by direction(s) (one for each --sort).'),
        ),
    ]


# ***
# *** [POST PROCESS] Sort/Order Options.
# ***


def _postprocess_options_results_options_sort_to_sort_cols(kwargs):
    if 'sort' not in kwargs:
        return

    if kwargs['sort']:
        kwargs['sort_cols'] = kwargs['sort']
    del kwargs['sort']


def _postprocess_options_results_options_direction_to_sort_order(kwargs):
    if 'direction' not in kwargs:
        return

    last_direction = 'asc'
    sort_orders = []
    if 'sort_cols' in kwargs:
        # Ensure sort_orders same length as sort_cols.
        for idx in range(len(kwargs['sort_cols'])):
            try:
                last_direction = kwargs['direction'][idx]
            except IndexError:
                pass
            sort_orders.append(last_direction)
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
        help=_('Skip this number of records before returning results.'),
    ),
]


# ***
# *** [RESULTS HIDE] Description.
# ***

_cmd_options_results_hide_description = [
    click.option(
        '-P', '--hide-description', is_flag=True,
        help=_('Omit Fact description from results.'),
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
        help=_('Display duration time in results.'),
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
# *** [SEARCH RESULTS] Output file.
# ***

def _cmd_options_results_output_path(for_export=False):
    return [
        click.option(
            '-o', '--output',
            help=_('Write to file instead of stdout.'),
            metavar='PATH',
        ),
    ]


# ***
# *** [REPORT FORMAT] Basic Formats.
# ***


_standard_formats = [
    'csv',
    'json',
    'tsv',
    'xml',
    'table',
]


_single_fact_formats = [
    'ical',
    'factoid',
]


_fact_usage_formats = [
    'journal',
]


def _cmd_options_output_formats_basic(item=''):
    format_choices = []
    format_choices += _standard_formats
    format_choices += _single_fact_formats if item == 'fact' else []
    format_choices += _fact_usage_formats if item == 'fact' else []
    return format_choices


def cmd_options_output_format_facts_only():
    return _single_fact_formats


def _cmd_options_output_format_singular_options_any():
    # --format <format> aliases.
    cmd_options = [
        click.option(
            '--csv', is_flag=True,
            help=_('Output results using comma-separated values (CSV).'),
        ),
        click.option(
            '--json', is_flag=True,
            help=_('Output results using JavaScript Object Notation (JSON).'),
        ),
        click.option(
            '--tsv', is_flag=True,
            help=_('Output results using tab-separated values (TSV).'),
        ),
        click.option(
            '--xml', is_flag=True,
            help=_('Output results using Extensible Markup Language (XML).'),
        ),
        click.option(
            '--table', is_flag=True,
            help=_('Output results using an ASCII table format.'),
        ),
    ]
    return cmd_options


def _cmd_options_output_format_singular_options_fact():
    cmd_options = [
        click.option(
            '--ical', is_flag=True,
            help=_('Output Facts using iCalendar format.'),
        ),
        click.option(
            '--factoid', is_flag=True,
            help=_("Output Facts using dob's Factoid format."),
        ),
        click.option(
            '--journal', is_flag=True,
            help=_("Output Facts using dob's Journal format."),
        ),
    ]
    return cmd_options


def _cmd_options_output_format_multiple_choices_option(command='', item=''):
    format_choices = _cmd_options_output_formats_basic(item)

    if command == 'export':
        default_format = 'factoid'
    elif command == 'journal':
        default_format = 'journal'
    else:
        default_format = 'table'

    cmd_options = [
        click.option(
            '-f', '--format',
            type=click.Choice(format_choices),
            default=default_format,
            show_default=True,
            help=_('Alias of format options (one allowed).'),
        ),
    ]
    return cmd_options


def _cmd_options_output_format_choices(command='', item=''):
    cmd_options = []
    cmd_options += _cmd_options_output_format_singular_options_any()
    if item == 'fact':
        cmd_options += _cmd_options_output_format_singular_options_fact()
    cmd_options += _cmd_options_output_format_multiple_choices_option(command, item)
    return cmd_options


def _postprocess_options_output_format_choices(kwargs):
    if 'format' not in kwargs:
        return

    format_choices = _cmd_options_output_formats_basic(item='fact')
    fmts_specified = []
    for choice in format_choices:
        try:
            if kwargs[choice]:
                kwargs['format'] = choice
                fmts_specified.append(choice)
            del kwargs[choice]
        except KeyError:
            # 'choice' is 'factoid' or 'journal', because item=='fact' unknown, so
            # always trying, even for commands that do not output Fact reports.
            pass

    if len(fmts_specified) > 1:
        dob_in_user_warning(_(
            'More than one format specified: {}'
        ).format(fmts_specified))

    kwargs['output_format'] = kwargs['format']
    del kwargs['format']


# ***
# *** [REPORT FORMAT] Table Formats.
# ***


_ascii_table_libs = [
    'texttable',
    'tabulate',
    'friendly',
]


_tabulate_tablefmts_unwrapped = [
    'fancy_grid',
    #   ╒════════════╤════════════╤════════════╕
    #   │ Header 1   │ Header 2   │ Header 3   │
    #   ╞════════════╪════════════╪════════════╡
    #   │ value 1    │ value 2    │ value 3    │
    #   ╘════════════╧════════════╧════════════╛

    'grid',
    #   +------------+------------+------------+
    #   | Header 1   | Header 2   | Header 3   |
    #   +============+============+============+
    #   | value 1    | value 2    | value 3    |
    #   +------------+------------+------------+

    'pretty',
    #   +----------+----------+----------+
    #   | Header 1 | Header 2 | Header 3 |
    #   +----------+----------+----------+
    #   | value 1  | value 2  | value 3  |
    #   +----------+----------+----------+

    'presto',
    #    Header 1   | Header 2   | Header 3
    #   ------------+------------+------------
    #    value 1    | value 2    | value 3

    'simple',
    #   Header 1    Header 2    Header 3
    #   ----------  ----------  ----------
    #   value 1     value 2     value 3

    'plain',
    #   Header 1    Header 2    Header 3
    #   value 1     value 2     value 3

    'psql',
    #   +------------+------------+------------+
    #   | Header 1   | Header 2   | Header 3   |
    #   |------------+------------+------------|
    #   | value 1    | value 2    | value 3    |
    #   +------------+------------+------------+

    'pipe',
    #   | Header 1   | Header 2   | Header 3   |
    #   |:-----------|:-----------|:-----------|
    #   | value 1    | value 2    | value 3    |
]


_tabulate_tablefmts_markup = [
    'github',
    #   | Header 1   | Header 2   | Header 3   |
    #   |------------|------------|------------|
    #   | value 1    | value 2    | value 3    |

    'html',
    #   <table>
    #   <thead>
    #   <tr><th>Header 1  </th><th>Header 2  </th><th>Header 3  </th></tr>
    #   </thead>
    #   <tbody>
    #   <tr><td>value 1   </td><td>value 2   </td><td>value 3   </td></tr>
    #   </tbody>
    #   </table>

    # 'jira',  # MEH: Could add if requested.
    #   || Header 1   || Header 2   || Header 3   ||
    #   | value 1    | value 2    | value 3    |

    # 'latex',  # MEH: Could add if requested.
    #   \begin{tabular}{lll}
    #   \hline
    #    Header 1   & Header 2   & Header 3   \\
    #   \hline
    #    value 1    & value 2    & value 3    \\
    #   \hline
    #   \end{tabular}

    # 'latex_raw',  # SKIP: Same as 'latex'
    #   \begin{tabular}{lll}
    #   \hline
    #    Header 1   & Header 2   & Header 3   \\
    #   \hline
    #    value 1    & value 2    & value 3    \\
    #   \hline
    #   \end{tabular}

    # 'latex_booktabs',  # MEH: Could add if requested.
    #   \begin{tabular}{lll}
    #   \toprule
    #    Header 1   & Header 2   & Header 3   \\
    #   \midrule
    #    value 1    & value 2    & value 3    \\
    #   \bottomrule
    #   \end{tabular}

    'mediawiki',
    #   {| class="wikitable" style="text-align: left;"
    #   |+ <!-- caption -->
    #   |-
    #   ! Header 1   !! Header 2   !! Header 3
    #   |-
    #   | value 1    || value 2    || value 3
    #   |}

    # 'moinmoin',  # For MoinMoin Wiki Engine. MEH: Could add if requested.
    #   || ''' Header 1   ''' || ''' Header 2   ''' || ''' Header 3   ''' ||
    #   ||  value 1     ||  value 2     ||  value 3     ||

    'orgtbl',
    #   | Header 1   | Header 2   | Header 3   |
    #   |------------+------------+------------|
    #   | value 1    | value 2    | value 3    |

    'rst',
    #   ==========  ==========  ==========
    #   Header 1    Header 2    Header 3
    #   ==========  ==========  ==========
    #   value 1     value 2     value 3
    #   ==========  ==========  ==========

    # 'textile',  # MEH: Could add if requested.
    #   |_.  Header 1   |_. Header 2   |_. Header 3   |
    #   |<. value 1     |<. value 2    |<. value 3    |

    # 'unsafehtml',  # MEH.
    #   Header 1    Header 2    Header 3
    #   ----------  ----------  ----------
    #   value 1     value 2     value 3

    # 'youtrack',  # Similar to 'jira'
    #   ||  Header 1    ||  Header 2    ||  Header 3    ||
    #   |  value 1     |  value 2     |  value 3     |
]


def _cmd_options_output_formats_table(item=''):
    table_choices = []
    # LATER: (lb): None of the 'tabulate' styles wrap, nor does 'friendly',
    #        so the table output is practically useless. Exclude these
    #        options until/unless tabulate_results is updated to wrap long
    #        cell values.
    #  table_choices += _ascii_table_libs
    #  table_choices += _tabulate_tablefmts_unwrapped
    # We can at least support the markup format options, which are not
    # meant to be viewed in the terminal.
    # MAGIC_VALUE: Use 'normal' to refer to the nice, wrapped ASCII table
    #              that 'texttable' generates by default.
    table_choices += ['normal']
    table_choices += _tabulate_tablefmts_markup
    return table_choices


def _cmd_options_output_format_tabling():
    formats_table = _cmd_options_output_formats_table()

    cmd_options = [
        click.option(
            '--table-style', '--style',
            type=click.Choice(formats_table),
            nargs=1,
            default='normal',
            show_default=True,
            help=_('ASCII table style.'),
        ),
    ]
    return cmd_options


def _postprocess_options_output_format_tabling(kwargs):
    if 'table_style' not in kwargs:
        return

    if kwargs['table_style'] == 'normal':
        kwargs['table_style'] = 'texttable'


# ***
# *** [REPORT FORMAT] Basic Formats and Table Styles.
# ***

def cmd_options_output_format_any_input(func):
    cmd_options = []
    cmd_options.extend(_cmd_options_output_format_choices())
    cmd_options.extend(_cmd_options_output_format_tabling())
    for option in reversed(cmd_options):
        func = option(func)
    return func


def postprocess_options_output_format_any_input(kwargs, cmd_journal=False):
    _postprocess_options_output_format_choices(kwargs)
    _postprocess_options_output_format_tabling(kwargs)


# ***
# *** [EXPORT FORMAT] Factoid Option.
# ***

_cmd_options_output_factoids_hrule = [
    click.option(
        # MEH: We could alias '-R', or reserve -R for later.
        '--factoid-rule', '--rule',
        nargs=1,
        default='',
        metavar='SEP',
        help=_('Separate Factoids with a horizontal rule.'),
    ),
]


# ***
# *** [REPORT/EXPORT/OUTPUT FORMAT] Sparkline Options.
# ***

_cmd_options_output_sparkline_format = [
    click.option(
        # MEH: We could alias '-W', or reserve -W for later.
        '--spark-width', '--swid',
        type=int,
        default='12',
        metavar='INT',
        # (lb): I like the idea of showing "block (█) character"
        #       but it's very distracting.
        help=_("Number of block characters in full spark [default: 12]."),
    ),
    click.option(
        # MEH: We could alias '-V', or reserve -V for later.
        '--spark-total', '--stot',
        nargs=1,
        default='max',
        metavar='MAX',
        # show_default=True,
        help=_(
            "Number of seconds in full spark: "
            "'max' or 'net' duration, or number [default: 'max']."
        ),
    ),
    click.option(
        # MEH: We could alias '-S', or reserve -S for later.
        '--spark-secs', '--ssec',
        metavar='WIDTH',
        help=_("Seconds per block character [default: total / width]."),
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


def postprocess_options_normalize_search_args(kwargs, cmd_journal=False):
    _postprocess_options_matching(kwargs)
    _postprocess_options_grouping(kwargs, cmd_journal=cmd_journal)
    _postprocess_options_results_options_sort_to_sort_cols(kwargs)
    _postprocess_options_results_options_direction_to_sort_order(kwargs)
    _postprocess_options_results_show_hide(kwargs)
    postprocess_options_output_format_any_input(kwargs, cmd_journal=cmd_journal)
    _postprocess_options_sparkline(kwargs)
    _postprocess_options_search_term(kwargs)


# ***
# *** [ALL TOGETHER NOW] One @decorator is all you need.
# ***

# *** One @decorator for all your search command option needs.

def cmd_options_any_search_query(command='', item='', match=False, group=False):
    def _cmd_options_any_search_query():
        options = []
        append_cmd_options_filter_by_pk(options)
        append_cmd_options_filter_by_time(options)
        append_cmd_options_matching(options)
        append_cmd_options_group_by(options)
        append_cmd_options_results_sort_limit(options)
        append_cmd_options_results_column_choices(options)
        append_cmd_options_output_file(options)
        append_cmd_options_results_report_formats(options)
        append_cmd_options_filter_by_search_terms(options)

        def _cmd_options_search_query(func):
            for option in reversed(options):
                func = option(func)
            return func

        return _cmd_options_search_query

    # +++

    def append_cmd_options_filter_by_pk(options):
        if command == 'export':
            return

        options.extend(_cmd_options_search_item_key)

    def append_cmd_options_filter_by_time(options):
        options.extend(_cmd_options_search_time_window(command))

    def append_cmd_options_filter_by_search_terms(options):
        options.extend(_cmd_options_search_search_term)

    # +++

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

        if item == 'fact':
            options.extend(_cmd_options_search_fuzzy_terms)

    # +++

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

    # +++

    def append_cmd_options_results_sort_limit(options):
        options.extend(_cmd_options_results_sort_order(item, command, group))
        options.extend(_cmd_options_search_limit_offset)

    # +++

    def append_cmd_options_results_column_choices(options):
        if command == 'export':
            return

        append_cmd_options_results_basic_usage_hide_show(options)
        append_cmd_options_results_fact_attrs_hide_show(options)
        append_cmd_options_results_chopped(options)

    def append_cmd_options_results_report_formats(options):
        if command == 'export':
            return

        append_cmd_options_output_format(options)
        append_cmd_options_format_factoid_output(options)
        append_cmd_options_format_fact_values(options)
        append_cmd_options_table_style(options)

        append_cmd_options_results_re_sort(options)

    # +++

    def append_cmd_options_results_basic_usage_hide_show(options):
        # Search results report output column values hide/show options.
        if command == 'usage':
            options.extend(_cmd_options_results_hide_usage)
            options.extend(_cmd_options_results_hide_duration)
        elif command in ['list', 'journal']:
            options.extend(_cmd_options_results_show_usage)
            options.extend(_cmd_options_results_show_duration)
        elif command == 'export':
            pass  # Show neither.
        else:  # Impossible.
            raise False  # pragma: no cover

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

    def append_cmd_options_results_re_sort(options):
        if item != 'fact':
            return

        # (lb): It'd be nice to squelch this option unless config['dev.catch_errors']
        #       but I guess that's what Click 'hidden' option feature is for.
        options.extend(_postprocess_options_results_options_sort_double_sort)

    # +++

    def append_cmd_options_output_file(options):
        for_export = (command == 'export')
        options.extend(_cmd_options_results_output_path(for_export=for_export))

    # +++

    def append_cmd_options_output_format(options):
        options.extend(_cmd_options_output_format_choices(command, item))

    def append_cmd_options_format_factoid_output(options):
        if item != 'fact':
            return

        options.extend(_cmd_options_output_factoids_hrule)

    def append_cmd_options_format_fact_values(options):
        if item != 'fact':
            return

        options.extend(_cmd_options_output_sparkline_format)

    def append_cmd_options_table_style(options):
        options.extend(_cmd_options_output_format_tabling())

    # +++

    return _cmd_options_any_search_query()

