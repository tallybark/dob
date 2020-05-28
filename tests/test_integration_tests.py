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

from dob.cmds_list import fact as list_fact


class TestBasicRun(object):
    def test_basic_run(self, runner):
        """Make sure that invoking the command passes without exception."""
        result = runner()
        assert result.exit_code == 0


class TestSearchWithoutInitPrintsSetupMessage(object):
    def test_search_all(self, runner):
        """Running search command fails until dob conf and store are initialized."""
        result = runner(['search'])
        assert result.exit_code == 1
        assert "Let’s get you setup!" in result.stdout


class TestDobSearchCommandCallsFeatureHandler(object):
    def test_dob_search_command_calls(
        self,
        mocker,
        dob_runner,
        capsys,
    ):
        """Running search command fails until dob conf and store are initialized."""
        mocker.patch.object(list_fact, 'list_facts')
        result = dob_runner(['search'])
        assert result.exit_code == 0
        assert list_fact.list_facts.called
        # We stubbed list_facts, so there won't be any output.
        out, err = capsys.readouterr()
        assert not out and not err

