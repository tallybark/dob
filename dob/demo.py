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
        self.create_actegories()
        self.populate_facts()

    # ***

    def create_actegories(self):
        self.create_categories()
        self.create_activities()

    def create_categories(self):
        self.cats = {
            'welcome': Category(name=_('Welcome')),
            'intermediate': Category(name=_('Intermediate Skills')),
        }

    def create_activities(self):
        self.acts = {
            'demo@intermediate': Activity(name=_('Demo'), category=self.cats['intermediate']),
            'demo@welcome': Activity(name=_('Demo'), category=self.cats['welcome']),
        }

    # ***

    def demo_facts(self):
        for demo_fact in self._demo_facts:
            yield demo_fact

    def populate_facts(self):
        self._demo_facts = []
        prev_fact = None
        for name in list(filter(lambda name: name.startswith('demo_fact_'), dir(self))):
            demo_fact = getattr(self, name)(prev_fact)
            self._demo_facts.append(demo_fact)
            prev_fact = demo_fact

    # ***

    def demo_fact_00(self, _prev_fact):
        return self.first_fact()

    def demo_fact_99(self, _prev_fact):
        return self.final_fact()

    def final_fact(self):
        demo_fact = PlaceableFact(
            start=self.controller.now - timedelta(hours=1),
            end=None,
            activity=self.acts['demo@welcome'],
            #tags=['dob-life', 'welcome',],
            tags=['hello, dobber!',],
            description=_('''
Welcome to the dob demo!

Do you want to learn the basics of dob? Then follow along!

* To quit at any time, press the "q" key.

Let‘s get started! You‘re looking at the last, final Fact.

* Press the "g" key twice ("gg") to go to the first Fact.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def first_fact(self):
        since_time = self.controller.now - timedelta(days=14)
        until_time = since_time + timedelta(minutes=90)
        demo_fact = PlaceableFact(
            start=since_time,
            end=until_time,
            activity=self.acts['demo@welcome'],
            tags=['first-fact',],
            description=_('''
Congratulations, you made it to the first Fact in the demo!

The "gg" command takes you to the first Fact in your database.

The "G" command (uppercase), similarly, takes you to the last Fact.

* Press "G" now to try it, then press "gg" to return here.

* To continue, press the "k" key to advance to the next Fact.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_01(self, prev_fact):
        demo_fact = PlaceableFact(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(minutes=66),
            activity=self.acts['demo@welcome'],
            tags=['learning fast',],
            description=_('''
You're learning fast!

To go backward one Fact, press the "j" key.

* Press "j" now to try it, then press "k" to return here.

You can also use the left and right arrow keys to change Facts.

* To continue, press the right arrow key "→" to advance one Fact.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_02(self, prev_fact):
        demo_fact = PlaceableFact(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=12),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #3',],
            description=_('''
Wow! You can sure get around dob now!

You can also navigate dob by jumping Facts one day at a time.

* Press (uppercase) "K" to jump to the Fact 1 day from now.

  Return to this entry with (uppercase) "J".

* Then press (lowercase) "k" (or "→") to keep reading the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_03(self, prev_fact):
        demo_fact = PlaceableFact(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=9),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #5', ],
            # E501 line too long (✗✗✗ > 89 characters)
            description=_('''
You‘ve become a pro at navigating between Facts!

Now let‘s learn about navigating the *description*, which is what you‘re reading.

You can move the cursor using -- surprise! -- the up and down arrow keys!

* Press and hold the down arrow key "↓" until the cursor scrolls down the window.

  You should eventually see more text.




Hi! You made it!!

You can use the up "↑" arrow key, naturally, to move the cursor up.

And you can use a three-button mouse wheel to scroll the description, too.

To scroll by the pageful, use the Page Up and Page Down keys ("PgUp" and "PgDn").

* Press "PgUp" a few times and then "PgDn" back here to try for yourself.

To jump to the very beginning of the description, use "Home".

To jump to the very end, use "End".

* To keep reading the demo, press "End" now.








This is the end of the description!

* To keep learning, jump one day -- press "K" -- because you‘ve read the next Fact.

  Hint: Look at the status bar below this text and you‘ll see
  the "Fact ID #4" change to "Fact ID #6" after pressing "K".
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_04(self, prev_fact):
        demo_fact = PlaceableFact(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=6),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #4',],
            description=_('''
Did you just press "K" to jump forward one day? Congrats!

Bonus Feature: If you press and hold "K", dob will start jumping by weeks.

To continue the demo, jump back one day to the last entry you read.

* Press "J" to jump back one day to continue the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_05(self, prev_fact):
        demo_fact = PlaceableFact(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=18),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #6',],
            description=_('''
            '''.strip()),  # noqa: E501
        )
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

