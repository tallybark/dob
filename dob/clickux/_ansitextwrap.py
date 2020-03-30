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

"""TextWrapper ansiwrap wrapper class."""

from ansiwrap import fill

from click_hotoffthehamster._textwrap import TextWrapper


class AnsiTextWrapper(TextWrapper):
    def fill(self, text):
        filled = fill(
            text,
            initial_indent=self.initial_indent,
            subsequent_indent=self.subsequent_indent,
        )
        # The ansiwrap library returns empty when given empty.
        # The Python textwrap built return initial_indent when
        # given an empty string. And Click uses the initial_indent
        # to print the first part of the usage message, so that
        # subcommand options are right-aligned and align in their
        # own column... but this can make some command help funky.
        if filled:
            return filled
        return self.initial_indent

