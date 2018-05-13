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

import datetime
import os
import random
import re
import sys
from gettext import gettext as _

import click
from click.parser import split_arg_string

from hamster_lib import Fact
from hamster_lib.helpers.parsing import ParserMissingActivityException
from hamster_lib.helpers.parsing import ParserMissingDatetimeOneException
from hamster_lib.helpers.parsing import ParserMissingDatetimeTwoException

__all__ = ['tab_complete']

INSERT_COMMAND_TIME_HINT = {
    'on': 'verify-none',
    'now': 'verify-none',
    'at': 'verify-start',
    'to': 'verify-end',
    'until': 'verify-end',
    'from': 'verify-both',
}

def tab_complete(controller):
    def _complete_cmd(controller):
        args, incomplete = _do_complete()
        if len(args) < 1:
            return

        try:
            time_hint = INSERT_COMMAND_TIME_HINT[args[0]]
        except KeyError:
            # Not an add_fact command! Fall-back to Click's complete.
            return

        for item in _get_choices(args[1:], incomplete, time_hint):
            click.echo(item)

    # NOTE: (lb): This fcn. was copied from click/_bashcomplete.py::do_complete().
    #       Then it was modified.
    def _do_complete():
        try:
            cwords = split_arg_string(os.environ['COMP_WORDS'])
        except KeyError:
            controller.client_logger.error(_(
                'Expected environ "COMP_WORDS" not set.'
            ))
            sys.exit(1)
        try:
            cword = int(os.environ['COMP_CWORD'])
        except ValueError:
            # This should only happen if your testing the complete command.
            assert os.environ['COMP_CWORD'] == ''
            cword = 0
        args = cwords[1:cword]
        try:
            incomplete = cwords[cword]
        except IndexError:
            incomplete = ''
        return (args, incomplete)

    def _get_choices(args, incomplete, time_hint):
        choices = []
        try:
            fact = Fact.create_from_raw_fact(args, time_hint=time_hint)
        except ParserMissingDatetimeOneException as err:
            choices = _choices_datetimes(controller, incomplete, time_hint, err)
        except ParserMissingDatetimeTwoException as err:
            choices = _choices_datetimes(controller, incomplete, time_hint, err)
        except ParserMissingActivityException:
            # See if we should suggest tags, activities, or activity-categories.
            if (not incomplete) or (not re.match(r'''^['"]?[#@]''', incomplete)):
                choices = _choices_activities(
                    controller, incomplete, whitespace_ok=False,
                )
            else:
                choices = _choices_tags(
                    controller, incomplete, whitespace_ok=False,
                )
        else:
            choices = [
                'Now_You_Write_A_Description',
                'Where-do-hamsters-go-after-graduation?__Hamsterdam!',
            ]

        return choices

    # The shim to the inline main(), above.
    _complete_cmd(controller)

def _choices_datetimes(controller, incomplete, time_hint, parser_err):
    """Suggest times."""
    now = datetime.datetime.now()
    # Show friendly usage reminders.
    # - For 'verify-start' (hamster-at), show now and very recent times.
    # - For 'verify-end' (hamster-to-/-until), show now (and very recent).
    # - For 'verify-both', with show less freshly recent for start,
    #   and show more recent times for second, end time.
    # NOTE: We underscore because Bash complete splits words,
    #       and thankfully the friendly `dateparser` understand this
    #       (for the most part; e.g., 'three years ago' works, but
    #       not 'three_years_ago', though '3_years_ago' works, go figure).
    friendly_at_hints = [
        '10_minutes_ago',
        '5_seconds_ago',
        'at_1_pm',
        'an_hour_ago',
        'noon',
        'midnight',
    ]
    friendly_from_hints = [
        #'yesterday at 3 PM',
        'yesterday_at_3_PM',
        #'one week ago',
        '1_week_ago',
        #'three years ago',
        '3_years_ago',
        #'Monday at 16:44',
        'Monday_at_16:44',
        'at_noon'
        #'last week at midnight',
        '1_week_ago_at_midnight',
        # Hahaha, futuristic!
        'tomorrow',
    ]
    random.shuffle(friendly_at_hints)
    random.shuffle(friendly_from_hints)

    if time_hint == 'verify-start':
        # What the heck, show just one friendly date example, randomly selected..
        #friendly_hint = [random.choices(friendly_at_hints)]
        friendly_hint = friendly_at_hints[:2]
    elif time_hint == 'verify-end':
        friendly_hint = ['now']
    elif time_hint == 'verify-both':
        if isinstance(parser_err, ParserMissingDatetimeOneException):
            #friendly_hint = [random.choice(friendly_from_hints)]
            friendly_hint = friendly_from_hints[:2]
        else:
            assert isinstance(parser_err, ParserMissingDatetimeTwoException)
            #friendly_hint = [random.choice(friendly_at_hints)]
            friendly_hint = friendly_at_hints[:2]
            friendly_hint.append('now')
    choices = [
        now.strftime('%Y-%m-%d'),
        now.strftime('%H:%M'),
        # Bash will split the completion word in a space,
        # so use \S+ form of YYYY-MM-DD and %H:M.
        # MEH: dateparser recognizes almost any delimiter
        # between the YYYY-MM-DD and the %H:%M, except
        # '-' and '+' indicate time zone. 'T' seems fine.
        now.strftime('%Y-%m-%dT%H:%M'),
    ]
    choices += friendly_hint
    if incomplete:
        choices = [
            ch for ch in choices if not incomplete or ch.startswith(incomplete)
        ]
    #elif len(args) > 0:
    #    choices = [ch for ch in choices if ch.startswith(args[-1])]
    return choices

def _choices_tags(controller, incomplete='', whitespace_ok=False):
    """Suggest tags."""
    # Grab the last 20 or so tags used (by Facts, chronologically),
    # and also the most used (top ten) 10 or so tags used by all Facts.
    # FIXME: Make these limits settable.


    tags_counts = controller.tags.get_all_by_usage(sort_col='start', limit=21)
    tags_counts += controller.tags.get_all_by_usage(sort_col='usage', limit=13)

    choices = [
        '@{}'.format(tag.name) for tag, _uses
        in tags_counts if not incomplete or tag.name.startswith(incomplete[1:])
    ]
    # MEH: We cull, even though we set limit above, so total count might be even smaller.
    #   (We could solve at the SQL query level, but who wants to go to the trouble?)
    if not whitespace_ok:
        choices = [tag for tag in choices if ' ' not in tag]
    return choices

def _choices_activities(controller, incomplete='', whitespace_ok=False):
    """Suggest activities."""
    acty = controller.activities.get_all_by_usage(sort_col='start')
    choices = [
        '{}@{}'.format(
            act.name, act.category.name if act.category else ''
        ) for act, count in acty
    ]
    # (lb): Bash complete doesn't handle spaces well, so ignore
    # those activities@categories with and spaces.
    if not whitespace_ok:
        choices = [atc for atc in choices if ' ' not in atc]
    if incomplete:
        choices = [atc for atc in choices if atc.startswith(incomplete)]
    max_choices = 50
    if len(choices) > max_choices:
        choices = random.sample(choices, max_choices)
    return choices

