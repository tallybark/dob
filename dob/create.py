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
import glob
import json
import os
import pygments.lexers
import traceback
from inflector import Inflector, English
from io import open

# FIXME: Move this to an intermediate carousel-managing class.
#        (lb): That is, decouple PPT implementation from create.py?
from prompt_toolkit.lexers import PygmentsLexer

from nark.helpers.colored import fg, attr
from nark.helpers.parsing import ParserException

from . import interrogate
from .cmd_common import echo_block_header
from .cmd_config import get_appdirs_subdir_file_path, AppDirs
from .helpers import (
    click_echo,
    dob_in_user_exit,
    dob_in_user_warning,
    echo_fact,
    highlight_value
)
from .helpers.crude_progress import CrudeProgress
from .helpers.fix_times import (
    mend_facts_times,
    must_complete_times,
    reduce_time_hint,
    unite_and_stretch
)
from .helpers.path import compile_and_eval_source
from .traverser import various_lexers
from .traverser import various_styles
from .traverser.placeable_fact import PlaceableFact

__all__ = [
    'add_fact',
    'cancel_fact',
    'mend_facts_confirm_and_save_maybe',
    'stop_fact',
    # Private:
    #   'echo_ongoing_completed',
    #   'mend_fact_timey_wimey',
    #   'must_confirm_fact_edits',
    #   'must_create_fact_from_factoid',
    #   'save_facts_maybe',
]


def add_fact(
    controller,
    factoid,
    time_hint,
    ask=False,
    yes=False,
    dry=False,
    use_carousel=True,
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
            'verify_then': Optional time is new start; and either extend
                            ongoing fact to new start, or back-fill interval gap.
            'verify_still': Optional time is new start; copy prev meta to new Fact;
                            either extend ongoing fact, or back-fill interval gap.
            'verify_after': No time spec. Start new Fact at time of previous end.

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

    # Make a new Fact from the command line input.
    new_fact = must_create_fact_from_factoid(
        controller, factoid, time_hint, ask,
    )

    # If there's an ongoing Fact, we might extend or squash it.
    # Also, if the new Fact overlaps existing Facts, those Facts'
    # times might be changed, and/or existing Facts might be deleted.
    new_fact_or_two, conflicts = mend_fact_timey_wimey(
        controller, new_fact, time_hint,
    )

    edit_facts = []
    orig_facts = []
    new_fact_pk = -1
    for new_fact in new_fact_or_two:
        # If ongoing was squashed, edited_fact.pk > 0, else < 0.
        # There might also be an extended filler gap Fact added.
        if new_fact.pk is None:
            new_fact.pk = new_fact_pk
            new_fact_pk -= 1
            edit_facts.append(new_fact)
        else:
            # The edited fact is in conflicts, and carousel will start on it.
            assert new_fact.pk > 0

    for edited, original in conflicts:
        edit_facts.append(edited)
        # (lb): This is the only place orig_facts is not [edit_fact.copy(), ...].
        orig_facts.append(original)

    if use_carousel:
        saved_facts = prompt_and_save(controller, edit_facts, orig_facts)
    else:
        edited_fact = edit_facts[0]
        interrogate.ask_user_for_edits(controller, edited_fact) if ask else None
        # Verify at least start time is set; end may or may not be set.
        time_hint = 'verify_last'
        saved_facts = mend_facts_confirm_and_save_maybe(
            controller, edited_fact, time_hint, other_edits={}, yes=yes, dry=dry,
        )

    return saved_facts


# ***

def mend_facts_confirm_and_save_maybe(
    controller, fact, time_hint, other_edits, yes, dry,
):
    """"""
    def _mend_facts_confirm_and_save_maybe():
        new_fact_or_two, conflicts = mend_fact_timey_wimey(
            controller, fact, time_hint, other_edits,
        )
        saved_facts = confirm_conflicts_and_save_all(new_fact_or_two, conflicts)
        return saved_facts

    def confirm_conflicts_and_save_all(new_fact_or_two, conflicts):
        """"""
        # Ask user what to do about conflicts/edits.
        ignore_pks = other_edits.keys()
        must_confirm_fact_edits(controller, conflicts, yes, dry)
        saved_facts = save_facts_maybe(
            controller, new_fact_or_two, conflicts, ignore_pks, dry,
        )
        return saved_facts

    return _mend_facts_confirm_and_save_maybe()


def mend_fact_timey_wimey(controller, fact, time_hint, other_edits={}):
    """"""
    def _mend_fact_timey_wimey():
        must_complete_time(controller, fact, other_edits)
        # Fill in the start and, or, end times, maybe.
        # Possibly correct the times of 2 other Facts!
        # Or die if too many Facts are abound tonight.
        conflicts = mend_facts_times(controller, fact, time_hint)
        # Resolve conflicts from store with other edited facts being saved.
        conflicts = rebuild_conflicts(fact, conflicts, other_edits)
        new_fact_or_two = unite_and_stretch_fact_per_conflicts(conflicts)
        return new_fact_or_two, conflicts

    def unite_and_stretch_fact_per_conflicts(conflicts):
        # On `to` and `then`, combine fact and latest.
        # Note that insert_forcefully will handle ``to`` for ongoing fact;
        # otherwise unite_and_stretch handles it for ended latest.
        if fact.deleted:
            return []
        return unite_and_stretch(controller, fact, time_hint, conflicts)

    def must_complete_time(controller, fact, other_edits):
        reset_end = fact.end is None
        if fact.end is None:
            fact.end = controller.now
        new_facts = [fact, ]
        must_complete_times(
            controller,
            new_facts,
            ongoing_okay=True,
            leave_blanks=True,
            other_edits=other_edits,
        )
        assert len(new_facts) == 1
        fact.end = None if reset_end else fact.end

    def rebuild_conflicts(fact, conflicts, other_edits):
        if not other_edits:
            return conflicts
        culled_conflicts = []
        for conflict in conflicts:
            verify_conflict(fact, conflict, other_edits, culled_conflicts)
        return culled_conflicts

    def verify_conflict(fact, conflict, other_edits, culled_conflicts):
        auto_edit, orig_fact = conflict
        assert auto_edit.pk == orig_fact.pk
        try:
            edit_fact = other_edits[orig_fact.pk]
        except KeyError:
            # Fact was not separately edited, so conflict from store stands.
            culled_conflicts.append(conflict)
        else:
            new_conflict = recheck_conflict(edit_fact, orig_fact)
            if new_conflict is not None:
                culled_conflicts.append(new_conflict)

    def recheck_conflict(edit_fact, orig_fact):
        # Both Facts should have a start, and only 1 may be unended.
        assert fact.start and edit_fact.start
        assert fact.end or edit_fact.end
        if edit_fact.end is None:
            # If edit_fact is ongoing, should start after fact.
            if edit_fact.start >= fact.end:
                return None
        elif fact.end is None:
            # If fact is ongoing, should start after edit_fact.
            if fact.start >= edit_fact.end:
                return None
        elif edit_fact.start == edit_fact.end:
            # Momentaneous can only happen on boundary.
            if (edit_fact.start <= fact.start) or (edit_fact.start >= fact.end):
                return None
        elif fact.start == fact.end:
            # Momentaneous can only happen on boundary.
            if (fact.start <= edit_fact.start) or (fact.start >= edit_fact.end):
                return None
        elif (edit_fact.end <= fact.start) or (edit_fact.start >= fact.end):
            # Both facts complete, neither is momentaneous, and ranges are distinct.
            return None
        # If we made it here, whoa! Unexpected time conflict after using carousel?
        new_conflict = (edit_fact, orig_fact, )
        return new_conflict

    # ***

    return _mend_fact_timey_wimey()


# ***

def must_create_fact_from_factoid(
    controller, factoid, time_hint, ask,
):

    def _must_create_fact_from_factoid(
        controller, factoid, time_hint, ask,
    ):
        separators = must_prepare_factoid_item_separators(controller)
        use_hint = reduce_time_hint(time_hint)
        try:
            fact, err = PlaceableFact.create_from_factoid(
                factoid=factoid,
                time_hint=use_hint,
                separators=separators,
                lenient=True,
            )
            controller.client_logger.info(str(err)) if err else None
        except ParserException as err:
            msg = _('Oops! {}').format(err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        fact_set_start_time_after_hack(fact, time_hint)
        return fact

    def must_prepare_factoid_item_separators(controller):
        sep_string = controller.client_config['separators']
        if not sep_string:
            return None
        try:
            separators = json.loads(sep_string)
        except json.decoder.JSONDecodeError as err:
            msg = _(
                "The 'separators' config value is not valid JSON: {}"
            ).format(err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        return separators

    # FIXME/DRY: See create.py/transcode.py.
    def fact_set_start_time_after_hack(fact, time_hint):
        if time_hint != "verify_after":
            return
        assert fact.start is None and fact.end is None
        # (lb): How's this for a hack!?
        fact.start = "+0"

    # ***

    return _must_create_fact_from_factoid(controller, factoid, time_hint, ask)


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
        n_confirms = 0
        for edited_fact, original in conflicts:
            n_conflict += 1
            if not yes:
                confirmed = echo_confirmation_edited(
                    n_conflict, edited_fact, original,
                )
                n_confirms += 1 if confirmed else 0
            else:
                controller.client_logger.debug(
                    _('Editing fact: {}').format(edited_fact)
                )
        if n_conflict != n_confirms:
            dob_in_user_exit(_("Please try again."))

    def cull_stopped_ongoing(conflicts):
        return [con for con in conflicts if 'stopped' not in con[0].dirty_reasons]

    def echo_confirmation_banner(conflicts):
        click.echo()
        click.echo(_(
            'Found {}{}{} {}. '
            '{}Please confirm the following changes:{}'
            .format(
                fg('magenta'), len(conflicts), attr('reset'),
                Inflector(English).conditional_plural(len(conflicts), 'conflict'),
                attr('underlined'), attr('reset'),
            )
        ))

    def echo_confirmation_edited(n_conflict, edited_fact, original):
        click.echo()
        # MAYBE:
        #   from .helpers.re_confirm import confirm
        #   confirmed = confirm()
        confirmed = click.confirm(
            text=_('Conflict #{}\n-----------\n{}\nReally edit fact?').format(
                n_conflict,
                original.friendly_diff(edited_fact),
            ),
            default=False,
            abort=False,
            # prompt_suffix=': ',
            # show_default=True,
            # err=False,
        )
        return confirmed

    # ***

    _must_confirm_fact_edits(conflicts, yes, dry)


# ***

def save_facts_maybe(controller, new_facts, conflicts, ignore_pks, dry):
    """"""

    def _save_facts_maybe(controller, new_facts, conflicts, ignore_pks, dry):
        new_and_edited = []
        if conflicts and dry:
            echo_dry_run()
        for edited_fact, original in conflicts:
            if not dry:
                new_and_edited += save_fact(controller, edited_fact, dry)
                if 'stopped' in edited_fact.dirty_reasons:
                    echo_ongoing_completed(controller, edited_fact)
            else:
                click.echo(original.friendly_diff(edited_fact))

        for fact in new_facts:
            new_and_edited += save_fact(controller, fact, dry, ignore_pks=ignore_pks)
        return new_and_edited

    def echo_dry_run():
        click.echo()
        click.echo('{}Dry run! These facts will be edited{}:\n '.format(
            attr('underlined'),
            attr('reset'),
        ))

    def save_fact(controller, fact, dry, ignore_pks=[]):
        if fact.pk and fact.pk < 0:
            fact.pk = None
        if fact.pk is None and fact.deleted:
            controller.client_logger.debug('{}: {}'.format(_('Dead fact'), fact))
            return []
        if not dry:
            controller.client_logger.debug('{}: {}'.format(_('Save fact'), fact))
            try:
                new_fact = controller.facts.save(fact, ignore_pks=ignore_pks)
            except Exception as err:
                traceback.print_exc()
                dob_in_user_exit(str(err))
        else:
            new_fact = fact
            echo_fact(fact)
        return [new_fact, ]

    # ***

    return _save_facts_maybe(controller, new_facts, conflicts, ignore_pks, dry)


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
    except KeyError:
        msg = _(
            "It doesn't look like there's any current Fact {}to{} stop."
        ).format(attr('italic'), attr('res_italic'))
        dob_in_user_exit(msg)
    else:
        echo_ongoing_completed(controller, fact, cancelled=False)
        return fact


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
        fact = controller.facts.cancel_current_fact(purge=purge)
    except KeyError:
        message = _("Nothing tracked right now. Not doing anything.")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    else:
        echo_ongoing_completed(controller, fact, cancelled=True)
        return fact


# ***

def echo_ongoing_completed(controller, fact, cancelled=False):
    """"""
    def _echo_ongoing_completed():
        colorful = controller.client_config['term_color']
        leader = _('Completed: ') if not cancelled else _('Cancelled: ')
        cut_width = width_avail(len(leader))
        completed_msg = echo_fact(leader, colorful, cut_width)
        controller.client_logger.debug(completed_msg)

    def width_avail(leader_len):
        term_width = click.get_terminal_size()[0]
        width_avail = term_width - leader_len
        return width_avail

    def echo_fact(leader, colorful, cut_width):
        completed_msg = (
            leader +
            fact.friendly_str(
                shellify=False,
                description_sep=': ',
                # FIXME: (lb): Implement localize.
                localize=True,
                colorful=colorful,
                cut_width=cut_width,
                show_elapsed=True,
            )
        )
        click_echo(completed_msg)
        return completed_msg

    _echo_ongoing_completed()

