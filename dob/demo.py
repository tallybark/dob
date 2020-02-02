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

"""dob-demo command"""

from gettext import gettext as _

import tempfile
from datetime import timedelta
from functools import update_wrapper

from nark.items.activity import Activity
from nark.items.category import Category

from dob_viewer.crud.fact_dressed import FactDressed

# We could use the wrapper method and tell it to Carousel:
#  from .facts.save_confirmed import prompt_and_save_confirmed
# Or we could just call the Carousel wrapper directly:
from dob_viewer.crud.save_confirmer import prompt_and_save_confirmer

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

        prompt_and_save_confirmer(controller, edit_facts=demo_facts, dry=False)

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
            'demo@intermediate': Activity(
                name=_('Demo'), category=self.cats['intermediate'],
            ),
            'demo@welcome': Activity(
                name=_('Demo'), category=self.cats['welcome'],
            ),
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
        demo_fact = FactDressed(
            start=self.controller.now - timedelta(hours=1),
            end=None,
            activity=self.acts['demo@welcome'],
            # tags=['dob-life', 'welcome', ],
            tags=['hello, dobber!', ],
            description=_('''
Welcome to the dob demo!

Do you want to learn the basics of dob? Then follow along!

* To quit at any time, press the "q" key.

Let’s get started! You’re looking at the last, final Fact.

* Press the "g" key twice ("gg") to go to the first Fact.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def first_fact(self):
        since_time = self.controller.now - timedelta(days=14)
        until_time = since_time + timedelta(minutes=90)
        demo_fact = FactDressed(
            start=since_time,
            end=until_time,
            activity=self.acts['demo@welcome'],
            tags=['first-fact', ],
            description=_('''
Congratulations, you made it to the first Fact in the demo!

The "gg" command takes you to the first Fact in your database.

The "G" command (uppercase), similarly, takes you to the last Fact.

* Press "G" now to try it, then press "gg" to return here.

* To continue, press the "k" key to advance to the next Fact.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    # (lb): My apologies, this could be a maintenance pain, the way
    # I've named the methods, encoding their order therein. It's not
    # going to be easy to move sections around!

    def demo_fact_01(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(minutes=66),
            activity=self.acts['demo@welcome'],
            tags=['learning fast', ],
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
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=12),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #3', ],
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
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=9),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #5', ],
            # E501 line too long (✗✗✗ > 89 characters)
            description=_('''
You’ve become a pro at navigating between Facts!

Let’s learn how to navigate the *description*, which is what you’re reading.

You can move the cursor using "h" and "l", or using the up and down arrow keys.

* Press and hold "l" or the down arrow key "↓" until the cursor scrolls down the window.

  You should eventually see more text.




Hi! You made it!!

To move the cursor up, you can use either "h" or the up "↑" arrow key.

And you can use a three-button mouse wheel to scroll the description, too.

To scroll by the pageful, you can use Page Up and Page Down ("PgUp" and "PgDn").

* Press "PgUp" a few times and then "PgDn" back here to try for yourself.

To jump to the very beginning of the description, use "Home".

To jump to the very end, use "End".

* To keep reading the demo, press "End" now.








This is the end of the description!

* To keep learning, jump one day -- press "K" -- because you’ve read the next Fact.

  Hint: Look at the status bar below this text and you’ll see
  the "Fact ID #4" change to "Fact ID #6" after pressing "K".
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_04(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=6),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #4', ],
            description=_('''
Did you just press "K" to jump forward one day? Congrats!

Bonus Feature: If you press and hold "K" (don't do it now), dob will start jumping by weeks.

To continue the demo, jump back one day, to the last entry you read.

* Press "J" to jump back one day to continue the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_05(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=18),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #6', ],
            description=_('''
Before we can learn how to create and edit Facts, there are a few more basics!

(And remember to scroll down, using the down arrow key "↓", or "PgDn".)

Immediate Help
--------------

You can access the help at any time by pressing the question mark "?" key.

* Press "?" to view the online help now.

  Then, press "?" twice more to return here:

  - The second "?" will show you the second page of the help.

  - The third "?" will exit the help. (You can also press "q" to close the help.)

Gaps
----

* Press "→" or "l" to learn about Gap Facts.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_06(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=18),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #7', ],
            description=_('''
Gap Facts
---------

Each Fact has a *start time* and an *end time*.

* You can see the start and end for this Fact in the headers shown above.

In dob, Facts are ordered chronologically.

* When you press "j", dob shows you the previous Fact in time.

  When you press "k", dob shows you the next Fact in time.

If there is a gap in time between two Facts, dob will add what's called a "Gap Fact".

A Gap Fact is simply a placeholder -- it is not part of your data... yet.

If you want, you can edit and save a Gap Fact, and then it will be stored.

But, if not, you can ignore the Gap Fact, and dob will not save it.

Example Gap
-----------

To see a Gap Fact for real, the next Fact in the demo starts 17 minutes later, after the end of this Fact.

* To continue the demo, move 2 Facts forward:

  - Press "k" (or "→") twice, but pause between presses to examine the Gap Fact.

    - The next Fact is a Gap Fact, and it is not technically part of the demo data.

    - You’ll notice that the Gap Fact has a special background color, sorta pink.

      You will also see that the status message, below this text, says “Gap Fact”.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_07(self, prev_fact):
        since_time = prev_fact.end + timedelta(minutes=17)
        demo_fact = FactDressed(
            start=since_time,
            end=since_time + timedelta(hours=6),
            activity=self.acts['demo@intermediate'],
            tags=['After the Gap Fact #8', ],
            description=_('''
Gap Review
----------

As stated in the last step of the demo, the previous Fact has a sorta pinkish background because it's a *Gap Fact*. It is considered a temporary placeholder unless you edit and save it.

Speaking of editing, let’s talk about that finally!

* Press "k" (or "→") to learn how to edit Fact times.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_08(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #9', ],
            description=_('''
Edit Time
---------

To edit the start time or end time of the current Fact, move the cursor to the corresponding widget.

Tab Focus
---------

To move the cursor between the description, the start time, and the end time, press "Tab".

* Press "Tab" three times now.

  You’ll move the cursor to the start time, to the end time, and then back here.

You can also press "Shift-Tab" to move the cursor in the reverse direction.

Send Focus
----------

Instead of "Tab" or "Shift-Tab":

* You can press "s" to send the cursor to the start time widget.

* You can press "e" to send the cursor to the end time widget.

* From within the start or end time widget, you can press "d" to send the cursor to the description, or content area.

Manual Time
-----------

When the cursor is in the start or end time widget, you can edit the value as expected.

* Use the left and right arrow keys to move the cursor back and forth across the time value.

* Use the "Backspace" key to delete characters, and use the number keys and punctuation to enter a new time.

* Press "Enter" (or "Tab" away) to apply the new time.

Audit Time
----------

Note that changing the start or end time can affect surrounding Facts!

* If you change the start time to an earlier time, dob may edit the Fact before, and might change its end time to match the start time.

  Likewise, for an edited end time, dob may edit the start time of the following Fact.

* To protect the integrity of your data, dob will not let you specify a time that completely shadows any other Facts' time.

  For instance, you can not change the start time of a Fact so that it precedes the start of any other Fact.

  * If you try, dob will correct your mistake and set the edited time to the closest time allowed to not obliterate any Facts.

Quick Time
----------

You can quickly edit time using "Shift", "Ctrl", and "Ctrl-Shift" modifiers with the left and right arrow keys.

* Press "Shift-left" to decrement the start time one minute.

* Press "Shift-right" to increment the start time one minute.

* Press "Ctrl-left" to decrement the end time one minute.

* Press "Ctrl-right" to increment the end time one minute.

* Press "Ctrl-Shift-left" to decrement both the start time and the end time by one minute.

* Press "Ctrl-Shift-right" to increment both the start time and the end time by one minute.

You can also press-and-hold to continuously increment or decrement by one minute intervals -- which grow longer than one minute as you keep holding.

Fact Editing
------------

To read about editing the Description, Activity & Category, and Tags, move forward 1 Fact.

* Press "k" (or "→") to continue the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_09(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #10', ],
            description=_('''
Meta Edits
----------

Besides editing the start and end time, you can edit the
Fact Description, the Activity & Category, and the Tags.

* To edit the Fact description using your preferred editor, press "d".

  You may need to set the EDITOR environment variable before running dob, e.g.,

    $ export EDITOR=/usr/bin/vim
    $ dob demo

  Make and save any changes, then exit the editor to return to dob.

* To edit the Activity & Category, press "a".

  dob will show you an advanced, interactive interface.

  You can type a new ``activity@category``.

  You can also choose from names you’ve used on other Facts, and you can
  sort the drop down lists in various ways to make it easier to choose
  Activity and Category names.

* To edit Tags, press "t".

  dob will show you an advanced tag editor.

  You can enter new tags, or you can choose from existing tags.

  And you can sort the list of recommended tags in different ways,
  including by recently used, or by most used, etc., using the F-keys.

  Read the help at the bottom of the tags display for more.

Save
----

* Press "k" (or "→") to learn how to save edits.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_10(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #11', ],
            description=_('''
Saving
------

dob does not automatically save your edits.

* To save changes you’ve made, press "Ctrl-s".

If you have any unsaved edits, the "q" shortcut to quit will not work.

* You can force-quit instead using "Ctrl-Q" (uppercase), and dob will prompt you to exit without saving.

You can also press "u" repeatedly to undo all of your changes (and then "q" will work again).

Undo/Redo
---------

* Press "k" (or "→") to continue the demo and learn how to undo and redo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_11(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #12', ],
            description=_('''
Undo/Redo
---------

dob supports a typical undo and redo workflow.

* Press "Ctrl-z" (or "u") to undo the last change.

  Press again to keep undoing.

* Press "Ctrl-y" (or "r", or "Ctrl-r") to redo the last undo.

  Press again to keep redoing.

  (Note that the multitude of aliases is because parity with Vim.)

If there are no more undos or redos, dob will display a message in the status bar.

Ctrl-c/-v
---------

The next Fact explains how copy and paste work in dob.

* Press "k" (or "→") to continue the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_12(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #13', ],
            description=_('''
Copy/Paste
----------

* Press "Ctrl-c" to copy a Fact.

  Then navigate to another Fact and press "Ctrl-v" to paste it.

* Press "Ctrl-x" instead to cut a Fact.

  The original Fact (that you copied) will be removed when you paste it (and dob will show you an empty Gap Fact in the display where the original Fact used to be).

* If you want to copy and paste a smaller part of the Fact, it's easy:

  * Press "A" followed by "Ctrl-c" to copy the Activity & Category.

  * Press "T" followed by "Ctrl-c" to copy the current Fact's tags.

  * Press "D" followed by "Ctrl-c" to copy the current Fact's description.

  Then paste like normal, using "Ctrl-v".

Split/Merge
-----------

* Press "k" (or "→") to continue the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_13(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #14', ],
            description=_('''
Split/Merge/Delete
------------------

* Press "Alt-p" to split the current Fact into two Facts.

  Then edit each Fact separately, including adjusting the times accordingly.

* Press "Alt-e" to delete the current Fact.

  dob will remove the Fact and replace it in the display with a Gap Fact.

  When you save, the removed Fact will be marked deleted in the data store.

* Press "Alt-m" followed by "→" to merge the current Fact with the next Fact.

  Press "Alt-m" followed by "←" to merge the current Fact with the prior Fact.

Start using dob
---------------

To get up and running, read the next Fact.

* Press "k" ("→") to learn how to dob yourself.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_14(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #15', ],
            description=_('''
Getting Started
---------------

The easiest way to start dobbin' is from scratch.

Run the init command to create a config and a database:

  $ dob init

And then fire up the Carousel (whatever this interface is called that you're using):

  $ dob edit

If you'd like to upgrade from an existing Hamster database, that's easy, too:

  $ dob init
  $ legacy_db=~/.local/share/hamster-applet/hamster.db
  $ dob store upgrade-legacy ${legacy_db}
  $ dob edit

You can always run this demo, even after setting up your own database.

You're a pro!
-------------

* Press "k" ("→") to conclude the demo.
            '''.strip()),  # noqa: E501
        )
        return demo_fact

    def demo_fact_15(self, prev_fact):
        demo_fact = FactDressed(
            start=prev_fact.end,
            end=prev_fact.end + timedelta(hours=4.75),
            activity=self.acts['demo@intermediate'],
            tags=['choose your own demo #16', 'end of the ride', ],
            description=_('''
You made it to the end of the demo!! -- But there's much more you can do with dob:

  - Import Facts from raw text (collected while, say, on vacation).
  - Generate reports (e.g., show time spent on each Activity).
  - Find and install (and write your own) plugins.
  - Export data to other APIs (e.g., upload time to JIRA at your job).

This demo gives you the gist of dob. We hope you enjoyed it!!

Happy dobbin!
            '''.strip()),  # noqa: E501
        )
        return demo_fact


# ***

def _demo_prep(controller):
    """"""

    def __demo_prep():
        tmpfile = create_temporary_file()
        demoize_config(db_path=tmpfile.name)
        controller.standup_store(fact_cls=FactDressed)
        return tmpfile

    def create_temporary_file():
        tmpfile = tempfile.NamedTemporaryFile(
            prefix='dob-demo-',
            suffix='.sqlite',
        )
        return tmpfile

    def demoize_config(db_path):
        controller.config['db.orm'] = 'sqlalchemy'
        controller.config['db.engine'] = 'sqlite'
        controller.config['db.path'] = db_path
        # For completeness, reset the others.
        controller.config['db.host'] = ''
        controller.config['db.port'] = ''
        controller.config['db.name'] = ''
        controller.config['db.user'] = ''

    return __demo_prep()

