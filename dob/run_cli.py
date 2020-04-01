# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
#
# 'dob' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'dob' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

"""Defines the main Click Group."""

import sys

import click_hotoffthehamster as click

# BREADCRUMP: PROFILING
from nark.helpers.dev.profiling import profile_elapsed, timefunct

from dob_bright.controller import Controller
from dob_bright.termio import click_echo, echo_exit
from dob_bright.termio.paging import set_paging

from .clickux import help_strings
from .clickux.aliasable_bunchy_plugin import ClickAliasableBunchyPluginGroup
from .copyright import echo_copyright

__all__ = (
    'pass_controller',
    'dob_versions',
    'run',
    # Private:
    #  'CONTEXT_SETTINGS',
)


# Profiling: Controller is made during Command.invoke via click.MultiCommand.invoke.
# Profiling: Controller calls _get_store: ~ 0.173 secs.
pass_controller = click.make_pass_decorator(Controller, ensure=True)


# ***
# *** [VERSION] Version command helper.
# ***

def dob_versions(include_all=False):
    '''Return CLI version information, either for this package, or all HOTH packages.
    '''
    vers = ''
    include_head = include_all
    import importlib
    # MAYBE/2020-04-01: Add config_decorator and pedantic_timedelta.
    hothlibs = ['dob']
    if include_all:
        hothlibs += [
            'dob_viewer',
            'dob_prompt',
            'dob_bright',
            'nark',
        ]
    minlen = max([len(name) for name in hothlibs])
    for hothlib in hothlibs:
        mod = importlib.import_module(hothlib, package=None)
        vers += '\n' if vers else ''
        vers += '{name:{minlen}s} version {vers}'.format(
            minlen=minlen,
            name=mod.__package_name__,
            vers=mod.get_version(include_head=include_head),
        )
    return vers


# ***
# *** [CLICK ROOT CONTEXT] Twiddle default Context behavior.
# ***

CONTEXT_SETTINGS = dict(
    # Tell Click to plumb the -h and --help options.
    help_option_names=['-h', '--help'],
    # But also tell Click not to invoke the help callback,
    # which it would otherwise do immediately when it sees
    # the help option.
    #
    # By default, Click processes help immediately when spotted.
    #
    # This has a few consequences:
    #
    # - If --help is seen before the subcommand in args, the run() method
    #   below is not called, because Click handles the --help before invoking
    #   the callback, and the Click help callback prints the help and exits.
    #   As such, color and paging will not be setup properly for root help.
    #   However, for subcommand help, our run() will be called, and then color
    #   and paging will be setup properly for the subcommand help!
    #
    # - If the user wants help on a subcommand, Click forces them to specify
    #   the --help option after the command, i.e., `dob --help command` would
    #   normally print the same thing as `dob --help`. But we'd rather print
    #   the help for the subcommand specified. (This also makes such obvious
    #   commands like `dob help command` work as expected as well!)
    #
    # So tell Click not to process help upon sight, but to mark a flag.
    # Later, we'll look for help_option_spotted on the root context.
    help_option_fallthrough=True,
    max_content_width=85,
)


# ***
# *** [BASE COMMAND GROUP] One Group to rule them all.
# ***

# (lb): Use invoke_without_command so `dob -v` works, otherwise Click's
# Group (MultiCommand ancestor) does not allow it ('Missing command.').
@click.group(
    # (lb): Use our Plugin group class , which dynamically loads pluggable
    # commands from user's, e.g., ~/.config/dob/plugins directory. That class
    # derives from an Aliasable group class, which empowers us to assign command
    # name aliases. That class, in turn, derives from Click's base Group class.
    cls=ClickAliasableBunchyPluginGroup,
    invoke_without_command=True,
    help=help_strings.RUN_HELP_OVERVIEW,
    context_settings=CONTEXT_SETTINGS,
)
# (lb): Also include version to avoid RuntimeError, ha!
@click.version_option(message=dob_versions(), version='')
# (lb): Hide -v: version_option adds help for --version, so don't repeat ourselves.
@click.option('-v', is_flag=True, help=help_strings.VERSION_HELP, hidden=True)
# (lb): Note that universal --options must com before the sub command.
# FIXME: Need universal options in cmd_options? Or can I apply to Groups?
#          These aren't recognized by other fcns...
#        OH! These have to come *before* the command??
@click.option('-V', '--verbose', is_flag=True,
              help=help_strings.GLOBAL_OPT_VERBOSE)
@click.option('-VV', '--verboser', is_flag=True, hidden=True,
              help=help_strings.GLOBAL_OPT_VERBOSER)
# (lb): 2019-11-19: Trying -X, like you're PAINTING the screen.
@click.option('-C', '--color/--no-color', '-X', default=None,
              help=help_strings.GLOBAL_OPT_COLOR_NO_COLOR)
@click.option('-P', '--pager/--no-pager', default=None,
              help=help_strings.GLOBAL_OPT_PAGER_NO_PAGER)
@click.option('-c', '--config', multiple=True, metavar='KEY=VALUE',
              help=help_strings.GLOBAL_OPT_CONFIG)
# (lb): We could use `type=click.File('r')` here. Or not.
@click.option('-F', '--configfile', metavar='PATH',
              help=help_strings.GLOBAL_OPT_CONFIGFILE)
# Profiling: pass_controller appears to take ~ ¼ seconds.
@timefunct('run: create Controller [_get_store]')
@pass_controller
@click.pass_context
# NOTE: @click.group transforms this func. definition into a callback that
#       we use as a decorator for the top-level commands (see: @run.command).
def run(ctx, controller, v, verbose, verboser, color, pager, config, configfile):
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
        profile_elapsed('To dob:    run')
        controller.ensure_config(ctx, configfile, *config)
        _setup_tty_options(ctx, controller)
        _run_handle_banner()
        _run_handle_version(ctx, show_version)
        _run_handle_without_command(ctx)
        controller.setup_logging(verbose, verboser)

    def _setup_tty_options(ctx, controller):
        # If piping output, Disable color and paging.
        # MAYBE: (lb): What about allowing color for outputting to ANSI file? Meh.
        use_color = color
        if use_color is None and not sys.stdout.isatty():
            controller.config['term.use_pager'] = False
            controller.config['term.use_color'] = False
        _setup_tty_paging(controller)
        _setup_tty_color(ctx, controller)

    def _setup_tty_paging(controller):
        use_pager = pager
        if use_pager is None:
            # None if --pager nor --no-pager specified,
            # so fallback to what's in the user config.
            use_pager = controller.config['term.use_pager']
        set_paging(use_pager)

    def _setup_tty_color(ctx, controller):
        use_color = color
        controller.setup_tty_color(use_color)
        # We'll set the Click Context object's color attribute, too, but note
        # that only Click's echo() method strips color based on that attribute;
        # the format_help() methods do not scrub ANSI codes, so we still need
        # to be color-aware ourselves. (So setting ctx.color here is more of a
        # formality than something that actually does anything.)
        ctx.color = color

    def _run_handle_banner():
        # (lb): I find the greeting annoying, and somewhat boastful.
        #   It's not that I'm against self-promotion, per se -- and I
        #   recognize that the GPL instructs open source software to
        #   always output a license, on every invocation -- but I like
        #   the clean aesthetics of not showing it. Though I suppose
        #   it's easy enough just to make a config option for it....
        if not controller.config['term.show_greeting']:
            return
        echo_copyright()
        click_echo()

    def _run_handle_version(ctx, show_version):
        if show_version:
            echo_exit(ctx, dob_versions(include_all=False))

    def _run_handle_without_command(ctx):
        # Because we set invoke_without_command, we have to check ourselves
        # if invoked without any command, in which case show the help.
        # Note this code originally, naively checked `if len(sys.argv) == 1`,
        # but the context (which is always root when run() is invoked) knows
        # if there's a subcommand specified, so check that attribute instead.
        if ctx.invoked_subcommand is None:
            echo_exit(ctx, ctx.get_help())

    # Shim to the private run() functions.

    _run(ctx, controller, show_version=v)

