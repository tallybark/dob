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

"""A lite wrapper around the dob-bright Controller."""

from dob_bright.controller import Controller

from dob_viewer.config.styling.apply_styles import pre_apply_style_conf

__all__ = (
    'Controller',
)


class DobController(Controller):
    """
    A custom controller that ensures the style config is ready when needed.
    """

    def __init__(self, *args, **kwargs):
        super(DobController, self).__init__(*args, **kwargs)
        self.applied_style_conf = False

    def setup_logging(self, *args, **kwargs):
        self.pre_apply_style_conf()
        return super(DobController, self).setup_logging(*args, **kwargs)

    def standup_store(self, *args, **kwargs):
        self.pre_apply_style_conf()
        return super(DobController, self).standup_store(*args, **kwargs)

    def pre_apply_style_conf(self):
        if self.applied_style_conf:
            return
        # Trigger the cache mechanism for the style conf.
        pre_apply_style_conf(self)
        self.applied_style_conf = True

