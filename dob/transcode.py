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

"""A time tracker for the command line. Utilizing the power of nark."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import copy
import re
import sys
from datetime import datetime, timedelta
from six import text_type

from nark import Fact, reports
from nark.helpers.colored import fg, bg, attr
from nark.helpers.dated import (
    datetime_from_clock_after,
    datetime_from_clock_prior,
    parse_clock_time,
    parse_relative_minutes,
)
from nark.helpers.parsing import parse_factoid

from . import __appname__
from .cmd_common import barf_and_exit, echo_block_header, fact_block_header
from .cmds_list.fact import search_facts
from .create import echo_fact, mend_facts_times, save_facts_maybe
from .interrogate import ask_user_for_edits

__all__ = ['export_facts', 'import_facts']


def export_facts(
    controller,
    to_format,
    start,
    end,
    filename=None,
    deleted=False,
    hidden=False,
    key=None,
    # search_term='',
    activity=None,
    category=None,
    sort_order='desc',
    limit='',
    offset='',
):
    """
    Export all facts in the given timeframe in the format specified.

    Args:
        format (str): Format to export to.
            Valid options are: ``csv``, ``xml`` and ``ical``.
        start (datetime.datetime): Restrict to facts starting at this time or later.
        end (datetime.datetime): Restrict to facts ending no later than this time.

    Returns:
        None: If everything went alright.

    Raises:
        click.Exception: If format is not recognized.
    """

    def _export_facts(start, end):
        must_verify_format(to_format)

        start, end = resolve_start_end(start, end)

        filepath = resolve_filepath(filename, to_format)

        facts = search_facts(
            controller,
            key=key,
            start=start,
            end=end,
            # deleted
            # search_term
            activity=activity,
            category=category,
            # sort_col
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            # **kwarg
        )

        export_formatted(facts, filepath, to_format)

    def must_verify_format(to_format):
        accepted_formats = ['csv', 'tsv', 'ical', 'xml']
        # [TODO]
        # Once nark has a proper 'export' register available we should be able
        # to streamline this.
        if to_format not in accepted_formats:
            message = _("Unrecocgnized export format received")
            controller.client_logger.info(message)
            raise click.ClickException(message)

    def resolve_start_end(start, end):
        if not start:
            start = None
        if not end:
            end = None
        return start, end

    def resolve_filepath(filename, to_format):
        if filename:
            filepath = filename
        else:
            filepath = controller.client_config['export_path']
            filepath = filepath + '.' + to_format
        return filepath

    def export_formatted(facts, filepath, to_format):
        if to_format == 'csv':
            writer = reports.CSVWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
        elif to_format == 'tsv':
            writer = reports.TSVWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
        elif to_format == 'ical':
            writer = reports.ICALWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
        else:
            assert to_format == 'xml'
            writer = reports.XMLWriter(filepath)
            writer.write_report(facts)
            click.echo(_("Facts have been exported to: {path}".format(path=filepath)))

    # ***

    _export_facts(start, end)

# ***


def import_facts(
    controller,
    file_in=None,
    file_out=None,
    rule='',
    ask=False,
    yes=False,
    dry=False,
):
    """
    Import Facts from STDIN or a file.
    """

    # MAYBE/2018-05-16 00:11: (lb): Parse whole file before prompting.
    #                               Allow --yes to work here, too?
    #                               Not sure...
    #   For now, we'll just read one fact at a time.

    def _import_facts():
        redirecting = must_specify_input(file_in)
        input_f = must_open_file(redirecting, file_in)
        unprocessed_facts = parse_facts_from_stream(input_f, ask, yes, dry)
        new_facts = hydrate_facts(unprocessed_facts)
        raw_facts = copy.deepcopy(new_facts)
        must_complete_times(new_facts)
        must_not_conflict_existing(new_facts)
        confirm_all_facts(new_facts, raw_facts, file_out, rule, ask, yes, dry)
        persist_facts(new_facts, file_out, dry)
        celebrate(new_facts)

    # ***

    def must_specify_input(file_in):
        redirecting = False
        # See if the user is piping or redirecting STDIN, e.g.,
        #   echo "derp" | nark import
        #   nark import < path/to/file
        if not sys.stdin.isatty():
            # Bingo!
            redirecting = True
            if file_in:
                # NOTE: You cannot set a breakpoint here if you do something
                #       weird like: ``cat import.nark | nark import -``
                #               or: ``nark import - < import.nark``
                # MEH: (lb): This is sorta an optparser layer concern and
                # maybe should be handled from the caller (CLI) rather than
                # from the import/export processing routines. But, meh.
                msg = 'Weirdo, why are you redirecting STDIN and specifying a file?'
                click.echo(msg)
                sys.exit(1)
        elif not file_in:
            # MEH: (lb): Same idea as earlier comment: Maybe echo() and exit()
            # should be done by caller, and not by library routine.
            msg = (
                'Please specify a file, or send something on STDIN.\n'
                'For examples: `cat {{file}} | {appname} import`\n'
                '          or: `{appname} import < {{file}})\n'
                '          or: `{appname} import {{file}}'
            ).format(appname=__appname__)
            click.echo(msg)
            sys.exit(1)
        return redirecting

    # ***

    def must_open_file(redirecting, file_in):
        if redirecting:
            f_in = sys.stdin
        else:
            # Nice! click handles file opening for us, and complains if it cannot!
            #   try:
            #       f_in = open(filename, 'r')
            #   except Exception as err:
            #       # I.e., FileNotFoundError, PermissionError, etc.
            #       msg = (
            #           'Failed to open file at "{}": {}'
            #           .format(filename, err)
            #       )
            #       click.echo(msg)
            #       sys.exit(1)
            f_in = file_in
        return f_in

    # ***

    def parse_facts_from_stream(input_f, ask, yes, dry):
        # Track current empty line run count, to know when to check if line
        # starts a new Fact. Keep at -1 until we've seen the first fact.
        bl_count = -1

        # Coalesce each Fact, line by line.
        current_fact_dict = None
        accumulated_fact = []
        unprocessed_facts = []

        for line in input_f:
            (
                bl_count, processed,
            ) = gobble_blank_or_continued(line, accumulated_fact, bl_count)
            if processed:
                continue

            fact_dict = gobble_if_not_new_fact(line, accumulated_fact, bl_count)
            if fact_dict is None:
                bl_count = 0
                continue
            elif not accumulated_fact:
                # First Fact.
                assert current_fact_dict is None
                assert not accumulated_fact
                current_fact_dict = fact_dict
                accumulated_fact.append(line)
                bl_count = 0
                continue
            else:
                assert current_fact_dict is not None
                assert accumulated_fact

            # Woot, woot! We parsed a complete Fact.
            if current_fact_dict:
                unprocessed_facts.append((current_fact_dict, accumulated_fact,))
            current_fact_dict = fact_dict
            accumulated_fact = [line, ]
            bl_count = 0

        # end: for

        if accumulated_fact:
            unprocessed_facts.append((current_fact_dict, accumulated_fact,))
        else:
            msg = _('What is this, an empty file?')
            barf_and_exit(msg)

        return unprocessed_facts

    def gobble_blank_or_continued(line, accumulated_fact, blank_line_count):
        processed = False
        if blank_line_count < 0:
            # Start of file.
            assert blank_line_count == -1
            if not line.strip():
                controller.client_logger.debug(_('Skip premature blank line'))
                # Skip blank lines pre-Facts.
                processed = True
            # else, we found the first non-blank line. We now
            #   expect to find the date:time & meta, or death.
        elif not line.strip():  # remove trailing newline
            controller.client_logger.debug(_('- Blank line in desc.'))
            accumulated_fact.append(line)
            blank_line_count += 1
            processed = True
        elif blank_line_count == 0:
            controller.client_logger.debug(_('- Part of desc.:\n') + line.strip())
            accumulated_fact.append(line)
            processed = True
        # else, any content that follows blank line(s) is either:
        # (1) more content; (2) a new Fact; or (3) Fact separator.
        return (blank_line_count, processed)

    def gobble_if_not_new_fact(line, accumulated_fact, blank_line_count):
        fact_dict = dissect_meta_line(line)
        if fact_dict is None:
            # If not parsed, and first line we've seen, die.
            missing_fact_must_come_early(line, blank_line_count)
            # else, more content, or a Fact separator.
            controller.client_logger.debug(_('- More desc.: ') + line.strip())
            accumulated_fact.append(line)
        return fact_dict

    def missing_fact_must_come_early(line, blank_line_count):
        if blank_line_count == -1:
            msg = (
                '{}: {}{}{}{}{}\n'
                .format(
                    _('The first nonempty line is not a recognized Fact.'),
                    bg('white'), fg('black'), attr('underlined'),
                    line.strip(),
                    attr('reset'),
                )
            )
            barf_and_exit(msg)

    # See also: parsing.TIME_HINT_MAP

    RE_TIME_HINT = re.compile(
        # Skipping: on|now.
        r'^('
            '(?P<verify_start>at)|'  # noqa: E131
            '(?P<verify_end>to|until)|'
            '(?P<verify_both>from|between)'
        ' )'
    )

    def dissect_meta_line(line):
        sussed_hint, time_hint, line = suss_the_time_format(line)
        fact_dict, err = run_parser(line, time_hint)
        if not fact_dict['start'] and not fact_dict['end']:
            controller.client_logger.debug(_('unmeta: {}'.format(err)))
            fact_dict = None
        else:
            # The user could specify, e.g., just a single datetime (followed
            # by a description), and we can fill in the other datetime and
            # ask the user for more details about the fact.
            #   Not always True:  assert not err
            controller.client_logger.debug(_(
                'new fact_dict: {}'.format(fact_dict)
            ))
        return fact_dict

    def suss_the_time_format(line):
        sussed_hint = ''
        match = RE_TIME_HINT.match(line)
        if match is not None:
            for hint, matched in match.groupdict().items():
                if matched is not None:
                    assert not sussed_hint
                    sussed_hint = hint
                    # Remove the time hint prefix.
                    line = RE_TIME_HINT.sub('', line).lstrip()
        time_hint = sussed_hint or 'verify_start'
        controller.client_logger.debug(_(
            'time_hint: {}{}'.format(
                time_hint, ' [sussed]' if sussed_hint else ' [default]',
            )
        ))
        return sussed_hint, time_hint, line

    def run_parser(line, time_hint):
        # Parse the line as if it were a new fact. And don't strip the line.
        # Parser expects metadata to be separated from description (so leave
        # the newline). And we can be strict and require that the date data
        # starts the line.

        # Per dob-insert commands, parser expects iterable.
        factoid = (line,)

        fact_dict, err = parse_factoid(
            factoid=factoid,
            time_hint=time_hint,
            # MEH: (lb): Should we leave hash_stamps='#@' ?
            #   I sorta like using the proper tag symbol
            #   when not worried about shell interpolation.
            hash_stamps='#',
            # We'll handle errors ourselves, later, in bulk, either
            # `--ask`'ing the user for more Fact details, or barfing
            # all the errors and exiting.
            lenient=True,
        )
        return fact_dict, err

    # ***

    def hydrate_facts(unprocessed_facts):
        new_facts = []
        temp_id = -1
        for fact_dict, accumulated_fact in unprocessed_facts:
            hydrate_description(fact_dict, accumulated_fact)
            new_fact = Fact.create_from_parsed_fact(fact_dict, lenient=True)
            new_fact.pk = temp_id
            new_facts.append(new_fact)
            temp_id -= 1
        new_facts = sorted(new_facts, key=lambda fact: fact.start or fact.end)
        return new_facts

    # Horizontal rule separator matches same character repeated at least thrice.
    # FIXME/2018-05-18: (lb): Document: HR is any repeated one of -, =, #, |.
    FACT_SEP_HR = re.compile(r'^([-=#|])\1{2}\1*$')

    def hydrate_description(fact_dict, accumulated_fact):
        # The first entry is the meta line, so ignore it.
        desc_lines = accumulated_fact[1:]
        # However, the user is allowed to start the description
        # on the meta line.
        if fact_dict['description']:
            desc_lines.insert(0, fact_dict['description'])

        # To make import file more readable, user can add
        # separator line between facts. Cull it if found.
        # MAYBE/2018-05-18: (lb): Make this operation optional?
        while len(desc_lines) > 0 and not desc_lines[-1].strip():
            desc_lines.pop()

        if (
            len(desc_lines) > 1
            and not desc_lines[-2].strip()
            and FACT_SEP_HR.match(desc_lines[-1])
        ):
            desc_lines.pop()

        # desc_lines are already newlined.
        desc = ''.join(desc_lines).strip()

        fact_dict['description'] = desc

    # ***

    def must_complete_times(new_facts):
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
            if not ante_fact.end:
                assert False  # Caught earlier by backend_integrity().
                raise Exception(_(
                    'Found saved fact without end_time: {}'.format(ante_fact)
                ))
            isinstance(ante_fact.end, datetime)
            prev_time = ante_fact.end

        later_facts = new_facts[0:]
        if seqt_fact:
            if not seqt_fact.start:
                assert False  # Caught earlier by: backend_integrity().
                raise Exception(_(
                    'Found saved fact without start_time: {}'.format(seqt_fact)
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
                dt_suss = datetime_from_clock_prior(dt_oppo, clock_time)
            else:
                dt_suss = datetime_from_clock_after(dt_oppo, clock_time)
        elif prev_time is not None:
            # If fact's other time not set, prefer earlier clock time.
            dt_suss = datetime_from_clock_after(prev_time, clock_time)
        else:
            # Last resort: go hunting for the next actual, factual real datetime.
            # FIXME/2018-05-21 12:17: (lb): Will this ever happen?
            #   Probably only if antecedent_fact not found??
            next_time, _next_fact = find_next_datetime(later_facts)
            if next_time is not None:
                dt_suss = datetime_from_clock_prior(next_time, clock_time)

        if dt_suss is not None:
            setattr(fact, which, dt_suss)
            prev_time = dt_suss
        else:
            conflicts.append((
                fact,
                None,
                _(
                    'Cannot infer date of {} time specified with clock time'
                ).format(which),
            ))
        return prev_time

    # ...

    def fix_delta_times_relative(new_facts, ante_fact, seqt_fact, conflicts):
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
                delta_mins = parse_relative_minutes(dt_fact)
                if delta_mins is not None:
                    prev_time = infer_datetime_from_delta(
                        delta_mins, fact, which, prev_time, later_facts, conflicts
                    )
        return prev_time

    def infer_datetime_from_delta(
        delta_mins, fact, which, prev_time, later_facts, conflicts,
    ):
        # If -delta, relative to *next* time; if +delta, relative to *prev* time.
        dt_suss = None
        # FIXME/MAYBE/2018-05-21 12:51: (lb): Should we only accept prev_time
        #                               or next_time if immediately before/after?
        if delta_mins >= 0:
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
            conflicts.append((
                fact,
                None,
                _('Cannot infer date of {} time specified with delta time'
                    .format(which)),
            ))
        return prev_time

    # ...

    def fix_blank_times_relative(new_facts, ante_fact, seqt_fact, conflicts):
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
        if dt_fact is not None:
            assert isinstance(dt_fact, datetime)
            prev_time = dt_fact
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
                conflicts.append((
                    fact,
                    None,
                    _('Cannot infer date of {} time left blank'
                        .format(which)),
                ))

        return prev_time

    # ...

    def verify_datetimes_sanity(new_facts, ante_fact, seqt_fact, conflicts):
        prev_time, later_facts = prev_and_later(new_facts, ante_fact, seqt_fact)
        prev_fact = ante_fact
        for fact in new_facts:
            assert fact is later_facts[0]
            later_facts.pop(0)

            if not fact.start:
                # Rather than adding it again, e.g.,
                #   conflicts.append((
                #     fact, None, _('Could not determine start of new fact')))
                # just verify we already caught it.
                verify_datetimes_missing_already_caught(fact, conflicts)
            else:
                if prev_time and fact.start < prev_time:
                    conflicts.append((
                        fact, prev_fact, _('New fact starts before previous fact ends'),
                    ))
                prev_time = fact.start

            if not fact.end:
                verify_datetimes_missing_already_caught(fact, conflicts)
            else:
                next_time, next_fact = find_next_datetime(later_facts)
                if next_time and fact.end > next_time:
                    conflicts.append((
                        fact, next_fact, _('New fact ends after next fact starts'),
                    ))
                prev_time = fact.end

            if fact.start and fact.end and fact.start > fact.end:
                conflicts.append((
                    fact, None, _('New fact starts after it ends/ends before it starts'),
                ))

            prev_fact = fact

    def verify_datetimes_missing_already_caught(fact, conflicts):
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
            echo_block_header(_('{} Fact Datetime Conflict!'.format(prefix)))
            click.echo()
            click.echo(fact.friendly_diff(fact, truncate=True))
            click.echo()
            click.echo('{}: {}{}{}'.format(
                _('Problem'),
                fg('dodger_blue_1'),
                reason,
                attr('reset'),
            ))
            if other:
                # FIXME/2018-06-12: (lb): Subtract edges; this is too much.
                cut_width = click.get_terminal_size()[0]

                click.echo('{}: {}{}'.format(
                    _('Compare',),
                    other_pk,
                    other.friendly_str(colorful=colorful, cut_width=cut_width),
                ))
            click.echo()
        msg = _(
            'Could not determine, or did not validate, start and/or stop'
            ' for one or more new Facts.'
            '\nScroll up for details.'
        )
        barf_and_exit(msg)

    '''
[c.brief for c in conflicts]
    '''

    # ***

    def must_not_conflict_existing(new_facts):
        all_conflicts = []
        for fact in new_facts:
            conflicts = mend_facts_times(controller, fact, time_hint='verify_both')
            if conflicts:
                all_conflicts.append((fact, conflicts,))
        # MAYBE/2018-05-19: (lb): Import *could* deal with conflicts (both
        # programmatically and morally), but I don't see a need currently.
        barf_on_overlapping_facts_old(all_conflicts)

    def barf_on_overlapping_facts_old(conflicts):
        if not conflicts:
            return

        for fact, resolved_edits in conflicts:
            for edited_fact, original in resolved_edits:
                echo_saved_fact_conflict(fact, edited_fact, original)
        msg = _(
            'One or more new Facts would conflict with existing Facts.'
            ' This Is Not Allowed'
        )
        barf_and_exit(msg)

    def echo_saved_fact_conflict(fact, edited_fact, original):
        echo_block_header(_('Saved Fact Datetime Conflict!'))
        click.echo()
        click.echo(_('  Fact being imported:'))
        click.echo(_('  ───────────────────'))
        click.echo(fact.friendly_diff(fact, truncate=True))
        click.echo()
        click.echo(_('  Impact on saved Fact:'))
        click.echo(_('  ────────────────────'))
        click.echo(original.friendly_diff(edited_fact))
        click.echo()

    # ***

    def interactive_cleanup(fact):
        # FIXME/2018-06-10: Do we need to specify prompt_agent?
        #   I need to test importing multiple facts from a file
        #   to see what interaction is like. It might not matter
        #   to keep the same prompter around. In which case,
        #   remove prompt_agent param from ask_user_for_edits.
        # (lb): Set always_ask=True, so even if act@cat is set,
        #   user is still prompted.
        #   MAYBE/2018-06-10: We do this so user can correct
        #     spelling errors/incomplete names, etc. We could
        #     add a feature that only asks if the act@cat would
        #     create a new act and/or cat. I.e., if the act@cat
        #     is already in the existing, don't bug the user.
        #     (But the win would be small; I don't have any
        #     act@cat's exactly memorized, so every fact from
        #     an import on mine would always need act@cat editing.)
        return ask_user_for_edits(controller, fact, always_ask=True)

    # ***

    def confirm_all_facts(new_facts, raw_facts, file_out, rule, ask, yes, dry):
        if not dry:
            pass

        # Remember prompter state between inquisitions.
        prompt_agent = None

        if not yes and not dry:
            click.echo('You may now edit facts being imported...')
            click.echo()
        for idx, raw_fact in enumerate(raw_facts):
            new_fact = new_facts[idx]
            if not yes and not dry:
                prompt_agent = confirm_fact(
                    idx, raw_fact, new_fact, prompt_agent, ask,
                )
            else:
                echo_block_header(_('Such Fact!'))
                click.echo()
                click.echo(raw_fact.friendly_diff(new_fact))
                click.echo()
            persist_fact_file(new_fact, file_out, rule, dry, idx)

    def confirm_fact(idx, raw_fact, new_fact, prompt_agent, ask):
        """"""
        def _confirm_fact():
            used_prompt_agent = prompt_agent
            ask_at_least_once = ask
            confirmed = False
            while not confirmed:
                confirmed = ask_at_least_once
                ask_at_least_once = False
                confirmed = interact_confirm(confirmed)
                if not confirmed:
                    used_prompt_agent = interactive_cleanup(new_fact)
                else:
                    click.echo()
            return used_prompt_agent

        def interact_confirm(confirmed):
            if confirmed:
                return confirmed
            return confirm_with_user()

        def confirm_with_user():
            header = fact_block_header(_('New fact #{}').format(idx + 1))
            # MAYBE/2018-05-21: (lb): Option to skip fact?
            confirmed = click.confirm(
                text=_('{}\n\n{}\n\nLook good?').format(
                    header, raw_fact.friendly_diff(new_fact, truncate=True),
                ),
                default=True,
                abort=False,
                # prompt_suffix=': ',
                # show_default=True,
                # err=False,
            )
            return confirmed

        return _confirm_fact()

    # ***

    def persist_facts(new_facts, file_out=None, dry=False):
        for fact in new_facts:
            persist_fact(fact, file_out, dry)
        # (lb): Click will close the file, but we can also cleanup.
        if file_out and not dry:
            file_out.close()

    def persist_fact(fact, file_out, dry):
        if not dry:
            if not file_out:
                persist_fact_save(fact, dry)
            # else, we called persist_fact_file earlier.
        else:
            echo_block_header(_('Fresh Fact!'))
            click.echo()
            echo_fact(fact)
            click.echo()

    def persist_fact_file(fact, file_out, rule, dry, idx):
        if dry:
            return
        write_fact_separator(file_out, rule, idx)
        file_out.write(
            fact.friendly_str(
                description_sep='\n\n',
                shellify=False,
                colorful=False,
            )
        )
        file_out.flush()

    RULE_WIDTH = 76  # How wide to print the between-facts separator.

    def write_fact_separator(file_out, rule, idx):
        if idx == 0:
            return
        file_out.write('\n\n')
        if rule:
            file_out.write('{}\n\n'.format(rule * RULE_WIDTH))

    def persist_fact_save(fact, dry):
        raise NotImplementedError  # FIXME: Needs testing!
        conflicts = []
        save_facts_maybe(controller, fact, conflicts, dry)

    # ***

    def celebrate(fact):
        click.echo('{}{}{}'.format(
            attr('underlined'), _('Voilà!'), attr('reset'),
        ))

    # *** [export_facts] entry.

    _import_facts()

