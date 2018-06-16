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

"""A time tracker for the command line. Utilizing the power of hamster! [nark]."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import logging
import os
import sys
from click_alias import ClickAliasedGroup
from functools import update_wrapper

from nark import __version__ as nark_version
from nark.helpers import logging as logging_helpers
from nark.helpers.colored import disable_colors, enable_colors

from . import cmd_options
from . import help_strings
from . import migrate
from . import update
from . import __BigName__
from . import __appname__ as dob_appname
from . import __version__ as dob_version
from . import __libname__ as nark_appname
from .cmd_common import induct_newbies, must_no_more_than_one_file
from .cmd_options import (
    cmd_options_factoid,
    cmd_options_insert,
    cmd_options_limit_offset,
    cmd_options_list_activitied,
    cmd_options_list_categoried,
    cmd_options_list_fact,
    cmd_options_search,
    cmd_options_table_bunce,
    cmd_options_usage,
    postprocess_options_table_bunce,
)
from .cmds_list import activity as list_activity
from .cmds_list import category as list_category
from .cmds_list import fact as list_fact
from .cmds_list import tag as list_tag
from .cmds_list.fact import list_current_fact
from .cmds_usage import activity as usage_activity
from .cmds_usage import category as usage_category
from .cmds_usage import tag as usage_tag
from .complete import tab_complete
from .controller import Controller
from .copyright import echo_copyright
from .create import add_fact, cancel_fact, stop_fact
from .details import app_details, hamster_time
from .migrate import upgrade_legacy_database_file
from .transcode import export_facts, import_facts

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    # 'pass_controller',
    # '_dob_version',
    # 'run',
    # '_setup_logging',
    # '_disable_logging',
    # 'version',
    # '_version',
    # 'license',
    # '_license',
    # 'copyright',
    # 'banner',  # 'dance',
    # 'details',
    # 'list_group',
    # 'list_activities',
    # 'list_categories',
    # 'list_tags',
    # 'list_facts',
    # 'search',
    # 'usage_group',
    # 'usage_activities',
    # 'usage_categories',
    # 'usage_tags',
    # 'stop',
    # 'cancel',
    # 'current',
    # 'on',
    # 'at',
    # 'to',
    # 'between',
    # 'edit_group',
    # 'edit_fact',
    # 'transcode_export',
    # 'transcode_import',
    # 'complete',
    # 'migrate_group',
    # 'migrate_control',
    # 'migrate_downgrade',
    # 'migrate_upgrade',
    # 'migrate_version',
]


pass_controller = click.make_pass_decorator(Controller, ensure=True)


# ***
# *** [VERSION] Version command helper.
# ***


def _dob_version():
    vers = '{} version {}\n{} version {}'.format(
        dob_appname,
        dob_version,
        nark_appname,
        nark_version,
    )
    return vers


# ***
# *** [BASE COMMAND GROUP] One Group to rule them all.
# ***

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# (lb): Use invoke_without_command so `dob -v` works, otherwise Click's
# Group (MultiCommand ancestor) does not allow it ('Missing command.').
@click.group(
    cls=ClickAliasedGroup,
    invoke_without_command=True,
    help=help_strings.RUN_HELP,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(message=_dob_version())
# (lb): Hide -v: version_option adds help for --version, so don't repeat ourselves.
@click.option('-v', is_flag=True, help=help_strings.VERSION_HELP, hidden=True)
# (lb): Note that universal --options must com before the sub command.
# FIXME: Need universal options in cmd_options? Or can I apply to Groups?
#          These aren't recognized by other fcns...
#        OH! These have to come *before* the command??
@click.option('-V', '--verbose', is_flag=True, help=_('Be chatty. (-VV for more.)'))
@click.option('-VV', '--verboser', is_flag=True, help=_('Be chattier.'), hidden=True)
@click.option('--color/--no-color', '-C', default=None, help=_('Color, or plain.'))
@pass_controller
@click.pass_context
# NOTE: @click.group transforms this func. definition into a callback that
#       we use as a decorator for the top-level commands (see: @run.command).
def run(ctx, controller, v, verbose, verboser, color):
    """General context run right before any of the commands."""

    def _run(ctx, controller, show_version):
        """
        Do stuff before running the command.

        Setup paging, if paging.
        Enable/disable color, per config.
        No longer show a banner.
        Show version and exit, if user specified -v option.
        Setup up loggers.
        """
        _setup_tty_options(controller)
        _run_handle_banner()
        _run_handle_version(show_version, ctx)
        _run_handle_without_command(ctx)
        _setup_logging(controller, verbose, verboser)

    def _setup_tty_options(controller):
        # If piping output, Disable color and paging.
        # MAYBE: (lb): What about allowing color for outputting to ANSI file? Meh.
        if not sys.stdout.isatty():
            controller.client_config['term_paging'] = False
            controller.client_config['term_color'] = False
        _setup_tty_paging(controller)
        _setup_tty_color(controller)

    def _setup_tty_paging(controller):
        if controller.client_config['term_paging']:
            # FIXME/2018-04-22: (lb): Implement term_paging? Add --paging option?
            #   For now, we just clear the screen...
            click.clear()

    def _setup_tty_color(controller):
        use_color = color
        if use_color is None:
            use_color = controller.client_config['term_color']
        if use_color:
            enable_colors()
        else:
            disable_colors()

    def _run_handle_banner():
        # (lb): I find the greeting annoying, and somewhat boastful.
        #   It's not that I'm against self-promotion, per se -- and I
        #   recognize that the GPL instructs open source software to
        #   always output a license, on every invocation -- but I like
        #   the clean aesthetics of not showing it. Though I suppose
        #   it's easy enough just to make a config option for it....
        if not controller.client_config['show_greeting']:
            return
        echo_copyright()
        click.echo()

    def _run_handle_version(show_version, ctx):
        if show_version:
            click.echo(_dob_version())
            ctx.exit(0)

    def _run_handle_without_command(ctx):
        if len(sys.argv) == 1:
            # Because invoke_without_command, we have to check ourselves
            click.echo(ctx.get_help())

    # Shim to the private run() functions.

    _run(ctx, controller, show_version=v)


def _setup_logging(controller, verbose=False, verboser=False):
    """Setup logging for the lib_logger as well as client specific logging."""
    controller.client_logger = logging.getLogger('dob')
    loggers = [
        controller.lib_logger,
        controller.sql_logger,
        controller.client_logger,
    ]
    # Clear existing Handlers, and set the level.
    # MAYBE: Allow user to specify different levels for different loggers.
    client_level = controller.client_config['log_level']
    log_level, warn_name = logging_helpers.resolve_log_level(client_level)
    # We can at least allow some simpler optioning from the command args.
    if verbose:
        log_level = min(logging.INFO, log_level)
    if verboser:
        log_level = min(logging.DEBUG, log_level)
    for logger in loggers:
        logger.handlers = []
        logger.setLevel(log_level)

    color = controller.client_config['term_color']
    formatter = logging_helpers.formatter_basic(color=color)

    if controller.client_config['log_console']:
        console_handler = logging.StreamHandler()
        logging_helpers.setupHandler(console_handler, formatter, *loggers)

    if controller.client_config['logfile_path']:
        filename = controller.client_config['logfile_path']
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        logging_helpers.setupHandler(file_handler, formatter, *loggers)

    if warn_name:
        controller.client_logger.warning(
            _('Unknown Client.log_level specified: {}')
            .format(client_level)
        )


def _disable_logging(controller):
    loggers = [
        controller.lib_logger,
        controller.sql_logger,
        controller.client_logger,
    ]
    for logger in loggers:
        logger.handlers = []
        logger.setLevel(logging.NOTSET)


# ***
# *** [VERSION] Ye rote version command.
# ***

@run.command(help=help_strings.VERSION_HELP)
def version():
    """Show version information."""
    _version()


def _version():
    """Show version information."""
    click.echo(_dob_version())


# ***
# *** [LICENSE] Command.
# ***

@run.command(hidden=True, help=help_strings.LICENSE_HELP)
def license():
    """Show license information."""
    _license()


def _license():
    """Show license information."""
    # FIXME: (lb): Replace appname with $0, or share module var with setup.py.
    # MAYBE: (lb): Read and print LICENSE file instead of hard coding herein?
    license = """
{app_name} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

{app_name} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
""".strip()
    license = license.format(app_name=__BigName__)
    click.echo(license)


# ***
# *** [BANNER] Command.
# ***

@run.command(aliases=['about'], help=_('View copyright information'))
@pass_controller
def copyright(controller):
    """Display copyright information.."""
    echo_copyright()


# ***
# *** [DANCE] Command [Easter egg].
# ***

# FIXME: (lb): This used to be `hamster dance`, now it's `dob dance`.
#          Does the name still make sense??
@run.command('dance', hidden=True, help=_('Hamster time!'))
@click.argument('posits', nargs=-1)
@pass_controller
def banner(controller, posits):
    """ASCII Art helper."""
    hamster_time(posits)


# ***
# *** [DETAILS] Command [about paths, config, etc.].
# ***

# MAYBE: (lb): Call this dob-show? dob-status? dob-info?
#   (2018-06-09: Trying aliases for now)
#   Some ideas: aliases=['show', 'status', 'info', 'config', 'details', 'appinfo'])
#   Though maybe 'show' should be alias for dob-current?
# MAYBE: Calling this 'appinfo' would make this command first in the --help....
#   @run.command(aliases=['show', 'status', 'info'], help=help_strings.DETAILS_HELP)
@run.command(aliases=['info'], help=help_strings.DETAILS_HELP)
@click.option('--tmi', is_flag=True, help=_('Show AppDirs paths, too.'))
@pass_controller
def details(controller, tmi):
    """List details about the runtime environment."""
    app_details(controller, full=tmi)


# ***
# *** [CONFIG] Commands.
# ***

@run.group('config', cls=ClickAliasedGroup, help=help_strings.CONFIG_GROUP_HELP)
@click.pass_context
def config_group(controller):
    """Base `config` group command run prior to any of the dob-config commands."""
    pass


@config_group.command('create', aliases=['new'], help=help_strings.CONFIG_CREATE_HELP)
@click.option('-f', '--force', is_flag=True,
              help=_('If specified, overwrite config file if is exists'))
@pass_controller
def create(controller, force):
    """"""
    controller.create_config(force)


# ***
# *** [LIST] Commands.
# ***

# Use a command alias to avoid conflict with builtin of same name
# (i.e., we cannot declare this function, `def list()`).
@run.group('list', help=help_strings.LIST_GROUP_HELP)
@pass_controller
@click.pass_context
def list_group(ctx, controller):
    """Base `list` group command run prior to any of the dob-list commands."""
    pass


# *** ACTIVITIES.

@list_group.command('activities', help=help_strings.LIST_ACTIVITIES_HELP)
@cmd_options_search
@cmd_options_list_categoried
@cmd_options_usage
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def list_activities(controller, *args, usage=False, **kwargs):
    """List matching activities, filtered and sorted."""
    category = cmd_options.postprocess_options_list_categoried(kwargs)
    postprocess_options_table_bunce(kwargs)
    if usage:
        handler = usage_activity.usage_activities
    else:
        handler = list_activity.list_activities
    handler(
        controller,
        *args,
        filter_category=category,
        **kwargs
    )


# *** CATEGORIES.

@list_group.command('categories', help=help_strings.LIST_CATEGORIES_HELP)
@cmd_options_usage
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def list_categories(controller, *args, usage=False, **kwargs):
    """List matching categories, filtered and sorted."""
    postprocess_options_table_bunce(kwargs)
    if usage:
        handler = usage_category.usage_categories
    else:
        handler = list_category.list_categories
    handler(
        controller,
        *args,
        **kwargs,
    )


# *** TAGS.

@list_group.command('tags', help=help_strings.LIST_TAGS_HELP)
@cmd_options_search
@cmd_options_list_activitied
@cmd_options_list_categoried
@cmd_options_usage
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def list_tags(controller, *args, usage=False, **kwargs):
    """List all tags, with filtering and sorting options."""
    activity = cmd_options.postprocess_options_list_activitied(kwargs)
    category = cmd_options.postprocess_options_list_categoried(kwargs)
    postprocess_options_table_bunce(kwargs)
    if usage:
        handler = usage_tag.usage_tags
    else:
        handler = list_tag.list_tags
    handler(
        controller,
        *args,
        filter_activity=activity,
        filter_category=category,
        **kwargs,
    )


# *** FACTS.

def _list_facts(controller, *args, usage=False, **kwargs):
    """List matching facts, filtered and sorted."""
    """Fetch facts matching certain criteria."""
    activity = cmd_options.postprocess_options_list_activitied(kwargs)
    category = cmd_options.postprocess_options_list_categoried(kwargs)
    postprocess_options_table_bunce(kwargs)
    list_fact.list_facts(
        controller,
        *args,
        include_usage=usage,
        filter_activity=activity,
        filter_category=category,
        **kwargs,
    )


def generate_list_facts_command(func):
    @cmd_options_search
    @cmd_options_list_activitied
    @cmd_options_list_categoried
    @cmd_options_usage
    @cmd_options_table_bunce
    @cmd_options_limit_offset
    @cmd_options_list_fact
    @pass_controller
    def list_facts(controller, *args, **kwargs):
        _list_facts(controller, *args, **kwargs)
    return update_wrapper(list_facts, func)


@list_group.command('facts', help=help_strings.LIST_FACTS_HELP)
@generate_list_facts_command
def list_facts(controller, *args, **kwargs):
    assert(False)  # Not reachable, because generate_list_facts_command.
    pass


# MAYBE: Should we alias the command at dob-search?
@run.command('search', help=help_strings.SEARCH_HELP)
@generate_list_facts_command
def search_facts(controller, *args, **kwargs):
    assert(False)  # Not reachable, because generate_list_facts_command.
    pass


# ***
# *** [USAGE] Commands.
# ***

@run.group('usage', help=help_strings.USAGE_GROUP_HELP)
@pass_controller
@click.pass_context
def usage_group(ctx, controller):
    """Base `usage` group command run prior to any of the dob-usage commands."""
    pass


# *** ACTIVITIES.

@usage_group.command('activities', help=help_strings.USAGE_ACTIVITIES_HELP)
@cmd_options_search
@cmd_options_list_categoried
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def usage_activities(controller, *args, **kwargs):
    """List all activities. Provide optional filtering by name."""
    category = cmd_options.postprocess_options_list_categoried(kwargs)
    postprocess_options_table_bunce(kwargs)
    usage_activity.usage_activities(
        controller,
        *args,
        filter_category=category,
        **kwargs
    )


# *** CATEGORIES.

@usage_group.command('categories', help=help_strings.USAGE_CATEGORIES_HELP)
@cmd_options_search
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def usage_categories(controller, *args, **kwargs):
    """List all categories. Provide optional filtering by name."""
    postprocess_options_table_bunce(kwargs)
    usage_category.usage_categories(
        controller,
        *args,
        **kwargs
    )


# *** TAGS.

@usage_group.command('tags', help=help_strings.USAGE_TAGS_HELP)
@cmd_options_search
@cmd_options_list_activitied
@cmd_options_list_categoried
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def usage_tags(controller, *args, **kwargs):
    """List all tags' usage counts, with filtering and sorting options."""
    activity = cmd_options.postprocess_options_list_activitied(kwargs)
    category = cmd_options.postprocess_options_list_categoried(kwargs)
    postprocess_options_table_bunce(kwargs)
    usage_tag.usage_tags(
        controller,
        *args,
        filter_activity=activity,
        filter_category=category,
        **kwargs,
    )


# *** FACTS.

@usage_group.command('facts', help=help_strings.USAGE_FACTS_HELP)
@cmd_options_search
@cmd_options_list_activitied
@cmd_options_list_categoried
@cmd_options_table_bunce
@cmd_options_limit_offset
@pass_controller
def usage_facts(controller, *args, **kwargs):
    """List all tags' usage counts, with filtering and sorting options."""
    activity = cmd_options.postprocess_options_list_activitied(kwargs)
    category = cmd_options.postprocess_options_list_categoried(kwargs)
    postprocess_options_table_bunce(kwargs)
    list_fact.list_facts(
        controller,
        *args,
        include_usage=True,
        filter_activity=activity,
        filter_category=category,
        **kwargs,
    )


# ***
# *** [CURRENT-FACT] Commands: stop/cancel/current.
# ***

@run.command('stop', help=help_strings.STOP_HELP)
@pass_controller
def stop(controller):
    """Stop tracking current fact (by setting its 'end')."""
    stop_fact(controller)


@run.command('cancel', help=help_strings.CANCEL_HELP)
@click.option(
    '-f', '--force', '--purge',
    help=_('Completely delete fact, rather than just marking deleted.'),
)
@pass_controller
def cancel(controller, force):
    """Cancel 'ongoing fact'. Stop it without storing in the backend."""
    cancel_fact(controller, force)


@run.command('current', aliases=['show'], help=help_strings.CURRENT_HELP)
@pass_controller
def current(controller):
    """Display current *ongoing fact*."""
    list_current_fact(controller)


# ***
# *** [CREATE-FACT] Commands.
# ***

@run.command(aliases=['now'], help=help_strings.START_HELP_ON)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
def on(controller, *args, **kwargs):
    """Start or add a fact using the `on`/`now`/`start` directive."""
    add_fact(controller, *args, time_hint='verify_none', **kwargs)


@run.command(help=help_strings.START_HELP_AT)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
def at(controller, *args, **kwargs):
    """Start or add a fact using the `at` directive."""
    add_fact(controller, *args, time_hint='verify_start', **kwargs)


@run.command(aliases=['until'], help=help_strings.START_HELP_TO)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
def to(controller, *args, **kwargs):
    """Start or add a fact using the `to`/`until` directive."""
    add_fact(controller, *args, time_hint='verify_end', **kwargs)


# (lb): We cannot name the function `from`, which is a Python reserved word,
# so set the command name via the composable group command() decorator.
@run.command('from', help=help_strings.START_HELP_BETWEEN)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
def between(controller, *args, **kwargs):
    """Add a fact using the `from ... to` directive."""
    add_fact(controller, *args, time_hint='verify_both', **kwargs)


# ***
# *** [EDIT] Command(s).
# ***

@run.group('edit', help=help_strings.EDIT_GROUP_HELP)
@pass_controller
@click.pass_context
def edit_group(ctx, controller):
    """Base `edit` group command run prior to any of the dob-edit commands."""
    pass


# *** FACTS.

@edit_group.command('fact', help=help_strings.EDIT_FACT_HELP)
@click.argument('key', nargs=1, type=int)
@pass_controller
def edit_fact(controller, *args, **kwargs):
    """Inline-Edit specified Fact using preferred $EDITOR."""
    update.edit_fact(controller, *args, **kwargs)


# ***
# *** [EXPORT] Command.
# ***

@run.command('export', help=help_strings.EXPORT_HELP)
# (lb): show_default=True is not recognized for click.argument.
@click.argument('format', nargs=1, default='csv')
@click.argument('start', nargs=1, default='')
@click.argument('end', nargs=1, default='')
@click.option(
    '-f', '--filename',
    help=_('The filename where to store the export file.'),
)
@cmd_options_search
@cmd_options_limit_offset
@cmd_options_list_activitied
@cmd_options_list_categoried
@pass_controller
def transcode_export(
    controller, *args, format, **kwargs
):
    """Export all facts of within a given timewindow to a file of specified format."""
    export_facts(controller, *args, to_format=format, **kwargs)


# ***
# *** [IMPORT] Command.
# ***

@run.command('import', help=help_strings.IMPORT_HELP)
@click.argument('filename', nargs=-1, type=click.File('r'))
@click.option('-o', '--output', type=click.File('w', lazy=True),
              help=_('If specified, write to output file rather than saving'))
@click.option('-f', '--force', is_flag=True,
              help=_('If specified, overwrite --output file if is exists'))
@click.option('-r', '--rule', '--sep', nargs=1, default='',
              help=_('With --output, split facts with a horizontal rule'))
@cmd_options_insert
# FIXME/2018-06-10: (lb) Apply backend_integrity to other/most commands?
#   Or at least those that touch the db...
#   NOTE/2018-06-11: This checks there are no endless facts, so rather specific
#     (i.e., no ongoing). You could split into another decorator for just checking
#     database is under migration control. But that doesn't matter so much,
#     does it? Or is the idea we'd rather print a nice, friendly error message?
#     Otherwise, if code fails later, we'd print a dirty stack trace.
@pass_controller
@backend_integrity
def transcode_import(controller, filename, output, force, *args, **kwargs):
    """Import from file or STDIN (pipe)."""
    file_in = must_no_more_than_one_file(filename)

    # NOTE: You can get tricky and enter Facts LIVE! E.g.,
    #
    #           dob import -
    #
    #       will open pipe from STDIN, and Dob will wait for
    #       you to type! (lb): Though I did not verify ^D EOFs.

    if output and not force and os.path.exists(output.name):
        msg = _('Outfile already exists at: {}'.format(output.name))
        click.echo(msg)
        sys.exit(1)

    import_facts(controller, *args, file_in=file_in, file_out=output, **kwargs)


# ***
# *** [COMPLETE] Command [Bash tab completion].
# ***

# FIXME: YAS! `hidden` is from a branch at:
#          sstaszkiewicz-copperleaf:6.x-maintenance
#        Watch the PR, lest you want to remove this before publishing:
#          https://github.com/pallets/click/pull/985
#          https://github.com/pallets/click/pull/500
@run.command('complete', hidden=True, help=help_strings.COMPLETE_HELP)
@pass_controller
def complete(controller):
    """Bash tab-completion helper."""
    _disable_logging(controller)
    tab_complete(controller)


# ***
# *** [MIGRATE] Commands [database transformations].
# ***

@run.group('migrate', help=help_strings.MIGRATE_GROUP_HELP)
@pass_controller
@click.pass_context
def migrate_group(ctx, controller):
    """Base `migrate` group command run prior to any of the dob-migrate commands."""
    pass


@migrate_group.command('control', help=help_strings.MIGRATE_CONTROL_HELP)
@pass_controller
def migrate_control(controller):
    """Mark a database as under version control."""
    migrate.control(controller)


@migrate_group.command('down', help=help_strings.MIGRATE_DOWN_HELP)
@pass_controller
def migrate_downgrade(controller):
    """Downgrade the database according to its migration version."""
    migrate.downgrade(controller)


@migrate_group.command('up', help=help_strings.MIGRATE_UP_HELP)
@pass_controller
def migrate_upgrade(controller):
    """Upgrade the database according to its migration version."""
    migrate.upgrade(controller)


@migrate_group.command('version', help=help_strings.MIGRATE_VERSION_HELP)
@pass_controller
def migrate_version(controller):
    """Show migration information about the database."""
    migrate.version(controller)

