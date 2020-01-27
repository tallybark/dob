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

import tempfile

import editor

from nark.items.activity import Activity

# Lazy-load AwesomePrompt to save ~0.1 seconds when not needed.
from dob_prompt import prompters

__all__ = (
    'ask_user_for_edits',
    'ask_edit_with_editor',
)


# ***

def ask_user_for_edits(
    controller,
    fact,
    always_ask=False,
    prompt_agent=None,
    restrict_edit='',
    no_completion=None,
):
    """
    """

    def _ask_user_for_edits():
        verify_always_ask()

        prompter = get_prompter()

        ask_act_cat(prompter, fact)

        ask_for_tags(prompter, fact)

        fact_ask_description(fact)

        return prompter

    # ***

    def verify_always_ask():
        assert always_ask in [
            True, False, 'actegory', 'tags', 'description',
        ]

    # ***

    def get_prompter():
        if prompt_agent is None:
            return prompters.path.AwesomePrompt(controller)
        else:
            assert isinstance(prompt_agent, prompters.path.PrompterCommon)
            return prompt_agent

    # ***

    def ask_act_cat(prompter, fact):
        filter_activity, filter_category = prepare_ask_act_cat(fact)
        if (
            (filter_activity and filter_category and always_ask is False)
            or ('' != restrict_edit and 'actegory' != restrict_edit)
        ):
            return

        no_completion_act = None
        no_completion_cat = None
        if no_completion is not None:
            no_completion_act = no_completion.re_act
            no_completion_cat = no_completion.re_cat

        act_name, cat_name = prompter.ask_act_cat(
            filter_activity,
            filter_category,
            no_completion_act=no_completion_act,
            no_completion_cat=no_completion_cat,
        )
        set_actegory(fact, act_name, cat_name)

    def prepare_ask_act_cat(fact):
        filter_activity = ''
        if fact.activity and fact.activity.name:
            filter_activity = fact.activity.name

        filter_category = ''
        if fact.activity and fact.activity.category and fact.activity.category.name:
            filter_category = fact.activity.category.name

        return filter_activity, filter_category

    def set_actegory(fact, act_name, cat_name):
        fact.activity = Activity.create_from_composite(act_name, cat_name)
        try:
            fact.activity = controller.activities.get_by_composite(
                fact.activity.name, fact.activity.category, raw=False,
            )
        except KeyError:
            pass

    # ***

    def ask_for_tags(prompter, fact):
        if (
            (fact.tags and always_ask is False)
            or ('' != restrict_edit and 'tags' != restrict_edit)
        ):
            return

        no_complete_tag = None
        if no_completion is not None:
            no_complete_tag = no_completion.re_tag

        chosen_tags = prompter.ask_for_tags(
            already_selected=fact.tags,
            activity=fact.activity,
            no_completion=no_complete_tag,
        )
        fact.tags_replace(chosen_tags)

    # ***

    def fact_ask_description(fact):
        if (
            (fact.description and always_ask is False)
            or ('' != restrict_edit and 'description' != restrict_edit)
        ):
            return

        # (lb): Strip whitespace from the description. This is how `git` works.
        # Not that we have to be like git. But it makes parsed results match
        # the input, i.e., it we didn't strip() and then re-parsed the non-
        # stripped description, the parser would strip, and we'd see a difference
        # between the pre-parsed and post-parsed description, albeit only
        # leading and/or trailing whitespace. (If we wanted to preserve whitespace,
        # we'd have to make the parser a little more intelligent, but currently
        # the parser strip()s while it parses, to simplify the parsing algorithm.)
        raw_description = ask_edit_with_editor(controller, fact, fact.description)
        fact.description = raw_description.strip()

    # ***

    return _ask_user_for_edits()


# ***

def ask_edit_with_editor(controller, fact=None, content=''):
    def _ask_edit_with_editor():
        contents = prepare_contents(content)
        filename = temp_filename()
        edited = run_editor(filename, contents)
        return edited

    def prepare_contents(content):
        content = content if content else ''
        # # FIXME: py2 compatible? Or need to six.b()?
        # #contents = six.b(str(content))  # NOPE: Has problems with Unicode, like: ½
        # contents = text_type(content).encode()
        # FIXME/2020-01-26: (lb): Verify no longer an issue.
        contents = str(content).encode()
        return contents

    def temp_filename():
        tmpfile = tempfile.NamedTemporaryFile(
            prefix=prepare_prefix(),
            suffix=prepare_suffix(),
        )
        filename = tmpfile.name
        return filename

    def prepare_prefix():
        # Vim names the terminal with the file's basename, which is
        # normally meaningless, e.g., "tmprvapy77w.rst (/tmp)", but
        # we can give the randomly-named temp file a prefix to make
        # the title more meaningful.
        prefix = None
        if fact is not None:
            # E.g., "17:33 07 Apr 2018 "
            timefmt = '%H:%M %d %b %Y '
            if fact.start:
                prefix = fact.start.strftime(timefmt)
            elif fact.end:
                prefix = fact.end.strftime(timefmt)
        return prefix

    def prepare_suffix():
        # User can set a suffix, which can be useful so, e.g., Vim
        # sees the extension and set filetype appropriately.
        # (lb): I like my Hamster logs to look like reST documents!
        suffix = controller.config['term.editor_suffix'] or None
        return suffix

    def run_editor(filename, contents):
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
        result = editor.edit(filename=filename, contents=contents)
        # FIXME/2018-05-10: (lb): Is this py2 compatible? (2018-06-29: Do I care?)
        edited = result.decode()
        # Necessary?:
        #   edited = result.decode('utf-8')
        return edited

    return _ask_edit_with_editor()

