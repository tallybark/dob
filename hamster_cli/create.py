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
import sys
from gettext import gettext as _

import click
import inquirer

from hamster_lib import Activity, Category, Fact, Tag
from hamster_lib.helpers import time as time_helpers
from hamster_lib.helpers.colored import fg, attr
from hamster_lib.helpers.parsing import ParserException


__all__ = ['add_fact', 'cancel_fact', 'start_fact', 'stop_fact']


def add_fact(controller, factoid, time_hint, yes=False, ask=False):
    """
    Start or add a fact.

    Args:
        factoid: ``factoid`` containing information about the Fact to be started. As an absolute
            minimum this must be a string representing the 'activityname'.
        start (optional): When does the fact start?
        end (optional): When does the fact end?

    Returns:
        None: If everything went alright.

    Note:
        * Whilst it is possible to pass timeinformation as part of the ``factoid`` as
            well as dedicated ``start`` and ``end`` arguments only the latter will be represented
            in the resulting fact in such a case.
    """

    # FIXME: (lb): I'm not a big fan on inline methods, but it seems to be
    #        a common pattern in this codebase. Perhaps we could find a
    #        more elegant way to do this? (I don't like that the actual
    #        function code comes much further down, after the inline
    #        function definitions, because it's obvious it's there.)
    #        Can we at least do an inline function for the main function,
    #        and put that up here?

    # NOTE: factoid is an ordered tuple of args.

    def insert_factoid(controller, factoid, time_hint, yes, ask):
        # Parse the user's input.
        try:
            fact = Fact.create_from_raw_fact(
               factoid, time_hint=time_hint, lenient=ask,
            )
        except ParserException as err:
            msg = _('Failed to add factoid: {}').format(err)
            controller.client_logger.error(msg)
            click.echo(msg)
            sys.exit(1)

        if ask:
            fact.tags = new_fact_ask_tags(controller)
            fact.activity = new_fact_ask_act_cat(controller)

        # Fill in the start and, or, end times, maybe.
        # Possibly correct the times of 2 other Facts!
        # Or die if too many Facts are abound tonight.
        conflicts = mend_facts_times(controller, fact, time_hint)

        # Ask user what to do about conflicts/edits.
        confirm_fact_edits(conflicts, yes)

        # Finally, save the new fact. If we're not dead.
        # FIXME/2018-05-09: (lb): We should use a transaction!
        for edited_fact, _original in conflicts:
            save_fact(controller, edited_fact)
        save_fact(controller, fact)

    def new_fact_ask_tags(controller):
        # FIXME: (lb): The inquirer list doesn't work if more lines than
        #        screen height (it's unusable for me, seems to scroll,
        #        then jumps back; and I don't see the selection at all).
        choices = _choices_tags(controller, whitespace_ok=True)
        questions = [
            inquirer.Checkbox(
                'tags',
                message="What tags would you like to apply?",
                choices=choices,
            ),
        ]
        cbox = inquirer.prompt(questions)
        # The prompt returns a dict with one entry, keys with
        # name we gave it. See these as the tags, removing the
        # '@' prefix that we added previously for show.
        tags = [Tag(name=tag[1:]) for tag in cbox['tags']]
        return tags

    def new_fact_ask_act_cat(controller):
        magic_ask_me = '<Create new activity>'
        choices = _choices_activities(controller, whitespace_ok=True)
        choices.insert(0, magic_ask_me)
        questions = [
            inquirer.List(
                'act_cat',
                message="What activity@category would you like to use?",
                choices=choices[:20],
            ),
        ]
        cbox = inquirer.prompt(questions)

        if cbox['act_cat'] != magic_ask_me:
            act_name, cat_name = cbox['act_cat'].split('@', 1)
        else:
            questions = [inquirer.Text('activity', message="Activity")]
            answers = inquirer.prompt(questions)
            act_cat_names = answers['activity'].split('@', 1)
            act_name = act_cat_names[0]
            if len(act_cat_names) > 1:
                cat_name = act_cat_names[1]
            else:
                questions = [inquirer.Text('category', message="Category")]
                answers = inquirer.prompt(questions)
                cat_name = answers['category']

        activity = Activity(act_name.strip())
        if cat_name.strip():
            activity.category = Category(cat_name.strip())
        return activity

    def mend_facts_times(controller, fact, time_hint):
        now = datetime.datetime.now()
        leave_open = new_fact_fill_now(fact, time_hint, now)
        conflicts = controller.facts.insert_forcefully(fact)

        # Note that start/end may be None due to partial completion.
        # Verify that start > end, if neither are None.
        time_helpers.validate_start_end_range((fact.start, fact.end))

        if leave_open:
            fact.end = None

        return conflicts

    def new_fact_fill_now(fact, time_hint, now):
        # We might temporarily set the end time to look for overlapping
        # facts, so remember if we need to leave the fact open.
        leave_open = False

        if (time_hint == 'verify-none'):
            assert not fact.start
            assert not fact.end
            fact.start = now
        elif (time_hint == 'verify-both'):
            assert fact.start and fact.end
        elif (time_hint == 'verify-start'):
            assert not fact.end
            leave_open = True
            if not fact.start:
                fact.start = now
        elif (time_hint == 'verify-end'):
            assert not fact.start
            if not fact.end:
                fact.end = now

        return leave_open

    def confirm_fact_edits(conflicts, yes):
        if not conflicts:
            return
        if not yes:
            # FIXME: (lb): Pluralizer: "conflict(s)" / # FIXME: (lb): Add Inflector
            #        Inflector.pluralize('conflict', len(conflicts) != 1)
            click.echo(_(
                'Found {}{}{} conflict(s). {}Please confirm the following changes:{}'.format(
                    fg('magenta'), len(conflicts), attr('reset'),
                    attr('underlined'), attr('reset'),
                )
            ))
        n_conflict = 0
        for edited_fact, original in conflicts:
            n_conflict += 1
            if not yes:
                click.echo()
                click.confirm(
                    text='Conflict #{}\n-----------\n{}\nReally edit fact?'.format(
                        n_conflict,
                        #len(conflicts),
                        original.friendly_diff(edited_fact),
                    ),
                    default=False,
                    abort=True,
                    #prompt_suffix=': ',
                    #show_default=True,
                    #err=False,
                )
            else:
                controller.client_logger.debug(_('Editing fact: {}').format(edited_fact))

    def save_fact(controller, fact):
        controller.client_logger.debug('{}: {}'.format(_('Save fact'), fact))
        fact = controller.facts.save(fact)

    # The actual `def add_fact()` function:
    insert_factoid(controller, factoid, time_hint, yes, ask)


def start_fact(controller, raw_fact, start='', end=''):
    """
    Start or add a fact.

    Args:
        raw_fact: ``raw_fact`` containing information about the Fact to be started. As an absolute
            minimum this must be a string representing the 'activityname'.
        start (optional): When does the fact start?
        end (optional): When does the fact end?

    Returns:
        None: If everything went alright.

    Note:
        * Whilst it is possible to pass timeinformation as part of the ``raw_fact`` as
            well as dedicated ``start`` and ``end`` arguments only the latter will be represented
            in the resulting fact in such a case.
    """
    fact = Fact.create_from_raw_fact(raw_fact)

    # Explicit trumps implicit!
    if start:
        fact.start = time_helpers.parse_time(start)
    if end:
        fact.end = time_helpers.parse_time(end)

    if not fact.end:
        # We seem to want to start a new tmp fact
        # Neither the raw fact string nor an additional optional end time have
        # been passed.
        # Until we decide wether to split this into start/add command we use the
        # presence of any 'end' information as indication of the users intend.
        tmp_fact = True
    else:
        tmp_fact = False

    # We complete the facts times in both cases as even an new 'ongoing' fact
    # may be in need of some time-completion for its start information.

    # Complete missing fields with default values.
    # legacy hamster_cli seems to have a different fallback behaviour than
    # our regular backend, in particular the way 'day_start' is handled.
    # For maximum consistency we use the backends unified ``complete_timeframe``
    # helper instead. If behaviour similar to the legacy hamster-cli is desired,
    # all that seems needed is to change ``day_start`` to '00:00'.

    # The following is needed becauses start and end may be ``None``.
    if not fact.start:
        # No time information has been passed at all.
        fact.start = datetime.datetime.now()

    else:
        # We got some time information, which may be incomplete however.
        if not fact.end:
            end_date = None
            end_time = None
        else:
            end_date = fact.end.date()
            end_time = fact.end.time()

        timeframe = time_helpers.TimeFrame(
            fact.start.date(), fact.start.time(), end_date, end_time, None)
        fact.start, fact.end = time_helpers.complete_timeframe(timeframe, controller.config)

    if tmp_fact:
        # Quick fix for tmp facts. that way we can use the default helper
        # function which will autocomplete the end info as well.
        # Because of our use of ``complete timeframe our 'ongoing fact' may have
        # received an ``end`` value now. In that case we reset it to ``None``.
        fact.end = None

    controller.client_logger.debug(_(
        "New fact instance created: {fact}".format(fact=fact)
    ))
    fact = controller.facts.save(fact)


def stop_fact(controller):
    """
    Stop cucrrent 'ongoing fact' and save it to the backend.

    Returns:
        None: If successful.

    Raises:
        ValueError: If no *ongoing fact* can be found.
    """
    try:
        fact = controller.facts.stop_current_fact()
    except ValueError:
        message = _(
            "Unable to end current fact. Are you sure there is one?"
            "Try running `hamster current`"
        )
        raise click.ClickException(message)
    else:
        echo_ongoing_completed(controller, fact)




def cancel_fact(controller, purge=False):
    """
    Cancel current fact, either marking it deleted, or really removing it.

    Returns:
        None: If success.

    Raises:
        KeyErŕor: No *ongoing fact* can be found.
    """
    try:
        controller.facts.cancel_current_fact(purge=purge)
    except KeyError:
        message = _("Nothing tracked right now. Not doing anything.")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    else:
        message = _("Tracking canceled.")
        click.echo(message)
        controller.client_logger.debug(message)


# ***


def echo_ongoing_completed(controller, fact):
    colorful = controller.client_config['term_color']
    click.echo(
        _('Completed: ') +
        fact.friendly_str(
            shellify=False,
            description_sep=': ',

            # FIXME/2018-06-10: (lb): fact being saved as UTC
            localize=True,

            colorful=colorful,
            show_elapsed=True,
        )
    )

