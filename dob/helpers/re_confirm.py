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
"""Facts Carousel"""

from __future__ import absolute_import, unicode_literals

from six import text_type

from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession

__all__ = [
    'confirm',
    # Private:
    #  'create_confirm_session',
]

# (lb): This is ripped from PPT's shortcuts/prompt.py


def create_confirm_session(message, suffix=' (y/n) ',  **kwargs):
    """
    Create a `PromptSession` object for the 'confirm' function.
    """
    assert isinstance(message, text_type)
    bindings = KeyBindings()

    @bindings.add('y')
    @bindings.add('Y')
    def yes(event):
        session.default_buffer.text = 'y'
        event.app.exit(result=True)

    @bindings.add('n')
    @bindings.add('N')
    @bindings.add('c-c')
    def no(event):
        session.default_buffer.text = 'n'
        event.app.exit(result=False)

    @bindings.add(Keys.Any)
    def _(event):
        " Disallow inserting other text. "
        pass

    complete_message = merge_formatted_text([message, suffix])
    session = PromptSession(complete_message, key_bindings=bindings, **kwargs)
    return session


def confirm(message='Confirm?', suffix=' (y/n) ',  **kwargs):
    """
    Display a confirmation prompt that returns True/False.
    """
    session = create_confirm_session(message, suffix,  **kwargs)
    return session.prompt()

