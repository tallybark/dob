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

import os
import shutil
import sys

from gettext import gettext as _

from nark import __file__ as nark___file__

from dob_bright.help_newbs import NEWBIE_HELP_WELCOME
# Profiling: load AppDirs: ~ 0.011 secs.
from dob_bright.config.app_dirs import AppDirs
from dob_bright.termio import (
    attr,
    click_echo,
    dob_in_user_exit,
    dob_in_user_warning,
    fg,
    highlight_value
)

from . import __arg0name__

__all__ = (
    'control',
    'downgrade',
    'upgrade',
    'version',
    'latest_version',
    'upgrade_legacy_database_file',
    'upgrade_legacy_database_instructions',
    # Private:
    #  '_barf_legacy_database',
    #  '_instruct_upgrade',
    #  '_upgrade_legacy_database_file',
)


def control(controller):
    err_msg = None
    success = False
    versioned = version(controller, silent_check=True, must=False)
    if not versioned:
        # MAYBE/2018-05-18: (lb): Also check if legacy database!
        success = controller.store.migrations.control()
        if success is None:
            err_msg = _('Something went wrong! Sorry!!')
    if not success and not err_msg:
        err_msg = _('The database is already versioned!')
    if err_msg:
        dob_in_user_exit(err_msg)


def downgrade(controller):
    version(controller, silent_check=True, must=True)
    response = controller.store.migrations.downgrade()
    assert response is not None
    if not response:
        dob_in_user_exit(_('The database is already at the earliest version'))


def upgrade(controller):
    version(controller, silent_check=True, must=True)
    response = controller.store.migrations.upgrade()
    assert response is not None
    if not response:
        dob_in_user_exit(_('The database is already at the latest version'))


def version(controller, silent_check=False, must=True):
    db_version = controller.store.migrations.version()
    if db_version is not None:
        if not silent_check:
            click_echo(db_version)
        return db_version
    elif must:
        _barf_legacy_database(controller)
    return None


def latest_version(controller, silent_check=False, must=True):
    latest_ver = controller.store.migrations.latest_version()
    if latest_ver is not None:
        if not silent_check:
            click_echo(latest_ver)
        return latest_ver
    elif must:
        _barf_legacy_database(controller)
    return None


# ***

UPGRADE_INSTRUCTIONS = _(
    """
If your database was created long ago by the original hamster,
`hamster-applet`, run the legacy database upgrade script, e.g.,

  {mintgreen}{prog_name} store upgrade-legacy \\
    {legacy_path}{reset}

Be sure to make a backup first, in case something goes wrong!
"""
)
# 2020-03-31: I had a link to the project page here but there's
# no additional information there, so why bother. It read,
#
#   See the project page for more information:
#
#       https://github.com/hotoffthehamster/nark
#
# As for actual upgrade help online, there's only one spot, but
# it says nothing more than what we've said here. It's at
#
#   https://dob.readthedocs.io/en/latest/usage.html#upgrade-hamster

# USER: If your database was created more recently by the new `hamster-lib`
# rewrite (2016-2017), there are 3 database changes to make. (lb): I did not
# add an upgrade path from hamster-lib because it seemed like that project
# was never quite released. So I assume no one's using it?


def upgrade_legacy_database_instructions(controller):
    """"""
    nark_path = os.path.dirname(os.path.dirname(nark___file__))
    up_legacy_rel = os.path.join(
        'migrations', 'legacy', 'upgrade_hamster-applet_db.sh',
    )
    up_legacy_path = os.path.join(nark_path, up_legacy_rel)
    db_path = controller.config['db.path']
    instructions = UPGRADE_INSTRUCTIONS.format(
        prog_name=__arg0name__,
        legacy_path="~/.local/share/hamster-applet/hamster.db",
        db_path=db_path,
        nark_path=nark_path,
        up_legacy_path=up_legacy_path,
        # green=(fg('light_green') + attr('bold')),
        mintgreen=(fg('spring_green_2a') + attr('bold')),
        # magenta_2a=(fg('magenta_2a') + attr('bold')),
        reset=attr('reset'),
    )
    return instructions


def _barf_legacy_database(controller):
    """"""
    prefix = '''
If this is a legacy database, upgrade and register the database.
'''.strip()
    msg1 = prefix + upgrade_legacy_database_instructions(controller)
    msg2 = _('The database is not versioned!')
    msg2 = '{}{}{}'.format(fg('red_3b'), msg2, attr('reset'))
    msg = '{}\n{}'.format(msg2, msg1)
    click_echo(msg)
    sys.exit(1)


# ***

def upgrade_legacy_database_file(ctx, controller, file_in, force):
    """"""
    db_path = controller.config['db.path']

    def _upgrade_legacy_database_file():
        if file_in is None:
            echo_help()
            return None
        else:
            copy_and_upgrade()
            return True

    def copy_and_upgrade():
        copy_into_place()
        run_upgrade()
        run_migrations()
        click_echo(
            _('Seeded data store at {}')
            .format(highlight_value(db_path))
        )

    def copy_into_place():
        if os.path.exists(db_path) and os.path.samefile(db_path, file_in.name):
            return
        controller.must_unlink_db_path(force=force)
        must_copy_new_db_to_db_path()

    def must_copy_new_db_to_db_path():
        try:
            db_dir = os.path.dirname(db_path)
            AppDirs._ensure_directory_exists(db_dir)
            shutil.copyfile(file_in.name, db_path)
        except Exception as err:
            msg = _('Failed to copy new database to ‘{}’').format(str(err))
            dob_in_user_warning(msg)

    def echo_help():
        if controller.is_germinated:
            click_echo(ctx.get_help())
        else:
            _instruct_upgrade(ctx, controller)

    def run_upgrade():
        try:
            controller.store.migrations.legacy_upgrade_from_hamster_applet(db_path)
        except Exception as err:
            dob_in_user_exit(_('Upgrade failed! ERROR: {}').format(str(err)))

    def run_migrations():
        db_version = controller.store.migrations.version()
        assert db_version is None
        control(controller)
        db_version = controller.store.migrations.version()
        assert db_version == 0
        response = True
        while response:
            response = controller.store.migrations.upgrade()

    return _upgrade_legacy_database_file()


def _instruct_upgrade(ctx, controller):
    click_echo(
        '\n{}\n{}'.format(
            NEWBIE_HELP_WELCOME(ctx),
            upgrade_legacy_database_instructions(controller),
        )
    )

