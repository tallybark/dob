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

"""Tests hard to reach methods using Carousel."""

import pytest

# (lb): This is the only place in dob project that uses prompt_toolkit
# (which is why it's a requirements/test.pip dependency and not setup.py).
# We need it to fake output to Carousel so we can test a callback method
# that's embedded (out of scope) inside another method (so we cannot call
# directly).
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from dob_viewer.ptkui import re_confirm

from dob.facts.import_facts import import_facts

from dob.facts import save_confirmer as proper_confirmer
from dob_viewer.crud import save_confirmer as viewer_confirmer

# FIXME/2020-02-01: Could probably simply this test module and use 1 or 2
# Facts from Fact factory -- then moved IMPORT_PATH et al to new module,
# test_import_facts.
IMPORT_PATH = './tests/fixtures/test-import-fixture.rst'
"""Path to the import file fixture, which is full of Factoids."""


# ***

class TestPromptAndSaveBackedUpViaImportFacts(object):
    """Methods to test write_facts_file via the Carousel."""

    def setup_method(self, method):
        self.was_propers = proper_confirmer.prompt_and_save_confirmer
        self.was_viewers = viewer_confirmer.prompt_and_save_confirmer

    def teardown_method(self, method):
        proper_confirmer.prompt_and_save_confirmer = self.was_propers
        viewer_confirmer.prompt_and_save_confirmer = self.was_viewers

    @pytest.mark.parametrize('tres_bools', [
        (True, False, False, ),
        (False, True, False, ),
        (False, False, True, ),
    ])
    def test_prompt_and_save_backedup(
        self,
        controller_with_logging,
        tres_bools,
        mocker,
    ):
        """Tests save_backedup functionality."""

        (backup, use_carousel, dry, ) = tres_bools

        proper_confirmer.prompt_and_save_confirmer = mocker.MagicMock()
        viewer_confirmer.prompt_and_save_confirmer = mocker.MagicMock()

        input_stream = open(IMPORT_PATH, 'r')

        # (lb): A somewhat roundabout route to test prompt_and_save_backedup.
        # - Also tests parse_input!
        import_facts(
            controller_with_logging,
            file_in=input_stream,
            use_carousel=use_carousel,
            backup=backup,
            dry=dry,
            # Set 'input' to avoid a guard clause in our code,
            #   "Commands requires user confirmation, or --yes or --dry."
            # The 'input' is usually sent to PTK, but we've mocked that out,
            # so this touch-file, in a sense, is more a slight of hand.
            input=True,
        )


# ***

def _feed_cli_with_input(
    controller_with_logging,
    key_sequence,
    dry,
    mocker,
):
    inp = create_pipe_input()
    input_stream = open(IMPORT_PATH, 'r')
    # Because the key_sequence force-quits, Carousel prompts "Ok?".
    re_confirm.confirm = mocker.MagicMock(return_value=True)
    try:
        inp.send_text(key_sequence)
        import_facts(
            controller_with_logging,
            file_in=input_stream,
            use_carousel=True,
            # Use backup so backup method actually called!
            backup=True,
            # Testing dry=True adds 1 whole line of coverage!
            dry=dry,
            # Redirect input and output for the test test.
            input=inp,
            output=DummyOutput(),
        )
    finally:
        inp.close()


class TestCarouselBackupCallbackWriteFactsFile(object):
    """Methods to test write_facts_file via the Carousel."""

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
            [
                # Sneak in a test of FactDressed.has_prev_fact:
                '\x1bOD',   # Left arrow ←.
                '\x11',     # Ctrl-Q.
                '\x11',     # Ctrl-Q.
                '\x11',     # Ctrl-Q.
                # We can skip b'' (or '\r') EOL because of the ^Q³.
            ],
        ],
    )
    @pytest.mark.parametrize('dry', [True, False, ])
    def test_carousel_backup_callback_write_facts_file(
        self,
        controller_with_logging,
        key_sequence,
        dry,
        mocker,
    ):
        """Tests write_facts_file via the Carousel, because."""
        # Because the write_facts_file method is embedded in prompt_and_save_backedup,
        # we cannot call it directly to test it. So unless we pull that
        # function out to module scope, or find another way to reach it
        # (perhaps convert prompt_and_save into a class), we can only get
        # at it via Carousel's gallop() -- which we normally wouldn't bother
        # to call from dob, because it's part of a separate component,
        # dob-viewer. So generally we mock out the carousel, but not here.
        # Here, invoke the carousel so that it'll call our callback that we
        # want to test.
        # MAYBE/2020-01-29: What this last comment said.
        # - Maybe make prompt_and_save into a class, or put write_facts_file
        #   at module level, so we can unit test write_facts_file (what we do
        #   here feels more like an integration test).
        _feed_cli_with_input(
            controller_with_logging,
            ''.join(key_sequence),
            dry,
            mocker,
        )

