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

import os
import traceback

from gettext import gettext as _

from dob_bright.termio import (
    click_echo,
    dob_in_user_exit,
    dob_in_user_warning,
    highlight_value
)
from dob_bright.config.app_dirs import AppDirs, get_appdirs_subdir_file_path

from .echo_fact import write_fact_block_format
from .save_confirmed import prompt_and_save_confirmed


__all__ = (
    # (lb): aka 'prompt_and_save_paranoid'
    'prompt_and_save_backedup',
)


# ***

def prompt_and_save_backedup(
    controller,
    backup=True,
    leave_backup=False,
    rule='',
    dry=False,
    **kwargs,
):
    """"""

    def _prompt_and_save():
        backup_f = prepare_backup_file(backup)
        delete_backup = False
        inner_error = None
        saved_facts = []
        try:
            backup_callback = write_facts_file(backup_f, rule, dry)
            saved_facts = prompt_and_save_confirmed(
                controller,
                rule=rule,
                backup_callback=backup_callback,
                dry=dry,
                **kwargs,
            )
            delete_backup = True
        except SystemExit:
            # Explicit sys.exit() from our code.
            # The str(err) is just the exit code #.
            raise
        except BaseException as err:
            # NOTE: Using BaseException, not just Exception, so that we
            #       always catch (KeyboardInterrupt, SystemExit), etc.
            # Don't cleanup backup file.
            traceback.print_exc()
            inner_error = str(err)
        finally:
            if not delete_backup:
                traceback.print_exc()
                msg = 'Something horrible happened!'
                if inner_error is not None:
                    msg += _(' err: "{}"').format(inner_error)
                if backup_f:
                    msg += (
                        _("\nBut don't worry. A backup of edits was saved at: {}")
                        .format(backup_f.name)
                    )
                dob_in_user_exit(msg)
            cleanup_files(backup_f, delete_backup)
        return saved_facts

    # ***

    def prepare_backup_file(backup):
        if not backup:
            return None
        backup_path, backup_link = get_import_ephemeral_backup_path()
        backup_f = None
        log_msg = _("Creating backup at {0}").format(backup_path)
        controller.client_logger.info(log_msg)
        try:
            backup_f = open(backup_path, 'w')
        except Exception as err:
            msg = (
                'Failed to create temporary backup file at "{}": {}'
                .format(backup_path, str(err))
            )
            dob_in_user_exit(msg)
        try:
            # NOTE: os.remove removes the file being linked; we want unlink.
            #   We also want lexists, not exists, to get True for broken links.
            os.unlink(backup_link) if os.path.lexists(backup_link) else None
            os.symlink(backup_path, backup_link)
        except Exception as err:
            msg = (
                'Failed to remove temporary backup file link at "{}": {}'
                .format(backup_link, str(err))
            )
            dob_in_user_warning(msg)
        return backup_f

    IMPORT_BACKUP_DIR = 'carousel'

    def get_import_ephemeral_backup_path():
        backup_prefix = 'dob.import'
        backup_tstamp = controller.now.strftime('%Y%m%d%H%M%S')
        backup_basename = backup_prefix + '-' + backup_tstamp
        backup_fullpath = get_appdirs_subdir_file_path(
            file_basename=backup_basename,
            dir_dirname=IMPORT_BACKUP_DIR,
            appdirs_dir=AppDirs.user_cache_dir,
        )
        # 2018-06-29 18:56: This symlink really isn't that helpful...
        #   but we'll see if I start using it. At least for DEVing.
        backup_linkpath = get_appdirs_subdir_file_path(
            file_basename=backup_prefix,
            dir_dirname=IMPORT_BACKUP_DIR,
            appdirs_dir=AppDirs.user_cache_dir,
        )
        return backup_fullpath, backup_linkpath

    # ***

    def cleanup_files(backup_f, delete_backup):
        if not backup_f:
            return
        backup_f.close()
        if not delete_backup:
            return
        if not leave_backup:
            try:
                os.unlink(backup_f.name)
            except FileNotFoundError:
                # [lb]: 2019-01-17: Happening occasionally on dob-import
                # testing, not sure if related dev_breakpoint usage, or
                # not editing any Facts, or what, but not predictably
                # recreating. Not a problem if it fails, but why would it
                # fail, especially given that the code just called close().
                controller.client_logger.warning(
                    'nothing to cleanup?: backup file missing: {}'
                    .format(backup_f.name)
                )
        else:
            click_echo(
                _('Abandoned working backup at: {}')
                .format(highlight_value(backup_f.name))
            )

    # ***

    def write_facts_file(fact_f, rule, dry):
        def wrapper(carousel):
            if dry or not fact_f:
                return
            fact_f.truncate(0)
            # (lb): truncate doesn't move the pointer (you can peek()), and while
            # write seems to still work, it feels best to reset the pointer.
            fact_f.seek(0)
            for idx, fact in enumerate(carousel.prepared_facts):
                # The Carousel should only send us facts that need to be
                # stored, which excludes deleted Facts that were never stored.
                controller.affirm((not fact.deleted) or (fact.pk > 0))
                write_fact_block_format(fact_f, fact, rule, is_first_fact=(idx == 0))
            fact_f.flush()

        return wrapper

    # ***

    return _prompt_and_save()

