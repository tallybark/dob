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

"""Copyright output UX methods."""

import os
from datetime import datetime

from gettext import gettext as _

from dob_bright.termio import click_echo

from . import (
    get_version,
    __arg0name__,
    __author_name__,
    __author_link__,
    __package_name__
)

__all__ = (
    'assemble_copyright',
    'echo_copyright',
    'echo_license',
)


def assemble_copyright():
    """Display a greeting message providing basic set of information."""
    cur_year = str(datetime.now().year)
    year_range = '2018'
    if cur_year != year_range:
        year_range = '2018-{}'.format(cur_year)
    gpl3_notice_2018 = [
        'This is {pkgname} v{version}.'.format(
            pkgname=__package_name__,
            version=get_version(),
        ),
        '',
        'Copyright (C) {years} {aname} <{alink}>'.format(
            years=year_range,
            aname=__author_name__,
            alink=__author_link__,
        ),
        # Be nice and call out the significant copyright holders from the years.
        # (lb): What about Right to be forgotten?
        'Copyright (C) 2015-2016 Eric Goller <elbenfreund@DenkenInEchtzeit.net>',
        '',
        _('This program comes with ABSOLUTELY NO WARRANTY. This is free software,'),
        _('and you are welcome to redistribute it under certain conditions.'),
        _(''),
        _('Run `{} license` for your legal rights and responsibilities.'
          ).format(__arg0name__),
    ]
    copy_notice = gpl3_notice_2018
    return copy_notice


def echo_copyright():
    notice = assemble_copyright()
    for line in notice:
        click_echo(line)


def echo_license():
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
    license_txt = license.format(app_name=__package_name__)
    # MAYBE: (lb): Prefer the LICENSE file?
    # FIXME: LICENSE is probably not copied via pip-install.
    #        This will be good learning on installing non-package files.
    license_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'LICENSE',
    )
    if os.path.exists(license_path):
        with open(license_path, 'rb') as f:
            license_txt = f.read().decode('utf-8').strip()
    click_echo(license_txt)

