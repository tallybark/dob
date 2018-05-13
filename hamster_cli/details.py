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

import click

__all__ = ['app_details']

def app_details(controller):
    """List details about the runtime environment."""
    def get_db_info():
        result = None

        def get_sqlalchemy_info():
            engine = controller.config['db_engine']
            if engine == 'sqlite':
                sqlalchemy_string = _(
                    "Using 'sqlite' with database stored under: {}"
                    .format(controller.config['db_path'])
                )
            else:
                port = controller.config.get('db_port', '')
                if port:
                    port = ':{}'.format(port)

                sqlalchemy_string = _(
                    "Using '{engine}' connecting to database {name} on {host}{port}"
                    " as user {username}.".format(
                        engine=engine,
                        host=controller.config['db_host'],
                        port=port,
                        username=controller.config['db_user'],
                        name=controller.config['db_name'],
                    )
                )
            return sqlalchemy_string

        # For now we do not need to check for various store option as we allow
        # only one anyway.
        result = get_sqlalchemy_info()
        return result

    click.echo(_(
        "You are running {name} version {version}".format(
            name=hamster_cli_appname,
            version=hamster_cli_version,
        )
    ))
    click.echo(
        "Configuration found under: {}".format(get_config_path())
    )
    click.echo(
        "Logfile stored under: {}".format(controller.client_config['logfile_path'])
    )
    click.echo(
        "Reports exported to: {}".format(controller.client_config['export_path'])
    )
    click.echo(get_db_info())

