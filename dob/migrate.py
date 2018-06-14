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
        barf_legacy_database(controller)
    return None


def latest_version(controller, silent_check=False, must=True):
    latest_ver = controller.store.migrations.latest_version()
    if latest_ver is not None:
        if not silent_check:
            click.echo(latest_ver)
        return latest_ver
    elif must:
        barf_legacy_database(controller)
    return None


# ***


def barf_legacy_database(controller):
    nark_path = os.path.dirname(os.path.dirname(nark.__file__))
    up_legacy_rel = os.path.join('migrations', 'upgrade_hamster-applet_db.sh')
    up_legacy_path = os.path.join(nark_path, up_legacy_rel)
    up_hamlib_rel = os.path.join('migrations', 'upgrade_hamster-lib_db.sh')
    up_hamlib_path = os.path.join(nark_path, up_hamlib_rel)
    db_path = controller.config['db_path']
    msg1 = _(
        '''
If this is a legacy database, upgrade and register the database.

If your database was created long ago by the original hamster,
`hamster-applet`, run the legacy database upgrade script, e.g.,

  {mintgreen}{up_legacy_path} \\
    {db_path}{reset}

Be sure to make a backup first, in case something goes wrong!

If your database was created more recently by the new `hamster-lib`
rewrite (2016-2017), run the hamster-lib upgrade script, e.g.,

  {mintgreen}{up_hamlib_path} \\
    {db_path}{reset}

See the project page for more information:

  https://github.com/hotoffthehamster/nark

After you upgrade the database, register it. E.g.,

  {mintgreen}{prog_name} migrate control{reset}

        '''.rstrip()
    )
    msg1 = msg1.format(
        prog_name=os.path.basename(sys.argv[0]),  # See also: dob.__appname__
        db_path=db_path,
        nark_path=nark_path,
        up_legacy_path=up_legacy_path,
        up_hamlib_path=up_hamlib_path,
        # green=(fg('light_green') + attr('bold')),
        mintgreen=(fg('spring_green_2a') + attr('bold')),
        # magenta_2a=(fg('magenta_2a') + attr('bold')),
        reset=attr('reset'),
    )
    msg2 = _('The database is not versioned!')
    msg2 = '{}{}{}'.format(fg('red'), msg2, attr('reset'))
    msg = '{}\n{}'.format(msg2, msg1)
    click.echo(msg)
    sys.exit(1)

