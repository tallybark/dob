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

from gettext import gettext as _

import pyparsing as pp

import click
from six import string_types

from hamster_lib.helpers import time as time_helpers

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = ['search_facts']

def search_facts(
    controller,
    start=None,
    end=None,
    activity=None,
    category=None,
    tag=None,
    description=None,
    key=None,
):
    """
    Search facts machting given timerange and search term. Both are optional.

    Matching facts will be printed in a tabular representation.

    Make sure that arguments are converted into apropiate types before passing
    them on to the backend.

    We leave it to the backend to first parse the timeinfo and then complete any
    missing data based on the passed config settings.

    Args:
        search_term: Term that need to be matched by the fact in order to be considered a hit.
        time_range: Only facts within this timerange will be considered.
        tag: ...
    """

    # FIXME/2018-05-05: (lb): This is from the scientificsteve PR that adds tags:
    #   DRY: Refactor this code; there is a lot of copy-paste code.
    def _search_facts(tree, search_list, search_attr, search_sub_attr=None):
        '''
        '''
        def search_value(fact):
            if search_attr == 'description':
                return getattr(fact, search_attr)
            else:
                return getattr(fact, search_attr).name

        if len(tree) == 1:
            if isinstance(tree[0], string_types):
                l_term = tree[0]
                if search_sub_attr:
                    search_list = [
                        fact for fact in search_list if l_term.lower()
                        in getattr(getattr(fact, search_attr), search_sub_attr).lower()
                    ]
                else:
                    search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and l_term.lower() in search_value(fact).lower()
                    ]
            else:
                search_list = _search_facts(tree[0], search_list, search_attr, search_sub_attr)

        if len(tree) == 2:
            # This is the NOT operator.
            op = tree[0]
            r_term = tree[1]
            if isinstance(r_term, string_types):
                if search_sub_attr:
                    r_search_list = [
                        fact for fact in search_list if r_term.lower()
                        in getattr(search_value(fact), search_sub_attr).lower()
                    ]
                else:
                    r_search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and r_term.lower() in search_value(fact).lower()
                    ]
            else:
                r_search_list = _search_facts(r_term, search_list, search_attr, search_sub_attr)
            search_list = [x for x in search_list if x not in r_search_list]

        elif len(tree) == 3:
            l_term = tree[0]
            r_term = tree[2]
            op = tree[1]

            if isinstance(l_term, string_types):
                if search_sub_attr:
                    l_search_list = [
                        fact for fact in search_list if l_term.lower()
                        in getattr(search_value(fact), search_sub_attr).lower()
                    ]
                else:
                    l_search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and l_term.lower() in search_value(fact).lower()
                    ]
            else:
                l_search_list = _search_facts(l_term, search_list, search_attr, search_sub_attr)

            if isinstance(r_term, string_types):
                if search_sub_attr:
                    r_search_list = [
                        fact for fact in search_list if r_term.lower()
                        in getattr(search_value(fact), search_sub_attr).lower()
                    ]
                else:
                    r_search_list = [
                        fact for fact in search_list if getattr(fact, search_attr)
                        is not None and r_term.lower() in search_value(fact).lower()
                    ]
            else:
                r_search_list = _search_facts(r_term, search_list, search_attr, search_sub_attr)

            if op == 'AND':
                search_list = [x for x in l_search_list if x in r_search_list]
            elif op == 'OR':
                search_list = l_search_list
                search_list.extend(r_search_list)

        return search_list

    # FIXME/2018-05-05: (lb): This is from the scientificsteve PR that adds tags:
    #   DRY: Refactor this code; there is a lot of copy-paste code.
    def search_tags(tree, search_list):
        '''
        '''
        if len(tree) == 1:
            if isinstance(tree[0], string_types):
                l_term = tree[0]
                search_list = [
                    fact for fact in search_list if l_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                search_list = search_tags(tree[0], search_list)
        elif len(tree) == 2:
            # This is the NOT operator.
            op = tree[0]
            r_term = tree[1]
            if isinstance(r_term, string_types):
                r_search_list = [
                    fact for fact in search_list if r_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                r_search_list = search_tags(r_term, search_list)

            search_list = [x for x in search_list if x not in r_search_list]
        elif len(tree) == 3:
            l_term = tree[0]
            r_term = tree[2]
            op = tree[1]

            if isinstance(l_term, string_types):
                l_search_list = [
                    fact for fact in search_list if l_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                l_search_list = search_tags(l_term, search_list)

            if isinstance(r_term, string_types):
                r_search_list = [
                    fact for fact in search_list if r_term.lower()
                    in [x.name.lower() for x in fact.tags]
                ]
            else:
                r_search_list = search_tags(r_term, search_list)

            if op == 'AND':
                search_list = [x for x in l_search_list if x in r_search_list]
            elif op == 'OR':
                search_list = l_search_list
                search_list.extend(r_search_list)

        return search_list

    # (lb): Hahaha: end of inline defs. Now we start the _search method!

    # NOTE: (lb): ProjectHamster PR #176 by scientificsteve adds search --options
    #       but remove the two positional parameters.
    #
    #       Here's what the fcn. use to look like; I'll delete this comment
    #       and code once I'm more familiar with the project and am confident
    #       nothing here is broke (because I already found a few things! and
    #       I might want to just revert some parts of the PR so I can move on
    #       with life (but keep parts of the PR I like, like tags support!)).
    #
    if False:  # removed by scientificsteve
        def _search(controller, search_term, time_range):
            # [FIXME]
            # As far as our backend is concerned search_term as well as time range are
            # optional. If the same is true for legacy hamster-cli needs to be checked.
            if not time_range:
                start, end = (None, None)
            else:
                # [FIXME]
                # This is a rather crude fix. Recent versions of ``hamster-lib`` do not
                # provide a dedicated helper to parse *just* time(ranges) but expect a
                # ``raw_fact`` text. In order to work around this we just append
                # whitespaces to our time range argument which will qualify for the
                # desired parsing.
                # Once raw_fact/time parsing has been refactored in hamster-lib, this
                # should no longer be needed.
                time_range = time_range + '  '
                timeinfo = time_helpers.extract_time_info(time_range)[0]
                start, end = time_helpers.complete_timeframe(timeinfo, controller.config)
            # (lb): In lieu of filter_term, which justs searches facts,
            # scientificsteve switched to `hamster-cli search --description foo`.
            results = controller.facts.get_all(filter_term=search_term, start=start, end=end)
            return results
    # end: disabled code...

    if key:
        results = [controller.facts.get(pk=key), ]
    else:
        # Convert the start and time strings to datetimes.
        if start:
            start = time_helpers.parse_time(start)
        if end:
            end = time_helpers.parse_time(end)

        results = controller.facts.get_all(start=start, end=end)

        # (lb): scientificsteve's PR adds these if's, but they seem wrong,
        # i.e., if you specify --activity and --category, then only
        # category matches are returned! But I don't care too much,
        # because I use hamster_briefs for searching and reports!
        # Granted, it's coupled to SQLite3, but that's probably easy
        # to fix, and I don't care; SQLite3 is perfectly fine. I have
        # no idea why SQLAlchemy was a priority for the redesign.
        #
        # Also: It looks like we post-processing database results?
        # Wouldn't it be better to craft the SQL query to do the
        # filtering? Another reason I like hamster_briefs so much better!

        # FIXME/2018-05-05: (lb): The next 4 if-blocks are from the scientificsteve PR
        #   that adds tags: DRY: Refactor this code; there is a lot of copy-paste code.

        if activity:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("NOT", 1, pp.opAssoc.RIGHT, ),
                                                 ("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(activity)

            results = _search_facts(search_tree, results, 'activity', 'name')

        if category:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(category)

            results = _search_facts(search_tree, results, 'category', 'name')

        if tag:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("NOT", 1, pp.opAssoc.RIGHT, ),
                                                 ("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(tag)

            results = search_tags(search_tree, results)

        if description:
            identifier = pp.Word(pp.alphanums + pp.alphas8bit + '_' + '-')

            expr = pp.operatorPrecedence(baseExpr=identifier,
                                         opList=[("AND", 2, pp.opAssoc.LEFT, ),
                                                 ("OR", 2, pp.opAssoc.LEFT, )])
            search_tree = expr.parseString(description)

            results = _search_facts(search_tree, results, 'description')

    return results

