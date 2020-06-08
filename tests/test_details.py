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

from dob import __package_name__, get_version

from dob.details import echo_app_details


class TestDetails(object):
    """Unittests for the ``details`` command."""

    def test_details_general_data_is_shown(self, controller, capsys):
        """Make sure user recieves the desired output."""
        controller.setup_tty_color(use_color=False)
        echo_app_details(controller)
        out, err = capsys.readouterr()
        startswiths = (
            'You are running {} version {}'.format(
                __package_name__, get_version(),
            ),
            'Configuration file at: ',
            'Plugins directory at: ',
            'Logfile stored at: ',
            'Using sqlite on database: :memory:',
        )
        for idx, line in enumerate(out.splitlines()):
            assert line.startswith(startswiths[idx])

    def test_details_sqlite(self, controller, appdirs, mocker, capsys):
        """Make sure database details for sqlite are shown properly."""
        mocker.patch.object(controller, '_get_store')
        engine, path = 'sqlite', appdirs.user_data_dir
        controller.config['db.engine'] = engine
        controller.config['db.path'] = path
        echo_app_details(controller)
        out, err = capsys.readouterr()
        for item in (engine, path):
            assert item in out
        assert out.splitlines()[-1] == 'Using {} on database: {}'.format(engine, path)

    def test_details_non_sqlite(
        self,
        controller,
        capsys,
        db_port,
        db_host,
        db_name,
        db_user,
        db_password,
        mocker,
    ):
        """
        Make sure database details for non-sqlite are shown properly.

        We need to mock the backend Controller because it would try to setup a
        database connection right away otherwise.
        """
        mocker.patch.object(controller, '_get_store')
        controller.config['db.engine'] = 'postgres'
        controller.config['db.name'] = db_name
        controller.config['db.host'] = db_host
        controller.config['db.user'] = db_user
        controller.config['db.password'] = db_password
        controller.config['db.port'] = db_port
        echo_app_details(controller)
        out, err = capsys.readouterr()
        for item in ('postgres', db_host, db_name, db_user):
            assert item in out
        if db_port:
            assert db_port in out
        assert db_password not in out

