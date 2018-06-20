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

from . import __appname__ as dob_appname
from . import __version__ as dob_version
from .cmd_config import get_config_path, AppDirs
from .helpers import ascii_art, click_echo, highlight_value

__all__ = ['app_details', 'hamster_time']


def app_details(controller, full=False):
    """List details about the runtime environment."""
    def get_db_info():
        result = None

        def get_sqlalchemy_info():
            engine = controller.config['db_engine']
            if engine == 'sqlite':
                sqlalchemy_string = _(
                    "Using {engine} on database: {db_path}"
                    .format(
                        engine=highlight_value('sqlite'),
                        db_path=highlight_value(controller.config['db_path']),
                    )
                )
            else:
                port = controller.config.get('db_port', '')
                if port:
                    port = ':{}'.format(port)

                sqlalchemy_string = _(
                    "Using {engine} on database {db_name} at:"
                    " {username}@{host}{port}".format(
                        engine=highlight_value(engine),
                        db_name=highlight_value(controller.config['db_name']),
                        username=highlight_value(controller.config['db_user']),
                        host=highlight_value(controller.config['db_host']),
                        port=highlight_value(port),
                    )
                )
            return sqlalchemy_string

        # For now we do not need to check for various store option as we allow
        # only one anyway.
        result = get_sqlalchemy_info()
        return result

    click_echo(_(
        "You are running {name} version {version}".format(
            name=highlight_value(dob_appname),
            version=highlight_value(dob_version),
        )
    ), color=True)
    click_echo(
        "Configuration file at: {}".format(
            highlight_value(get_config_path()),
        )
    )
    click_echo(
        "Logfile stored at: {}".format(
            highlight_value(controller.client_config['logfile_path']),
        )
    )
    click_echo(
        "Reports exported to: {}".format(
            highlight_value(controller.client_config['export_path']),
        )
    )
    click_echo(get_db_info())

    if full:
        for prop in [
            'user_data_dir',
            'site_data_dir',
            'user_config_dir',
            'site_config_dir',
            'user_cache_dir',
            'user_log_dir',
        ]:
            try:
                path = getattr(AppDirs, prop)
            except Exception as err:
                # (lb): Seems to happen when path does not exist, e.g.,
                #  AppDirs.site_data_dir: /usr/share/mate/dob
                #  AppDirs.site_config_dir: /etc/xdg/xdg-mate
                path = None
            except PermissionError as err:
                path = '<{}>'.format(err)
            if path is not None:
                click_echo('AppDirs.{}: {}'.format(prop, highlight_value(path)))


def hamster_time(posits=[]):
    if posits:
        arts = ascii_art.fetch_asciis(posits)
    else:
        arts = [ascii_art.randomster()]

    for one_art_please in arts:
        click_echo(one_art_please)

