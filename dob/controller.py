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

"""The Controller."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import logging
import os
import sys

from nark.control import HamsterControl
from nark.helpers import logging as logging_helpers
from nark.helpers.colored import disable_colors, enable_colors

from . import __arg0name__
from . import help_strings
from .copyright import echo_copyright
from .cmd_config import get_config_path, furnish_config, replenish_config
from .helpers import click_echo, dob_in_user_exit, highlight_value
from .migrate import upgrade_legacy_database_instructions
from .traverser.placeable_fact import PlaceableFact

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'Controller',
]


# ***
# *** [CONTROLLER] HamsterControl Controller.
# ***

class Controller(HamsterControl):
    """
    A custom controller that adds config handling on top of its regular functionality.
    """

    POST_PROCESSORS = []

    def __init__(self, nark_preset=None, dob_preset=None):
        """Load backend and client configs, and instantiate controller."""
        nark_config, dob_config, preexists = furnish_config(nark_preset, dob_preset)
        self._adjust_log_level(nark_config)
        super(Controller, self).__init__(nark_config)
        self.client_config = dob_config
        self.cfgfile_exists = preexists

    @property
    def now(self):
        return self.store.now

    @property
    def data_store_exists_at(self):
        return _(
            'Data store already exists at {}'
        ).format(self.config['db_path'])

    @property
    def data_store_url(self):
        return self.store.get_db_url()

    @property
    def sqlite_db_path(self):
        if self.config['db_engine'] == 'sqlite':
            return self.config['db_path']
        else:
            # (lb): I don't super-like this. It's a weird side effect.
            #   And it's knowledgeable about the CLI command API. Meh.
            dob_in_user_exit(_(
                'Not a SQLite database. Try `{} store url`'
            ).format(__arg0name__))

    @property
    def is_germinated(self):
        if self.cfgfile_exists and self.store_exists:
            return True
        return False

    @property
    def store_exists(self):
        # Check either db_path is set, or all of db_host/_port/_name/_user.
        if self.config['db_engine'] == 'sqlite':
            return os.path.isfile(self.config['db_path'])
        else:
            return bool(self.store.get_db_url())

    def standup_store(self):
        self.store.fact_cls = PlaceableFact
        return super(Controller, self).standup_store()

    def insist_germinated(self):
        """Assist user if config or database not present."""
        def _insist_germinated():
            store_exists = self.store_exists
            if self.cfgfile_exists and store_exists:
                self.standup_store()
                return
            if not self.cfgfile_exists and not store_exists:
                help_newbie_onboard()
            else:
                berate_user_files_unwell(store_exists)
            echo_copyright()
            sys.exit(1)

        def help_newbie_onboard():
            click_echo(
                help_strings.NEWBIE_HELP_ONBOARDING.format(
                    legacy_help=upgrade_legacy_database_instructions(self),
                ),
                err=True,
            )

        def berate_user_files_unwell(store_exists):
            if not self.cfgfile_exists:
                oblige_user_create_config()
            if not store_exists:
                oblige_user_create_store()

        def oblige_user_create_config():
            click_echo(help_strings.NEWBIE_HELP_CREATE_CONFIG, err=True)

        def oblige_user_create_store():
            click_echo(help_strings.NEWBIE_HELP_CREATE_STORE, err=True)

        _insist_germinated()

    def create_config(self, force):
        exists = os.path.exists(get_config_path())
        if exists and not force:
            dob_in_user_exit(_('Config file exists'))
        nark_config, dob_config, file_path = replenish_config()
        self._adjust_log_level(nark_config)
        self.config = nark_config
        self.client_config = dob_config
        click_echo(
            _('Initialized default Dob configuration at {}').format(
                highlight_value(file_path),
            )
        )

    def create_data_store(self, force):
        skip_standup = self.check_sqlite_store_ready()
        if skip_standup:
            if force:
                self._reset_data_store()
                unlinked_db = True
            else:
                dob_in_user_exit(self.data_store_exists_at)
        self._standup_and_version_store()
        if unlinked_db:
            self._announce_recreated_store()

    def create_config_and_store(self):
        def _create_config_and_store():
            if not self.is_germinated:
                germinate_config_and_store()
            else:
                exit_already_germinated()

        def germinate_config_and_store():
            create_config_maybe()
            create_store_maybe()

        def create_config_maybe():
            cfg_path = get_config_path()
            if not os.path.exists(cfg_path):
                self.create_config(force=False)
            else:
                click_echo(
                    _('Configuration already exists at {}').format(
                        highlight_value(cfg_path),
                    )
                )

        def create_store_maybe():
            # MEH: (lb): If the engine is not SQLite, this function cannot behave
            # like create_config_maybe, which tells the user if the things exists
            # already, because the storage class, SQLAlchemyStore, blindly calls
            # create_all (in create_storage_tables) without checking if db exists.
            skip_standup = self.check_sqlite_store_ready()
            if skip_standup:
                click_echo(self.data_store_exists_at)
            else:
                self._standup_and_version_store()

        def exit_already_germinated():
            dob_in_user_exit(_(
                'Dob is already setup. Run `{} details` for info.'
            ).format(__arg0name__))

        _create_config_and_store()

    def _adjust_log_level(self, nark_config):
        # *cough*hack!*cough*”
        # Because invoke_without_command, we allow command-less invocations.
        #   For one such invocation -- dob -v -- tell the store not to log.
        # Also tell the store not to log if user did not specify anything,
        #   because we'll show the help/usage (which Click would normally
        #   handle if we had not tampered with invoke_without_command).
        if (
            (len(sys.argv) > 2) or
            ((len(sys.argv) == 2) and (sys.argv[1] not in ('-v', 'version')))
        ):
            return
        nark_config['sql_log_level'] = 'WARNING'

    def check_sqlite_store_ready(self):
        if self.config['db_engine'] != 'sqlite':
            return None
        db_path = self.config['db_path']
        if not os.path.isfile(db_path):
            return False
        return True

    def _reset_data_store(self):
        if self.config['db_engine'] != 'sqlite':
            # raise NotImplementedError
            dob_in_user_exit(_(
                'FIXME: Reset non-SQLite data store not supported (yet).'
            ))
        else:
            self.must_unlink_db_path(force=True)

    def must_unlink_db_path(self, *_args, force):
        db_path = self.config['db_path']
        if not os.path.exists(db_path):
            return
        if not os.path.isfile(db_path):
            dob_in_user_exit(_(
                'Data store exists but is not a file, so not overwriting {}'
            ).format(db_path))
        if not force:
            dob_in_user_exit(self.data_store_exists_at)
        os.unlink(db_path)

    def _announce_recreated_store(self):
        click_echo(
            _('Recreated data store at {}')
            .format(highlight_value(self.config['db_path']))
        )

    def _standup_and_version_store(self):
        created_fresh = self.standup_store()
        if created_fresh:
            verb = _('created')
        else:
            verb = _('already ready')
        click_echo(
            _('Dob database {verb} at {url}').format(
                verb=verb, url=highlight_value(self.store.get_db_url()),
            )
        )

    @staticmethod
    def post_processor(func):
        Controller.POST_PROCESSORS.append(func)

    @staticmethod
    def _post_process(controller, fact):
        for handler in Controller.POST_PROCESSORS:
            handler(controller, fact)

    def post_process(self, controller, fact):
        Controller._post_process(controller, fact)

    def setup_tty_color(self, use_color):
        if use_color is None:
            use_color = self.client_config['term_color']
        else:
            self.client_config['term_color'] = use_color
        if use_color:
            enable_colors()
        else:
            disable_colors()

    # ***

    def setup_logging(self, verbose=False, verboser=False):
        """Setup logging for the lib_logger as well as client specific logging."""
        self.client_logger = logging.getLogger('dob')
        loggers = self.get_loggers()
        # Clear existing Handlers, and set the level.
        # MAYBE: Allow user to specify different levels for different loggers.
        client_level = self.client_config['log_level']
        log_level, warn_name = logging_helpers.resolve_log_level(client_level)
        # We can at least allow some simpler optioning from the command args.
        if verbose:
            log_level = min(logging.INFO, log_level)
        if verboser:
            log_level = min(logging.DEBUG, log_level)
        for logger in loggers:
            logger.handlers = []
            logger.setLevel(log_level)

        color = self.client_config['log_color']
        formatter = logging_helpers.formatter_basic(color=color)

        if self.client_config['log_console']:
            console_handler = logging.StreamHandler()
            logging_helpers.setup_handler(console_handler, formatter, *loggers)

        if self.client_config['logfile_path']:
            filename = self.client_config['logfile_path']
            file_handler = logging.FileHandler(filename, encoding='utf-8')
            logging_helpers.setup_handler(file_handler, formatter, *loggers)

        if warn_name:
            self.client_logger.warning(
                _('Unknown Client.log_level specified: {}')
                .format(client_level)
            )

    def get_loggers(self):
        loggers = [
            self.lib_logger,
            self.sql_logger,
            self.client_logger,
        ]
        return loggers

    def bulk_set_log_levels(self, log_level):
        for logger in self.get_loggers():
            logger.setLevel(log_level)

    def disable_logging(self):
        loggers = [
            self.lib_logger,
            self.sql_logger,
            self.client_logger,
        ]
        for logger in loggers:
            logger.handlers = []
            logger.setLevel(logging.NOTSET)

    # ***

    def affirm(self, condition):
        if condition:
            return
        self.client_logger.error(_('Something catastrophic happened!'))
        if not self.client_config['devmode']:
            return
        import traceback
        traceback.print_stack()
        traceback.print_exc()
        import pdb
        pdb.set_trace()
        # This makes neither input echo nor any command output appear!
        #   import sys, pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        #   import sys, pdb; pdb.Pdb(stdout=STDOUT).set_trace()

    # ***

    def wire_pdb_pipes(self):
        if not self.client_config['devmode']:
            return
        if not self.client_config['fifo_dir']:
            return
        # Fix terminal echo in PDB on breakpoint.
        # NOTE: Readline-ish stuff does not work, like previous history with up arrow.
        #       But copy-paste works, TFG.
        # https://stackoverflow.com/questions/17074177/
        #   how-to-debug-python-cli-that-takes-stdin
        try:
            self.monkey_patch_set_trace()
        except FileNotFoundError as err:
            self.client_logger.warning(
                _('Cannot patch set_trace: ‘{}’'.format(err))
            )

    def monkey_patch_set_trace(self):
        import pdb
        basename = self.client_config['fifo_dir']
        fifo_stdin = open(os.path.join(basename, 'fifo_stdin'), 'r')
        fifo_stdout = open(os.path.join(basename, 'fifo_stdout'), 'w')
        mypdb = pdb.Pdb(stdin=fifo_stdin, stdout=fifo_stdout)
        pdb.set_trace = mypdb.set_trace

    # ANOTHER OPTION:
    # def tty_pdb():
    #     from contextlib import (
    #         _RedirectStream, redirect_stdout, redirect_stderr
    #     )
    #     class redirect_stdin(_RedirectStream):
    #         _stream = 'stdin'
    #     with open('/dev/tty', 'r') as new_stdin, \
    #          open('/dev/tty', 'w') as new_stdout, \
    #          open('/dev/tty', 'w') as new_stderr, \
    #          redirect_stdin(new_stdin), \
    #          redirect_stdout(new_stdout), redirect_stderr(new_stderr):
    #         __import__('pdb').set_trace()

