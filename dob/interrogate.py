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

import editor
import six

from hamster_lib import Activity

from .prompters.prompt__awesome import AwesomePrompt
from .prompters.sophisti_prompt import SophisticatedPrompt

__all__ = [
    'ask_user_for_edits',
]


# ***


def ask_user_for_edits(
    controller,
    fact,
    always_ask=False,
    prompt_agent=None,
):
    """
    """

    def _ask_user_for_edits():
        prompter = get_prompter()

        act_name, cat_name = ask_act_cat(prompter, fact, always_ask)

        fact.activity = Activity.create_from_composite(act_name, cat_name)
        try:
            fact.activity = controller.activities.get_by_composite(
                fact.activity.name, fact.activity.category, raw=False,
            )
        except KeyError:
            pass

        chosen_tags = ask_for_tags(prompter, fact)
        fact.tags_replace(chosen_tags)

        fact.description = fact_ask_description(fact, always_ask)

        return prompter

    # ***

    def get_prompter():
        if prompt_agent is None:
            return AwesomePrompt(controller)
        else:
            assert isinstance(prompt_agent, SophisticatedPrompt)
            return prompt_agent

    # ***

    def ask_act_cat(prompter, fact, always_ask=False):
        filter_activity, filter_category = prepare_ask_act_cat(fact)
        if (not always_ask) and filter_activity and filter_category:
            return filter_activity, filter_category

        return prompter.ask_act_cat(filter_activity, filter_category)

    def prepare_ask_act_cat(fact):
        filter_activity = ''
        if fact.activity and fact.activity.name:
            filter_activity = fact.activity.name

        filter_category = ''
        if fact.activity and fact.activity.category and fact.activity.category.name:
            filter_category = fact.activity.category.name

        return filter_activity, filter_category

    # ***

    def ask_for_tags(prompter, fact):
        return prompter.ask_for_tags(
            already_selected=fact.tags, activity=fact.activity,
        )

    # ***

    def fact_ask_description(fact, prompter, always_ask=False):
        # Skip if already set.
        if fact.description and not always_ask:
            return fact.description

        return ask_edit_with_editor(fact.description)

    # ***

    def ask_edit_with_editor(content):
        # NOTE: You'll find EDITOR features in multiple libraries.
        #       The UX should be indistinguishable to the user.
        #       E.g., we could use click's `edit` instead of editor's:
        #
        #           click.edit(text=None,
        #                      editor=None,
        #                      env=None,
        #                      require_save=True,
        #                      extension='.txt',
        #                      filename=None)
        #
        content = content if content else ''
        contents = six.b(str(content))
        result = editor.edit(contents=contents)
        # FIXME/2018-05-10: (lb): Is this py2 compatible?
        edited = result.decode()
        return edited

    # ***

    return _ask_user_for_edits()

