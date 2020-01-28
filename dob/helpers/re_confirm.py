# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

"""Facts Carousel"""

from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession

__all__ = (
    'confirm',
    # Private:
    #  'create_confirm_session',
)

# (lb): This is ripped from PPT's shortcuts/prompt.py


def create_confirm_session(message, suffix=' (y/n) ', **kwargs):
    """
    Create a `PromptSession` object for the 'confirm' function.
    """
    assert isinstance(message, str)
    bindings = KeyBindings()

    count = {'cc': 0, }

    @bindings.add('y')
    @bindings.add('Y')
    def yes(event):
        count['cc'] = 0
        session.default_buffer.text = 'y'
        event.app.exit(result=True)

    @bindings.add('n')
    @bindings.add('N')
    # (lb): PPT's confirm behavior is to assume Ctrl-c means No,
    #   in which case you end up with the following flow in dob:
    #       Ctrl-c => Break out of Application and Bring up confirmation;
    #       Ctrl-c => Confirmation returns No, so re-run Application.
    #   2018-06-17: I'm not sold on any particular work-flow, but I think
    #   I'd like Ctrl-c -- if you mash it enough -- to finally break out.
    #   Or, at least. I think Ctrl-c followed by Ctrl-c should not act as
    #   a toggle; the second (and subsequent) Ctrl-c's should be ignored,
    #   if nothing else.
    # @bindings.add('c-c')
    def no(event):
        count['cc'] = 0
        session.default_buffer.text = 'n'
        event.app.exit(result=False)

    # (lb): 2018-06-17: Here's the workflow I'd think.
    #   First Ctrl-c: Break out of Application, and bring up quit-okay? prompt.
    #   Second Ctrl-c: Ignored (increment count from 0 to 1).
    #   Third Ctrl-c: Bingo! Really exit.
    # MAYBE: Keep temp file of edits and tell user where/how they can recover.
    @bindings.add('c-q')
    def mash(event):
        count['cc'] += 1
        if count['cc'] > 1:
            event.app.exit(result=True)

    @bindings.add(Keys.Any)
    def _(event):
        """Disallow inserting other text."""
        pass

    complete_message = merge_formatted_text([message, suffix])
    session = PromptSession(complete_message, key_bindings=bindings, **kwargs)
    return session


def confirm(message='Confirm?', suffix=' (y/n) ', **kwargs):
    """
    Display a confirmation prompt that returns True/False.
    """
    session = create_confirm_session(message, suffix, **kwargs)
    return session.prompt()

