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

from click_hotoffthehamster import ClickException

import pytest

from dob.facts.cancel_fact import cancel_fact


class TestCancel(object):
    """Unit tests related to cancelation of an ongoing fact."""

    def test_cancel_existing_ongoing_fact(
        self, ongoing_fact, controller_with_logging, mocker, capsys,
    ):
        """Test cancelation in case there is an ongoing fact."""
        controller = controller_with_logging
        current_fact = mocker.MagicMock(return_value=ongoing_fact)
        controller.facts.cancel_current_fact = current_fact
        cancel_fact(controller)
        out, err = capsys.readouterr()
        assert controller.facts.cancel_current_fact.called
        assert out.startswith('Cancelled: ')

    def test_cancel_no_existing_ongoing_fact(self, controller_with_logging, capsys):
        """Test cancelation in case there is no actual ongoing fact."""
        with pytest.raises(ClickException):
            cancel_fact(controller_with_logging)
            assert False  # Unreachable.

