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

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import sys

from nark.helpers.colored import fg, attr, colorize

from . import migrate
from .helpers import ascii_art

__all__ = [
    'backend_integrity',
    'barf_and_exit',
    'echo_block_header',
    'fact_block_header',
    'hydrate_activity',
    'hydrate_category',
]


def backend_integrity(func):
    """
    Verify that data in the database is integrit.

    (lb): I wonder if the backend should enforce this better.
    In any case, telling the user at the CLI level is better
    than not telling the user at all, I suppose.
    """

    def wrapper(controller, *args, **kwargs):
        version_must_be_latest(controller)
        time_must_be_gapless(controller)
        func(controller, *args, **kwargs)

    # ***

    def version_must_be_latest(controller):
        db_version = migrate.version(
            controller, silent_check=True, must=True,
        )
        latest_version = migrate.latest_version(
            controller, silent_check=True, must=True,
        )
        if db_version != latest_version:
            assert db_version < latest_version
            msg = _(
                'Expected database to be same version as latest migration.'
                ' {} != {}'
                '\nTrying running `hamster migrate up`'
            ).format(db_version, latest_version)
            barf_and_exit(msg)

    # ***

    def time_must_be_gapless(controller):
        endless_facts = controller.facts.endless()
        barf_on_endless_facts(endless_facts)

    def barf_on_endless_facts(endless_facts):
        if not endless_facts:
            return

        for fact in endless_facts:
            # FIXME/2018-05-18: (lb): Make this prettier.
            echo_block_header(_('Endless Fact Found!'))
            click.echo()
            click.echo(fact.friendly_diff(fact))
            click.echo()
        msg = _(
            'Found saved fact(s) without start_time and/or end_time.'
            '\nSee list of offending Facts above.'
            # MAYBE/2018-05-23 17:05: (lb): We could offer an easy way out, e.g.,
            #   '\n\nTry, e.g.,\n\n  hamster edit {} --end now'
        )
        barf_and_exit(msg)

    # ***

    return wrapper


# ***


def barf_and_exit(msg, crude=True):
    if crude:
        click.echo()
        click.echo(ascii_art.lifeless().rstrip())
        click.echo(ascii_art.infection_notice().rstrip())
        click.pause(info='')
    click.echo()
    click.echo(colorize(msg, 'red'))
    sys.exit(1)


def barf_on_error(msg, crude=False):
    if not msg:
        return
    barf_and_exit(msg, crude=False)


# ***


def echo_block_header(title):
    click.echo(fact_block_header(title))


def fact_block_header(title, sep='━'):
    header = []
    highlight_col = 'red_1'
    header.append('{}{}{}'.format(
        fg(highlight_col),
        title,
        attr('reset'),
    ))
    header.append('{}{}{}'.format(
        fg(highlight_col),
        sep * len(title),
        attr('reset'),
    ))
    return '\n'.join(header)


# ***


def hydrate_activity(controller, activity_name):
    """Fetch a activity from the backend."""
    activity = False
    if activity_name:
        # FIXME: (lb): This raises KeyError if no exact match found.
        #        We should at least gracefully exit,
        #        if not do a fuzzy search.
        result = controller.activities.get_by_name(activity_name)
        activity = result if result else False
    return activity

# ***


def hydrate_category(controller, category_name):
    """Fetch a category from the backend."""
    category = False
    if category_name:
        # FIXME: (lb): This raises KeyError if no exact match found.
        #        We should at least gracefully exit,
        #        if not do a fuzzy search.
        result = controller.categories.get_by_name(category_name)
        category = result if result else False
    return category

