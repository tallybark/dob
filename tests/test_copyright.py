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

from dob import dob


class TestCommandCopyright(object):
    """Make shure our greeting function behaves as expected."""

    def test_shows_copyright(self, capsys):
        """Make sure we show basic copyright information."""
        dob.echo_copyright()
        out, err = capsys.readouterr()
        assert "Copyright" in out

    # Already tested, really; see: test_dob_license_wrapper (dob._license() test).
    def test_shows_license(self, capsys):
        """Make sure we display a brief reference to the license."""
        dob.echo_license()
        out, err = capsys.readouterr()
        assert 'GNU GENERAL PUBLIC LICENSE' in out
        assert 'Version 3' in out

