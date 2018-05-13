# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import datetime
from gettext import gettext as _

import click

from hamster_lib.helpers import time as time_helpers

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True


__all__ = ['cancel_fact', 'start_fact', 'stop_fact']


def start_fact(controller, raw_fact, start='', end=''):
    """
    Start or add a fact.

    Args:
        raw_fact: ``raw_fact`` containing information about the Fact to be started. As an absolute
            minimum this must be a string representing the 'activityname'.
        start (optional): When does the fact start?
        end (optional): When does the fact end?

    Returns:
        None: If everything went alright.

    Note:
        * Whilst it is possible to pass timeinformation as part of the ``raw_fact`` as
            well as dedicated ``start`` and ``end`` arguments only the latter will be represented
            in the resulting fact in such a case.
    """
    fact = Fact.create_from_raw_fact(raw_fact)

    # Explicit trumps implicit!
    if start:
        fact.start = time_helpers.parse_time(start)
    if end:
        fact.end = time_helpers.parse_time(end)

    if not fact.end:
        # We seem to want to start a new tmp fact
        # Neither the raw fact string nor an additional optional end time have
        # been passed.
        # Until we decide wether to split this into start/add command we use the
        # presence of any 'end' information as indication of the users intend.
        tmp_fact = True
    else:
        tmp_fact = False

    # We complete the facts times in both cases as even an new 'ongoing' fact
    # may be in need of some time-completion for its start information.

    # Complete missing fields with default values.
    # legacy hamster_cli seems to have a different fallback behaviour than
    # our regular backend, in particular the way 'day_start' is handled.
    # For maximum consistency we use the backends unified ``complete_timeframe``
    # helper instead. If behaviour similar to the legacy hamster-cli is desired,
    # all that seems needed is to change ``day_start`` to '00:00'.

    # The following is needed becauses start and end may be ``None``.
    if not fact.start:
        # No time information has been passed at all.
        fact.start = datetime.datetime.now()

    else:
        # We got some time information, which may be incomplete however.
        if not fact.end:
            end_date = None
            end_time = None
        else:
            end_date = fact.end.date()
            end_time = fact.end.time()

        timeframe = time_helpers.TimeFrame(
            fact.start.date(), fact.start.time(), end_date, end_time, None)
        fact.start, fact.end = time_helpers.complete_timeframe(timeframe, controller.config)

    if tmp_fact:
        # Quick fix for tmp facts. that way we can use the default helper
        # function which will autocomplete the end info as well.
        # Because of our use of ``complete timeframe our 'ongoing fact' may have
        # received an ``end`` value now. In that case we reset it to ``None``.
        fact.end = None

    controller.client_logger.debug(_(
        "New fact instance created: {fact}".format(fact=fact)
    ))
    fact = controller.facts.save(fact)


def stop_fact(controller):
    """
    Stop cucrrent 'ongoing fact' and save it to the backend.

    Returns:
        None: If successful.

    Raises:
        ValueError: If no *ongoing fact* can be found.
    """
    try:
        fact = controller.facts.stop_tmp_fact()
    except ValueError:
        message = _(
            "Unable to continue temporary fact. Are you sure there is one?"
            "Try running *current*."
        )
        raise click.ClickException(message)
    else:
        #message = '{fact} ({duration} minutes)'.format(
        #            fact=str(fact), duration=fact.get_string_delta())
        start = fact.start.strftime("%Y-%m-%d %H:%M")
        end = fact.end.strftime("%Y-%m-%d %H:%M")
        fact_string = u'{0:s} to {1:s} {2:s}@{3:s}'.format(
            start, end, fact.activity.name, fact.category.name
        )
        message = "Stopped {fact} ({duration} minutes).".format(
            fact=fact_string, duration=fact.get_string_delta()
        )
        controller.client_logger.info(_(message))
        click.echo(_(message))


def cancel_fact(controller):
    """
    Cancel tracking current temporary fact, discaring the result.

    Returns:
        None: If success.

    Raises:
        KeyErŕor: No *ongoing fact* can be found.
    """
    try:
        controller.facts.cancel_tmp_fact()
    except KeyError:
        message = _("Nothing tracked right now. Not doing anything.")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    else:
        message = _("Tracking canceled.")
        click.echo(message)
        controller.client_logger.debug(message)

