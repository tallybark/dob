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
from datetime import datetime

from . import __author__, __author_email__, __BigName__
from . import __appname__ as dob_appname
from . import __version__ as dob_version

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'echo_copyright',
    'echo_license',
]


def echo_copyright():
    """Display a greeting message providing basic set of information."""
    cur_year = str(datetime.now().year)
    year_range = '2018'
    if cur_year != year_range:
        year_range = '2018-{}'.format(year_range)
    gpl3_notice_2018 = [
        '{app_name} {version}'.format(
            app_name=__BigName__,
            version=dob_version,
        ),
        '',
        'Copyright (C) {years} {author} <{email}>'.format(
            years=year_range,
            author=__author__,
            email=__author_email__,
        ),
        # Be nice and call out the significant copyright holders from the years.
        # (lb): What about Right to be forgotten?
        'Copyright (C) 2015-2016 Eric Goller <elbenfreund@DenkenInEchtzeit.net>',
        'Copyright (C) 2007-2014 Toms Baugis <toms.baugis@gmail.com>',
        'Copyright (C) 2007-2008 Patryk Zawadzki <patrys at pld-linux.org>',
        '',
        _('This program comes with ABSOLUTELY NO WARRANTY.'),
        _('This is free software, and you are welcome to'),
        _('redistribute it under certain conditions.'),
        _('Run `{} license` for details.').format(dob_appname),
    ]
    notice = gpl3_notice_2018
    for line in notice:
        click.echo(line)


def echo_license():
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

