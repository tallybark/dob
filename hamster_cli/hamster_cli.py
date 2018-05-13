# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

"""A time tracker for the command line. Utilizing the power of hamster-lib."""


from __future__ import absolute_import, unicode_literals

import datetime
import logging
import os
import sys
from collections import namedtuple
from gettext import gettext as _

import pyparsing as pp

import click
import hamster_lib
from six import string_types

from hamster_cli import __version__ as hamster_cli_version
from hamster_cli import __appname__ as hamster_cli_appname
from hamster_lib import __version__ as hamster_lib_version
from hamster_lib import Fact, HamsterControl, reports
from hamster_lib.helpers import time as time_helpers
from hamster_lib.helpers import logging as logging_helpers

from . import help_strings
from .cmd_config import get_config, get_config_instance, get_config_path
from helpers.ascii_table import generate_table

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True


# ***
# *** HamsterControl Controller.
# ***

class Controller(HamsterControl):
    """A custom controller that adds config handling on top of its regular functionality."""

    def __init__(self):
        """Instantiate controller instance and adding client_config to it."""
        lib_config, client_config = get_config(get_config_instance())
        self._verify_args(lib_config)
        super(Controller, self).__init__(lib_config)
        self.client_config = client_config

    def _verify_args(self, lib_config):
        # *cough*hack!*cough*”
        # Because invoke_without_command, we allow command-less hamster
        #   invocations. For one such invocation -- murano -v -- tell the
        #   store not to log.
        # Also tell the store not to log if user did not specify anything,
        #   because we'll show the help/usage (which Click would normally
        #   handle if we hadn't tampered with invoke_without_command).
        if (
            (len(sys.argv) == 1) or
            ((len(sys.argv) == 2) and (sys.argv[1] in ('-v', 'version')))
        ):
            lib_config['sql_log_level'] = 'WARNING'
        elif len(sys.argv) == 1:
            # Because invoke_without_command, now we handle command-less
            # deliberately ourselves.
            pass


pass_controller = click.make_pass_decorator(Controller, ensure=True)


# ***
# *** Version command helper.
# ***

def _hamster_version():
    vers = '{} version {}\nhamster-lib version {}'.format(
        hamster_cli_appname,
        hamster_cli_version,
        hamster_lib_version,
    )
    return vers


# ***
# *** One Group to rule them all.
# ***

# (lb): Use invoke_without_command so `hamster -v` works, otherwise click's
# Group (MultiCommand ancestor) does not allow it ('Missing command.').
@click.group(
    invoke_without_command=True, help=help_strings.RUN_HELP,
)
@click.version_option(message=_hamster_version())
@click.option('-v', is_flag=True, help=help_strings.VERSION_HELP)
@pass_controller
@click.pass_context
# NOTE: @click.group transforms this func. definition into a callback that
#       we use as a decorator for the top-level commands (see: @run.command).
def run(ctx, controller, v):
    """General context run right before any of the commands."""
    _run(ctx, controller, show_version=v)


def _run(ctx, controller, show_version):
    """Make sure that loggers are setup properly."""
    _run_handle_paging(controller)
    _run_handle_banner()
    _run_handle_version(show_version, ctx)
    _run_handle_without_command(ctx)
    _setup_logging(controller)


# ***
# *** Ye rote version command.
# ***

@run.command(help=help_strings.VERSION_HELP)
def version():
    """Show version information."""
    _version()


def _version():
    """Show version information."""
    click.echo(_hamster_version())


# ***
# *** Command: SEARCH.
# ***

@run.command(help=help_strings.SEARCH_HELP)
@click.argument('search_term', nargs=-1, default=None)
# MAYBE/2018-05-05: (lb): Restore the time_range arg scientificsteve removed:
#  @click.argument('time_range', default='')
@click.option('-s', '--start', help='The start time string (e.g. "2017-01-01 00:00").')
@click.option('-e', '--end', help='The end time string (e.g. "2017-02-01 00:00").')
@click.option('-a', '--activity', help="The search string applied to activity names.")
@click.option('-c', '--category', help="The search string applied to category names.")
@click.option('-t', '--tag', help='The tags search string (e.g. "tag1 AND (tag2 OR tag3)".')
@click.option('-d', '--description',
              help='The description search string (e.g. "string1 OR (string2 AND string3).')
@click.option('-k', '--key', help='The database key of the fact.')
@pass_controller
def search(controller, start, end, activity, category, tag, description, key, search_term):
    """Fetch facts matching certain criteria."""
    # [FIXME]
    # Check what we actually match against.
    # NOTE: (lb): Before scientificsteve added all the --options, the
    #       original command accepted a search_term and a time_range,
    #       e.g.,
    #
    #         @click.argument('search_term', default='')
    #         @click.argument('time_range', default='')
    #         def search(controller, search_term, time_range):
    #           return _search(controller, search_term, time_range)
    #           # And then the table and click.echo were at the bottom of
    #           # _search! And I'm not sure why they were moved here....
    #
    #       MAYBE: Restore supprt for time_range, i.e., let user specify
    #       2 positional args in addition to any number of options. And
    #       figure out why the generate-table and click.echo were moved
    #       here?
    if search_term:
        description = description or ''
        description += ' AND ' if description else ''
        description += ' AND '.join(search_term)
    results = _search(controller, start, end, activity, category, tag, description, key)
    table, headers = _generate_facts_table(results)
    click.echo(generate_table(table, headers=headers))


def _search(
    controller,
    start=None,
    end=None,
    activity=None,
    category=None,
    tag=None,
    description=None,
    key=None,
):
    """
    Search facts machting given timerange and search term. Both are optional.

    Matching facts will be printed in a tabular representation.

    Make sure that arguments are converted into apropiate types before passing
    them on to the backend.

    We leave it to the backend to first parse the timeinfo and then complete any
    missing data based on the passed config settings.

    Args:
        search_term: Term that need to be matched by the fact in order to be considered a hit.
        time_range: Only facts within this timerange will be considered.
        tag: ...
    """

    # FIXME/2018-05-05: (lb): This is from the scientificsteve PR that adds tags:
    #   DRY: Refactor this code; there is a lot of copy-paste code.
    def search_facts(tree, search_list, search_attr, search_sub_attr=None):
        '''
        '''
        def search_value(fact):
            if search_attr == 'description':
                return getattr(fact, search_attr)
            else:
                return getattr(fact, search_attr).name

        if len(tree) == 1:
            if isinstance(tree[0], string_types):
                l_term = tree[0]
                if search_sub_attr:
                    search_list = [
                        fact for fact in search_list if l_term.lower()
                        in getattr(getattr(fact, search_attr), search_sub_attr).lower()
                    ]
                else:
                    search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and l_term.lower() in search_value(fact).lower()
                    ]
            else:
                search_list = search_facts(tree[0], search_list, search_attr, search_sub_attr)

        if len(tree) == 2:
            # This is the NOT operator.
            op = tree[0]
            r_term = tree[1]
            if isinstance(r_term, string_types):
                if search_sub_attr:
                    r_search_list = [
                        fact for fact in search_list if r_term.lower()
                        in getattr(search_value(fact), search_sub_attr).lower()
                    ]
                else:
                    r_search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and r_term.lower() in search_value(fact).lower()
                    ]
            else:
                r_search_list = search_facts(r_term, search_list, search_attr, search_sub_attr)
            search_list = [x for x in search_list if x not in r_search_list]

        elif len(tree) == 3:
            l_term = tree[0]
            r_term = tree[2]
            op = tree[1]

            if isinstance(l_term, string_types):
                if search_sub_attr:
                    l_search_list = [
                        fact for fact in search_list if l_term.lower()
                        in getattr(search_value(fact), search_sub_attr).lower()
                    ]
                else:
                    l_search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and l_term.lower() in search_value(fact).lower()
                    ]
            else:
                l_search_list = search_facts(l_term, search_list, search_attr, search_sub_attr)

            if isinstance(r_term, string_types):
                if search_sub_attr:
                    r_search_list = [
                        fact for fact in search_list if r_term.lower()
                        in getattr(search_value(fact), search_sub_attr).lower()
                    ]
                else:
                    r_search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and r_term.lower() in search_value(fact).lower()
                    ]
            else:
                r_search_list = search_facts(r_term, search_list, search_attr, search_sub_attr)

            if op == 'AND':
                search_list = [x for x in l_search_list if x in r_search_list]
            elif op == 'OR':
                search_list = l_search_list
                search_list.extend(r_search_list)

        return search_list

    # FIXME/2018-05-05: (lb): This is from the scientificsteve PR that adds tags:
    #   DRY: Refactor this code; there is a lot of copy-paste code.
    def search_tags(tree, search_list):
        '''
        '''
        if len(tree) == 1:
            if isinstance(tree[0], string_types):
                l_term = tree[0]
                search_list = [
                    fact for fact in search_list if l_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                search_list = search_tags(tree[0], search_list)
        elif len(tree) == 2:
            # This is the NOT operator.
            op = tree[0]
            r_term = tree[1]
            if isinstance(r_term, string_types):
                r_search_list = [
                    fact for fact in search_list if r_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                r_search_list = search_tags(r_term, search_list)

            search_list = [x for x in search_list if x not in r_search_list]
        elif len(tree) == 3:
            l_term = tree[0]
            r_term = tree[2]
            op = tree[1]

            if isinstance(l_term, string_types):
                l_search_list = [
                    fact for fact in search_list if l_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                l_search_list = search_tags(l_term, search_list)

            if isinstance(r_term, string_types):
                r_search_list = [
                    fact for fact in search_list if r_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                r_search_list = search_tags(r_term, search_list)

            if op == 'AND':
                search_list = [x for x in l_search_list if x in r_search_list]
            elif op == 'OR':
                search_list = l_search_list
                search_list.extend(r_search_list)

        return search_list

    # (lb): Hahaha: end of inline defs. Now we start the _search method!

    # NOTE: (lb): ProjectHamster PR #176 by scientificsteve adds search --options
    #       but remove the two positional parameters.
    #
    #       Here's what the fcn. use to look like; I'll delete this comment
    #       and code once I'm more familiar with the project and am confident
    #       nothing here is broke (because I already found a few things! and
    #       I might want to just revert some parts of the PR so I can move on
    #       with life (but keep parts of the PR I like, like tags support!)).
    #
    if False:  # removed by scientificsteve
        def _search(controller, search_term, time_range):
            # [FIXME]
            # As far as our backend is concerned search_term as well as time range are
            # optional. If the same is true for legacy hamster-cli needs to be checked.
            if not time_range:
                start, end = (None, None)
            else:
                # [FIXME]
                # This is a rather crude fix. Recent versions of ``hamster-lib`` do not
                # provide a dedicated helper to parse *just* time(ranges) but expect a
                # ``raw_fact`` text. In order to work around this we just append
                # whitespaces to our time range argument which will qualify for the
                # desired parsing.
                # Once raw_fact/time parsing has been refactored in hamster-lib, this
                # should no longer be needed.
                time_range = time_range + '  '
                timeinfo = time_helpers.extract_time_info(time_range)[0]
                start, end = time_helpers.complete_timeframe(timeinfo, controller.config)
            # (lb): In lieu of filter_term, which justs searches facts,
            # scientificsteve switched to `hamster-cli search --description foo`.
            results = controller.facts.get_all(filter_term=search_term, start=start, end=end)
            return results
    # end: disabled code...

    if key:
        results = [controller.facts.get(pk=key), ]
    else:
        # Convert the start and time strings to datetimes.
        if start:
            start = time_helpers.parse_time(start)
        if end:
            end = time_helpers.parse_time(end)

        results = controller.facts.get_all(start=start, end=end)

        # (lb): scientificsteve's PR adds these if's, but they seem wrong,
        # i.e., if you specify --activity and --category, then only
        # category matches are returned! But I don't care too much,
        # because I use hamster_briefs for searching and reports!
        # Granted, it's coupled to SQLite3, but that's probably easy
        # to fix, and I don't care; SQLite3 is perfectly fine. I have
        # no idea why SQLAlchemy was a priority for the redesign.
        #
        # Also: It looks like we post-processing database results?
        # Wouldn't it be better to craft the SQL query to do the
        # filtering? Another reason I like hamster_briefs so much better!

        # FIXME/2018-05-05: (lb): The next 4 if-blocks are from the scientificsteve PR
        #   that adds tags: DRY: Refactor this code; there is a lot of copy-paste code.

        if activity:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("NOT", 1, pp.opAssoc.RIGHT, ),
                                                 ("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(activity)

            results = search_facts(search_tree, results, 'activity', 'name')

        if category:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(category)

            results = search_facts(search_tree, results, 'category', 'name')

        if tag:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("NOT", 1, pp.opAssoc.RIGHT, ),
                                                 ("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(tag)

            results = search_tags(search_tree, results)

        if description:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(description)

            results = search_facts(search_tree, results, 'description')

    return results


# ***
# *** Command: LIST [facts].
# ***

@run.command(help=help_strings.LIST_HELP)
@click.option('-s', '--start', help='The start time string (e.g. "2017-01-01 00:00").')
@click.option('-e', '--end', help='The end time string (e.g. "2017-02-01 00:00").')
@pass_controller
def list(controller, start, end):
    """List all facts within a timerange."""
    results = _search(controller, start=start, end=end)
    table, headers = _generate_facts_table(results)
    click.echo(generate_table(table, headers=headers))


# ***
# *** Command: INSERT [fact].
# ***

@run.command(help=help_strings.START_HELP)
@click.argument('raw_fact')
@click.argument('start', default='')
@click.argument('end', default='')
@pass_controller
def start(controller, raw_fact, start, end):
    """Start or add a fact."""
    # [FIXME]
    # The original semantics do not work anymore. As we make a clear difference
    # between *adding* a (complete) fact and *starting* a (ongoing) fact.
    # This needs to be reflected in this command.
    _start(controller, raw_fact, start, end)


def _start(controller, raw_fact, start='', end=''):
    """
    Start or add a fact.

    Args:
        raw_fact: ``raw_fact`` containing information about the Fact to be started. As an absolute
            minimum this must be a string representing the 'activityname'.
        start (optional): When does the fact start?
        end (optional): When does the fact end?

    Returns:
        None: If everything went alright.

    Note:
        * Whilst it is possible to pass timeinformation as part of the ``raw_fact`` as
            well as dedicated ``start`` and ``end`` arguments only the latter will be represented
            in the resulting fact in such a case.
    """
    fact = Fact.create_from_raw_fact(raw_fact)

    # Explicit trumps implicit!
    if start:
        fact.start = time_helpers.parse_time(start)
    if end:
        fact.end = time_helpers.parse_time(end)

    if not fact.end:
        # We seem to want to start a new tmp fact
        # Neither the raw fact string nor an additional optional end time have
        # been passed.
        # Until we decide wether to split this into start/add command we use the
        # presence of any 'end' information as indication of the users intend.
        tmp_fact = True
    else:
        tmp_fact = False

    # We complete the facts times in both cases as even an new 'ongoing' fact
    # may be in need of some time-completion for its start information.

    # Complete missing fields with default values.
    # legacy hamster_cli seems to have a different fallback behaviour than
    # our regular backend, in particular the way 'day_start' is handled.
    # For maximum consistency we use the backends unified ``complete_timeframe``
    # helper instead. If behaviour similar to the legacy hamster-cli is desired,
    # all that seems needed is to change ``day_start`` to '00:00'.

    # The following is needed becauses start and end may be ``None``.
    if not fact.start:
        # No time information has been passed at all.
        fact.start = datetime.datetime.now()

    else:
        # We got some time information, which may be incomplete however.
        if not fact.end:
            end_date = None
            end_time = None
        else:
            end_date = fact.end.date()
            end_time = fact.end.time()

        timeframe = time_helpers.TimeFrame(
            fact.start.date(), fact.start.time(), end_date, end_time, None)
        fact.start, fact.end = time_helpers.complete_timeframe(timeframe, controller.config)

    if tmp_fact:
        # Quick fix for tmp facts. that way we can use the default helper
        # function which will autocomplete the end info as well.
        # Because of our use of ``complete timeframe our 'ongoing fact' may have
        # received an ``end`` value now. In that case we reset it to ``None``.
        fact.end = None

    controller.client_logger.debug(_(
        "New fact instance created: {fact}".format(fact=fact)
    ))
    fact = controller.facts.save(fact)


@run.command(help=help_strings.STOP_HELP)
@pass_controller
def stop(controller):
    """Stop tracking current fact. Saving the result."""
    _stop(controller)


def _stop(controller):
    """
    Stop cucrrent 'ongoing fact' and save it to the backend.

    Returns:
        None: If successful.

    Raises:
        ValueError: If no *ongoing fact* can be found.
    """
    try:
        fact = controller.facts.stop_tmp_fact()
    except ValueError:
        message = _(
            "Unable to continue temporary fact. Are you sure there is one?"
            "Try running *current*."
        )
        raise click.ClickException(message)
    else:
        #message = '{fact} ({duration} minutes)'.format(
        #            fact=str(fact), duration=fact.get_string_delta())
        start = fact.start.strftime("%Y-%m-%d %H:%M")
        end = fact.end.strftime("%Y-%m-%d %H:%M")
        fact_string = u'{0:s} to {1:s} {2:s}@{3:s}'.format(
            start, end, fact.activity.name, fact.category.name
        )
        message = "Stopped {fact} ({duration} minutes).".format(
            fact=fact_string, duration=fact.get_string_delta()
        )
        controller.client_logger.info(_(message))
        click.echo(_(message))


# ***
# *** Command: CANCEL [current fact].
# ***

@run.command(help=help_strings.CANCEL_HELP)
@pass_controller
def cancel(controller):
    """Cancel 'ongoing fact'. E.g stop it without storing in the backend."""
    _cancel(controller)


def _cancel(controller):
    """
    Cancel tracking current temporary fact, discaring the result.

    Returns:
        None: If success.

    Raises:
        KeyErŕor: No *ongoing fact* can be found.
    """
    try:
        controller.facts.cancel_tmp_fact()
    except KeyError:
        message = _("Nothing tracked right now. Not doing anything.")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    else:
        message = _("Tracking canceled.")
        click.echo(message)
        controller.client_logger.debug(message)


# ***
# *** Command: REMOVE [facts? really??].
# ***

# (lb): This is a scientificsteve command: Beware!
# - It is not tested.
# - This is wrong, for one:
#     help=help_strings.EXPORT_HELP
#   Should be, i.e.,
#     help=help_strings.REMOVE_HELP
@run.command(help=help_strings.EXPORT_HELP)
@click.option('-s', '--start', help='The start time string (e.g. "2017-01-01 00:00").')
@click.option('-e', '--end', help='The end time string (e.g. "2017-02-01 00:00").')
@click.option('-a', '--activity', help="The search string applied to activity names.")
@click.option('-c', '--category', help="The search string applied to category names.")
@click.option('-t', '--tag', help='The tags search string (e.g. "tag1 AND (tag2 OR tag3)".')
@click.option('-d', '--description',
              help='The description search string (e.g. "string1 OR (string2 AND string3).')
@click.option('-k', '--key', help='The database key of the fact.')
@pass_controller
def remove(controller, start, end, activity, category, tag, description, key):
    """Export all facts of within a given timewindow to a file of specified format."""
    facts = _search(controller, start, end, activity, category, tag, description, key)
    table, headers = _generate_facts_table(facts)
    click.echo(generate_table(table, headers=headers))
    if click.confirm('Do you really want to delete the facts listed above?', abort=True):
        for cur_fact in facts:
            controller.facts.remove(cur_fact)


# ***
# *** Command: TAG [list or remove... both in same cmd??].
# ***

# (lb): This is a scientificsteve command: Beware!
# - It is not tested.
# - This is wrong, for one:
#     help=help_strings.EXPORT_HELP
#   Should be, i.e.,
#     help=help_strings.TAG_HELP
@run.command(help=help_strings.EXPORT_HELP)
@click.argument('tag_name', nargs=1, default=None)
@click.option('-s', '--start', help='The start time string (e.g. "2017-01-01 00:00").')
@click.option('-e', '--end', help='The end time string (e.g. "2017-02-01 00:00").')
@click.option('-a', '--activity', help="The search string applied to activity names.")
@click.option('-c', '--category', help="The search string applied to category names.")
@click.option('-t', '--tag', help='The tags search string (e.g. "tag1 AND (tag2 OR tag3)".')
@click.option('-d', '--description',
              help='The description search string (e.g. "string1 OR (string2 AND string3).')
@click.option('-k', '--key', help='The database key of the fact.')
@click.option('-r', '--remove', is_flag=True,
              help='Set this flag to remove the specified tag_name from the selected facts.')
@pass_controller
def tag(controller, tag_name, start, end, activity, category, tag, description, key, remove):
    """Export all facts of within a given timewindow to a file of specified format."""
    facts = _search(controller, start, end, activity, category, tag, description, key)
    table, headers = _generate_facts_table(facts)
    click.echo(generate_table(table, headers=headers))

    if remove:
        if click.confirm(
            'Do you really want to REMOVE the tag #%s to the facts listed above?' % (tag_name,),
            abort=True
        ):
            for cur_fact in facts:
                cur_fact.tags = [x for x in cur_fact.tags if x.name != tag_name]
                controller.facts._update(cur_fact)
    else:
        if click.confirm(
            'Do you really want to ADD the tag #%s to the facts listed above?' % (tag_name,),
            abort=True,
        ):
            for cur_fact in facts:
                cur_fact.tags.append(hamster_lib.Tag(name=tag_name))
                controller.facts._update(cur_fact)


# (lb): This is a scientificsteve command. Take it with a grain of salt.
# - It is not tested.
# - This is wrong, for one:
#     help=help_strings.EXPORT_HELP
#   Should be, i.e.,
#     help=help_strings.EDIT_HELP
@run.command(help=help_strings.EXPORT_HELP)
@click.argument('key', nargs=1)
@click.option('-s', '--start', help='The new start time string (e.g. "2017-01-01 00:00").')
@click.option('-e', '--end', help='The new end time string (e.g. "2017-02-01 00:00").')
@click.option('-a', '--activity', help="The new activity.")
@click.option('-c', '--category', help="The new category.")
@click.option('-d', '--description', help='The new description.')
@pass_controller
def edit(controller, key, start, end, activity, category, description):
    """Export all facts of within a given timewindow to a file of specified format."""
    fact = controller.facts.get(pk=key)

    if fact:
        if start:
            start = time_helpers.parse_time(start)
            fact.start = start

        if end:
            end = time_helpers.parse_time(end)
            fact.end = end

        if activity and category:
            fact.activity = hamster_lib.Activity(name=activity, category=category)
        elif activity or category:
            click.echo('Please specify an activity AND a category.')

        if description:
            fact.description = description

        controller.facts._update(fact)


# ***
# *** Command: EXPORT [facts].
# ***

@run.command(help=help_strings.EXPORT_HELP)
@click.argument('format', nargs=1, default='csv')
@click.argument('start', nargs=1, default='')
@click.argument('end', nargs=1, default='')
@click.option('-a', '--activity', help="The search string applied to activity names.")
@click.option('-c', '--category', help="The search string applied to category names.")
@click.option('-t', '--tag', help='The tags search string (e.g. "tag1 AND (tag2 OR tag3)".')
@click.option('-d', '--description',
              help='The description search string (e.g. "string1 OR (string2 AND string3).')
@click.option('-k', '--key', help='The database key of the fact.')
@click.option('-f', '--filename', help="The filename where to store the export file.")
@pass_controller
def export(controller, format, start, end, activity, category, tag, description, key, filename):
    """Export all facts of within a given timewindow to a file of specified format."""
    _export(controller, format, start, end, activity, category, tag, description, key, filename)


def _export(
    controller,
    format,
    start,
    end,
    activity=None,
    category=None,
    tag=None,
    description=None,
    key=None,
    filename=None,
):
    """
    Export all facts in the given timeframe in the format specified.

    Args:
        format (str): Format to export to. Valid options are: ``csv``, ``xml`` and ``ical``.
        start (datetime.datetime): Consider only facts starting at this time or later.
        end (datetime.datetime): Consider only facts starting no later than this time.

    Returns:
        None: If everything went alright.

    Raises:
        click.Exception: If format is not recognized.
    """
    accepted_formats = ['csv', 'tsv', 'ical', 'xml']
    # [TODO]
    # Once hamster_lib has a proper 'export' register available we should be able
    # to streamline this.
    if format not in accepted_formats:
        message = _("Unrecocgnized export format received")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    if not start:
        start = None
    if not end:
        end = None

    if filename:
        filepath = filename
    else:
        filepath = controller.client_config['export_path']
        filepath = filepath + '.' + format

    #facts = controller.facts.get_all(start=start, end=end)
    facts = _search(controller,
                    start=start,
                    end=end,
                    activity=activity,
                    category=category,
                    tag=tag,
                    description=description,
                    key=key)

    if format == 'csv':
        writer = reports.CSVWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
    elif format == 'tsv':
        writer = reports.TSVWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
    elif format == 'ical':
        writer = reports.ICALWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))
    else:
        assert format == 'xml'
        writer = reports.XMLWriter(filepath)
        writer.write_report(facts)
        click.echo(_("Facts have been exported to: {path}".format(path=filepath)))


# ***
# *** [LIST] Command: CATEGORIES.
# ***

@run.command(help=help_strings.CATEGORIES_HELP)
@pass_controller
def categories(controller):
    """List all existing categories, ordered by name."""
    _categories(controller)


def _categories(controller):
    """
    List all existing categories, ordered by name.

    Returns:
        None: If success.
    """
    result = controller.categories.get_all()
    # [TODO]
    # Provide nicer looking tabulated output.
    for category in result:
        click.echo(category.name)


# ***
# *** Command: CURRENT [fact, show].
# ***

@run.command(help=help_strings.CURRENT_HELP)
@pass_controller
def current(controller):
    """Display current *ongoing fact*."""
    _current(controller)


def _current(controller):
    """
    Return current *ongoing fact*.

    Returns:
        None: If everything went alright.

    Raises:
        click.ClickException: If we fail to fetch any *ongoing fact*.
    """
    try:
        fact = controller.facts.get_tmp_fact()
    except KeyError:
        message = _(
            "There seems no be no activity beeing tracked right now."
            " maybe you want to *start* tracking one right now?"
        )
        raise click.ClickException(message)
    else:
        fact.end = datetime.datetime.now()
        string = '{fact} ({duration} minutes)'.format(fact=fact, duration=fact.get_string_delta())
        click.echo(string)


# ***
# *** [LIST] Command: ACTIVITIES.
# ***

@run.command(help=help_strings.ACTIVITIES_HELP)
@click.argument('search_term', default='')
@click.option('-c', '--category', help="The search string applied to category names.")
@click.option('-C', '--sort-by-category', is_flag=True,
              help="Sort by category name, then activity name.")
@pass_controller
def activities(controller, search_term, category, sort_by_category):
    """List all activities. Provide optional filtering by name."""
    category_name = category if category else ''
    _activities(controller, search_term, category_name, sort_by_category)


def _activities(controller, search_term='', category_name='', sort_by_category=False):
    """
    List all activities. Provide optional filtering by name.

    Args:
        search_term (str): String to match ``Activity.name`` against.

    Returns:
        None: If success.
    """
    category = False
    if category_name:
        # FIXME: (lb): This raises KeyError if no exact match found.
        #        We should at least gracefully exit,
        #        if not do a fuzzy search.
        result = controller.categories.get_by_name(category_name)
        category = result if result else False
    result = controller.activities.get_all(
        search_term=search_term, category=category, sort_by_category=sort_by_category,
    )
    table = []
    headers = (_("Activity"), _("Category"))
    for activity in result:
        if activity.category:
            category = activity.category.name
        else:
            category = None
        table.append((activity.name, category))

    click.echo(generate_table(table, headers=headers))


# ***
# *** Command: LICENSE [list].
# ***

@run.command(help=help_strings.LICENSE_HELP)
def license():
    """Show license information."""
    _license()


def _license():
    """Show license information."""
    license = """
        'hamster_cli' is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        'hamster_cli' is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with .  If not, see <http://www.gnu.org/licenses/>.
        """
    click.echo(license)


# ***
# *** Command: DETAILS [about paths, config, etc.].
# ***

@run.command(help=help_strings.DETAILS_HELP)
@pass_controller
def details(controller):
    """List details about the runtime environment."""
    _details(controller)


def _details(controller):
    """List details about the runtime environment."""
    def get_db_info():
        result = None

        def get_sqlalchemy_info():
            engine = controller.config['db_engine']
            if engine == 'sqlite':
                sqlalchemy_string = _(
                    "Using 'sqlite' with database stored under: {}"
                    .format(controller.config['db_path'])
                )
            else:
                port = controller.config.get('db_port', '')
                if port:
                    port = ':{}'.format(port)

                sqlalchemy_string = _(
                    "Using '{engine}' connecting to database {name} on {host}{port}"
                    " as user {username}.".format(
                        engine=engine,
                        host=controller.config['db_host'],
                        port=port,
                        username=controller.config['db_user'],
                        name=controller.config['db_name'],
                    )
                )
            return sqlalchemy_string

        # For now we do not need to check for various store option as we allow
        # only one anyway.
        result = get_sqlalchemy_info()
        return result

    click.echo(_(
        "You are running {name} version {version}".format(
            name=hamster_cli_appname,
            version=hamster_cli_version,
        )
    ))
    click.echo(
        "Configuration found under: {}".format(get_config_path())
    )
    click.echo(
        "Logfile stored under: {}".format(controller.client_config['logfile_path'])
    )
    click.echo(
        "Reports exported to: {}".format(controller.client_config['export_path'])
    )
    click.echo(get_db_info())


# ***
# *** Helper Functions: _run().
# ***

# FIXME: (lb): Refactor: Move this code to immediately following: def _run().

def _run_handle_paging(controller):
    if controller.client_config['term_paging']:
        # FIXME/2018-04-22: (lb): Well, actually, don't clear, but rely on paging...
        #   after implementing paging. (Also add --paging option.)
        click.clear()


def _run_handle_banner():
    # FIXME/2018-04-22: (lb): I disabled the _show_greeting code;
    #                   it's not useful info. And a little boastful.
    # Instead, we could maybe make a hamster-about command?
    #   _show_greeting()
    pass


def _run_handle_version(show_version, ctx):
    if show_version:
        click.echo(_hamster_version())
        ctx.exit(0)


def _run_handle_without_command(ctx):
    if len(sys.argv) == 1:
        # Because invoke_without_command, we have to check ourselves
        click.echo(ctx.get_help())


def _setup_logging(controller):
    """Setup logging for the lib_logger as well as client specific logging."""
    controller.client_logger = logging.getLogger('hamster_cli')
    loggers = [
        controller.lib_logger,
        controller.sql_logger,
        controller.client_logger,
    ]
    # Clear any existing (null)Handlers, and set the level.
    # MAYBE: Allow user to specify different levels for different loggers.
    log_level = controller.client_config['log_level']
    for logger in loggers:
        logger.handlers = []
        logger.setLevel(log_level)

    formatter = logging_helpers.formatter_basic()

    if controller.client_config['log_console']:
        console_handler = logging.StreamHandler()
        logging_helpers.setupHandler(console_handler, formatter, *loggers)

    if controller.client_config['logfile_path']:
        filename = controller.client_config['logfile_path']
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        logging_helpers.setupHandler(file_handler, formatter, *loggers)


# ***
# *** Helper Functions: TABLE [facts].
# ***

def _generate_facts_table(facts):
    """
    Create a nice looking table representing a set of fact instances.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances representing a single fact.
    """
    # If you want to change the order just adjust the dict.
    headers = {
        'key': _("Key"),
        'start': _("Start"),
        'end': _("End"),
        'activity': _("Activity"),
        'category': _("Category"),
        'tags': _("Tags"),
        'description': _("Description"),
        'delta': _("Duration")
    }

    columns = (
        'key', 'start', 'end', 'activity', 'category', 'tags', 'description', 'delta',
    )

    header = [headers[column] for column in columns]

    TableRow = namedtuple('TableRow', columns)

    table = []
    for fact in facts:
        if fact.category:
            category = fact.category.name
        else:
            category = ''

        if fact.tags:
            tags = '#'
            tags += '#'.join(sorted([x.name + ' ' for x in fact.tags]))
        else:
            tags = ''

        table.append(TableRow(
            key=fact.pk,
            activity=fact.activity.name,
            category=category,
            description=fact.description,
            tags=tags,
            start=fact.start.strftime('%Y-%m-%d %H:%M'),
            end=fact.end.strftime('%Y-%m-%d %H:%M'),
            # [TODO]
            # Use ``Fact.get_string_delta`` instead!
            delta='{minutes} min.'.format(minutes=(int(fact.delta.total_seconds() / 60))),
        ))

    return (table, header)


# ***
# *** Helper Functions: GREETING.
# ***

def _show_greeting():
    """Display a greeting message providing basic set of information."""
    # 2018-04-22: (lb): It seems to me there are no i18n/l10n files for gettext/_.
    click.echo(_("Welcome to 'hamster_cli', your friendly time tracker for the command line."))
    click.echo("Copyright (C) 2015-2016, Eric Goller <elbenfreund@DenkenInEchtzeit.net>")
    click.echo(_(
        "'hamster_cli' is published under the terms of the GPL3, for details please use"
        " the 'license' command."
    ))
    click.echo()

