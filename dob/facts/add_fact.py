# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
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

import random

from gettext import gettext as _

from dob_bright.termio import dob_in_user_exit

from dob_viewer.crud.fact_from_factoid import must_create_fact_from_factoid
from dob_viewer.crud.fix_times import mend_fact_timey_wimey
from dob_viewer.crud.interrogate import ask_user_for_edits

from .save_backedup import prompt_and_save_backedup

__all__ = (
    'add_fact',
)


# ***

def add_fact(
    controller,
    factoid,
    time_hint,
    use_carousel=False,
    edit_text=False,
    edit_meta=False,
    yes=False,
    dry=False,
):
    """
    Start or add a fact.

    Args:
        factoid (str): ``factoid`` detailing Fact to be added.
            See elsewhere for the factoid format.

        time_hint (str, optional): One of:
            | 'verify_none': Do not expect to find any time encoded in factoid.
            | 'verify_both': Expect to find both start and end times.
            | 'verify_start': Expect to find just one time, which is the start.
            | 'verify_end': Expect to find just one time, which is the end.
            | 'verify_then': Optional time is new start; and either extend
            ongoing fact to new start, or back-fill interval gap.
            | 'verify_still': Optional time is new start; copy prev meta to new Fact;
            either extend ongoing fact, or back-fill interval gap.
            | 'verify_after': No time spec. Start new Fact at time of previous end.

        yes (bool, optional): If True, update other Facts changed by the new
            fact being added (affects other Facts' start/end/deleted attrs).
            If False, prompt user (i.e., using fancy interface built with
            python-prompt-toolkit) for each conflict.

        edit_meta (bool, optional): If True, prompt user for activity and/or
            category, if not indicated; and prompt user for tags. Shows
            MRU lists to try to make it easy for user to specify commonly
            used items.

    Returns:
        Nothing: If everything went alright. (Otherwise, will have exited.)
    """

    def _add_fact():
        new_fact = _create_fact()
        new_fact_or_two, conflicts = _mend_times(new_fact)
        edit_facts, orig_facts = _prepare_facts(new_fact_or_two)
        edit_fact = _add_conflicts(conflicts, edit_facts, orig_facts)
        _maybe_prompt_description(edit_fact)
        _maybe_prompt_actegory(edit_fact)
        saved_facts = _prompt_and_save(edit_facts, orig_facts)
        return saved_facts

    def _create_fact():
        # NOTE: factoid is an ordered tuple of args; e.g., sys.argv[2:], if
        #       sys.argv[0] is the executable name, and sys.argv[1] is command.
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
            controller, factoid, time_hint,
        )
        return new_fact

    def _mend_times(new_fact):
        # If there's an ongoing Fact, we might extend or squash it.
        # Also, if the new Fact overlaps existing Facts, those Facts'
        # times might be changed, and/or existing Facts might be deleted.
        try:
            new_fact_or_two, conflicts = mend_fact_timey_wimey(
                controller, new_fact, time_hint,
            )
        except ValueError as err:
            # (lb): I'm very indecisive.
            choices = [
                _("Not so fast!"),
                _("Cannawt!"),
                _("Unpossible!"),
                _("Insidious!"),
                _("Think again!"),
            ]
            msg = _('{} {}').format(random.choice(choices), err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        return new_fact_or_two, conflicts

    def _prepare_facts(new_fact_or_two):
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
        return edit_facts, orig_facts

    def _add_conflicts(conflicts, edit_facts, orig_facts):
        for edited, original in conflicts:
            edit_facts.append(edited)
            # (lb): This is the only place orig_facts is not [edit_fact.copy(), ...].
            orig_facts.append(original)
        edit_fact = edit_facts[0]
        return edit_fact

    def _maybe_prompt_description(edit_fact):
        if not edit_text:
            return

        # User wants to edit description first.
        ask_user_for_edits(
            controller,
            fact=edit_fact,
            always_ask=False,
            restrict_edit='description',
        )

    def _maybe_prompt_actegory(edit_fact):
        if not edit_meta:
            return

        ask_user_for_edits(
            controller,
            fact=edit_fact,
        )

    def _prompt_and_save(edit_facts, orig_facts):
        saved_facts = prompt_and_save_backedup(
            controller,
            edit_facts=edit_facts,
            orig_facts=orig_facts,
            use_carousel=use_carousel,
            yes=yes,
            dry=dry,
            progress=None,
        )
        return saved_facts

    return _add_fact()

