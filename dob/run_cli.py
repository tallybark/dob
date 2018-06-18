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
import sys

from nark import __version__ as nark_version
from nark.helpers import logging as logging_helpers
from nark.helpers.colored import disable_colors, enable_colors

from . import __appname__ as dob_appname
from . import __version__ as dob_version
from . import __libname__ as nark_appname
from . import help_strings
from .controller import Controller
from .copyright import echo_copyright

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'pass_controller',
    '_dob_version',
    'run',
    '_disable_logging',
    # Private:
    #  'CONTEXT_SETTINGS',
    #  '_setup_logging',
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

