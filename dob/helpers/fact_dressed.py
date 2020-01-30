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

from nark.items.fact import Fact

from .emphasis import colorize, set_coloring
from .facts_diff import FactsDiff
from .ppt_markup import namilize

__all__ = (
    'FactDressed',
    # PRIVATE:
    #  'FactoidSource',
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

    # ***

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

    # ***

    def copy(self, *args, **kwargs):
        """
        """
        new_fact = super(FactDressed, self).copy(*args, **kwargs)
        new_fact.dirty_reasons = set(list(self.dirty_reasons))
        new_fact.parsed_source = self.parsed_source
        new_fact.orig_fact = self.orig_fact or self
        # SKIP: next_fact, prev_fact.
        return new_fact

    # ***

    def friendly_diff(self, other, formatted=False, **kwargs):
        facts_diff = FactsDiff(self, other, formatted=formatted)
        return facts_diff.friendly_diff(**kwargs)

    # ***

    def friendly_str(self, *args, colorful=False, **kwargs):
        was_coloring = set_coloring(colorful)
        friendly_str = super(FactDressed, self).friendly_str(*args, **kwargs)
        set_coloring(was_coloring)
        return friendly_str

    def oid_colorize(self, oid_part, oid_text):
        """Stylizes parts of the Factoid with color and emphasis.
        """
        # FIXME: Turn this into config. (And check BonW vs WonB.)
        lookup = {
            'pk': ('grey_78'),
            'act@gory': ('cornflower_blue', 'bold', 'underlined'),
            '#': ('grey_78'),
            'tag': ('dark_olive_green_1b'),
            '#tag': ('underlined'),
            'start': ('sandy_brown'),
            'end': ('sandy_brown'),
            'to': ('grey_85'),
            'duration': ('grey_78'),
        }
        colorized = colorize(oid_text, *lookup[oid_part])
        return colorized

    # ***

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

    # ***

    @classmethod
    def create_from_factoid(cls, factoid, *args, **kwargs):
        """Creates a new Fact from Factoid text, and sets bulk import metadata.
        """
        new_fact, err = super(FactDressed, cls).create_from_factoid(
            factoid, *args, **kwargs
        )
        if new_fact is not None:
            line_num = 1
            line_raw = factoid
            new_fact.parsed_source = FactoidSource(line_num, line_raw)
        return new_fact, err

    # ***

    @property
    def dirty(self):  # MAYBE: Rename: positive()?
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

    # *** Presentation concerns.

    def oid_tags(self, *args, colorful=False, **kwargs):
        was_coloring = set_coloring(colorful)
        friendly_tags = super(FactDressed, self).oid_tags(*args, **kwargs)
        set_coloring(was_coloring)
        return friendly_tags

    # NOTE/2020-01-27: (lb): Returns PPT tuple, not something dob knows about.
    # - We could move this method to dob-viewer, to truly decouple.
    #   But then dob-viewer needs to override FactDressed (self.store.fact_cls).
    #   (For now, I'm happy this method at least made it out of nark!)
    def tags_tuples(
        self,
        hashtag_token='#',
        quote_tokens=False,
        colorful=False,
        underlined=False,
        split_lines=False,
    ):

        def format_tagname(tag):
            # FIXME/2020-01-28: (lb): make underline and colors configable.
            underline_fmt = ' underline' if colorful else ''
            tagged = []
            #
            tclss_fmt = ' class:tag-{}'.format(namilize(tag.name))
            #
            token_fmt = 'fg: ' if (colorful or underline_fmt) else ''
            token_fmt += '#C6C6C6' if colorful else ''
            token_fmt += underline_fmt
            token_fmt += tclss_fmt
            tagged.append((token_fmt, hashtag_token))
            #
            tname_fmt = 'fg: ' if (colorful or underline_fmt) else ''
            tname_fmt += '#D7FF87' if colorful else ''
            tname_fmt += underline_fmt
            tname_fmt += tclss_fmt
            tagged.append((tname_fmt, tag.name))
            #
            if quote_tokens:
                fmt_quote = ('', '"')
                tagged.insert(0, fmt_quote)
                tagged.append(fmt_quote)
            return tagged

        # NOTE: The returned string includes leading space if nonempty!
        tagnames = []
        if self.tags:
            # Build array of PPT tuples.
            fmt_sep = ('', "\n") if split_lines else ('', ' ')
            n_tag = 0
            for fmtd_tagn in self.tagnames_sorted_formatted(format_tagname):
                if n_tag > 0:
                    tagnames += [fmt_sep]
                n_tag += 1
                tagnames += fmtd_tagn
        return tagnames

    # ***

    @property
    def html_notif(self):
        """
        A briefer Fact one-liner using HTML. Useful for, e.g., notifier toast.
        """
        was_coloring = set_coloring(False)
        duration = '[{}]'.format(self.format_delta(style=''))
        actegory = self.oid_actegory(omit_empty_actegory=True)
        actegory = actegory or '<i>No activity</i>'
        description = self.oid_description(cut_width=39, sep=': ')
        simple_str = (
            '{} {}{}'
            .format(
                duration,
                actegory,
                description,
            )
        )
        set_coloring(was_coloring)
        return simple_str

    # ***

