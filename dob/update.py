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

import click
import editor
import six

from .create import mend_facts_confirm_and_save_maybe

__all__ = ['edit_fact']


def edit_fact(controller, key):
    """"""
    def _edit_fact():
        old_fact = fact_from_key(key)
        edit_old_fact(old_fact)

    def fact_from_key(key):
        if not key:
            return None

        if key > 0:
            old_fact = controller.facts.get(pk=key)
        else:
            # FIXME/2018-06-10: (lb): This is crudely implemented, and
            # won't work in edges cases (e.g., if you add a fact, then
            # edit another fact, then `edit -1`, you'll edit the fact
            # you edited, and not the latest fact, as this feature should
            # work.
            offset = -1 - key
            old_fact = controller.facts.get_all(
                order='desc',
                limit=1,
                offset=offset,
                deleted=False,
            )
        return old_fact

    def edit_old_fact(old_fact):
        if old_fact is None:
            return

        # FIXME/2018-06-11: (lb): Wire --ask option. For now, just open editor.
        raw_fact = editor_interact(old_fact)
        time_hint = fact_time_hint(old_fact)
        new_fact = new_fact_from_factoid(raw_fact, old_fact, time_hint)
        echo_edited_fact(new_fact, old_fact)
        confirm_and_save(new_fact, time_hint)

    def editor_interact(old_fact):
        # FIXME/2018-06-11: (lb): Be explicit about str fcn. being called.
        contents = six.b(str(old_fact))
        result = editor.edit(contents=contents)
        # FIXME/2018-05-10: (lb): Is this py2 compatible?
        raw_fact = result.decode()
        return raw_fact

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
            (raw_fact,), time_hint=time_hint,
        )
        # FIXME/2018-06-10: (lb): Do we care about the error?

        # (lb): Start with the PK of the old fact. On save/update, the
        # store will see that the fact already exists, so it'll make a
        # new copy of the fact (with a new ID), and mark the old fact
        # 'deleted' (thereby acting like a Wiki -- never delete!).
        new_fact.pk = old_fact.pk

        return new_fact

    def echo_edited_fact(new_fact, old_fact):
        click.echo('An edited fact!: {}'.format(str(new_fact)))
        click.echo('\nThe diff!\n')
        click.echo(old_fact.friendly_diff(new_fact))

    def confirm_and_save(new_fact, time_hint):
        # FIXME/2018-05-13: (lb): I have not tested beyond this point!
        #   So dying young. I'll get around to this soon, probably the
        #   next time I run the edit command and see it die horribly here.
        raise NotImplementedError

        mend_facts_confirm_and_save_maybe(
            controller, new_fact, time_hint, yes=False, dry=False,
        )

    _edit_fact()

