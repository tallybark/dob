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
"""dob-demo command"""

from __future__ import absolute_import, unicode_literals

import os
import tempfile
from datetime import timedelta
from functools import update_wrapper

from nark.items.activity import Activity

from .cmd_config import AppDirs
from .create import prompt_and_save
from .traverser.placeable_fact import PlaceableFact

__all__ = (
    'demo_config',
    'demo_dob',
    # Private:
    # '_demo_prep'
)


def demo_config(func):
    """
    """
    def wrapper(controller, *args, **kwargs):
        tmpfile = _demo_prep(controller)
        func(controller, *args, **kwargs)
        # The temp. file is removed on exit regardless, but just to be clear:
        tmpfile.close()

    return update_wrapper(wrapper, func)


# ***

def demo_dob(controller):
    def _demo_dob():
        genator = DemoFactGenerator(controller)
        _saved_facts = prompt_and_save(
            controller,
            edit_facts=[genator.first_fact(), ],
            use_carousel=True,
            yes=False,
            dry=False,
        )

    return _demo_dob()


class DemoFactGenerator(object):
    """"""
    def __init__(self, controller):
        self.controller = controller
        self.last_fact_pk = -1

    def first_fact(self):
        activity = Activity(name='')
        since_time = self.controller.now - timedelta(hours=1)
        demo_fact = PlaceableFact(
            pk=self.last_fact_pk,
            activity=activity,
            start=since_time,
            end=None,
        )
        self.last_fact_pk -= 1
        return demo_fact


# ***

def _demo_prep(controller):
    """"""

    def __demo_prep():
        tmpfile = create_temporary_file()
        demoize_config(db_path=tmpfile.name)
        controller.standup_store()
        return tmpfile

    def create_temporary_file():
        tmpfile = tempfile.NamedTemporaryFile(
            prefix='dob-demo-',
            suffix='.sqlite',
        )
        return tmpfile

    def demoize_config(db_path):
        controller.config['store'] = 'sqlalchemy'
        controller.config['db_engine'] = 'sqlite'
        controller.config['db_path'] = db_path
        # For completeness, reset the others.
        controller.config['db_host'] = ''
        controller.config['db_port'] = ''
        controller.config['db_name'] = ''
        controller.config['db_user'] = ''

    return __demo_prep()

