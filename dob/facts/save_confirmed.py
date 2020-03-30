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

from gettext import gettext as _

import sys


__all__ = (
    'prompt_and_save_confirmed',
)


# ***

def prompt_and_save_confirmed(
    controller,
    edit_facts=None,
    orig_facts=None,
    use_carousel=False,
    backup_callback=None,
    file_out=None,
    rule='',
    yes=False,
    dry=False,
    progress=None,
    **kwargs,
):
    """"""

    def _prompt_and_save_confirmed():
        saved_facts = []
        if not edit_facts:
            return saved_facts
        must_isatty_unless_testing()
        saved_facts = launch_carousel_or_prompt_directly()
        return saved_facts

    def must_isatty_unless_testing():
        if (
            not use_carousel
            or sys.stdin.isatty()
            or 'input' in kwargs  # PTK3's input test hook.
        ):
            return
        raise Exception(_(
            'Commands requires user confirmation, or --yes or --dry.'
        ))

    def launch_carousel_or_prompt_directly():
        if use_carousel:
            return launch_carousel()
        else:
            return prompt_directly()

    def launch_carousel():
        # Not just lazy loading, but allows test_save_backedup to mock away.
        from dob_viewer.crud.save_confirmer import prompt_and_save_confirmer
        prompt_and_save_confirmer(
            controller,
            edit_facts=edit_facts,
            orig_facts=orig_facts,
            backup_callback=backup_callback,
            dry=dry,
            **kwargs,
        )
        return []

    def prompt_directly():
        # Not just lazy loading, but allows test_save_backedup to mock away.
        from .save_confirmer import prompt_and_save_confirmer
        saved_facts = prompt_and_save_confirmer(
            controller,
            edit_facts=edit_facts,
            orig_facts=orig_facts,
            backup_callback=backup_callback,
            file_out=file_out,
            rule=rule,
            yes=yes,
            dry=dry,
            progress=progress,
            **kwargs,
        )
        return saved_facts

    # ***

    return _prompt_and_save_confirmed()

