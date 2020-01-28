# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

"""Fact Editing State Machine"""

from collections import namedtuple

from nark.items import Fact

from .facts_diff import FactsDiff

__all__ = (
    'FactDressed',
)


FactoidSource = namedtuple(
    'FactoidSource', ('line_num', 'line_raw'),
)


class FactDressed(Fact):
    """"""

    def __init__(
        self,
        *args,
        dirty_reasons=None,
        line_num=None,
        line_raw=None,
        **kwargs
    ):
        super(FactDressed, self).__init__(*args, **kwargs)
        # For tracking edits between store saves.
        self.dirty_reasons = dirty_reasons or set()
        # For identifying errors in the input.
        self.parsed_source = FactoidSource(line_num, line_raw)
        self.orig_fact = None
        # For Carousel (dob-viewer) navigation.
        self.next_fact = None
        self.prev_fact = None

    @property
    def short(self):
        friendly = (
            '0x{:12x} / 🏭 {} / {} to {:23} / prev: {:12x} / next: {:12x}'.format(
                id(self),
                self.pk is not None and '{:6d}'.format(self.pk) or '<None>',
                self.start_fmt_local,
                self.end_fmt_local or '..........now..........',
                self.prev_fact and id(self.prev_fact) or 0,
                self.next_fact and id(self.next_fact) or 0,
            )
        )
        return friendly

    def copy(self, *args, **kwargs):
        """
        """
        new_fact = super(FactDressed, self).copy(*args, **kwargs)
        new_fact.dirty_reasons = set(list(self.dirty_reasons))
        new_fact.parsed_source = self.parsed_source
        new_fact.orig_fact = self.orig_fact or self
        # SKIP: next_fact, prev_fact.
        return new_fact

    def friendly_diff(self, other, formatted=False, **kwargs):
        facts_diff = FactsDiff(self, other, formatted=formatted)
        return facts_diff.friendly_diff(**kwargs)

    def squash(self, other, squash_sep=''):
        def _squash():
            # (lb): The squash is a useful end user application feature for existing
            # facts, and I'm not sure what else it might be used for, so I'm putting
            # a bunch of asserts here to force you to re-read this comment when next
            # this code blows up because new usage and you realize you can assuredly
            # delete this comment and one or all of these assert and you will likely
            # be just fine.
            assert other.pk is None or other.pk < 0
            assert not self.deleted
            assert not other.deleted
            assert not other.split_from
            # When squashing, the first fact should have a start, but not an end.
            # And we do not care about other; it could have a start, or an end, or
            # neither.
            assert self.start
            assert not self.end

            self.end = other.start or other.end

            if other.activity_name or other.category_name:
                # (lb): MAYBE: Do we care that this is destructive?
                self.activity = other.activity

            self.tags_replace(self.tags + other.tags)

            description_squash(other, squash_sep)

            self.dirty_reasons.add('squash')
            if self.end:
                self.dirty_reasons.add('stopped')
                self.dirty_reasons.add('end')

            other.deleted = True
            # For completeness, and to make verification easier.
            other.start = self.start
            other.end = self.end

            other.dirty_reasons.add('deleted-squashed')

        def description_squash(other, squash_sep=''):
            if not other.description:
                return
            # (lb): Build local desc. copy, because setter stores None, never ''.
            new_description = self.description or ''
            new_description += squash_sep if new_description else ''
            new_description += other.description
            self.description = new_description
            other.description = None

        _squash()

    @classmethod
    def create_from_factoid(cls, factoid, *args, **kwargs):
        """
        """
        new_fact, err = super(FactDressed, cls).create_from_factoid(
            factoid, *args, **kwargs
        )
        if new_fact is not None:
            line_num = 1
            line_raw = factoid
            new_fact.parsed_source = FactoidSource(line_num, line_raw)
        return new_fact, err

    @property
    def dirty(self):
        # MAYBE/FIXME: Set dirty_reasons if fact.pk < 0, on new FactDressed.
        return (
            (self.unstored or len(self.dirty_reasons) > 0)
            and ('interval-gap' not in self.dirty_reasons)
        )

    # *** Linked list methods.

    @property
    def has_next_fact(self):
        return self.next_fact is not None

    @property
    def has_prev_fact(self):
        return self.prev_fact is not None

