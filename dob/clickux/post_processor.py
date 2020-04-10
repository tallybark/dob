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

from functools import update_wrapper

__all__ = (
    'post_processor',
)


# ***

def post_processor(func):
    """
    """

    def wrapper(ctx, controller, *args, **kwargs):
        # Ensure that plugins are loaded. Plugins may have functions
        # decorated with @Controller.post_processor to be called.
        # - ctx.parent is a click_hotoffthehamster.core.Context, and
        #   ctx.parent.command is <ClickAliasableBunchyPluginGroup run>.
        ctx.parent.command.ensure_plugged_in(controller)
        facts = func(ctx, controller, *args, **kwargs)
        controller.post_process(controller, facts, show_plugin_error=None)

    return update_wrapper(wrapper, func)

