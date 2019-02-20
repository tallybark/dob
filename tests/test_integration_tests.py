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


class TestBasicRun(object):
    def test_basic_run(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner()
        assert result.exit_code == 0


class TestSearchWithoutTermEmptyDatabase(object):
    def test_search_all(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner(['search'])
        assert result.exit_code == 1

# FIXME/2019-01-12 15:07: Reimplement this.
# exit codes have changed, especially for commands run against empty database.
# may also need/want database fixture to really do this right.
FIXME_2019_01_12='''

class TestSearchWithoutTermTest0Database(object):
    def test_search_all(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner(['search'])
#
        import pdb;pdb.set_trace()

        assert result.exit_code == 0


class TestListFacts(object):
    def test_search_all(self, runner):
        """Make sure that invoking the command passes without exception."""
        # Wired to same code as `dob search`.
        result = runner(['list', 'facts'])
        assert result.exit_code == 0


# FIXME/2019-01-12 13:49: 2 issues: (1) rewire database;
#   (2) fix `dob search`, not finding anything against my own data.

class TestSearchTerm(object):
    def test_search_term(self, runner):
        """Make sure that invoking the command passes without exception."""
#
        import pdb;pdb.set_trace()

        result = runner(['search', 'foobar'])
# FIXME: this should fail, correct?
#   OR AM I TESTING AGAINST MY OWN DB????
#   I may need to address that... and stick in a test database?????? prolly yes prolly
#        assert result.exit_code == 0
        assert result.exit_code == 1
        assert result.stdout == 'No facts were found for the specified query.\n'


class TestList(object):
    def test_list(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner(['list'])
        assert result.exit_code == 0

# FIXME/2019-01-11 19:28: Is this the CLI front end tester I hadn't known about until now?

#class TestStart(object):
#    def test_start(self, runner):
class TestAddFactNow(object):
    def test_add_fact_now(self, runner):
        """Make sure that invoking the command passes without exception."""
#        result = runner(['start', 'coding', '', ''])
        result = runner(['now', 'coding', '', ''])
        assert result.exit_code == 0


class TestStop(object):
    def test_stop(self, runner):
        """
        Make sure that invoking the command passes without exception.

        As we don't have a ``ongoing fact`` by default, we expect an expectation to be raised.
        """
        result = runner(['stop'])
        assert result.exit_code == 1


class TestCancel(object):
    def test_cancel(self, runner):
        """
        Make sure that invoking the command passes without exception.

        As we don't have a ``ongoing fact`` by default, we expect an expectation to be raised.
        """
        result = runner(['cancel'])
        assert result.exit_code == 1


class TestCurrent(object):
    def test_current(self, runner):
        """
        Make sure that invoking the command passes without exception.

        As we don't have a ``ongoing fact`` by default, we expect an expectation to be raised.
        """
        result = runner(['current'])
        assert result.exit_code == 1


class TestExport(object):
    def test_export(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner(['export'])
        assert result.exit_code == 0


class TestCategories(object):
    def test_categories(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner(['categories'])
        assert 'Error' not in result.output
        assert result.exit_code == 0


class TestActivities(object):
    def test_activities(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner(['activities'])
        assert 'Error' not in result.output
        assert result.exit_code == 0


class TestLicense(object):
    """Make sure command works as expected."""

    def test_license(self, runner):
        """Make sure command launches without exception."""
        result = runner(['license'])
        assert result.exit_code == 0


class TestDetails(object):
    """Make sure command works as expected."""

    def test_details(self, runner):
        """Make sure command launches without exception."""
        result = runner(['details'])
        assert result.exit_code == 0

'''

