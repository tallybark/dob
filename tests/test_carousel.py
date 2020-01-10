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

import os
import pty
import sys
from unittest.mock import Mock

from dob.transcode import import_facts

import prompt_toolkit
import pytest
# Load PosixStdinReader, though we don't use it, otherwise:
#   AttributeError: module 'prompt_toolkit.input' has no attribute 'posix_utils'
# F401 'prompt_toolkit.input.posix_utils.PosixStdinReader' imported but unused
from prompt_toolkit.input.posix_utils import PosixStdinReader  # noqa: F401

IMPORT_PATH = './tests/fixtures/test-import-fixture.rst'
"""Path to the import file fixture, which is full of Factoids."""


@pytest.fixture
def spoof_terminal(monkeypatch):
    """
    spoof_terminal redirects stdin to fool PPT.

    PPT needs to think it's talking to a terminal, so that we can write
    faux-interactive tests (that are almost integration tests, except we
    skip CliRunner, so they're not *quite* full integration, but still
    pretty close to it).

    Here we mock the read function, which PPT uses to poll stdin, with a
    sequence of keystrokes to send. (We do this tricky dance because we
    cannot otherwise monkeypatch stdin, e.g., this will not work::

        monkeypatch.setattr('sys.stdin', io.StringIO('\x11\x11\x11'))
    """

    # MAYBE/2019-02-20 11:55: Should async_enable be settable,
    #                         so we don't have to hack-mock?
    monkeypatch.setattr('dob_viewer.traverser.carousel.Carousel.async_enable', False)

    sys_stdin = sys.stdin
    # os.pipe() might also work, but pty was built to be a terminal spoof.
    primary_fd, _secondary_fd = pty.openpty()
    primary = os.fdopen(primary_fd, 'w')
    sys.stdin = primary
    yield
    sys.stdin = sys_stdin


__copy_paste_testing__ = '''
    py.test --pdb -vv -k TestBasicCarousel tests/
'''


class TestBasicCarousel(object):
    """Interactive Carousel tests."""

    def _test_basic_import(self, controller_with_logging, spoof_terminal, key_sequence):
        # In concert with spoof_terminal, fake a sequence of keystrokes on stdin.
        interaction = Mock()
        interaction.side_effect = key_sequence
        prompt_toolkit.input.posix_utils.PosixStdinReader.read = interaction

        # [lb]: Not sure what's up (I didn't trace code) but if you
        # try the CliRunner from here, e.g.,
        #       result = runner(['import', IMPORT_PATH])
        # you'll trigger PPT's "Stdin is not a terminal." error
        # (which is what spoof_terminal is trying to work around).
        # So I guess this isn't *quite* an integration test,
        # but it's pretty close -- c'mon! We're still testing the
        # UX with keystrokes! We're just not entering through Click.

        input_stream = open(IMPORT_PATH, 'r')
        import_facts(
            controller_with_logging,
            file_in=input_stream,
            file_out=None,
            use_carousel=True,
        )

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
            # Test left-arrowing and first (early Life) gap fact.
            # Left arrow three times.
            # - First time creates and jumps to gap fact.
            # - Second time causes at-first-fact message.
            # - Third time's a charm.
            [
                '\x1bOD',   # Left arrow ←.
                '\x1bOD',   # Left arrow ←.
                '\x1bOD',   # Left arrow ←.
                '\x11',     # Ctrl-Q.
                '\x11',     # Ctrl-Q.
                '\x11',     # Ctrl-Q.
                '',         # End of stream.
            ],
        ],
    )
    def test_basic_import4_left_arrow_three_time(
        self, controller_with_logging, spoof_terminal, key_sequence
    ):
        self._test_basic_import(controller_with_logging, spoof_terminal, key_sequence)

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
            [
                # Arrow right, arrow left.
                '\x1bOD',
                '\x1bOC',
                # Three Cancels don't make a Right.
                '\x11',
                '\x11',
                '\x11',
                # FIXME/2019-02-20: Because, what, arrowing left goes to
                #                   Previous Big Bang Gap Fact,
                #                   so extra Ctrl-Q needed?
                #                   Oddly, in log, I still only see 2 cancel_command's!
                #                   But apparently we need 4 strokes to exit.
                '\x11',
                '',
            ],
        ],
    )
    def test_basic_import4_right_arrow_left_arrow(
        self, controller_with_logging, spoof_terminal, key_sequence
    ):
        self._test_basic_import(controller_with_logging, spoof_terminal, key_sequence)

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
            [
                # Jump to final fact.
                'G',
                '\x11',
                '\x11',
                '\x11',
                '',
            ],
        ],
    )
    def test_basic_import4_G_go_last(
        self, controller_with_logging, spoof_terminal, key_sequence
    ):
        self._test_basic_import(controller_with_logging, spoof_terminal, key_sequence)

