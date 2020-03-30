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

"""A time tracker for the command line. Utilizing the power of nark."""

from dob_bright.termio.crude_progress import CrudeProgress

from dob_viewer.crud.parse_input import parse_input

from .save_backedup import prompt_and_save_backedup


__all__ = (
    'import_facts',
)


def import_facts(
    controller,
    file_in=None,
    file_out=None,
    rule='',
    backup=True,
    leave_backup=False,
    use_carousel=False,
    dry=False,
    **kwargs,
):
    """
    Import Facts from STDIN or a file.
    """

    # Bah. Progress is only useful if mend_facts_times calls insert_forcefully,
    # otherwise the import operation should be fast (at least for the 1Kish Fact
    # imports this author has ran). And insert_forcefully is only needed if the
    # Fact range being imported overlaps with existing Facts. Which it really
    # shouldn't, i.e., the use case is, I've been on vacation and Hamstering to
    # a file on my phone, and now I want that data imported into Hamster, which
    # will be strictly following the latest Fact saved in the store.
    progress = CrudeProgress(enabled=True)

    def _import_facts():
        new_facts = parse_input(
            controller,
            file_in=file_in,
            progress=progress,
        )
        saved_facts = prompt_and_save_backedup(
            controller,
            edit_facts=new_facts,
            file_out=file_out,
            rule=rule,
            backup=backup,
            leave_backup=leave_backup,
            use_carousel=use_carousel,
            dry=dry,
            yes=False,
            progress=progress,
            **kwargs,
        )
        return saved_facts

    # ***

    return _import_facts()

