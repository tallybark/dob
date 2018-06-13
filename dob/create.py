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
import json
from pyoiler_inflector import Inflector

from nark import Fact
from nark.helpers import time as time_helpers
from nark.helpers.colored import fg, attr
from nark.helpers.parsing import ParserException

from . import interrogate
from .helpers import click_echo_and_exit

__all__ = [
    'add_fact',
    'stop_fact',
    'cancel_fact',
    'mend_facts_confirm_and_save_maybe',
    'mend_facts_times',
    'save_facts_maybe',
    # Private:
    #   'must_confirm_fact_edits',
    #   'must_create_fact_from_factoid',
]


def add_fact(
    controller,
    factoid,
    time_hint,
    ask=False,
    yes=False,
    dry=False,
):
    """
    Start or add a fact.

    Args:
        factoid (text_type): ``factoid`` detailing Fact to be added.
            See elsewhere for the factoid format. At a minimum, the
            string must must specify an Activity name.

        time_hint (text_type, optional): One of:
            'verify_none': Do not expect to find any time encoded in factoid.
            'verify_both': Expect to find both start and end times.
            'verify_start': Expect to find just one time, which is the start.
            'verify_end': Expect to find just one time, which is the end.

        yes (bool, optional): If True, update other Facts changed by the new
            fact being added (affects other Facts' start/end/deleted attrs).
            If False, prompt user (i.e., using fancy interface built with
            python-prompt-toolkit) for each conflict.

        ask (bool, optional): If True, prompt user for activity and/or
            category, if not indicated; and prompt user for tags. Shows
            MRU lists to try to make it easy for user to specify commonly
            used items.

    Returns:
        Nothing: If everything went alright. (Otherwise, will have exited.)
    """

    # NOTE: factoid is an ordered tuple of args; e.g., sys.argv[2:], if
    #       sys,argv[0] is the executable name, and sys.argv[1] is command.
    #       Because dob is totes legit, it does not insist that the user
    #       necessary quote anything on the command line, but it does not
    #       insist not, either, so factoid might have just one element (a
    #       string) containing all the information; or factoid might be a
    #       list of strings that need to be parsed and reassembled (though
    #       not necessarily in that order).
    #
    #         tl;dr: factoid is a tuple of 1+ strings that together specify the Fact.

    fact = must_create_fact_from_factoid(
        controller, factoid, time_hint, ask,
    )

    if ask:
        interrogate.ask_user_for_edits(controller, fact)

    mend_facts_confirm_and_save_maybe(controller, fact, time_hint, yes, dry)


def mend_facts_confirm_and_save_maybe(controller, fact, time_hint, yes, dry):
    # Fill in the start and, or, end times, maybe.
    # Possibly correct the times of 2 other Facts!
    # Or die if too many Facts are abound tonight.
    conflicts = mend_facts_times(controller, fact, time_hint)

    # Ask user what to do about conflicts/edits.
    must_confirm_fact_edits(controller, conflicts, yes, dry)

    save_facts_maybe(controller, fact, conflicts, dry)


# ***


def must_create_fact_from_factoid(
    controller, factoid, time_hint, ask,
):

    def _must_create_fact_from_factoid(
        controller, factoid, time_hint, ask,
    ):
        separators = must_prepare_factoid_item_separators(controller)
        try:
            fact, err = Fact.create_from_factoid(
                factoid,
                time_hint=time_hint,
                separators=separators,
                lenient=ask,
            )
            if err:
                controller.client_logger.info(str(err))
        except ParserException as err:
            msg = _('Oops! {}').format(err)
            controller.client_logger.error(msg)
            click_echo_and_exit(msg)
        return fact

    def must_prepare_factoid_item_separators(controller):
        try:
            separators = json.loads(controller.client_config['separators'])
        except json.decoder.JSONDecodeError as err:
            msg = _(
                "The 'separators' config value is not valid JSON: {}"
            ).format(err)
            controller.client_logger.error(msg)
            click_echo_and_exit(msg)
        return separators

    # ***

    return _must_create_fact_from_factoid(controller, factoid, time_hint, ask)


# ***


# MAYBE/2018-06-09: (lb): Need to move any of this to LIB for other packages to use?
def mend_facts_times(controller, fact, time_hint):
    """"""

    def _mend_facts_times(controller, fact, time_hint):
        # The fact is considered "temporary", or open, if the user did not
        # specify an end time, and if there's no Fact following the new Fact.
        leave_open = new_fact_fill_now(fact, time_hint, controller.now)
        conflicts = controller.facts.insert_forcefully(fact)

        # Note that end may be None for ongoing Fact.
        # Verify that start > end, if neither are None.
        time_helpers.validate_start_end_range((fact.start, fact.end))

        if leave_open:
            fact.end = None

        return conflicts

    def new_fact_fill_now(fact, time_hint, now):
        # We might temporarily set the end time to look for overlapping
        # facts, so remember if we need to leave the fact open.
        leave_open = False

        if (time_hint == 'verify_none'):
            assert not fact.start
            assert not fact.end
            fact.start = now
            leave_open = True
        elif (time_hint == 'verify_both'):
            assert fact.start and fact.end
        elif (time_hint == 'verify_start'):
            assert not fact.end
            leave_open = True
            if not fact.start:
                fact.start = now
        elif (time_hint == 'verify_end'):
            assert not fact.start
            if not fact.end:
                fact.end = now

        return leave_open

    # ***

    return _mend_facts_times(controller, fact, time_hint)


# ***


def must_confirm_fact_edits(controller, conflicts, yes, dry):
    """"""

    def _must_confirm_fact_edits(conflicts, yes, dry):
        conflicts = cull_stopped_ongoing(conflicts)
        if not conflicts:
            return
        yes = yes or dry
        if not yes:
            echo_confirmation_banner(conflicts)
        n_conflict = 0
        for edited_fact, original in conflicts:
            n_conflict += 1
            if not yes:
                echo_confirmation_edited(
                    n_conflict, edited_fact, original,
                )
            else:
                controller.client_logger.debug(
                    _('Editing fact: {}').format(edited_fact)
                )

    def cull_stopped_ongoing(conflicts):
        return [con for con in conflicts if 'stopped' not in con[0].dirty_reasons]

    def echo_confirmation_banner(conflicts):
        click.echo()
        click.echo(_(
            'Found {}{}{} {}. '
            '{}Please confirm the following changes:{}'
            .format(
                fg('magenta'), len(conflicts), attr('reset'),
                Inflector.pluralize('conflict', len(conflicts) != 1),
                attr('underlined'), attr('reset'),
            )
        ))

    def echo_confirmation_edited(n_conflict, edited_fact, original):
        click.echo()
        click.confirm(
            text=_('Conflict #{}\n-----------\n{}\nReally edit fact?').format(
                n_conflict,
                original.friendly_diff(edited_fact),
            ),
            default=False,
            abort=True,
            # prompt_suffix=': ',
            # show_default=True,
            # err=False,
        )

    # ***

    _must_confirm_fact_edits(conflicts, yes, dry)


# ***


def save_facts_maybe(controller, fact, conflicts, dry):
    """"""

    def _save_facts_maybe(controller, fact, conflicts, dry):
        if conflicts and dry:
            echo_dry_run()
        for edited_fact, original in conflicts:
            if not dry:
                save_fact(controller, edited_fact, dry)
                if 'stopped' in edited_fact.dirty_reasons:
                    echo_ongoing_completed(controller, edited_fact)
            else:
                click.echo(original.friendly_diff(edited_fact))

        save_fact(controller, fact, dry)

    def echo_dry_run():
        click.echo()
        click.echo('{}Dry run! These facts will be edited{}:\n '.format(
            attr('underlined'),
            attr('reset'),
        ))

    def save_fact(controller, fact, dry):
        if not dry:
            controller.client_logger.debug('{}: {}'.format(_('Save fact'), fact))
            try:
                fact = controller.facts.save(fact)
            except Exception as err:
                click_echo_and_exit(str(err))
        else:
            echo_fact(fact)

    # ***

    _save_facts_maybe(controller, fact, conflicts, dry)


def echo_fact(fact):
    click.echo('{}Dry run! New fact{}:\n '.format(
        attr('underlined'),
        attr('reset'),
    ))
    click.echo('{}{}{}{}'.format(
        fg('steel_blue_1b'),
        attr('bold'),
        fact.friendly_str(description_sep='\n\n'),
        attr('reset'),
    ))


# ***


def stop_fact(controller):
    """
    Stop current 'ongoing fact' and save it to the backend.

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


# ***


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
    """"""
    def _echo_ongoing_completed():
        colorful = controller.client_config['term_color']
        leader = _('Completed: ')
        cut_width = width_avail(len(leader))
        echo_fact(leader, colorful, cut_width)

    def width_avail(leader_len):
        term_width = click.get_terminal_size()[0]
        width_avail = term_width - leader_len
        return width_avail

    def echo_fact(leader, colorful, cut_width):
        click.echo(
            leader +
            fact.friendly_str(
                shellify=False,
                description_sep=': ',

                # FIXME/2018-06-10: (lb): fact being saved as UTC
                localize=True,

                colorful=colorful,

                # FIXME/2018-06-12: (lb): Too wide (wraps to next line);
                # doesn't account for leading fact parts (times, act@gory, tags).
                cut_width=cut_width,

                show_elapsed=True,
            )
        )

    _echo_ongoing_completed()

