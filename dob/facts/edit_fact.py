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

import click_hotoffthehamster as click

from dob_bright.termio import dob_in_user_exit

from dob_viewer.crud.interrogate import ask_edit_with_editor, ask_user_for_edits

from .save_backedup import prompt_and_save_backedup
from .simple_prompts import mend_facts_confirm_and_save_maybe

__all__ = ('edit_fact_by_pk', )


def edit_fact_by_pk(
    controller,
    key,
    use_carousel=True,
    edit_text=False,
    edit_meta=False,
):
    """"""
    def _edit_fact_by_pk():
        old_fact = fact_from_key(key)
        if old_fact is None:
            return None
        unedited = old_fact.copy()
        # Pre-run Awesome Prompt and/or $EDITOR.
        # Then run the Interactive Editor Carousel, the star
        # of the show; or show the $EDITOR if nothing else done.
        # FIXME/2019-11-23: (lb): add_fact does $EDITOR, then Awesome.
        #                   - Which way is best? Make if configurable!!
        if edit_meta:
            _prompter = ask_user_for_edits(  # noqa: F841
                controller,
                # MAYBE: rename old_fact
                # fact=edit_fact,
                fact=old_fact,
                always_ask=True,
                # (lb): If we leave restrict_edit alone, the prompter will
                # prompt for act@gory, then tags, and description (show editor).
                # Otherwise, we could just ask for, e.g., act@gory, say:
                #   restrict_edit='actegory',
            )
            # FIXME: Missing diff with old Fact to see if edited (and tell user)
            #    and missing save Fact.
        if edit_text:
            _prompter = ask_user_for_edits(  # noqa: F841
                controller,
                # MAYBE: rename old_fact
                # fact=edit_fact,
                fact=old_fact,
                always_ask=True,
                restrict_edit='description',
            )
            # FIXME: Missing diff with old Fact to see if edited (and tell user)
            #    and missing save Fact.
        if use_carousel:
            edited_facts = edit_old_fact(old_fact)
        elif not edit_meta and not edit_text:
            edited_facts = edit_old_factoid(old_fact)
        elif old_fact != unedited:
            # So @post_processor get proper list of edited facts,
            # we have to check if really edited.
            edited_facts = [old_fact]
        else:
            edited_facts = []
        return edited_facts

    def fact_from_key(key):
        if not key:
            # (lb): This had been a happy path, e.g.,:
            #   return None
            # but really the caller should verify first, eh.
            assert False

        if key > 0:
            return fact_from_key_pk(key)
        else:
            return fact_from_key_relative(key)

    def fact_from_key_pk(key):
        try:
            old_fact = controller.facts.get(pk=key)
            return old_fact
        except KeyError:
            dob_in_user_exit(
                _("No fact found with ID “{0}”.").format(key)
            )

    def fact_from_key_relative(key):
        # FIXME/2018-06-10: (lb): This is crudely implemented, and won't
        # work in edges cases (e.g., if you add a fact, then edit another
        # fact, then `edit -1`, you'll edit the fact you edited, and not
        # the latest fact, as this feature should work.
        offset = -1 - key
        old_facts = controller.facts.get_all(
            sort_order='desc',
            limit=1,
            offset=offset,
            deleted=False,
        )
        return old_facts[0] if old_facts else None

    # ***

    def edit_old_fact(old_fact):
        saved_facts = prompt_and_save_backedup(
            controller,
            edit_facts=[old_fact],
            # (lb): The whole point on dob-edit is to fire up the Carousel.
            use_carousel=True,
            # MEH/2019-02-01: (lb) Support --yes or --dry on dob-edit?
            yes=False,
            dry=False,
        )
        return saved_facts

    # ***

    def edit_old_factoid(old_fact):
        raw_fact = editor_interact(old_fact)
        time_hint = fact_time_hint(old_fact)
        new_fact = new_fact_from_factoid(raw_fact, old_fact, time_hint)
        echo_edited_fact(new_fact, old_fact)
        new_and_edited = confirm_and_save(new_fact, time_hint)
        return new_and_edited

    def editor_interact(old_fact):
        """Presents user with their EDITOR displaying the Factoid text.
        """
        # So that the user can edit act@gory and tags, and not solely
        # the description, marshal the Fact to a factoid string and
        # let the user edit that.
        old_raw_fact = old_fact.friendly_str(
            shellify=False,
            description_sep='\n\n',
            localize=True,
            colorful=False,
            show_elapsed=False,
        )

        # MAYBE/2020-01-28: Give user option of using dob-prompt to edit
        # act@gory and tags, then the description, e.g., something like
        # this?:
        #
        #   # MAYBE/2019-11-23: Call ask_user_for_edits instead?
        #                       What happens on active Fact that has body?
        #   __prompter = ask_user_for_edits(
        #       controller,
        #       fact=old_fact,
        #       always_ask=True,
        #       restrict_edit='description',
        #   )

        new_raw_fact = ask_edit_with_editor(controller, old_fact, old_raw_fact)

        if old_raw_fact == new_raw_fact:
            dob_in_user_exit(
                _("Nothing changed! New Fact same as the old Fact.")
            )

        return new_raw_fact

    def fact_time_hint(old_fact):
        if old_fact.start and old_fact.end:
            time_hint = 'verify_both'
        else:
            assert old_fact.start
            time_hint = 'verify_start'
        return time_hint

    def new_fact_from_factoid(raw_fact, old_fact, time_hint):
        # NOTE: Parser expects Iterable of input parts.
        new_fact, __err = old_fact.create_from_factoid(
            (raw_fact,),
            time_hint=time_hint,  # Either 'verify_both' or 'verify_start'.
            lenient=True,
        )
        # FIXME/2018-06-10: (lb): Do we care about the error?

        # (lb): Start with the PK of the old fact. On save/update, the
        # store will see that the fact already exists, so it'll make a
        # new copy of the fact (with a new ID), and mark the old fact
        # 'deleted' (thereby acting like a Wiki -- never delete!).
        new_fact.pk = old_fact.pk

        return new_fact

    def echo_edited_fact(new_fact, old_fact):
        if new_fact == old_fact:
            dob_in_user_exit(
                _("Nothing changed! New Fact same as old Fact.")
            )

        click.echo('An edited fact!: {}'.format(str(new_fact)))
        click.echo('\nThe diff!\n')
        click.echo(old_fact.friendly_diff(new_fact))

    def confirm_and_save(new_fact, time_hint):
        new_and_edited = mend_facts_confirm_and_save_maybe(
            controller,
            new_fact,
            time_hint,
            other_edits={},
            yes=False,
            dry=False,
        )
        return new_and_edited

        # ***

    return _edit_fact_by_pk()

