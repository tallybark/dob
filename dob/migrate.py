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

from nark.helpers.colored import fg, attr

from .cmd_common import barf_on_error

__all__ = [
    'control',
    'downgrade',
    'upgrade',
    'version',
    'latest_version',
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
    barf_on_error(err_msg)


def downgrade(controller):
    version(controller, silent_check=True, must=True)
    response = controller.store.migrations.downgrade()
    assert response is not None
    if not response:
        barf_on_error(_('The database is already at the earliest version'))


def upgrade(controller):
    version(controller, silent_check=True, must=True)
    response = controller.store.migrations.upgrade()
    assert response is not None
    if not response:
        barf_on_error(_('The database is already at the latest version'))


def version(controller, silent_check=False, must=True):
    db_version = controller.store.migrations.version()
    if db_version is not None:
        if not silent_check:
            click.echo(db_version)
        return db_version
    elif must:
        barf_legacy_database()
    return None


def latest_version(controller, silent_check=False, must=True):
    latest_ver = controller.store.migrations.latest_version()
    if latest_ver is not None:
        if not silent_check:
            click.echo(latest_ver)
        return latest_ver
    elif must:
        barf_legacy_database()
    return None


# ***


def barf_legacy_database():
    msg1 = _(
        '''
If this is a legacy database, try running:

  {green}migrations/upgrade_legacy_hamster_v2.sh path/to/db{reset}

from the `nark` source repository, which can be found at:

  https://github.com/hotoffthehamster/nark

After upgrading a legacy database -- or if you are upgrading
a pre-fork modern Hamster database (circa 2016-2017, a/k/a
hamster-lib and hamster-cli) -- try registering the database:

  {green}{prog_name} migrate control{reset}
        '''.strip()
    )
    msg1 = msg1.format(
        prog_name=os.path.basename(sys.argv[0]),  # See also: dob.__appname__
        green=(fg('light_green') + attr('bold')),
        reset=attr('reset'),
    )
    msg2 = _('The database is not versioned!')
    msg2 = '{}{}{}'.format(fg('red'), msg2, attr('reset'))
    msg = '{}\n{}'.format(msg2, msg1)
    click.echo(msg)
    sys.exit(1)

