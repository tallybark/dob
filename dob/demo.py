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

from gettext import gettext as _

from nark.items.activity import Activity
from nark.items.category import Category
from nark.items.tag import Tag

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
        demo_facts = []
        # Save the facts to the temp. db., otherwise Carousel
        # won't quit on simple 'q', but will prompt user to save.
        for demo_fact in genator.demo_facts():
            saved_fact = controller.facts.save(demo_fact)
            demo_facts.append(saved_fact)

        _saved_facts = prompt_and_save(
            controller,
            edit_facts=demo_facts,
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
        self.create_actegories()

    # ***

    def create_actegories(self):
        self.create_categories()
        self.create_activities()

    def create_categories(self):
        self.cats = {
            'welcome': Category(name=_('Welcome')),
        }

    def create_activities(self):
        self.acts = {
            'demo@welcome': Activity(name=_('Demo'), category=self.cats['welcome']),
        }

    # ***

    def demo_facts(self):
        for name in list(filter(lambda name: name.startswith('demo_fact_'), dir(self))):
            yield getattr(self, name)()

    # ***

    def final_fact(self):
        demo_fact = PlaceableFact(
            activity=self.acts['demo@welcome'],
            start=self.controller.now - timedelta(hours=1),
            end=None,
            description=_(
                'Welcome to the dob demo!\n\n'
                'Want to learn the basics of dob? Then follow along!\n\n'
                '* To quit at any time, press the "q" key.\n\n'
                "Let's get started! You're looking at the last, final Fact.\n\n"
                '* Press the "g" key twice ("gg") to go to the first Fact.'
            ),
            #tags=['dob-life', 'welcome',],
            tags=['hello, dobber!',],
        )
        return demo_fact

    def first_fact(self):
        since_time = self.controller.now - timedelta(days=14)
        until_time = since_time + timedelta(minutes=90)
        demo_fact = PlaceableFact(
            activity=self.acts['demo@welcome'],
            start=since_time,
            end=until_time,
            description=_(
                'Congratulations, you made it to the first Fact in the demo!\n\n'
                'The "gg" command takes you to the first Fact in your database.\n\n'
                'The "G" command, similarly, takes you to the last Fact.\n\n'
                '* Press "G" now to try it, then press "gg" to return here.\n\n'
                '* To continue, press the "k" key to advance to the next Fact.'
            ),
            tags=['first-fact',],
        )
        return demo_fact

    def demo_fact_00(self):
        return self.first_fact()

    def demo_fact_99(self):
        return self.final_fact()


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

