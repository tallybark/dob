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

from gettext import gettext as _

from dob_bright.termio import (
    attr,
    click_echo,
    echo_block_header,
    highlight_value
)
from dob_bright.termio.crude_progress import CrudeProgress

from .echo_fact import echo_fact, write_fact_block_format
from .simple_prompts import mend_facts_confirm_and_save_maybe


__all__ = (
    'prompt_and_save_confirmer',
)


# ***

def prompt_and_save_confirmer(
    controller,
    edit_facts=None,
    orig_facts=None,
    backup_callback=None,
    file_out=None,
    rule='',
    yes=False,
    dry=False,
    progress=None,
    **kwargs,
):
    """"""
    progress = CrudeProgress(enabled=True) if progress is None else progress

    def _prompt_and_save():
        saved_facts = []
        try:
            saved_facts = persist_facts()
        finally:
            cleanup_files()
        return saved_facts

    def cleanup_files():
        # (lb): Click also closes; or we can hit it first.
        if file_out and not dry:
            file_out.close()

    # ***

    def persist_facts():
        if not edit_facts:
            return
        record_edited_facts()
        celebrate()

    def record_edited_facts():
        task_descrip = _('Saving facts')
        if progress is not None:
            term_width, dot_count, fact_sep = progress.start_crude_progressor(
                task_descrip,
            )

        new_and_edited = []

        other_edits = {fact.pk: fact for fact in edit_facts}

        for idx, fact in enumerate(edit_facts):
            if progress is not None:
                term_width, dot_count, fact_sep = progress.step_crude_progressor(
                    task_descrip, term_width, dot_count, fact_sep,
                )

            is_first_fact = idx == 0
            is_final_fact = idx == (len(edit_facts) - 1)
            fact_pk = fact.pk
            new_and_edited += persist_fact(
                fact, other_edits, is_first_fact, is_final_fact,
            )
            # If an existing Fact:
            #   - the pk is the same; and
            #   - the saved Fact is marked deleted, and a new one is created,
            #      or saved Fact is not marked deleted if it was ongoing Fact.
            # But if a new Fact, pk was < 0, now it's None, and new fact pk > 0.
            # Once saved, rely on Fact in store for checking conflicts.

            # If fact existed, fact.pk; else, fact_pk < 0 is in-app temp. ID.
            del other_edits[fact.pk is not None and fact.pk or fact_pk]

        assert len(other_edits) == 0

        # NOTE: It's up to the caller to ensure controller.post_process called,
        #       either via @post_processor, or by calling it directly.

        progress and progress.click_echo_current_task('')

    def persist_fact(fact, other_edits, is_first_fact, is_final_fact):
        new_and_edited = [fact, ]
        if not dry:
            # If user did not specify an output file, save to database
            # (otherwise, we may have been maintaining a temporary file).
            if not file_out:
                new_and_edited = persist_fact_save(
                    fact, is_final_fact, other_edits,
                )
            else:
                write_fact_block_format(file_out, fact, rule, is_first_fact)
        else:
            echo_block_header(_('Fresh Fact!'))
            click_echo()
            echo_fact(fact)
            click_echo()
        return new_and_edited

    # ***

    def persist_fact_save(fact, is_final_fact, other_edits):
        # (lb): This is a rudimentary check. I'm guessing other code
        # will prevent user from editing old Fact and deleting its
        # end, either creating a second ongoing Fact, OR, more weirdly,
        # creating an ongoing Fact that has closed Facts after it!
        # 2018-07-05/TEST_ME: Test previous comment: try deleting end of old Fact.
        # FIXME: Do we care to confirm if is_final_fact is indeed latest ever? Meh?
        time_hint = 'verify_both' if not is_final_fact else 'verify_last'
        new_and_edited = mend_facts_confirm_and_save_maybe(
            controller, fact, time_hint, other_edits, yes=yes, dry=dry,
        )
        return new_and_edited

    # ***

    def celebrate():
        if not edit_facts:
            return
        click_echo('{}{}{}! {}'.format(
            attr('underlined'),
            _('Voilà'),
            attr('reset'),
            _('Saved {} facts.').format(highlight_value(len(edit_facts))),
        ))

    # ***

    return _prompt_and_save()

