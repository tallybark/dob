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

import traceback

from gettext import gettext as _

import click_hotoffthehamster as click
from inflector import English, Inflector

from dob_bright.termio import (
    attr,
    click_echo,
    dob_in_user_exit,
    fg,
)

from dob_viewer.crud.fix_times import mend_fact_timey_wimey

from .echo_fact import echo_fact

__all__ = (
    'mend_facts_confirm_and_save_maybe',
    # Private:
    #   'echo_ongoing_completed',
    #   'must_confirm_fact_edits',
    #   'save_facts_maybe',
)


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
            # (lb): This function is not used by the carousel -- only by
            # one-off CLI commands -- so blowing up here is perfectly fine.
            # (The carousel has its own error message display mechanism;
            #  and more importantly the carousel should never die,
            #  but should only ever be asked to die by the user.)
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
        #   from dob_viewer.ptkui.re_confirm import confirm
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
                    # This'll happen on one-off dob-to/dob-at/etc., but it
                    # will not happen on dob-import, e.g., if dob-import
                    # closes ongoing fact, it'll be saved normally, and it
                    # will not be passed herein as part of conflicts.
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
        # (lb): SIMILAR: edits_manager.save_edited_fact, create.save_fact.
        if fact.pk and fact.pk < 0:
            fact.pk = None
        if fact.pk is None and fact.deleted:
            controller.client_logger.debug('{}: {}'.format(_('Dead fact'), fact.short))
            return []
        if not dry:
            controller.client_logger.debug('{}: {}'.format(_('Save fact'), fact.short))
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

def echo_ongoing_completed(controller, fact, cancelled=False):
    """"""
    def _echo_ongoing_completed():
        colorful = controller.config['term.use_color']
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
            leader
            + fact.friendly_str(
                shellify=False,
                description_sep=': ',

                # FIXME: (lb): Implement localize.
                # FIXME/2018-06-10: (lb): fact being saved as UTC
                localize=True,

                colorful=colorful,

                # FIXME/2018-06-12: (lb): Too wide (wraps to next line);
                # doesn't account for leading fact parts (times, act@gory, tags).
                cut_width=cut_width,

                show_elapsed=True,
            )
        )
        click_echo(completed_msg)
        return completed_msg

    _echo_ongoing_completed()

