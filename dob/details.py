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

from gettext import gettext as _

from nark.items.fact import Fact

from dob_bright.config.app_dirs import AppDirs
from dob_bright.termio import ascii_art, attr, click_echo, fg, highlight_value

from .clickux.plugin_group import ClickPluginGroup

from . import get_version, __package_name__

__all__ = (
    'echo_app_details',
    'echo_app_environs',
    'echo_data_stats',
    'hamster_time',
)


def echo_app_details(controller, full=False):
    """List details about the runtime environment."""
    def _echo_app_details():
        echo_name_version()
        echo_config_path()
        echo_plugins_basepath()
        echo_logfile_path()
        echo_export_path()
        echo_db_info()
        echo_app_dirs()

    def echo_name_version():
        click_echo(_(
            "You are running {appname} version {version}"
        ).format(
            appname=highlight_value(__package_name__),
            version=highlight_value(get_version()),
        ))

    def echo_config_path():
        click_echo(_(
            "Configuration file at: {}"
        ).format(
            highlight_value(controller.configurable.config_path),
        ))

    def echo_plugins_basepath():
        click_echo(_(
            "Plugins directory at: {}"
        ).format(
            # (lb): Such hack.
            highlight_value(ClickPluginGroup().plugins_basepath),
        ))

    def echo_logfile_path():
        click_echo(_(
            "Logfile stored at: {}"
        ).format(
            highlight_value(controller.config['log.filepath']),
        ))

    def echo_export_path():
        click_echo(_(
            "Reports exported to: {}"
        ).format(highlight_value(
            '{}.{{format}}'.format(controller.config['term.export_path']))
        ))

    def echo_db_info():
        click_echo(get_db_info())

    def get_db_info():
        result = None
        # For now we do not need to check for various store option as we allow
        # only one anyway.
        result = get_sqlalchemy_info()
        return result

    def get_sqlalchemy_info():
        """"""
        def _get_sqlalchemy_info():
            engine = controller.config['db.engine']
            if engine == 'sqlite':
                return sqlalchemy_string_sqlite()
            else:
                return sqlalchemy_string_remote(engine)

        def sqlalchemy_string_sqlite():
            sqlalchemy_string = _(
                "Using {engine} on database: {db_path}"
                .format(
                    engine=highlight_value('sqlite'),
                    db_path=highlight_value(controller.config['db.path']),
                )
            )
            return sqlalchemy_string

        def sqlalchemy_string_remote(engine):
            port = controller.config['db.port']
            if port:
                port = ':{}'.format(port)
            sqlalchemy_string = _(
                "Using {engine} on database {db_name} at:"
                " {username}@{host}{port}".format(
                    engine=highlight_value(engine),
                    db_name=highlight_value(controller.config['db.name']),
                    username=highlight_value(controller.config['db.user']),
                    host=highlight_value(controller.config['db.host']),
                    port=highlight_value(port),
                )
            )
            return sqlalchemy_string

        return _get_sqlalchemy_info()

    def echo_app_dirs():
        if not full:
            return
        appdir_paths = existent_app_dirs(include_errs=True, highlight=True)
        for prop in sorted(appdir_paths.keys()):
            path = appdir_paths[prop]
            click_echo('AppDirs.{}: {}'.format(prop, highlight_value(path)))

    _echo_app_details()


def echo_app_environs(controller):
    """List details about runtime in source'able name=value format."""
    environs = {}

    def _echo_app_environs():
        environs_add_all()
        environs_echo()

    def environs_add_all():
        environs_add_appname_ver()
        environs_add_config_path()
        environs_add_plugins_path()
        environs_add_log_path()
        environs_add_reports_dir()
        environs_add_db_url()
        environs_add_db_path()
        environs_add_user_app_dirs()

    def environs_echo():
        for key in sorted(environs.keys()):
            val = environs[key]
            click_echo('DOB_{}="{}"'.format(key.upper(), val))

    def environs_add_appname_ver():
        environs['appname'] = __package_name__
        environs['version'] = get_version()

    def environs_add_config_path():
        environs['conf'] = controller.configurable.config_path

    def environs_add_plugins_path():
        environs['plugins'] = ClickPluginGroup().plugins_basepath

    def environs_add_log_path():
        # environs['log_filepath'] = controller.config['log.filepath']
        environs['CONFIG_LOG_FILEPATH'] = controller.config['log.filepath']

    def environs_add_reports_dir():
        # environs['term_export_path'] = controller.config['term.export_path']
        environs['CONFIG_TERM_EXPORT_PATH'] = controller.config['term.export_path']

    def environs_add_db_url():
        environs['db_url'] = controller.store.db_url

    def environs_add_db_path():
        if controller.config['db.path']:
            # environs['db_path'] = controller.config['db.path']
            environs['CONFIG_DB_PATH'] = controller.config['db.path']

    def environs_add_user_app_dirs():
        for prop, path in existent_app_dirs().items():
            environs[prop] = path

    return _echo_app_environs()


def existent_app_dirs(include_errs=False, highlight=False):
    """"""
    def _existent_app_dirs():
        was_create = appdirs_disable_create()
        prop_paths = build_prop_paths()
        appdirs_restore_create(was_create)
        return prop_paths

    def appdirs_disable_create():
        # (lb): Our AppDirs defaults to trying to create directories. Tell it not to.
        #   NOTE: I consider this side effect a bug. Paths should be lazy-created only
        #   when a file stored therein is opened for writing.
        was_create = AppDirs.create
        AppDirs.create = False
        return was_create

    def appdirs_restore_create(was_create):
        AppDirs.create = was_create

    def build_prop_paths():
        actual_prop_paths = {}

        # CONFIRM: (lb): On virtualenv install, no site_* dirs.
        #   Will this not be the case for site-wide, non-virtenv installs?
        for prop in [
            'user_data_dir',
            'site_data_dir',
            'user_config_dir',
            'site_config_dir',
            'user_cache_dir',
            'user_log_dir',
        ]:
            path = getattr(AppDirs, prop)
            path = check_exists(path)
            if path is not None:
                actual_prop_paths[prop] = path

        return actual_prop_paths

    def check_exists(path):
        if not os.path.exists(path):
            if include_errs:
                dne = _(' [dne]')
                if highlight:
                    dne = _('{}{}{}').format(fg('red_3b'), dne, attr('reset'))
                path += dne
            else:
                path = None
        return path

    return _existent_app_dirs()


def echo_data_stats(controller):
    def _echo_data_stats():
        echo_counts()
        echo_facts_interesting()

    def echo_counts():
        # MAYBE: Add filtering, like activity, category, search_term, after, until, etc.
        num_activities = controller.activities.get_all(count_results=True)
        num_categories = controller.categories.get_all(count_results=True)
        num_facts = controller.facts.get_all(count_results=True)
        num_tags = controller.tags.get_all(count_results=True)
        # FIXME: Calculate length of Hamstering, i.e., delta first and last facts.
        # FIXME: Other stats?
        click_echo(_("No. of      facts: {}").format(highlight_value(num_facts)))
        click_echo(_("No. of  tag names: {}").format(highlight_value(num_tags)))
        click_echo(_("No. of activities: {}").format(highlight_value(num_activities)))
        click_echo(_("No. of categories: {}").format(highlight_value(num_categories)))

    def echo_facts_interesting():
        first_facts = controller.facts.get_all(
            sort_col='start', sort_order='asc', limit=1,
        )
        final_facts = controller.facts.get_all(
            sort_col='start', sort_order='desc', limit=1,
        )
        assert len(first_facts) <= 1
        assert len(final_facts) <= 1
        if not first_facts:
            assert not final_facts
            return
        first_fact = first_facts.pop()
        final_fact = final_facts.pop()
        time_0 = first_fact.start
        time_n = final_fact.end or controller.now
        spanner = Fact(activity=None, start=time_0, end=time_n)
        elapsed = spanner.format_delta(style='')
        click_echo(_("Hamstering Length: {}").format(highlight_value(elapsed)))

    _echo_data_stats()


def hamster_time(posits=[]):
    if posits:
        arts = ascii_art.fetch_asciis(posits)
    else:
        arts = [ascii_art.randomster()]

    for one_art_please in arts:
        click_echo(one_art_please)

