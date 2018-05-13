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
from gettext import gettext as _

import click
import hamster_lib

from hamster_cli import __version__ as hamster_cli_version
from hamster_cli import __appname__ as hamster_cli_appname
from hamster_lib import __version__ as hamster_lib_version
from hamster_lib import HamsterControl, reports
from hamster_lib.helpers import time as time_helpers
from hamster_lib.helpers import logging as logging_helpers

from . import help_strings
from cmd_config import get_config, get_config_instance, get_config_path
from cmd_options import cmd_options_search, cmd_options_limit_offset, cmd_options_table_bunce
from create import cancel_fact, start_fact, stop_fact
from search import search_facts
from helpers.ascii_table import generate_table, warn_if_truncated
import cmd_options
import cmds_list

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True


# ***
# *** [CONTROLLER] HamsterControl Controller.
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
# *** [VERSION] Version command helper.
# ***


def _hamster_version():
    vers = '{} version {}\nhamster-lib version {}'.format(
        hamster_cli_appname,
        hamster_cli_version,
        hamster_lib_version,
    )
    return vers


# ***
# *** [BASE COMMAND GROUP] One Group to rule them all.
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

    def _run(ctx, controller, show_version):
        """Make sure that loggers are setup properly."""
        _run_handle_paging(controller)
        _run_handle_banner()
        _run_handle_version(show_version, ctx)
        _run_handle_without_command(ctx)
        _setup_logging(controller)

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

    # Shim to the private run() functions.

    _run(ctx, controller, show_version=v)


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
# *** [VERSION] Ye rote version command.
# ***


@run.command(help=help_strings.VERSION_HELP)
def version():
    """Show version information."""
    _version()


def _version():
    """Show version information."""
    click.echo(_hamster_version())


# ***
# *** [LICENSE] Command.
# ***


@run.command(hidden=True, help=help_strings.LICENSE_HELP)
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
# *** [DETAILS] Command [about paths, config, etc.].
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
# *** [LIST] Commands.
# ***


# NOTE: Use an alias (don't `def list()`) because of builtin of same name!
@run.group('list', help=help_strings.LIST_GROUP_HELP)
@pass_controller
@click.pass_context
def list_group(ctx, controller):
    """Base `list` group command run prior to any of the hamster-list commands."""
    pass


# *** ACTIVITIES.

@list_group.command('activities', help=help_strings.LIST_ACTIVITIES_HELP)
@click.argument('search_term', default='')
@click.option('-c', '--category', help="The search string applied to category names.")
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def list_activities(controller, *args, **kwargs):
    """List all activities. Provide optional filtering by name."""
    category = kwargs['category'] if kwargs['category'] else ''
    del kwargs['category']
    cmd_options.postprocess_options_table_bunce(kwargs)
    cmds_list.activity.list_activities(
        controller,
        *args,
        filter_category=category,
        **kwargs
    )


# *** CATEGORIES.

@list_group.command('categories', help=help_strings.LIST_CATEGORIES_HELP)
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def list_categories(controller, *args, **kwargs):
    """List all existing categories, ordered by name."""
    cmds_list.category.list_categories(controller)


# *** TAGS.

@list_group.command('tags', help=help_strings.LIST_TAGS_HELP)
@click.argument('search_term', default='')
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def list_tags(controller, *args, **kwargs):
    """List all tags, with filtering and sorting options."""
    cmd_options.postprocess_options_table_bunce(kwargs)
    cmds_list.tag.list_tags(controller, *args, **kwargs)


# *** FACTS (w/ time range).
# FIXME/2018-05-12: (lb): Do we really need 2 Facts search commands?

@list_group.command('facts', help=help_strings.LIST_FACTS_HELP)
@cmd_options_search
@cmd_options_limit_offset
@pass_controller
def list_facts(controller, *args, **kwargs):
    """List all facts within a timerange."""
    results = search_facts(controller, *args, **kwargs)
    table, headers = cmds_list.fact.generate_facts_table(results)
    click.echo(generate_table(table, headers=headers))
    warn_if_truncated(controller, len(results), len(table))


# *** FACTS (w/ search term).
# FIXME/2018-05-12: (lb): Do we really need 2 Facts search commands?

@run.command(help=help_strings.SEARCH_HELP)
@click.argument('search_term', nargs=-1, default=None)
# MAYBE/2018-05-05: (lb): Restore the time_range arg scientificsteve removed:
#  @click.argument('time_range', default='')
@cmd_options_search
@cmd_options_limit_offset
@click.option('-a', '--activity', help="The search string applied to activity names.")
@click.option('-c', '--category', help="The search string applied to category names.")
@click.option('-t', '--tag', help='The tags search string (e.g. "tag1 AND (tag2 OR tag3)".')
@click.option('-d', '--description',
              help='The description search string (e.g. "string1 OR (string2 AND string3).')
@click.option('-k', '--key', help='The database key of the fact.')
@pass_controller
def search(controller, description, search_term, *args, **kwargs):
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
    #           return search_facts(controller, search_term, time_range)
    #           # And then the table and click.echo were at the bottom of
    #           # search_facts! And I'm not sure why they were moved here....
    #
    #       MAYBE: Restore supprt for time_range, i.e., let user specify
    #       2 positional args in addition to any number of options. And
    #       figure out why the generate-table and click.echo were moved
    #       here?
    if search_term:
        description = description or ''
        description += ' AND ' if description else ''
        description += ' AND '.join(search_term)
    results = search_facts(description, *args, **kwargs)
    table, headers = cmds_list.fact.generate_facts_table(results)
    click.echo(generate_table(table, headers=headers))
    warn_if_truncated(controller, len(results), len(table))


# ***
# *** [CURRENT-FACT] Commands: start/stop/cancel/current.
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
    start_fact(controller, raw_fact, start, end)


@run.command(help=help_strings.STOP_HELP)
@pass_controller
def stop(controller):
    """Stop tracking current fact. Saving the result."""
    stop_fact(controller)


@run.command(help=help_strings.CANCEL_HELP)
@pass_controller
def cancel(controller):
    """Cancel 'ongoing fact'. E.g stop it without storing in the backend."""
    cancel_fact(controller)


@run.command(help=help_strings.CURRENT_HELP)
@pass_controller
def current(controller):
    """Display current *ongoing fact*."""
    cmds_list.fact.list_current_fact(controller)


# ***
# *** [EXPORT] Command.
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
    facts = search_facts(
        controller,
        start=start,
        end=end,
        activity=activity,
        category=category,
        tag=tag,
        description=description,
        key=key,
    )

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
# ***


