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

import pytest

from dob.facts.echo_fact import echo_ongoing_fact


class TestCurrent(object):
    """Unittest for dealing with 'ongoing facts'."""

    def test_no_ongoing_fact(self, controller_with_logging, capsys):
        """Make sure we display proper feedback if there is no current 'ongoing fact."""
        controller = controller_with_logging
        with pytest.raises(SystemExit):
            echo_ongoing_fact(controller)
            assert False  # Unreachable.

