# -*- coding: utf-8 -*-

# This file is part of 'nark'.
#
# 'nark' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'nark' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'nark'. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import click

from future.utils import python_2_unicode_compatible
from six import text_type

from ..helpers.colored import attr, fg
from ..helpers.objects import resolve_attr_or_method
from ..helpers.strings import format_value_truncate

__all__ = (
    'FactsDiff',
)


# MAYBE: (lb): Move this module (FactsDiff) to dob?
#   And remove Fact.friendly_diff(), too?
# Because it's only used by the CLI...


@python_2_unicode_compatible
class FactsDiff(object):
    """"""
    def __init__(self, orig_fact, edit_fact, formatted=False):
        self.orig_fact = orig_fact
        self.edit_fact = edit_fact
        self.formatted = formatted
        self.include_newlines = False
        self.exclude_attrs = None

    def __str__(self):
        return 'FactsDiff:\n- orig: {}\n- edit: {}'.format(
            self.orig_fact.short, self.edit_fact.short,
        )

    # ***

    def friendly_diff(
        self,
        truncate=False,
        exclude=None,
        show_elapsed=False,
        show_midpoint=False,
        show_now=False,
    ):
        def _friendly_diff():
            self.include_newlines = True
            self.exclude_attrs = exclude

            result = '' if not self.formatted else []
            result = assemble_diff_attrs(result)

            self.include_newlines = False
            self.exclude_attrs = None

            if not self.formatted:
                result = result.rstrip()
            else:
                while (len(result) > 0) and (not result[-1][1].strip()):
                    result.pop()

            return result

        def assemble_diff_attrs(result):
            result += self.diff_line_assemble(
                None, self.time_humanize(show_now), 'interval',
            )
            if show_midpoint:
                result += self.diff_line_assemble(
                    None, self.time_midpoint(), 'midpoint',
                )
            if show_elapsed:
                self_val, other_val = self.diff_time_elapsed(show_now)
                result += self.diff_line_assemble(
                    self_val, other_val, 'duration',
                )
            result += self.diff_attrs('start_fmt_local', 'start')
            if not show_now:
                result += self.diff_attrs('end_fmt_local', 'end')
            else:
                result += self.diff_attrs('end_fmt_local_nowwed', 'end')
            if (not truncate) or self.orig_fact.pk or self.edit_fact.pk:
                result += self.diff_attrs('pk', 'id', beautify=self.beautify_pk)
            result += self.diff_attrs('deleted', 'deleted')
            # MAYBE?: (lb): Would we even want to show the split_from fact?
            #  result += self.diff_attrs('split_from', 'split_from')
            result += self.diff_attrs('activity_name', 'activity')
            result += self.diff_attrs('category_name', 'category')
            if not self.formatted:
                result += self.diff_attrs(
                    'tags_inline', 'tags', colorful=True, underlined=True,
                )
            else:
                result += self.diff_attrs(
                    'tags_tuples', 'tags', colorful=True, underlined=True,
                )
            result += self.diff_attrs('description', 'description', truncate=truncate)
            return result

        # ***

        return _friendly_diff()

    # ***

    def diff_attrs(self, prop, name=None, truncate=False, beautify=None, **kwargs):
        if (self.exclude_attrs is not None) and (name in self.exclude_attrs):
            return ''
        self_val = resolve_attr_or_method(self.orig_fact, prop, **kwargs)
        other_val = ''
        if self.edit_fact is not None:
            other_val = resolve_attr_or_method(self.edit_fact, prop, **kwargs)
            if callable(other_val):
                other_val = other_val()
            self_val, other_val = self.diff_values_enhance(
                self_val, other_val, truncate=truncate, beautify=beautify,
            )
        elif truncate:
            self_val = self.format_value_truncate(self_val)
            self_val = self.format_prepare(self_val)
            other_val = self.format_prepare(other_val)
        attr_diff = self.diff_line_assemble(self_val, other_val, name)
        return attr_diff

    def diff_line_assemble(self, self_val, other_val, name=None):
        prefix = self.diff_values_padded_prefix(name)
        if not self.formatted:
            return self.diff_line_inline_style(self_val, other_val, prefix)
        else:
            return self.diff_line_tuples_style(self_val, other_val, prefix)

    def diff_values_enhance(
        self, self_val, other_val, truncate=False, beautify=None,
    ):
        differ = False
        if self_val != other_val:
            differ = True
        if truncate:
            self_val = self.format_value_truncate(self_val)
            other_val = self.format_value_truncate(other_val)
        if beautify is not None:
            self_val, other_val = beautify(self_val, other_val)
            if self_val != other_val:
                differ = True
        if differ:
            self_val = self.format_edited_before(self_val)
            self_val, other_val = self.format_edited_after(self_val, other_val)
        else:
            self_val = self.format_prepare(self_val)
            other_val = self.format_prepare('')
        return (self_val, other_val)

    def format_prepare(self, some_val):
        if not self.formatted or not isinstance(some_val, text_type):
            return some_val
        return [('', some_val)]

    def format_value_truncate(self, val):
        # MAGIC_NUMBER: (lb): A third of the terminal (1 / 3.).
        # MAYBE/2019-02-15: Should have Carousel tells us width.
        term_width = click.get_terminal_size()[0]
        trunc_width = int(term_width * (1 / 3.))
        return format_value_truncate(val, trunc_width)

    # ***

    def diff_time_elapsed(self, show_now=False):
        self_val = self.time_elapsed(self.orig_fact, show_now)
        other_val = self.time_elapsed(self.edit_fact, show_now)
        if not self_val:
            # Make 'em the same, i.e., show no diff, no styling.
            self_val = other_val
        return self.diff_values_enhance(self_val, other_val)

    def time_elapsed(self, fact, show_now=False):
        # NOTE: start and/or end might be string; e.g., clock or rel. time.
        if (not fact.times_ok) and (not show_now):
            return None
        time_val = fact.format_delta(style='HHhMMm')
        return time_val

    def time_midpoint(self):
        return self.format_prepare(
            self.edit_fact.time_of_day_midpoint
        )

    def time_humanize(self, show_now=False):
        return self.format_prepare(
            self.edit_fact.time_of_day_humanize(show_now=show_now)
        )

    def beautify_pk(self, self_val, other_val):
        # (lb): NOTE: This is the only dirty_reasons usage in nark
        #               (most of its usage is in dob).
        if (
            'split' in self.edit_fact.dirty_reasons
            or 'split' in self.orig_fact.dirty_reasons
        ):
            pass
        if 'lsplit' in self.edit_fact.dirty_reasons:
            other_val = 'New split fact, created before new fact'
        if 'rsplit' in self.edit_fact.dirty_reasons:
            other_val = 'New split fact, created after new fact'
        return (self_val, other_val)

    # ***

    def format_edited_before(self, before_val):
        if not self.formatted:
            return '{}{}{}'.format(
                fg('spring_green_3a'),
                before_val,
                attr('reset'),
            )
        spring_green_3a = '00AF5F'
        style = 'fg:#{}'.format(spring_green_3a)
        before_parts = []
        if isinstance(before_val, text_type):
            before_parts += [(style, before_val)]
        elif before_val is not None:
            for tup in before_val:
                before_parts.append((style, tup[1]))
        return before_parts

    def format_edited_after(self, self_val, other_val):
        if not self.formatted:
            return '{}{}{}{}{} | was: '.format(
                attr('bold'),
                attr('underlined'),
                fg('light_salmon_3b'),
                other_val,
                attr('reset'),
                # (lb): What, colored has no italic option?
            ), self_val
        light_salmon_3b = 'D7875F'
        style = 'fg:#{} bold underline'.format(light_salmon_3b)
        after_parts = []
        if isinstance(other_val, text_type):
            after_parts += [(style, other_val)]
        elif other_val is not None:
            for tup in other_val:
                after_parts.append((style, tup[1]))
        # (lb): Swap the order, for display purposes.
        #   (These formatting functions are so janky!)
        if self_val and self_val[0][1]:
            after_parts += [('italic', ' | was: ')]
        return after_parts, self_val

    # ***

    def diff_values_padded_prefix(self, name):
        if name is None:
            return ''
        prefix_prefix = '  '
        padded_prefix = '{}{:.<19} : '.format(prefix_prefix, name)
        return padded_prefix

    def diff_line_inline_style(self, self_val, other_val, prefix=''):
        format_inline = '{}{}{}'.format(prefix, self_val or '', other_val or '')
        format_inline += "\n" if self.include_newlines else ''
        return format_inline

    def diff_line_tuples_style(self, self_val, other_val, prefix=''):
        format_tuples = []
        if prefix:
            format_tuples += [('', prefix)]
        if self_val:
            format_tuples += self_val
        if other_val:
            format_tuples += other_val
        if self.include_newlines:
            format_tuples += [('', '\n')]
        return format_tuples

