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
import os
import re
import sys
import traceback
from datetime import datetime, timedelta
from io import open
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
from .cmd_common import barf_and_exit, echo_block_header
from .cmd_config import get_appdirs_subdir_file_path, AppDirs
from .cmds_list.fact import search_facts
from .create import echo_fact, mend_facts_times, save_facts_maybe
from .helpers import click_echo, dob_in_user_exit, highlight_value
from .traverser.facts_carousel import FactsCarousel

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
    search_term='',
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
            # deleted=deleted,
            search_term=search_term,
            activity=activity,
            category=category,
            # sort_col=sort_col,
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
            click_echo(_("Facts have been exported to: {path}".format(path=filepath)))
        elif to_format == 'tsv':
            writer = reports.TSVWriter(filepath)
            writer.write_report(facts)
            click_echo(_("Facts have been exported to: {path}".format(path=filepath)))
        elif to_format == 'ical':
            writer = reports.ICALWriter(filepath)
            writer.write_report(facts)
            click_echo(_("Facts have been exported to: {path}".format(path=filepath)))
        else:
            assert to_format == 'xml'
            writer = reports.XMLWriter(filepath)
            writer.write_report(facts)
            click_echo(_("Facts have been exported to: {path}".format(path=filepath)))

    # ***

    _export_facts(start, end)

# ***


def import_facts(
    controller,
    file_in=None,
    file_out=None,
    rule='',
    backup=True,
    leave_backup=False,
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
        new_facts, hydrate_errs = hydrate_facts(unprocessed_facts)
        must_hydrated_all_facts(hydrate_errs)
        raw_facts = copy.deepcopy(new_facts)
        must_complete_times(new_facts)
        must_not_conflict_existing(new_facts)
        prompt_and_save(new_facts, raw_facts, backup, file_out, rule, ask, yes, dry)

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
                msg = 'Weirdo, why are you redirecting STDIN *and* specifying a file?'
                click_echo(msg)
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
            click_echo(msg)
            sys.exit(1)
        return redirecting

    # ***

    def must_open_file(redirecting, file_in):
        if redirecting:
            f_in = sys.stdin
        else:
            f_in = file_in
        return f_in

    # ***

    def parse_facts_from_stream(input_f, ask, yes, dry):
        # Track current empty line run count, to know when to check if line
        # starts a new Fact. Keep at -1 until we've seen the first fact.
        bl_count = -1

        line_num = 0

        # Coalesce each Fact, line by line.
        current_fact_dict = None
        accumulated_fact = []
        unprocessed_facts = []

        for line in input_f:
            line_num += 1
            (
                bl_count, processed,
            ) = gobble_blank_or_continued(line, accumulated_fact, bl_count)
            if processed:
                continue
            fact_dict = gobble_if_not_new_fact(line, accumulated_fact, bl_count)
            if fact_dict is None:
                bl_count = 0
                continue
            fact_dict['line_num'] = line_num
            fact_dict['raw_meta'] = line
            if not accumulated_fact:
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
        elif re.match(r'^\s', line):
            controller.client_logger.debug(_('- Leading whitesp.:\n') + line.strip())
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
        ' )',
        re.IGNORECASE,
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
        hydrate_errs = []
        temp_id = -1
        for fact_dict, accumulated_fact in unprocessed_facts:
            log_warnings_and_context(fact_dict)
            hydrate_description(fact_dict, accumulated_fact)
            new_fact, err = create_from_parsed_fact(fact_dict)
            if new_fact:
                temp_id = add_new_fact(new_fact, temp_id, new_facts)
            else:
                hydrate_errs.append(err)
        return new_facts, hydrate_errs

    def log_warnings_and_context(fact_dict):
        if not fact_dict['warnings']:
            return
        fact_warnings = '\n  '.join(fact_dict['warnings'])
        display_dict = copy.copy(fact_dict)
        del display_dict['warnings']
        controller.client_logger.warning(
            prepare_log_msg(display_dict, fact_warnings)
        )

    def prepare_log_msg(fact_or_dict, msg_content):
        try:
            line_num = fact_or_dict['line_num']
            raw_meta = fact_or_dict['raw_meta']
        except TypeError:
            line_num = fact_or_dict.ephemeral['line_num']
            raw_meta = fact_or_dict.ephemeral['raw_meta']
        # NOTE: Using colors overrides logger's coloring, which is great!
        return _(
            '{}At line: {}{} / {}\n  {}“{}”{}\n  {}{}{}'
            .format(
                attr('bold'),
                line_num,
                attr('reset'),

                msg_content,

                fg('hot_pink_2'),
                raw_meta.strip(),
                attr('reset'),

                fg('grey_78'),
                fact_or_dict,
                attr('reset'),
            )
        )

    # Horizontal rule separator matches same character repeated at least thrice.
    # FIXME/2018-05-18: (lb): Document: HR is any repeated one of -, =, #, |.
    FACT_SEP_HR = re.compile(r'^([-=#|])\1{2}\1*$')

    def hydrate_description(fact_dict, accumulated_fact):
        # The first entry is the meta line, so ignore it.
        desc_lines = accumulated_fact[1:]
        # However, the user is allowed to start the description
        # on the meta line.
        if fact_dict['description']:
            # Don't forget the newline -- it got culled (strip()ped) on parse.
            desc_lines.insert(0, fact_dict['description'] + "\n")

        cull_factless_fact_separator(desc_lines)

        # desc_lines are already newlined.
        desc = ''.join(desc_lines).strip()

        fact_dict['description'] = desc

    def cull_factless_fact_separator(desc_lines):
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
            # Remove optional horizontal rule, which user
            # can use to visual separate lines in import file.
            desc_lines.pop()

        return desc_lines

    def create_from_parsed_fact(fact_dict):
        new_fact = None
        err_msg = None
        ephemeral = {
            'line_num': fact_dict['line_num'],
            'raw_meta': fact_dict['raw_meta'],
        }
        try:
            new_fact = Fact.create_from_parsed_fact(
                fact_dict, lenient=True, ephemeral=ephemeral,
            )
        except Exception as err:
            err_msg = prepare_log_msg(fact_dict, str(err))
        # (lb): Returning a tuple that smells like Golang: (fact, err, ).
        return new_fact, err_msg

    def add_new_fact(new_fact, temp_id, new_facts):
        if new_fact is None:
            return temp_id
        new_fact.pk = temp_id
        new_facts.append(new_fact)
        temp_id -= 1
        return temp_id

    def must_hydrated_all_facts(hydrate_errs):
        if not hydrate_errs:
            return
        for err_msg in hydrate_errs:
            controller.client_logger.error(err_msg)
        msg = (_(
            'Please fix your import data and try again.'
            ' See log output for details.'
        ))
        barf_and_exit(msg)

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
            msg_content = _(
                'Could not infer delta time “{}” for {}'
            ).format(delta_mins, which)
            conflict_msg = prepare_log_msg(fact, msg_content)
            conflicts.append((fact, None, conflict_msg, ))
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
        barf_and_exit(msg)

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
        click_echo()
        click_echo(_('  Fact being imported:'))
        click_echo(_('  ───────────────────'))
        click_echo(fact.friendly_diff(fact, truncate=True))
        click_echo()
        click_echo(_('  Impact on saved Fact:'))
        click_echo(_('  ────────────────────'))
        click_echo(original.friendly_diff(edited_fact))
        click_echo()

    # ***

    def prompt_and_save(new_facts, raw_facts, backup, file_out, rule, ask, yes, dry):
        backup_f = prepare_backup_file(backup)
        delete_backup = False
        inner_error = None
        try:
            prompt_persist(new_facts, raw_facts, backup_f, rule, ask, yes, dry)
            delete_backup = True
        except SystemExit as err:
            # Explicit sys.exit() from our code. The str(err)
            # is just the exit code #.
            raise
        except BaseException as err:
            # NOTE: Using BaseException, not just Exception, so that we
            #       always catch (KeyboardInterrupt, SystemExit), etc.
            # Don't cleanup backup file.
            traceback.print_exc()
            inner_error = str(err)
        finally:
            if not delete_backup:
                msg = 'Something horrible happened!'
                if inner_error is not None:
                    msg += _(' err: "{}"').format(inner_error)
                if backup_f:
                    msg += (
                        _("\nBut don't worry. A backup of edits was saved at: {}")
                        .format(backup_f.name)
                    )
                dob_in_user_exit(msg)
            cleanup_files(backup_f, file_out, delete_backup)

    # ***

    def prepare_backup_file(backup):
        if not backup:
            return None
        backup_path = get_import_ephemeral_backup_path()
        backup_f = None
        try:
            backup_f = open(backup_path, 'w')
        except Exception as err:
            msg = (
                'Failed to open temporary backup file at "{}": {}'
                .format(backup_path, str(err))
            )
            dob_in_user_exit(msg)
        return backup_f

    IMPORT_BACKUP_DIR = 'importer'

    def get_import_ephemeral_backup_path():
        backup_prefix = 'dob.import-'
        backup_tstamp = controller.now.strftime('%Y%m%d%H%M%S')
        backup_basename = backup_prefix + backup_tstamp
        backup_fullpath = get_appdirs_subdir_file_path(
            file_basename=backup_basename,
            dir_dirname=IMPORT_BACKUP_DIR,
            appdirs_dir=AppDirs.user_cache_dir,
        )
        return backup_fullpath

    def cleanup_files(backup_f, file_out, delete_backup):
        if backup_f:
            backup_f.close()
            if delete_backup:
                if not leave_backup:
                    os.unlink(backup_f.name)
                else:
                    click_echo(
                        _('Abandoned working backup at: {}')
                        .format(highlight_value(backup_f.name))
                    )
        # (lb): Click will close the file, but we can also cleanup first.
        if file_out and not dry:
            file_out.close()

    # ***

    def prompt_persist(new_facts, raw_facts, backup_f, rule, ask, yes, dry):
        okay = prompt_all(new_facts, raw_facts, backup_f, rule, ask, yes, dry)
        persist_facts(okay, new_facts, file_out, dry)

    # ***

    def prompt_all(new_facts, raw_facts, backup_f, rule, ask, yes, dry):
        if yes:
            return True

        backup_callback = write_facts_file(new_facts, backup_f, rule, dry)
        # Create the tmp file.
        backup_callback()

        facts_carousel = FactsCarousel(
            controller, new_facts, raw_facts, backup_callback, dry,
        )

        confirmed_all = facts_carousel.gallop()

        return confirmed_all

    # ***

    def persist_facts(confirmed_all, new_facts, file_out, dry):
        if not confirmed_all:
            return
        record_new_facts(new_facts, file_out, dry)
        celebrate(new_facts)

    def record_new_facts(new_facts, file_out, dry):
        for idx, fact in enumerate(new_facts):
            fact.pk = None  # So FactManager._add is called, not FactManager._update.
            persist_fact(fact, idx, file_out, dry)

    def persist_fact(fact, idx, file_out, dry):
        if not dry:
            # If user did not specify an output file, save to database
            # (otherwise, we may have been maintaining a temporary file).
            if not file_out:
                persist_fact_save(fact, dry)
            else:
                write_fact_block_format(file_out, fact, rule, idx)
        else:
            echo_block_header(_('Fresh Fact!'))
            click_echo()
            echo_fact(fact)
            click_echo()

    # ***

    def write_facts_file(new_facts, fact_f, rule, dry):
        def wrapper():
            if dry or not fact_f:
                return
            fact_f.seek(0)
            for idx, fact in enumerate(new_facts):
                write_fact_block_format(fact_f, fact, rule, idx)
            fact_f.flush()

        return wrapper

    def write_fact_block_format(fact_f, fact, rule, idx):
        write_fact_separator(fact_f, rule, idx)
        fact_f.write(
            fact.friendly_str(
                description_sep='\n\n',
                shellify=False,
                colorful=False,
            )
        )

    RULE_WIDTH = 76  # How wide to print the between-facts separator.

    def write_fact_separator(fact_f, rule, idx):
        if idx == 0:
            return
        fact_f.write('\n\n')
        if rule:
            fact_f.write('{}\n\n'.format(rule * RULE_WIDTH))

    def persist_fact_save(fact, dry):
        conflicts = []
        save_facts_maybe(controller, fact, conflicts, dry)
        if conflicts:
            print(conflicts)
            assert False  # ????

    # ***

    def celebrate(new_facts):
        click_echo('{}{}{}! {}'.format(
            attr('underlined'),
            _('Voilà'),
            attr('reset'),
            _('Saved {} facts.').format(highlight_value(len(new_facts))),
        ))

    # *** [export_facts] entry.

    _import_facts()

