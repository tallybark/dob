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
import os
import sys
from click_alias import ClickAliasedGroup
from functools import update_wrapper

from . import cmd_options
from . import help_strings
from . import migrate
from . import update
from .cmd_common import induct_newbies, insist_germinated, must_no_more_than_one_file
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
from .copyright import echo_copyright, echo_license
from .create import add_fact, cancel_fact, stop_fact
from .details import echo_app_details, echo_app_environs, echo_data_stats
from .helpers import click_echo
from .migrate import upgrade_legacy_database_file
from .run_cli import disable_logging, dob_versions, pass_controller, run
from .transcode import export_facts, import_facts

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
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


# ***
# *** [HELP] Just a simple `help` alias.
# ***

@run.command(hidden=True, help=help_strings.HELP_HELP)
@click.pass_context
def help(ctx):
    """Show help."""
    click_echo(run.get_help(ctx))


# ***
# *** [VERSION] Ye rote version command.
# ***

@run.command(help=help_strings.VERSION_HELP)
def version():
    """Show version information."""
    _version()


def _version():
    """Show version information."""
    click_echo(dob_versions())


# ***
# *** [LICENSE] Command.
# ***

@run.command(hidden=True, help=help_strings.LICENSE_HELP)
def license():
    """Show license information."""
    _license()


def _license():
    """Show license information."""
    echo_license()


# ***
# *** [BANNER] Command.
# ***

@run.command(aliases=['about'], help=_('View copyright information'))
@pass_controller
def copyright(controller):
    """Display copyright information.."""
    echo_copyright()


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
@click.option('--tmi', '--full', is_flag=True, help=_('Show AppDirs paths, too.'))
@pass_controller
def details(controller, tmi):
    """List details about the runtime environment."""
    echo_app_details(controller, full=tmi)


# ***
# *** [ENVIRONS] Command [like details command, but shell-sourceable].
# ***

@run.command(help=help_strings.ENVIRONS_HELP)
@pass_controller
def environs(controller):
    """List shell-sourceable details about the runtime environment."""
    echo_app_environs(controller)


# ***
# *** [DEMO] Command.
# ***

@run.command('demo', help=help_strings.DEMO_HELP)
@pass_controller
def demo_dob_and_nark(controller):
    """"""
    raise NotImplementedError(_('FIXME: Implement `dob demo`'))


# ***
# *** [INIT] Command.
# ***

@run.command('init', help=help_strings.INIT_HELP)
@pass_controller
def init_config_and_store(controller):
    """"""
    controller.create_config_and_store()


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
def config_create(controller, force):
    """"""
    controller.create_config(force)


# ***
# *** [STORE] Commands.
# ***

# See also: 'migrate' commands. The store commands are mostly for initial setup.

@run.group('store', cls=ClickAliasedGroup, help=help_strings.STORE_GROUP_HELP)
@click.pass_context
def store_group(controller):
    """Base `store` group command run prior to dob-store commands."""
    pass


@store_group.command('create', aliases=['new'], help=help_strings.STORE_CREATE_HELP)
@click.option('-f', '--force', is_flag=True,
              help=_('If specified, recreate data store if is exists'))
@pass_controller
def store_create(controller, force):
    """"""
    controller.create_data_store(force)


@store_group.command('path', help=help_strings.STORE_PATH_HELP)
@pass_controller
def store_path(controller):
    """"""
    click_echo(controller.sqlite_db_path)


@store_group.command('url', help=help_strings.STORE_URL_HELP)
@pass_controller
def store_url(controller):
    """"""
    click_echo(controller.data_store_url)


@store_group.command('upgrade-legacy', help=help_strings.STORE_UPGRADE_LEGACY_HELP)
@click.argument('filename', nargs=-1, type=click.File('r'))
@click.option('-f', '--force', is_flag=True,
              help=_('If specified, overwrite data store if is exists'))
@pass_controller
@click.pass_context
def upgrade_legacy(ctx, controller, filename, force):
    """Migrate a legacy "Hamster" database."""
    file_in = must_no_more_than_one_file(filename)
    upgrade_legacy_database_file(ctx, controller, file_in, force)


# ***
# *** [STATS] Command.
# ***

@run.command('stats', help=help_strings.STATS_HELP)
@pass_controller
@induct_newbies
def nark_stats(controller):
    """List stats about the user's data."""
    echo_data_stats(controller)


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
@induct_newbies
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
@induct_newbies
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
@induct_newbies
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
    @induct_newbies
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
@induct_newbies
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
@induct_newbies
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
@induct_newbies
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
@induct_newbies
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
@induct_newbies
def stop(controller):
    """Stop tracking current fact (by setting its 'end')."""
    stop_fact(controller)


@run.command('cancel', help=help_strings.CANCEL_HELP)
@click.option(
    '-f', '--force', '--purge',
    help=_('Completely delete fact, rather than just marking deleted.'),
)
@pass_controller
@induct_newbies
def cancel(controller, force):
    """Cancel 'ongoing fact'. Stop it without storing in the backend."""
    cancel_fact(controller, force)


@run.command('current', aliases=['show'], help=help_strings.CURRENT_HELP)
@pass_controller
@induct_newbies
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
@induct_newbies
def on(controller, *args, **kwargs):
    """Start or add a fact using the `on`/`now`/`start` directive."""
    add_fact(controller, *args, time_hint='verify_none', **kwargs)


@run.command(help=help_strings.START_HELP_AT)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
@induct_newbies
def at(controller, *args, **kwargs):
    """Start or add a fact using the `at` directive."""
    add_fact(controller, *args, time_hint='verify_start', **kwargs)


@run.command(aliases=['until'], help=help_strings.START_HELP_TO)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
@induct_newbies
def to(controller, *args, **kwargs):
    """Start or add a fact using the `to`/`until` directive."""
    add_fact(controller, *args, time_hint='verify_end', **kwargs)


# (lb): We cannot name the function `from`, which is a Python reserved word,
# so set the command name via the composable group command() decorator.
@run.command('from', help=help_strings.START_HELP_BETWEEN)
@cmd_options_factoid
@cmd_options_insert
@pass_controller
@induct_newbies
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
@induct_newbies
def edit_fact(controller, *args, **kwargs):
    """Inline-Edit specified Fact using preferred $EDITOR."""
    update.edit_fact(controller, *args, **kwargs)


# ***
# *** [EXPORT] Command.
# ***

@run.command('export', help=help_strings.EXPORT_HELP)
# (lb): show_default=True is not recognized for click.argument.
@click.argument('format', nargs=1, default='csv')
@click.option(
    '-f', '--filename',
    help=_('The filename where to store the export file.'),
)
@cmd_options_search
@cmd_options_limit_offset
@cmd_options_list_activitied
@cmd_options_list_categoried
@pass_controller
@induct_newbies
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
              help=_('Overwrite --output file if is exists'))
@click.option('-r', '--rule', '--sep', nargs=1, default='',
              help=_('With --output, split facts with a horizontal rule'))
@click.option('--backup/--no-backup', '-B', default=True, show_default=True,
              help=_('Keep plaintext backup of edited facts until committed'))
@click.option('-X', '--leave-backup', is_flag=True,
              help=_('Leave working backup file after commit'))
@cmd_options_insert
@pass_controller
@induct_newbies
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
        click_echo(msg)
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
@induct_newbies
def complete(controller):
    """Bash tab-completion helper."""
    disable_logging(controller)
    tab_complete(controller)


# ***
# *** [MIGRATE] Commands [database transformations].
# ***

@run.group('migrate', help=help_strings.MIGRATE_GROUP_HELP, invoke_without_command=True)
@pass_controller
@click.pass_context
def migrate_group(ctx, controller):
    """Base `migrate` group command run prior to any of the dob-migrate commands."""
    if not ctx.invoked_subcommand:
        click_echo(ctx.get_help())


@migrate_group.command('control', help=help_strings.MIGRATE_CONTROL_HELP)
@pass_controller
@insist_germinated
def migrate_control(controller):
    """Mark a database as under version control."""
    migrate.control(controller)


@migrate_group.command('down', help=help_strings.MIGRATE_DOWN_HELP)
@pass_controller
@insist_germinated
def migrate_downgrade(controller):
    """Downgrade the database according to its migration version."""
    migrate.downgrade(controller)


@migrate_group.command('up', help=help_strings.MIGRATE_UP_HELP)
@pass_controller
@insist_germinated
def migrate_upgrade(controller):
    """Upgrade the database according to its migration version."""
    migrate.upgrade(controller)


@migrate_group.command('version', help=help_strings.MIGRATE_VERSION_HELP)
@pass_controller
@insist_germinated
def migrate_version(controller):
    """Show migration information about the database."""
    migrate.version(controller)

