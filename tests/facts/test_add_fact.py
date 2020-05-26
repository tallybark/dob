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

import datetime

from freezegun import freeze_time
import pytest

from dob.facts.add_fact import add_fact


class TestAddFact(object):
    """Unit test related to starting a new fact."""

    @freeze_time('2015-12-25 18:00')
    @pytest.mark.parametrize(
        ('raw_fact', 'time_hint', 'expectation'),
        [
            # Use clock-to-clock format, the date inferred from now; with actegory.
            ('13:00 to 16:30: foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 25, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 25, 16, 30, 0),
                'tags': [],
            }),
            # Use datetime-to-datetime format, with actegory.
            ('2015-12-12 13:00 to 2015-12-12 16:30: foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 12, 16, 30, 0),
                'tags': [],
            }),
            # The end date is inferred from start date.
            ('2015-12-12 13:00 - 18:00 foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 12, 18, 00, 0),
                'tags': [],
            }),
            # actegory spanning day (straddles) midnight) and spanning multiple days.
            ('2015-12-12 13:00 - 2015-12-25 18:00 foo@bar', 'verify_both', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': datetime.datetime(2015, 12, 25, 18, 00, 0),
                'tags': [],
            }),
            # Create open/ongoing/un-ended fact.
            ('2015-12-12 13:00 foo@bar', 'verify_start', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                'end': None,
                'tags': [],
            }),
            # Create ongoing fact starting at right now.
            ('foo@bar', 'verify_none', {
                'activity': 'foo',
                'category': 'bar',
                'start': datetime.datetime(2015, 12, 25, 18, 0, 0),
                'end': None,
                'tags': [],
            }),
            # Tags.
            (
                '2015-12-12 13:00 foo@bar: #precious #hashish, i like ike',
                'verify_start',
                {
                    'activity': 'foo',
                    'category': 'bar',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['precious', 'hashish'],
                    'description': 'i like ike',
                },
            ),
            # Multiple Tags are identified by a clean leading delimiter character.
            (
                '2015-12-12 13:00 foo@bar, #just walk away "#not a tag", blah',
                'verify_start',
                {
                    'activity': 'foo',
                    'category': 'bar',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['just walk away "#not a tag"'],
                    'description': 'blah',
                },
            ),
            # Alternative tag delimiter; and quotes are just consumed as part of tag.
            (
                '2015-12-12 13:00 foo@bar, #just walk away @"totes a tag", blah',
                'verify_start',
                {
                    'activity': 'foo',
                    'category': 'bar',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['just walk away', '"totes a tag"'],
                    'description': 'blah',
                },
            ),
            # Test '#' in description, elsewhere, after command, etc.
            (
                '2015-12-12 13:00 baz@bat",'
                ' #tag1, #tag2 tags cannot come #too late, aha!'
                ' Time is also ignored at end: 12:59',
                'verify_start',
                {
                    'activity': 'baz',
                    'category': 'bat"',
                    'start': datetime.datetime(2015, 12, 12, 13, 0, 0),
                    'end': None,
                    'tags': ['tag1'],
                    'description': '#tag2 tags cannot come #too late, aha!'
                                   ' Time is also ignored at end: 12:59',
                },
            ),
        ],
    )
    def test_add_new_fact(
        self,
        controller_with_logging,
        mocker,
        raw_fact,
        time_hint,
        expectation,
    ):
        """
        Test that input validation and assignment of start/end time(s) works as expected.

        To test just this function -- and the parametrize, above -- try:

          workon dob
          cdproject
          py.test --pdb -vv -k test_add_new_fact tests/

        """
        controller = controller_with_logging
        controller.facts.save = mocker.MagicMock()
        add_fact(controller, raw_fact, time_hint=time_hint, use_carousel=False)
        assert controller.facts.save.called
        args, kwargs = controller.facts.save.call_args
        fact = args[0]
        assert fact.start == expectation['start']
        assert fact.end == expectation['end']
        assert fact.activity.name == expectation['activity']
        assert fact.category.name == expectation['category']
        expecting_tags = ''
        tagnames = list(expectation['tags'])
        if tagnames:
            tagnames.sort()
            expecting_tags = ['#{}'.format(name) for name in tagnames]
            expecting_tags = '{}'.format(' '.join(expecting_tags))
        assert fact.tagnames() == expecting_tags
        expect_description = expectation.get('description', None)
        assert fact.description == expect_description


# ***

class TestStop(object):
    """Unit test concerning the stop command."""

    def test_stop_existing_ongoing_fact(
        self,
        ongoing_fact,
        controller_with_logging,
        mocker,
    ):
        """Make sure stopping an ongoing fact works as intended."""
        mockfact = mocker.MagicMock()
        mockfact.activity.name = 'foo'
        mockfact.category.name = 'bar'
        mocktime = mocker.MagicMock(return_value="%Y-%m-%d %H:%M")
        mockfact.start.strftime = mocktime
        mockfact.end.strftime = mocktime
        current_fact = mocker.MagicMock(return_value=mockfact)
        # While nark still has stop_current_fact, dob replaced stop_fact
        # with add_fact, so it can use all the same CLI magic that the
        # other add-fact commands use. So while we're testing stop-fact
        # here, we're really testing add-fact with a verify-end time-hint.
        controller_with_logging.facts.save = current_fact
        # 2019-12-06: stop_fact was deleted, replaced with add_fact + time_hint.
        add_fact(
            controller_with_logging,
            factoid='',
            time_hint='verify_end',
            use_carousel=False,
        )
        assert controller_with_logging.facts.save.called

    def test_stop_no_existing_ongoing_fact(self, controller_with_logging, capsys):
        """Make sure that stop without actually an ongoing fact leads to an error."""
        with pytest.raises(SystemExit):
            # 2019-12-06: stop_fact was deleted, replaced with add_fact + time_hint.
            add_fact(
                controller_with_logging,
                factoid='',
                time_hint='verify_end',
                use_carousel=False,
            )

