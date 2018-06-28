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
from io import open

from nark import Fact, reports
from nark.helpers.colored import fg, bg, attr
from nark.helpers.parsing import parse_factoid

from . import __appname__
from .cmd_common import (
    barf_and_exit,
    echo_block_header,
    hydrate_activity,
    hydrate_category
)
from .cmd_config import get_appdirs_subdir_file_path, AppDirs
from .cmds_list.fact import search_facts
from .create import echo_fact, save_facts_maybe
from .helpers import (
    click_echo,
    dob_in_user_exit,
    highlight_value,
    prepare_log_msg
)
from .helpers.crude_progress import CrudeProgress
from .helpers.fix_times import mend_facts_times, must_complete_times
from .traverser.facts_carousel import FactsCarousel

__all__ = ['export_facts', 'import_facts']


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
        # [TODO]
        # Once nark has a proper 'export' register available we should be able
        # to streamline this.
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
    ask=False,
    yes=False,
    dry=False,
):
    """
    Import Facts from STDIN or a file.
    """
    progress = CrudeProgress(enabled=True)

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
        must_complete_times(controller, new_facts)
        must_not_conflict_existing(new_facts)
        prompt_and_save(new_facts, raw_facts, backup, file_out, rule, ask, yes, dry)
        return new_facts

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
        progress.click_echo_current_task(_('Hydrating Facts...'))
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

    def must_not_conflict_existing(new_facts):
        # (lb): Yuck. Sorry about this. Totally polluting what was a small
        # function with lots of progress-output overhead.
        task_descrip = _('Verifying times nonconflicting')
        term_width, dot_count, fact_sep = progress.start_crude_progressor(task_descrip)

        all_conflicts = []
        for fact in new_facts:
            term_width, dot_count, fact_sep = progress.step_crude_progressor(
                task_descrip, term_width, dot_count, fact_sep,
            )

            conflicts = mend_facts_times(controller, fact, time_hint='verify_both')
            if conflicts:
                all_conflicts.append((fact, conflicts,))

        progress.click_echo_current_task('')

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
        task_descrip = _('Saving facts')
        term_width, dot_count, fact_sep = progress.start_crude_progressor(task_descrip)

        for idx, fact in enumerate(new_facts):
            term_width, dot_count, fact_sep = progress.step_crude_progressor(
                task_descrip, term_width, dot_count, fact_sep,
            )

            fact.pk = None  # So FactManager._add is called, not FactManager._update.
            persist_fact(fact, idx, file_out, dry)

        progress.click_echo_current_task('')

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

