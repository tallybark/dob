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

from gettext import gettext as _

from functools import update_wrapper

from dob_viewer.crud.fact_dressed import FactDressed

from dob_bright.termio import click_echo, dob_in_user_exit, echo_block_header

from .. import __arg0name__, migrate

__all__ = (
    'induct_newbies',
    'insist_germinated',
    # Private:
    #  'backend_integrity',
)


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
                '\nTrying running `{} migrate up`'
            ).format(db_version, latest_version, __arg0name__)
            dob_in_user_exit(msg)

    # ***

    def time_must_be_gapless(controller):
        endless_facts = controller.facts.endless()
        barf_on_endless_facts(endless_facts)

    def barf_on_endless_facts(endless_facts):
        # There can be only 1. Or none.
        if not endless_facts or len(endless_facts) == 1:
            return

        for fact in endless_facts:
            # FIXME/2018-05-18: (lb): Make this prettier.
            echo_block_header(_('Endless Fact Found!'))
            click_echo()
            click_echo(fact.friendly_diff(fact))
            click_echo()
        msg = _(
            'Found saved fact(s) without start time and/or end time.'
            '\nSee list of offending Facts above.'
            # MAYBE/2018-05-23 17:05: (lb): We could offer an easy way out, e.g.,
            #   '\n\nTry, e.g.,\n\n  {} edit {} --end now'.format(__arg0name__, ...)
        )
        dob_in_user_exit(msg)

    # ***

    return wrapper


def insist_germinated(func):
    """
    """

    def wrapper(controller, *args, **kwargs):
        controller.insist_germinated(fact_cls=FactDressed)
        func(controller, *args, **kwargs)

    return wrapper


def induct_newbies(func):
    """
    """
    @insist_germinated
    @backend_integrity
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return update_wrapper(wrapper, func)

