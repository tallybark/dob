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
from datetime import datetime, timedelta
from six import text_type

from nark.helpers import time as time_helpers
from nark.helpers.colored import fg, attr
from nark.helpers.dated import (
    datetime_from_clock_after,
    datetime_from_clock_prior,
    parse_clock_time,
    parse_relative_minutes,
)

from . import click_echo, prepare_log_msg
from ..cmd_common import barf_and_exit, echo_block_header


__all__ = [
    'insert_forcefully',
    'mend_facts_times',
    'must_complete_times',
    'resolve_overlapping',
]


def must_complete_times(
    controller,
    new_facts,
    progress=None,
    ongoing_okay=False,
    leave_blanks=False,
):
    """"""

    # ***

    def _must_complete_times():
        if not new_facts:
            return

        conflicts = []

        ante_fact = antecedent_fact(new_facts)
        seqt_fact = subsequent_fact(new_facts)

        # Clean up relative clock times first.
        fix_clock_times_relative(new_facts, ante_fact, seqt_fact, conflicts)

        # Clean up relative minutes times next.
        fix_delta_times_relative(new_facts, ante_fact, seqt_fact, conflicts)

        # Finally, fill in any blanks (with adjacent times).
        if not leave_blanks:
            fix_blank_times_relative(new_facts, ante_fact, seqt_fact, conflicts)

        # One final start < end < start ... check.
        verify_datetimes_sanity(new_facts, ante_fact, seqt_fact, conflicts)

        barf_on_overlapping_facts_new(conflicts)

    # ...

    def antecedent_fact(new_facts):
        for fact in new_facts:
            if fact.start and isinstance(fact.start, datetime):
                return controller.facts.antecedent(ref_time=fact.start)
            elif fact.end and isinstance(fact.end, datetime):
                return controller.facts.antecedent(ref_time=fact.end)
        return None

    def subsequent_fact(new_facts):
        for fact in reversed(new_facts):
            if fact.end and isinstance(fact.end, datetime):
                return controller.facts.subsequent(ref_time=fact.end)
            elif fact.start and isinstance(fact.start, datetime):
                return controller.facts.subsequent(ref_time=fact.start)
        return None

    def prev_and_later(new_facts, ante_fact, seqt_fact):
        prev_time = None
        if ante_fact:
            if ante_fact.end:
                isinstance(ante_fact.end, datetime)
                prev_time = ante_fact.end
            elif not ongoing_okay and len(new_facts) == 1 and seqt_fact is None:
                assert False  # Caught earlier by backend_integrity(). (Right?)
                raise Exception(_(
                    'Found saved fact without end time: {}'.format(ante_fact)
                ))

# ??? 1: ???
        later_facts = new_facts[0:]
        if seqt_fact:
            if not seqt_fact.start:
                assert False  # Caught earlier by: backend_integrity().
                raise Exception(_(
                    'Found saved fact without start time: {}'.format(seqt_fact)
                ))
            assert isinstance(seqt_fact.start, datetime)
            later_facts += [seqt_fact]

        return prev_time, later_facts

    def find_next_datetime(later_facts):
        for fact in later_facts:
            if isinstance(fact.start, datetime):
                return fact.start, fact
            if isinstance(fact.end, datetime):
                return fact.end, fact
        return None, None

    # ...

    def fix_clock_times_relative(new_facts, ante_fact, seqt_fact, conflicts):
        progress and progress.click_echo_current_task(_('Fixing relative times...'))
        prev_time, later_facts = prev_and_later(new_facts, ante_fact, seqt_fact)
        for fact in new_facts:
            assert fact is later_facts[0]
            later_facts.pop(0)
            prev_time = fix_clock_time_relative(
                fact, 'start', prev_time, later_facts, conflicts
            )
            prev_time = fix_clock_time_relative(
                fact, 'end', prev_time, later_facts, conflicts
            )

    def fix_clock_time_relative(fact, which, prev_time, later_facts, conflicts):
        dt_fact = getattr(fact, which)
        if dt_fact is not None:
            if isinstance(dt_fact, datetime):
                prev_time = dt_fact
            else:
                assert isinstance(dt_fact, text_type)
                clock_time = parse_clock_time(dt_fact)
                if clock_time is not None:
                    prev_time = infer_datetime_from_clock(
                        clock_time, fact, which, prev_time, later_facts, conflicts
                    )
        return prev_time

    def infer_datetime_from_clock(
        clock_time, fact, which, prev_time, later_facts, conflicts,
    ):
        dt_suss = None

        at_oppo = 'end' if which == 'start' else 'start'
        dt_oppo = getattr(fact, at_oppo)
        if isinstance(dt_oppo, datetime):
            # Prefer relative to fact's other time.
            if which == 'start':
                dt_suss, err = infer_from_clock_prior(fact, dt_oppo, clock_time)
            else:
                dt_suss, err = infer_from_clock_after(fact, dt_oppo, clock_time)
        elif prev_time is not None:
            # If fact's other time not set, prefer earlier clock time.
            dt_suss, err = infer_from_clock_after(fact, prev_time, clock_time)
        else:
            # Last resort: go hunting for the next actual, factual real datetime.
            # FIXME/2018-05-21 12:17: (lb): Will this ever happen?
            #   Probably only if antecedent_fact not found??
            next_time, _next_fact = find_next_datetime(later_facts)
            if next_time is not None:
                dt_suss, err = infer_from_clock_prior(fact, next_time, clock_time)

        if dt_suss is not None:
            assert err is None
            setattr(fact, which, dt_suss)
            prev_time = dt_suss
        else:
            msg_content = _(
                'Could not decipher clock time from {} for {}'
            ).format(clock_time, which)
            conflict_msg = prepare_log_msg(fact, msg_content)
            conflicts.append((fact, None, conflict_msg, ))
        return prev_time

    def infer_from_clock_prior(fact, dt_oppo, clock_time):
        dt_suss = None
        err_msg = None
        try:
            dt_suss = datetime_from_clock_prior(dt_oppo, clock_time)
        except Exception as err:
            err_msg = str(err)
        return dt_suss, err_msg

    def infer_from_clock_after(fact, dt_oppo, clock_time):
        dt_suss = None
        err_msg = None
        try:
            dt_suss = datetime_from_clock_after(dt_oppo, clock_time)
        except Exception as err:
            err_msg = str(err)
        return dt_suss, err_msg

    # ...

    def fix_delta_times_relative(new_facts, ante_fact, seqt_fact, conflicts):
        progress and progress.click_echo_current_task(_('Fixing relative deltas...'))
        prev_time, later_facts = prev_and_later(new_facts, ante_fact, seqt_fact)
        for fact in new_facts:
            assert fact is later_facts[0]
            later_facts.pop(0)
            prev_time = fix_delta_time_relative(
                fact, 'start', prev_time, later_facts, conflicts
            )
            prev_time = fix_delta_time_relative(
                fact, 'end', prev_time, later_facts, conflicts
            )

    def fix_delta_time_relative(fact, which, prev_time, later_facts, conflicts):
        dt_fact = getattr(fact, which)
        if dt_fact is not None:
            if isinstance(dt_fact, datetime):
                prev_time = dt_fact
            else:
                assert isinstance(dt_fact, text_type)
                delta_mins, delta_minus = parse_relative_minutes(dt_fact)
                if delta_mins is not None:
                    prev_time = infer_datetime_from_delta(
                        delta_mins,
                        delta_minus,
                        fact,
                        which,
                        prev_time,
                        later_facts,
                        conflicts,
                    )
        return prev_time

    def infer_datetime_from_delta(
        delta_mins, delta_minus, fact, which, prev_time, later_facts, conflicts,
    ):
        # If -delta, relative to *next* time; if +delta, relative to *prev* time.
        dt_suss = None
        if delta_minus is False:
            if prev_time is not None:
                dt_suss = prev_time + timedelta(minutes=delta_mins)
            # else, we'll add a conflict below.
        elif which == 'start' and isinstance(fact.end, datetime):
            # NOTE: delta_mins < 0, so add the delta (to subtract it).
            dt_suss = fact.end + timedelta(minutes=delta_mins)
        else:
            next_time, _next_fact = find_next_datetime(later_facts)
            if next_time is not None:
                # NOTE: delta_mins is negative, so add to next_time.
                dt_suss = next_time + timedelta(minutes=delta_mins)

        if dt_suss is not None:
            setattr(fact, which, dt_suss)
            prev_time = dt_suss
        else:
            msg_content = _(
                'Could not infer delta time “{}” for {}'
            ).format(delta_mins, which)
            conflict_msg = prepare_log_msg(fact, msg_content)
            conflicts.append((fact, None, conflict_msg, ))
        return prev_time

    # ...

    def fix_blank_times_relative(new_facts, ante_fact, seqt_fact, conflicts):
        progress and progress.click_echo_current_task(_('Fixing blank times...'))
        prev_time, later_facts = prev_and_later(new_facts, ante_fact, seqt_fact)
        for fact in new_facts:
            assert fact is later_facts[0]
            later_facts.pop(0)
            assert fact.start or fact.end
            prev_time = fix_blank_time_relative(
                fact, 'start', prev_time, later_facts, conflicts
            )
            prev_time = fix_blank_time_relative(
                fact, 'end', prev_time, later_facts, conflicts
            )

    def fix_blank_time_relative(fact, which, prev_time, later_facts, conflicts):
        dt_fact = getattr(fact, which)
        if isinstance(dt_fact, datetime):
            prev_time = dt_fact
        elif dt_fact:
            msg_content = _(
                'Could not translate relative date “{}” for {}'
            ).format(dt_fact, which)
            conflict_msg = prepare_log_msg(fact, msg_content)
            conflicts.append((fact, None, conflict_msg, ))
        else:
            dt_suss = None

            if which == 'start':
                dt_suss = prev_time
            elif which == 'end':
                dt_suss, _next_fact = find_next_datetime(later_facts)
                if dt_suss is None:
                    dt_suss = controller.store.now

            if dt_suss is not None:
                setattr(fact, which, dt_suss)
                prev_time = dt_suss
            else:
                msg_content = _(
                    'Could not infer date left blank for {}'
                ).format(which)
                conflict_msg = prepare_log_msg(fact, msg_content)
                conflicts.append((fact, None, conflict_msg, ))

        return prev_time

    # ...

    def verify_datetimes_sanity(new_facts, ante_fact, seqt_fact, conflicts):
        progress and progress.click_echo_current_task(_('Verifying sanity times...'))
        prev_time, later_facts = prev_and_later(new_facts, ante_fact, seqt_fact)
        prev_fact = ante_fact
        for fact in new_facts:
            assert fact is later_facts[0]
            later_facts.pop(0)
            n_datetimes = 0

            if not fact.start:
                # Rather than adding it again, e.g.,
                #   conflicts.append((
                #     fact, None, _('Could not determine start of new fact')))
                # just verify we already caught it.
                verify_datetimes_missing_already_caught(fact, conflicts)
            elif isinstance(fact.start, datetime):
                if prev_time and fact.start < prev_time:
                    msg_content = _('New fact starts before previous fact ends')
                    conflict_msg = prepare_log_msg(fact, msg_content)
                    conflicts.append((fact, prev_fact, conflict_msg, ))
                prev_time = fact.start
                n_datetimes += 1
            # else, a string that was unparsed; and conflict already added.

            if not fact.end:
                verify_datetimes_missing_already_caught(fact, conflicts)
            elif isinstance(fact.end, datetime):
                next_time, next_fact = find_next_datetime(later_facts)
                if next_time and fact.end > next_time:
                    msg_content = _('New fact ends after next fact starts')
                    conflict_msg = prepare_log_msg(fact, msg_content)
                    conflicts.append((fact, next_fact, conflict_msg, ))
                prev_time = fact.end
                n_datetimes += 1
            # else, a string that was unparsed; and conflict already added.

            if n_datetimes == 2 and fact.start > fact.end:
                msg_content = _('New fact starts after it ends/ends before it starts')
                conflict_msg = prepare_log_msg(fact, msg_content)
                conflicts.append((fact, None, conflict_msg, ))

            prev_fact = fact

    def verify_datetimes_missing_already_caught(fact, conflicts):
        if leave_blanks:
            return
        found_it = list(filter(lambda conflict: fact is conflict[0], conflicts))
        assert len(found_it) > 0

    # ...

    def barf_on_overlapping_facts_new(conflicts):
        if not conflicts:
            return

        colorful = controller.client_config['term_color']

        for fact, other, reason in conflicts:
            # other might be None, another new Fact, or ante_fact or seqt_fact.
            if other and other.pk:
                prefix = 'Saved'
                other_pk = '#{}: '.format(other.pk)
            else:
                prefix = 'New'
                other_pk = ''
            echo_block_header(
                _('{} Fact Datetime Conflict!'.format(prefix)),
                full_width=True,
            )
            click_echo()
            click_echo(fact.friendly_diff(fact, truncate=True))
            click_echo()
            click_echo('{}: {}{}{}'.format(
                _('Problem'),
                fg('dodger_blue_1'),
                reason,
                attr('reset'),
            ))
            if other:
                # FIXME/2018-06-12: (lb): Subtract edges; this is too much.
                cut_width = click.get_terminal_size()[0]

                click_echo('{}: {}{}'.format(
                    _('Compare',),
                    other_pk,
                    other.friendly_str(colorful=colorful, cut_width=cut_width),
                ))
            click_echo()
        msg = _(
            'Could not determine, or did not validate, start and/or stop'
            ' for one or more new Facts.'
            '\nScroll up for details.'
        )
        crude = len(new_facts) > 1
        barf_and_exit(msg, crude=crude)

    _must_complete_times()


# ***

# MAYBE/2018-06-09: (lb): Need to move any of this to LIB for other packages to use?
def mend_facts_times(controller, fact, time_hint):
    """"""

    def _mend_facts_times(controller, fact, time_hint):
        # The fact is considered "temporary", or open, if the user did not
        # specify an end time, and if there's no Fact following the new Fact.
        open_start, open_end = new_fact_fill_now(fact, time_hint, controller.now)
        conflicts = controller.facts.insert_forcefully(fact)

        # Note that end may be None for ongoing Fact.
        # Verify that start > end, if neither are None.
        time_helpers.validate_start_end_range((fact.start, fact.end))

        if open_start:
            fact.start = None
        if open_end:
            fact.end = None

        return conflicts

    def new_fact_fill_now(fact, time_hint, now):
        # We might temporarily set the end time to look for overlapping
        # facts, so remember if we need to leave the fact open.
        open_start = False
        open_end = False

        if (time_hint == 'verify_none'):
            assert not fact.start
            assert not fact.end
            fact.start = now
            open_end = True
        elif (time_hint == 'verify_both'):
            assert fact.start and fact.end
        elif (time_hint == 'verify_start'):
            assert not fact.end
            open_end = True
            if not fact.start:
                fact.start = now
        elif (time_hint == 'verify_end'):
            assert not fact.start
            open_start = True
            if not fact.end:
                fact.end = now

        return open_start, open_end

    # ***

    return _mend_facts_times(controller, fact, time_hint)


# ***

def insert_forcefully(controller, fact, squash_sep=''):
    """
    Insert the possibly open-ended Fact into the set of logical
    (chronological) Facts, possibly changing the time frames of,
    or removing, other Facts.

    Args:
        fact (nark.Fact):
            The Fact to insert, with either or both ``start`` and ``end`` set.

    Returns:
        list: List of edited ``Facts``, ordered by ``start``.

    Raises:
        ValueError: If start or end time is not specified and cannot be
            deduced by other Facts in the system.
    """
    # NOTE: controller is controller.facts.store.
    allow_momentaneous = controller.config['allow_momentaneous']

    def _insert_forcefully(facts, fact):
        # Steps:
        #   Find fact overlapping start.
        #   Find fact overlapping end.
        #   Find facts wholly contained between start and end.
        #   Return unique set of facts indicating edits and deletions.

        conflicts = []
        conflicts += find_conflict_at_edge(facts, fact, 'start')
        conflicts += find_conflict_at_edge(facts, fact, 'end')
        conflicts += find_conflicts_during(facts, fact)

        edited_conflicts = resolve_overlapping(
            fact, conflicts, squash_sep, allow_momentaneous,
        )

        return edited_conflicts

    # ***

    def find_conflict_at_edge(facts, fact, ref_time):
        conflicts = []
        find_edge = False
        fact_time = getattr(fact, ref_time)
        if fact_time:  # fact.start or fact.end
            conflicts = facts.surrounding(fact_time)
            if conflicts:
                if len(conflicts) != 1:
                    controller.client_logger.warning(_(
                        "Found more than one Fact ({} total) at: '{}'"
                        .format(len(conflicts), fact_time))
                    )
            else:
                find_edge = True
        else:
            find_edge = True
        if find_edge:
            assert not conflicts
            conflicts = inspect_time_boundary(facts, fact, ref_time)
        return conflicts

    def inspect_time_boundary(facts, fact, ref_time):
        conflict = None
        if ref_time == 'start':
            if fact.start is None:
                conflict = set_start_per_antecedent(facts, fact)
            else:
                conflict = facts.starting_at(fact)
        else:
            assert ref_time == 'end'
            if fact.end is None:
                set_end_per_subsequent(facts, fact)
            else:
                conflict = facts.ending_at(fact)
        conflicts = [conflict] if conflict else []
        return conflicts

    def set_start_per_antecedent(facts, fact):
        assert fact.start is None
        # Find a Fact with start < fact.end.
        ref_fact = facts.antecedent(fact)
        if not ref_fact:
            raise ValueError(_(
                'Please specify `start` for fact being added before time existed.'
            ))
        # Because we called surrounding and got nothing, we know that
        # found_fact.end < fact.end; or that found_fact.end is None,
        # a/k/a, the ongoing Fact.
        conflict = None
        if ref_fact.end is not None:
            assert ref_fact.end < fact.end
            fact.start = ref_fact.end
        else:
            # There's an ongoing Fact, and the new Fact has no start, which
            # indicates that these two facts should be squashed. (We'll create
            # an intermediate conflict now, and we'll squash the Facts later,
            # so that we include the ongoing Fact in the list of edited Facts
            # we return later.)
            assert ref_fact.start < fact.end
            conflict = ref_fact
        return conflict

    def set_end_per_subsequent(facts, fact):
        assert fact.end is None
        ref_fact = facts.subsequent(fact)
        if ref_fact:
            assert ref_fact.start > fact.start
            fact.end = ref_fact.start
        else:
            # This is ongoing fact/current.
            controller.client_logger.debug(
                _("No end specified for Fact; assuming now.")
            )
            fact.end = controller.now  # Same as: facts.store.now
            # NOTE: for dob-on, we'll start start, then end will be
            #       a few micros later... but the caller knows to unset
            #       this Fact's end later (see: leave_open).
            #       (lb): I wrote this code and I can't quite remember
            #       why we fact to do this. I think so comparing against
            #       other Facts works....

    # ***

    def find_conflicts_during(facts, fact):
        conflicts = []
        if fact.start and fact.end:
            found_facts = facts.strictly_during(fact.start, fact.end)
            conflicts += found_facts
        return conflicts

    # ***

    return _insert_forcefully(controller.facts, fact)


# ***

def resolve_overlapping(fact, conflicts, squash_sep='', allow_momentaneous=False):
    """"""
    def _resolve_overlapping(fact, conflicts):
        seen = set()
        resolved = []
        for conflict in conflicts:
            assert conflict.pk > 0
            if fact.pk == conflict.pk:
                # Editing existing Fact may find itself in db.
                continue
            if conflict.pk in seen:
                continue
            seen.add(conflict.pk)
            original = conflict.copy()
            edited_conflicts = resolve_fact_conflict(fact, conflict)
            for edited in edited_conflicts:
                resolved.append((edited, original,))
        return resolved

    def resolve_fact_conflict(fact, conflict):
        # If the conflict is contained within another Fact, that
        # other Fact will be split in twain, so we may end up
        # with more conflicts.
        resolved = []
        if fact.start is None and conflict.end is None:
            resolve_fact_squash_fact(fact, conflict, resolved)
        elif fact.start <= conflict.start:
            resolve_fact_starts_before(fact, conflict, resolved)
        elif conflict.end is None or fact.end >= conflict.end:
            resolve_fact_ends_after(fact, conflict, resolved)
        else:
            # The new fact is contained *within* the conflict!
            resolve_fact_is_inside(fact, conflict, resolved)
        return cull_duplicates(resolved)

    def resolve_fact_squash_fact(fact, conflict, resolved):
        conflict.dirty_reasons.add('stopped')
        conflict.dirty_reasons.add('end')
        conflict.dirty_reasons.add('squash')
        conflict.squash(fact, squash_sep)
        resolved.append(conflict)

    def resolve_fact_starts_before(fact, conflict, resolved):
        if fact.end <= conflict.start:
            # Disparate facts.
            return
        elif conflict.end and fact.end >= conflict.end:
            if (
                allow_momentaneous
                and (fact.start == conflict.start)
                and (conflict.start == conflict.end)
            ):
                # (lb): 0-length Fact is not surrounded by new Fact.
                #   As they say in Futurama, I'm going to allow this.
                return
            conflict.deleted = True
            conflict.dirty_reasons.add('deleted-starts_before')
        else:
            # This is either the last Fact in the database, which is still
            # open (if conflict.end is None); or fact ends before conflict
            # ends. And in either case, fact ends after conflict starts,
            # so move conflict's start to no longer conflict.
            assert conflict.start < fact.end
            conflict.start = fact.end
            conflict.dirty_reasons.add('start')
        resolved.append(conflict)

    def resolve_fact_ends_after(fact, conflict, resolved):
        if conflict.end is not None and fact.start >= conflict.end:
            # Disparate facts.
            return
        elif fact.start <= conflict.start:
            if (
                allow_momentaneous
                and (fact.end == conflict.end)
                and (conflict.start == conflict.end)
            ):
                # 0-length Fact is not surrounded by new Fact; I'll allow it.
                return
            conflict.deleted = True
            conflict.dirty_reasons.add('deleted-ends_after')
        else:
            # (lb): Here's where we might stop an ongoing fact
            # when adding a new fact.
            assert conflict.end is None or conflict.end > fact.start
            # A little hack: signal the caller if this is/was ongoing fact.
            if conflict.end is None:
                conflict.dirty_reasons.add('stopped')
            conflict.end = fact.start
            conflict.dirty_reasons.add('end')
        resolved.append(conflict)

    def resolve_fact_is_inside(fact, conflict, resolved):
        resolve_fact_split_prior(fact, conflict, resolved)
        resolve_fact_split_after(fact, conflict, resolved)

    def resolve_fact_split_prior(fact, conflict, resolved):
        # Make a copy of the conflict, to not affect resolve_fact_split_after.
        lconflict = conflict.copy()
        lconflict.split_from = conflict.pk
        # Leave lconflict.pk set so the old fact is marked deleted.
        lconflict.end = fact.start
        lconflict.dirty_reasons.add('lsplit')
        resolved.append(lconflict)

    def resolve_fact_split_after(fact, conflict, resolved):
        rconflict = conflict.copy()
        rconflict.split_from = conflict.pk
        rconflict.pk = None
        rconflict.start = fact.end
        rconflict.dirty_reasons.add('rsplit')
        resolved.append(rconflict)

    def cull_duplicates(resolved):
        seen = set()
        culled = []
        for conflict in resolved:
            if conflict in seen:
                continue
            seen.add(conflict)
            culled.append(conflict)
        return culled

    # ***

    return _resolve_overlapping(fact, conflicts)

