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

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from dob.transcode import import_facts

from dob.helpers import re_confirm


IMPORT_PATH = './tests/fixtures/test-import-fixture.rst'
"""Path to the import file fixture, which is full of Factoids."""


def _feed_cli_with_input(
    controller_with_logging, key_sequence, mocker, monkeypatch,
):
    inp = create_pipe_input()
    input_stream = open(IMPORT_PATH, 'r')
    re_confirm.confirm = mocker.MagicMock(return_value=True)
    try:
        inp.send_text(key_sequence)
        import_facts(
            controller_with_logging,
            file_in=input_stream,
            file_out=None,
            use_carousel=True,
            force_use_carousel=True,
            # Setting input and output is for us tests!
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
    def test_carousel_backup_callback_write_facts_file(
        self, controller_with_logging, key_sequence, mocker, monkeypatch,
    ):
        """Tests write_facts_file via the Carousel, because."""
        # Because the write_facts_file method is embedded in prompt_and_save,
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
            controller_with_logging, ''.join(key_sequence), mocker, monkeypatch,
        )

