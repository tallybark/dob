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
import sys
from collections import namedtuple

from nark.helpers.colored import colorize
from nark.helpers.parse_time import parse_dated

from ..cmd_common import error_exit_no_results, hydrate_activity, hydrate_category
from ..help_strings import NO_ACTIVE_FACT_HELP
from ..helpers import click_echo, dob_in_user_exit, dob_in_user_warning
from ..helpers.ascii_table import generate_table, warn_if_truncated


__all__ = [
    'echo_latest_ended',
    'echo_ongoing_fact',
    'echo_ongoing_or_ended',
    'find_latest_fact',
    'find_oldest_fact',
    'list_facts',
    'search_facts',
    'generate_facts_table',
    # Private:
    #  'echo_most_recent',
    #  'echo_single_fact',
]


# ***

def echo_latest_ended(controller):
    echo_most_recent(controller, restrict='ended')


def echo_ongoing_fact(controller):
    """
    Return current *ongoing fact*.

    Returns:
        None: If everything went alright.

    Raises:
        click.ClickException: If we fail to fetch any *ongoing fact*.
    """
    echo_most_recent(controller, restrict='ongoing', empty_msg=NO_ACTIVE_FACT_HELP)


def echo_ongoing_or_ended(controller):
    echo_most_recent(controller, restrict=None)


def echo_most_recent(controller, restrict=None, empty_msg=None):
    fact = find_latest_fact(controller, restrict=restrict)
    if fact is not None:
        echo_single_fact(controller, fact)
    else:
        empty_msg = empty_msg if empty_msg else _('No facts found.')
        dob_in_user_exit(empty_msg)


def find_latest_fact(controller, restrict=None):
    assert not restrict or restrict in ['ended', 'ongoing', ]
    fact = None
    if not restrict or restrict == 'ongoing':
        try:
            fact = controller.facts.get_current_fact()
        except KeyError:
            fact = None
        except Exception as err:
            # (lb): Unexpected! This could mean more than one ongoing Fact found!
            dob_in_user_warning(str(err))
    if fact is None and restrict != 'ongoing':
        results = controller.facts.get_all(
            sort_col='start', sort_order='desc', limit=1, exclude_ongoing=True,
        )
        if len(results) > 0:
            assert len(results) == 1
            fact, = results
    return fact


# ***

def find_oldest_fact(controller):
    fact = None
    results = controller.facts.get_all(
        sort_col='start', sort_order='asc', limit=1,
    )
    if len(results) > 0:
        assert len(results) == 1
        fact, = results
    return fact


# ***

def echo_single_fact(controller, fact):
    colorful = controller.client_config['term_color']
    localize = controller.config['tz_aware']
    click_echo(
        fact.friendly_str(
            shellify=False,
            description_sep=': ',
            localize=localize,
            colorful=colorful,
            show_elapsed=True,
        )
    )


# ***

def list_facts(
    controller,
    include_id=False,
    include_usage=False,
    filter_activity='',
    filter_category='',
    table_type='friendly',
    truncate=False,
    block_format=None,
    rule='',
    span=False,
    out_file=None,
    term_width=None,
    *args,
    **kwargs
):
    """
    List facts, with filtering and sorting options.

    Returns:
        None: If success.
    """
    activity = hydrate_activity(controller, filter_activity)
    category = hydrate_category(controller, filter_category)

    def _list_facts():
        results = search_facts(
            controller,
            *args,
            include_usage=include_usage,
            activity=activity,
            category=category,
            sort_col=sort_col(),
            **kwargs
        )
        if not results:
            error_exit_no_results(_('facts'))
        if block_format:
            output_block(results)
        else:
            output_table(results)

    def sort_col():
        if 'sort_col' in kwargs:
            return ''
        if not include_usage:
            return ''
        return 'time'

    def output_block(results):
        colorful = controller.client_config['term_color']
        sep_width = output_rule_width()
        cut_width = output_truncate_at()
        for idx, fact in enumerate(results):
            write_out() if idx > 0 else None
            output_fact_block(fact, colorful, cut_width)
            if sep_width:
                write_out()
                write_out(colorize(rule * sep_width, 'indian_red_1c'))

    def output_rule_width():
        if not rule:
            return None
        return terminal_width()

    def output_truncate_at():
        if not truncate:
            return None
        return terminal_width()

    def terminal_width():
        if term_width is not None:
            return term_width
        elif sys.stdout.isatty():
            return click.get_terminal_size()[0]
        else:
            return 80

    def output_fact_block(fact, colorful, cut_width):
        write_out(
            fact.friendly_str(
                shellify=False,
                description_sep='\n\n',
                localize=True,
                include_id=include_id,
                colorful=colorful,
                cut_width=cut_width,
                show_elapsed=span,
            )
        )

    def output_table(results):
        table, headers = generate_facts_table(
            controller,
            results,
            show_duration=span,
            include_usage=include_usage,
        )
        # 2018-06-08: headers is:
        #   ['Key', 'Start', 'End', 'Activity', 'Category', 'Tags', 'Description',]
        #   and sometimes + ['Duration']
        desc_col_idx = 6  # MAGIC_NUMBER: Depends on generate_facts_table.
        # FIXME: (lb): This is ridiculously slow on a mere 15K records! So
        #   Use --limit/--offset or other ways of filter filter
        #   We should offer a --limit/--offset feature.
        #   We could also fail if too many records; or find a better library.
        generate_table(table, headers, table_type, truncate, trunccol=desc_col_idx)
        warn_if_truncated(controller, len(results), len(table))

    def write_out(line=''):
        if out_file is not None:
            out_file.write(line + "\n")
        else:
            click_echo(line)

    _list_facts()


# ***

def search_facts(
    controller,
    key=None,
    since=None,
    until=None,
    *args,
    **kwargs
):
    """
    Search for one or more facts, given a set of search criteria and sort options.

    Args:
        search_term: Term that need to be matched by the fact in order to be
            considered a hit.

        FIXME: Keep documenting...
    """
    def _search_facts():
        if key:
            return [controller.facts.get(pk=key)]
        else:
            return get_all(since, until)

    def get_all(since, until):
        # Convert the since and until time strings to datetimes.
        since = parse_dated(since, controller.now) if since else None
        until = parse_dated(until, controller.now) if until else None

        results = controller.facts.get_all(
            since=since, until=until, *args, **kwargs
        )
        return results

    return _search_facts()


# ***

def generate_facts_table(controller, facts, show_duration=True, include_usage=False):
    """
    Create a nice looking table representing a set of fact instances.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances representing a single fact.
    """
    show_duration = show_duration or include_usage

    # If you want to change the order just adjust the dict.
    headers = {
        'key': _("Key"),
        'start': _("Start"),
        'end': _("End"),
        'activity': _("Activity"),
        'category': _("Category"),
        'tags': _("Tags"),
        'description': _("Description"),

    }
    columns = [
        'key', 'start', 'end', 'activity', 'category', 'tags', 'description',
    ]

    if show_duration:
        headers['delta'] = _("Duration")
        columns.append(_('delta'))

    header = [headers[column] for column in columns]

    TableRow = namedtuple('TableRow', columns)

    table = []

    n_row = 0
    # FIXME: tabulate is really slow on too many records, so bail for now
    #        rather than hang "forever", man.
    # 2018-05-09: (lb): Anecdotal evidence suggests 2500 is barely tolerable.
    #   Except it overflows my terminal buffer? and hangs it? Can't even
    #   Ctrl-C back to life?? Maybe less than 2500. 1000 seems fine. Why
    #   would user want that many results on their command line, anyway?
    #   And if they want to process more records, they might was well dive
    #   into the SQL, or run an export command instead.
    row_limit = 1001

    for fact in facts:
        if include_usage:
            # It's tuple: the Fact, the count, and the span.
            #  _span = fact[2]  # Should be same/similar to what we calculate.
            # The count column was faked (static count), so the table
            # has the same columns as the act/cat/tag usage tables.
            assert fact[1] == 1
            fact = fact[0]
        n_row += 1
        if n_row > row_limit:
            break

        if fact.category:
            category = fact.category.name
        else:
            category = ''

        if fact.tags:
            tags = '#'
            tags += '#'.join(sorted([x.name + ' ' for x in fact.tags]))
        else:
            tags = ''

        if fact.start:
            fact_start = fact.start.strftime('%Y-%m-%d %H:%M')
        else:
            fact_start = _('<genesis>')
            controller.client_logger.warning(_('Fact missing start: {}').format(fact))

        if fact.end:
            fact_end = fact.end.strftime('%Y-%m-%d %H:%M')
        else:
            # FIXME: This is just the start of supporting open ended Fact in db.
            fact_end = _('<ongoing>')
            # So that fact.delta() returns something.
            fact.end = controller.now

        additional = {}
        if show_duration:
            additional['delta'] = fact.format_delta(style='')

        table.append(
            TableRow(
                key=fact.pk,
                activity=fact.activity.name,
                category=category,
                description=fact.description or '',
                tags=tags,
                start=fact_start,
                end=fact_end,
                **additional,
            )
        )

    return (table, header)

