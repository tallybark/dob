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

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import os
import sys

import nark
from nark.helpers.colored import fg, attr

from . import help_strings
from .helpers import dob_in_user_exit

__all__ = [
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
]


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
            click.echo(db_version)
        return db_version
    elif must:
        _barf_legacy_database(controller)
    return None


def latest_version(controller, silent_check=False, must=True):
    latest_ver = controller.store.migrations.latest_version()
    if latest_ver is not None:
        if not silent_check:
            click.echo(latest_ver)
        return latest_ver
    elif must:
        _barf_legacy_database(controller)
    return None


# ***


UPGRADE_INSTRUCTIONS = _(
    """
If your database was created long ago by the original hamster,
`hamster-applet`, run the legacy database upgrade script, e.g.,

  {mintgreen}{up_legacy_path} \\
    {db_path}{reset}

Be sure to make a backup first, in case something goes wrong!

If your database was created more recently by the new `hamster-lib`
rewrite (2016-2017), you can register the database (see below), and
then run the `migrate up` command.

See the project page for more information:

  https://github.com/hotoffthehamster/nark

After you upgrade the database, register it. E.g.,

  {mintgreen}{prog_name} migrate control{reset}
"""
)


def upgrade_legacy_database_instructions(controller):
    """"""
    nark_path = os.path.dirname(os.path.dirname(nark.__file__))
    up_legacy_rel = os.path.join('migrations', 'upgrade_hamster-applet_db.sh')
    up_legacy_path = os.path.join(nark_path, up_legacy_rel)
    db_path = controller.config['db_path']
    instructions = UPGRADE_INSTRUCTIONS.format(
        prog_name=os.path.basename(sys.argv[0]),  # See also: dob.__appname__
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
    click.echo(msg)
    sys.exit(1)


# ***

def upgrade_legacy_database_file(ctx, controller, file_in):
    if file_in is None:
        if controller.is_germinated:
            click.echo(ctx.get_help())
        else:
            _instruct_upgrade(controller)
    else:
        _upgrade_legacy_database_file(file_in)


def _instruct_upgrade(controller):
    click.echo(
        '\n{}\n{}'.format(
            help_strings.NEWBIE_HELP_WELCOME,
            upgrade_legacy_database_instructions(controller),
        )
    )


def _upgrade_legacy_database_file(file_in):
    # FIXME: (lb): Yeah.......
    raise NotImplementedError

