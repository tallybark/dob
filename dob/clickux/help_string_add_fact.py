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

"""Module to provide u18n friendly help text strings for our CLI commands."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from .help_strings import common_format

# ***
# *** [CREATE-FACT] Commands help.
# ***

START_HELP = _(
    """
    Starts or adds a fact.

    If you add a fact without providing sufficient information about its end a
    *ongoing fact* will be created to capture you current work. Only one such
    fact can be present at any given time. Please refer to *stop*, *cancel*
    and *current* commands for further information.

    \b
    RAW_FACT:
    'raw_fact'-string containing information about the Fact to be started.
    'raw_fact' may have the following components:
    <timeinfo> <activityname>@<categoryname> #<tag1> #<tag2>, <description>'

      \b
      <timeinfo>
# FIXME/2018-06-09: (lb): Fix this:
      May have one of the following three formats: 'HH:MM', 'HH:MM-HH:MM' or
      ' -MM'.
        * 'HH:MM': Start time in hours and minutes.
        * 'HH:MM-HH:MM' Start and end time given in ours and minutes.
        * ' -MM' Start time given as 'minutes before *now*. Please be advised:
          You need to lead with a whitespace before the '-' sign or put ' -- '
          before the start of your raw_fact. For details refer to
          https://github.com/elbenfreund/hamster_cli/issues/108
      All times specified refer to *today*.

      \b
      <activity>
      Name of the activity. This is the name of the (potentially recurring)
      action you want to track. As an absolute minimum this needs to be
      present.

      \b
      <category>
      You assign activities to categories to group them together. Each
      activity/category combination is allowed only once. If you have to
      activitynames in two distinct categories however, they will be treated
      totaly independent however.

      \b
      <tag1>, <tag2>, etc
      Tags are currently unsupported.

      \b
      <description>
      A detailed description of that particular instance of performing this
      activity. Please note that that is not a description of the category or
      the activity in general but a way to provide additional context to this
      instance.

    \b
    START:
    When does the fact start? When specified this will override any start
    information present in the *raw fact*. This is usefull if you want to add
    a fact with a different date than today.

    \b
    END:
    When does the fact end? When specified this will override any end information
    present in the *raw fact*.
    """
)

