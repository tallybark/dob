# This file exists within 'nark':
#
#   https://github.com/hotoffthehamster/nark
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
#
# 'nark' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'nark' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

import sys

import ansi_escape_room

__all__ = (
    'disable_colors',
    'enable_colors',
    'coloring',
    'set_coloring',
    'fg',
    'bg',
    'attr',
    'colorize',
    # Private:
    #  'map_color'
)


# (lb): Retrieve pointer to module object instance, so functions can set.
# - If we did not do this, function scoping would create local variables.
# - I'll admit this feels a little weird, but we need to gait access to the
#   ansi_escape_room package. Using a fake "this", like we do here, is one
#   way to gait access. Another would be to use a module-level dictionary
#   variable that module functions could set. Or we could make a Singleton
#   class. A fourth option would be to move features in this wrapper inside
#   the ansi-escape-room package. (I created this file before creating
#   ansi-escape-room (a fork of another user's package, named "colored"),
#   and it works fine, and it's pretty simple, so keeping it... for now.)
this = sys.modules[__name__]

# (lb): We had been enabling colors until disabled, but it seems more
# normal to assume no colors until at least the user's config is read
# and the command line arguments are parsed! The one drawback is that
# now some module- and class-scope strings can no longer be formatted
# when sourced, but must be generated at runtime, after the config is
# loaded.
this.ENABLE_COLORS = False


def disable_colors():
    this.ENABLE_COLORS = False


def enable_colors():
    this.ENABLE_COLORS = True


def coloring():
    return this.ENABLE_COLORS


def set_coloring(new_coloring):
    was_coloring = this.ENABLE_COLORS
    this.ENABLE_COLORS = new_coloring
    return was_coloring


def fg(color):
    if not coloring():
        return ''
    return ansi_escape_room.fg(map_color(color))


def bg(color):
    if not coloring():
        return ''
    return ansi_escape_room.bg(map_color(color))


def attr(color):
    if not coloring():
        return ''
    return ansi_escape_room.attr(map_color(color))


def colorize(text, color, *args):
    if not coloring():
        return text
    more_attrs = ''.join([ansi_escape_room.attr(attr) for attr in args])
    return '{}{}{}{}'.format(
        ansi_escape_room.fg(color),
        more_attrs,
        text,
        ansi_escape_room.attr('reset'),
    )


def map_color(color):
    # FIXME/2018-06-08: (lb): Need a way to easily change palette.
    # Should at least have two profiles, one for black on white; and t'other.
    # Search all uses of fg and bg, and maybe even map attr?
    return color

