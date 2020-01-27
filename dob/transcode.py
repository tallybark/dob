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

import copy
import re
import sys
from datetime import datetime, time, timedelta

from gettext import gettext as _

import click
from nark import reports
from nark.helpers.emphasis import attr, bg, fg
from nark.helpers.parsing import parse_factoid

from dob_viewer.traverser.placeable_fact import PlaceableFact

from . import __package_name__
from .clickux.echo_assist import barf_and_exit, click_echo, echo_block_header
from .clickux.query_assist import hydrate_activity, hydrate_category
from .cmds_list.fact import search_facts
from .create import prompt_and_save
from .helpers import highlight_value, prepare_log_msg
from .helpers.crude_progress import CrudeProgress
from .helpers.fix_times import (
    DEFAULT_SQUASH_SEP,
    mend_facts_times,
    must_complete_times,
    reduce_time_hint,
    then_extend_fact
)

__all__ = (
    'export_facts',
    'import_facts',
)


def export_facts(
    controller,
    to_format='csv',
    file_out=None,
    since=None,
    until=None,
    deleted=False,
    hidden=False,
    key=None,
    search_term='',
    filter_activity='',
    filter_category='',
    sort_order='desc',
    limit='',
    offset='',
):
    """
    Export all facts in the given timeframe in the format specified.

    Args:
        format (str): Format to export to.
            Valid options are: ``csv``, ``xml`` and ``ical``.
        since (datetime.datetime): Restrict to facts starting at this time or later.
        until (datetime.datetime): Restrict to facts ending no later than this time.

    Returns:
        None: If everything went alright.

    Raises:
        click.Exception: If format is not recognized.
    """

    def _export_facts(since, until):
        must_verify_format(to_format)

        since, until = resolve_since_until(since, until)

        filepath = resolve_filepath(file_out, to_format)

        activity = hydrate_activity(controller, filter_activity)
        category = hydrate_category(controller, filter_category)

        facts = search_facts(
            controller,
            key=key,
            since=since,
            until=until,
            # deleted=deleted,
            search_term=search_term,
            activity=activity,
            category=category,
            # sort_col=sort_col,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            # **kwargs
        )

        export_formatted(facts, filepath, to_format)

    def must_verify_format(to_format):
        accepted_formats = ['csv', 'tsv', 'ical', 'xml']
        # (lb): An old hamster-lib comment:
        #   [TODO]
        #   Once nark has a proper 'export' register available we should be able
        #   to streamline this.
        # (lb): I think the comment means that formats should be registered
        # with nark (like how plugins register). And then we wouldn't need
        # a hard-coded accepted_formats lookup.
        if to_format not in accepted_formats:
            message = _("Unrecocgnized export format received")
            controller.client_logger.info(message)
            raise click.ClickException(message)

    def resolve_since_until(since, until):
        if not since:
            since = None
        if not until:
            until = None
        return since, until

    def resolve_filepath(file_out, to_format):
        if file_out:
            filepath = file_out.format(format=to_format)
        else:
            filepath = ''  # Tell ReportWriter to use sys.stdout.
        return filepath

    def export_formatted(facts, filepath, to_format):
        writer = fetch_export_writer(filepath, to_format)
        writer.write_report(facts)
        writer_report_path(filepath, facts)

    def fetch_export_writer(filepath, to_format):
        if to_format == 'csv':
            writer = reports.CSVWriter(filepath)
        elif to_format == 'tsv':
            writer = reports.TSVWriter(filepath)
        elif to_format == 'ical':
            writer = reports.ICALWriter(filepath)
        else:
            assert to_format == 'xml'
            writer = reports.XMLWriter(filepath)
        return writer

    def writer_report_path(filepath, facts):
        if file_out == filepath:
            # If supplied filename is same as filepath, no need to
            # tell user. Otherwise, filepath was formed from, e.g.,
            # "export.{format}", so spit out formatted filename.
            return

        click_echo(_(
            "{n_facts} Facts were exported to {path}"
        ).format(
            n_facts=highlight_value(len(facts)),
            path=highlight_value(filepath),
        ))

    # ***

    _export_facts(since, until)

# ***


def import_facts(
    controller,
    file_in=None,
    file_out=None,
    rule='',
    backup=True,
    leave_backup=False,
    use_carousel=False,
    dry=False,
):
    """
    Import Facts from STDIN or a file.
    """

    # Bah. Progress is only useful if mend_facts_times calls insert_forcefully,
    # otherwise the import operation should be fast (at least for the 1Kish Fact
    # imports this author has ran). And insert_forcefully is only needed if the
    # Fact range being imported overlaps with existing Facts. Which it really
    # shouldn't, i.e., the use case is, I've been on vacation and Hamstering to
    # a file on my phone, and now I want that data imported into Hamster, which
    # will be strictly following the latest Fact saved in the store.
    progress = CrudeProgress(enabled=True)

    # MAYBE/2018-05-16 00:11: (lb): Parse whole file before prompting.
    #                               Allow --yes to work here, too?
    #                               Not sure...
    #   For now, we'll just read one fact at a time.

    def _import_facts():
        redirecting = must_specify_input(file_in)
        input_f = must_open_file(redirecting, file_in)
        raw_facts = parse_facts_from_stream(input_f)
        new_facts = must_hydrate_facts(raw_facts)
        conflicts = must_complete_times(controller, new_facts, progress=progress)
        controller.affirm(not conflicts)  # (lb): 2019-01-19: This happen?
        repair_shoulder_fact_times(new_facts, raw_facts)
        must_not_conflict_existing(new_facts)
        saved_facts = prompt_and_save(
            controller,
            edit_facts=new_facts,
            file_in=file_in,
            file_out=file_out,
            rule=rule,
            backup=backup,
            leave_backup=leave_backup,
            use_carousel=use_carousel,
            dry=dry,
            yes=False,
            progress=progress,
        )
        return saved_facts

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
            ).format(appname=__package_name__)
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

    def parse_facts_from_stream(input_f):
        # Track current empty line run count, to know when to check if line
        # starts a new Fact. Keep at -1 until we've seen the first fact.
        bl_count = -1

        line_num = 0

        # Coalesce each Fact, line by line.
        current_fact_dict = None
        accumulated_fact = []
        unprocessed_facts = []

        progress.click_echo_current_task(_('Parsing factoids...'))
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
            fact_dict['parsed_source.line_num'] = line_num
            fact_dict['parsed_source.line_raw'] = line
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

    # FIXME/2019-01-21: Document all the different usage, both in test, and README.
    # E.g., "then: I did this" should be same as "at +0: I did this"
    #   but if you specify start you don't need colon
    #       "then 2019-01-21 23:47 I did this" should also work...
    #   FIXME: Parse "then" expecting 1+ datetimes, or "then:" expecting none.
    #   FIXME: Parse "still" expecting 1+ datetimes, or "still:" expecting none.
    # FIXME: Three tests:
    #           ``still <time-spec> <desc>``
    #       vs. ``still: <desc>``
    #       vs. ``still blah``
    RE_TIME_HINT = re.compile(
        # SYNC_ME: RE_TIME_HINT, TIME_HINT_MAP, and @generate_add_fact_command's.
        r'^('
            # Skipping: Doesn't make sense: '(?P<verify_none>on|now)'
            # MAYBE/2019-01-22: Is "between" okay here?
            #   We don't have a Click alias for it, so
            #   there's a `dob from` command, but not `dob between`,
            #   so maybe we want to remove "between" from here.
            '(?P<verify_both>from|between)'
            '|(?P<verify_start>at)'  # noqa: E131
            '|(?P<verify_end>to|until)'
            '|(?P<verify_then_none>then:)'
            '|(?P<verify_then_some>then)'
            '|(?P<verify_still_none>still:)'
            '|(?P<verify_still_some>still)'
            # NOTE: Require colon postfix for options w/o time component.
            # NOTE: 'now' would be confusing and conflict with other usage,
            #       (at least I think it would?). E.g., do not do this:
            #         '|(?P<verify_after>after:|since:|next:|now:)'
            '|(?P<verify_after>after:|since:|next:)'
        ' )',  # NOTE The SPACE CHARACTER following THE DIRECTIVE!
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
                # Including the description is too verbose:
                #   'new fact_dict: {}'.format(fact_dict)
                # so let's make a complicated dictionary comprehension instead.
                'new fact_dict: {}'.format(
                    {
                        key: val if key != 'description'
                        else val[:10] + ((len(val) > 10) and '...' or '')
                        for key, val in fact_dict.items()
                    }
                )
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

        use_hint = reduce_time_hint(time_hint)

        fact_dict, err = parse_factoid(
            factoid=factoid,
            time_hint=use_hint,
            # MEH: (lb): Should we leave hash_stamps='#@' ?
            #   I sorta like using the proper tag symbol
            #   when not worried about shell interpolation.
            hash_stamps='#',
            # We'll handle errors ourselves, later, in bulk, either
            # `--ask`'ing the user for more Fact details, or barfing
            # all the errors and exiting.
            lenient=True,
        )

        fact_dict_set_time_hint(fact_dict, time_hint)

        return fact_dict, err

    # FIXME/DRY: See create.py/transcode.py.
    def fact_dict_set_time_hint(fact_dict, time_hint):
        fact_dict['time_hint'] = time_hint
        if time_hint in ('verify_after', 'verify_then_none', 'verify_still_none'):
            assert not fact_dict['start'] and not fact_dict['end']
            # (lb): How's this for a hack!?
            fact_dict['start'] = "+0"

    # ***

    def must_hydrate_facts(raw_facts):
        new_facts, hydrate_errs = hydrate_facts(raw_facts)
        must_hydrated_all_facts(hydrate_errs)
        return new_facts

    def hydrate_facts(raw_facts):
        new_facts = []
        hydrate_errs = []
        temp_id = -1
        progress.click_echo_current_task(_('Hydrating Facts...'))
        for fact_dict, accumulated_fact in raw_facts:
            add_hydration_warnings(fact_dict, hydrate_errs)
            hydrate_description(fact_dict, accumulated_fact)
            new_fact, err_msg = create_fact_from_parsed_dict(fact_dict)
            if new_fact:
                assert not err_msg
                time_hint = fact_dict['time_hint']
                temp_id = add_new_fact(new_fact, time_hint, temp_id, new_facts)
            else:
                assert not new_fact
                hydrate_errs.append(err_msg)
        return new_facts, hydrate_errs

    def add_hydration_warnings(fact_dict, hydrate_errs):
        if not fact_dict['warnings']:
            return
        fact_warnings = '\n  '.join(fact_dict['warnings'])
        display_dict = copy.copy(fact_dict)
        del display_dict['warnings']
        err_msg = prepare_log_msg(display_dict, fact_warnings)
        hydrate_errs.append(err_msg)

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

    def create_fact_from_parsed_dict(fact_dict):
        new_fact = None
        err_msg = None
        try:
            new_fact = PlaceableFact.create_from_parsed_fact(
                fact_dict,
                lenient=True,
                line_num=fact_dict['parsed_source.line_num'],
                line_raw=fact_dict['parsed_source.line_raw'],
            )
        except ValueError as err:
            err_msg = prepare_log_msg(fact_dict, str(err))
        # (lb): Returning a tuple that smells like Golang: (fact, err, ).
        return new_fact, err_msg

    def add_new_fact(new_fact, time_hint, temp_id, new_facts):
        if new_fact is None:
            return temp_id
        add_facts = maybe_squash_extend_prev(new_fact, time_hint, new_facts)
        for add_fact in add_facts:
            temp_id = add_new_fact_maybe(add_fact, temp_id, new_facts)
        return temp_id

    def maybe_squash_extend_prev(new_fact, time_hint, new_facts):
        if time_hint not in [
            'verify_end',
            'verify_then_none',
            'verify_then_some',
            'verify_still_none',
            'verify_still_some',
        ]:
            return [new_fact]
        return squash_extend_if_prev(new_fact, time_hint, new_facts)

    def squash_extend_if_prev(new_fact, time_hint, new_facts):
        prev_fact = new_facts[-1] if new_facts else None
        new_new_facts = squend_check_noop_or_extend(prev_fact, new_fact, time_hint)
        if new_new_facts is not None:
            return new_new_facts
        return squend_squash_or_extend(prev_fact, new_fact, time_hint, new_facts)

    def squend_check_noop_or_extend(prev_fact, new_fact, time_hint):
        if prev_fact is None:
            # First fact in import. Will check store later for boundary fact.
            return [new_fact]
        elif prev_fact.end is not None:
            return maybe_set_start_maybe_extend_prev(
                prev_fact, new_fact, time_hint,
            )
        elif prev_fact.start is None:
            return [new_fact]
        elif new_fact.start and new_fact.end:
            # This fact is a `then ... to`, so really just a `from/between`.
            return [new_fact]
        # E.g., prev_fact is at-fact, with no end; and new_fact is to-fact,
        # with no start. Return None, and caller will squend_squash_or_extend.
        assert not new_fact.deleted
        return None

    def squend_squash_or_extend(prev_fact, new_fact, time_hint, new_facts):
        squash_facts_maybe(new_fact, prev_fact)
        if not new_fact.deleted:
            return [new_fact]

        prev_or_new_fact = maybe_extend_fact(controller, prev_fact, time_hint)
        # Return None is prev fact was extended.
        if prev_or_new_fact is not new_fact:
            assert prev_or_new_fact is new_facts[-1]
        return [prev_or_new_fact] if prev_or_new_fact is new_fact else []

    def maybe_set_start_maybe_extend_prev(prev_fact, new_fact, time_hint):
        if time_hint in [
            'verify_then_none',
            'verify_then_some',
            'verify_still_none',
            'verify_still_some',
        ]:
            extended_fact = then_extend_fact(controller, prev_fact)
            extended_fact.end = new_fact.start
            if time_hint in ['verify_still_none', 'verify_still_some']:
                new_fact.activity = prev_fact.activity
                new_fact.tags = list(prev_fact.tags)
            return [extended_fact, new_fact]
        else:
            assert time_hint == 'verify_end'  # ``to``
            assert new_fact.start is None
            # Fix it in post, er, fix_delta_time_relative.
            new_fact.start = "+0"
            return [new_fact]

    def squash_facts_maybe(new_fact, prev_fact):
        assert new_fact.pk is None
        # 2018-06-30: (lb): Ug. Why does this squash logic seem so forced?
        new_fact.pk = -1  # To appease squash().
        prev_fact.squash(new_fact, DEFAULT_SQUASH_SEP)
        new_fact.pk = None

    def maybe_extend_fact(controller, new_fact, time_hint):
        if time_hint not in ['verify_then_none', 'verify_then_some']:
            return new_fact
        return then_extend_fact(controller, new_fact)

    def add_new_fact_maybe(new_fact, temp_id, new_facts):
        if not new_fact or new_fact.deleted:
            return temp_id
        new_fact.pk = temp_id
        new_facts.append(new_fact)
        temp_id -= 1
        return temp_id

    # ***

    def must_hydrated_all_facts(hydrate_errs):
        if not hydrate_errs:
            return
        for err_msg in hydrate_errs:
            click_echo()
            click_echo(err_msg)
            click_echo()
        msg = (_(
            'Please fix your import data and try again.'
            ' Scroll up for details.'
        ))
        barf_and_exit(msg)

    # ***

    def repair_shoulder_fact_times(new_facts, raw_facts):
        # If user did not specify first fact start time, and/or last fact's
        # end time, fix_times.must_complete_times will have assigned times.
        # Note that there are a number of places where two facts may be merged:
        # - Earlier during this import task, under add_new_fact(), squash and
        #   extend code is used.
        # - Here, but just on the first and final import facts, to sew them
        #   into the fabric of the facts in the store.
        # - In many of the fix_times functions:
        #     unite_and_stretch, insert_forcefully, and resolve_overlapping.
        # (lb): Maybe someday we can combine this code better. The way different
        #   features were grown, however, resulted in squash code in a few places.

        if not new_facts[0].start:
            # User did not specify first fact's start, and we did not find
            # an antecedent fact in the data store, so, what? Set earliest
            # time ever? Clip to midnight that day?
            new_facts[0].start = datetime.combine(new_facts[0].end, time.min)
            if new_facts[0].start == new_facts[0].end:
                new_facts[0].start = new_facts[0].end - timedelta(days=1)
        elif not raw_facts[0][0]['start']:
            new_facts[0].start = None

        controller.affirm(new_facts[-1].end)
        if not raw_facts[-1][0]['end']:
            new_facts[-1].end = None

    # ***

    def must_not_conflict_existing(new_facts):
        # (lb): Yuck. Sorry about this. Totally polluting what was a small
        # function with lots of progress-output overhead.
        task_descrip = _('Verifying times nonconflicting')
        term_width, dot_count, fact_sep = progress.start_crude_progressor(task_descrip)

        could_be_more = fix_range_conflicts_easy(new_facts)

        all_conflicts = []
        for idx, fact in enumerate(new_facts):
            term_width, dot_count, fact_sep = progress.step_crude_progressor(
                task_descrip, term_width, dot_count, fact_sep,
            )

            if idx == len(new_facts) - 1:
                time_hint = 'verify_last'
            elif idx == 0 and not fact.start:
                time_hint = 'verify_end'
            else:
                time_hint = 'verify_both'

            conflicts = mend_facts_times(
                controller,
                fact,
                time_hint=time_hint,
                skip_store=not could_be_more,
            )
            assert not fact.deleted  # Only on squash, which shouldn't happen.

            if conflicts:
                all_conflicts.append((fact, conflicts,))

        progress.click_echo_current_task('')

        # Handling anything other than the ongoing fact seems beyond the
        # scope of the import function. dob is not a conflict resolution
        # application!
        barf_on_overlapping_facts_old(all_conflicts)

    def fix_range_conflicts_easy(new_facts):
        """
        Check time range of facts being imported against store.
        Returns True if time range overlaps with any existing facts;
        the ongoing fact only overlaps if it starts during the time
        range.
        """
        def _fix_range_conflicts_easy():
            first_time = new_facts[0].start or new_facts[0].end
            final_time = new_facts[-1].end or new_facts[-1].start
            # There's a compelling function, controller.facts.strictly_during,
            # but it ignores overlapping shoulder facts (and the ongoing fact).
            # Check instead manually against the fact before the last time,
            # and also the fact after the first time.
            ante_fact = controller.facts.antecedent(ref_time=final_time)
            seqt_fact = controller.facts.subsequent(ref_time=first_time)
            check_all = False
            check_all = easy_fix_final(check_all, seqt_fact, final_time)
            check_all = easy_fix_first(check_all, ante_fact, first_time)
            return check_all

        def easy_fix_final(check_all, seqt_fact, final_time):
            if not seqt_fact:
                return check_all
            if seqt_fact.start < final_time:
                # Fact found in store ends after first_time,
                #  and starts before final_time.
                return True
            if new_facts[-1].end:
                # The final import fact ends on or before
                #  the start of the after-fact.
                return check_all
            # If here, the final import fact is endless.
            # Obvious path is to end it using start of first fact after.
            if new_facts[-1].start == seqt_fact.start:
                # The ongoing final import fact starts at same time as final store fact.
                if not seqt_fact.end:
                    # To test this path: have ongoing fact in import with same start as
                    # ongoing fact in the store.
                    # (lb): We could end the existing fact, making it momentaneous,
                    # but that seems extreme; feels more natural to combine the 2
                    # facts. -- Alternatively, we could toss an error. But I could
                    # see just combining the 2 facts, seems like a pretty rare case
                    # anyway.
                    seqt_fact.squash(new_facts[-1], DEFAULT_SQUASH_SEP)
                    new_facts[-1] = seqt_fact
                    return check_all
                if not controller.config['time.allow_momentaneous']:
                    # User is not allowing momentaneous Facts, so disallow.
                    # Return True and we'll run thorough conflict check
                    # (and exit on error instead of continuing import).
                    return True
                # The final import fact is endless, but it conflicts with a
                # fact in the store. And the user is down with momentaneous
                # so crown it as such.
                # FIXME/2019-01-20 01:09: TESTME: Momentaneous feature.
                #  (I think it works in db and code, but no way for user
                #  to view in the UI. So they're essentially really well
                #  hidden. Which is a design feature, maybe?)
            new_facts[-1].end = seqt_fact.start
            return check_all

        def easy_fix_first(check_all, ante_fact, first_time):
            if not ante_fact:
                return check_all
            if ante_fact.end:
                if not new_facts[0].start:
                    # I.e., a to-Fact is 1st Fact in import,
                    #   and final Fact in store is closed.
                    new_facts[0].start = ante_fact.end
                if ante_fact.end > first_time:
                    # Fact from store starts before final_time,
                    #  and ends after first_time.
                    return True
                # else, first fact found before final_time
                #        ends before first_time.
                return check_all
            # If here, it's the ongoing fact.
            ongoing = controller.facts.endless()
            controller.affirm(ante_fact == ongoing[0])
            if new_facts[0].start:
                ante_fact.end = new_facts[0].start
                new_facts.insert(0, ante_fact)
            else:
                # Squash store's ongoing and import's first.
                ante_fact.squash(new_facts[0], DEFAULT_SQUASH_SEP)
                new_facts[0] = ante_fact

            return check_all

        return _fix_range_conflicts_easy()

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

    _import_facts()

