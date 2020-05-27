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

from freezegun import freeze_time

from nark.tests.conftest import *
from nark.tests.backends.sqlalchemy.conftest import *

from dob.cmds_list.fact import list_facts
from dob.cmds_list.fact import search_facts


class TestCmdsListFactSearchFacts(object):
    """Unit tests for search command."""

    @freeze_time('2015-12-12 18:00')
    def test_search_facts_since_until(
        self, controller, mocker, fact, search_parameter_parametrized,
    ):
        """Ensure since and until are converted to datetime for backend function."""
        # See also: nark's test_get_all_various_since_and_until_times
        since, until, description, expectation = search_parameter_parametrized
        controller.facts.gather = mocker.MagicMock(return_value=[fact])
        # F841 local variable '_facts' is assigned to but never used
        _facts = search_facts(controller, since=since, until=until)  # noqa: F841
        assert controller.facts.gather.called
        # call_args is (args, kwargs), and QueryTerms is the first args arg.
        query_terms = controller.facts.gather.call_args[0][0]
        assert query_terms.since == expectation['since']
        assert query_terms.until == expectation['until']

    def test_search_facts_fails_on_unsupported_store(self, controller, capsys):
        """Ensure search_facts prints a user warning on unsupported store type."""
        # MAYBE/2020-05-26: Add support for other data stores (other than SQLite),
        #   which requires using and wiring the appropriate DBMS-specific aggregate
        #   functions.
        #   - For now, dob is at least nice enough to print an error message.
        controller.store.config['db.engine'] += '_not'
        with pytest.raises(SystemExit):
            search_facts(controller)
            assert False  # Unreachable.
        # assert result.exit_code == 1
        out, err = capsys.readouterr()
        # See: must_support_db_engine_funcs.
        expect = 'This feature does not work with the current DBMS engine'
        assert err.startswith(expect)


class TestCmdsListFactSearchListFacts(object):
    """"""

    def test_list_facts_empty_store(self, controller_with_logging, capsys):
        """..."""
        controller = controller_with_logging
        with pytest.raises(SystemExit):
            list_facts(
                controller,
            )
            assert False  # Unreachable.
        out, err = capsys.readouterr()
        # See: error_exit_no_results.
        expect = 'No facts were found for the specified query.'
        assert err.startswith(expect)

    def test_list_facts_basic_store(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        capsys,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        list_facts(controller)
        out, err = capsys.readouterr()
        assert not err
        # We could verify the report looks like how we expect, but that seems
        # better suited for using a snapshots feature. It would be painful to
        # maintain here, especially as the report formats evolve.
        assert out

