# This file exists within 'dob-bright':
#
#   https://github.com/hotoffthehamster/dob-bright
#
# Copyright © 2018-2020 Landon Bouma, © 2015-2016 Eric Goller. All rights reserved.
#
# This program is free software:  you can redistribute it  and/or  modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any later version  (GPLv3+).
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY;  without even the implied warranty of MERCHANTABILITY or  FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU  General  Public  License  for  more  details.
#
# If you lost the GNU General Public License that ships with this software
# repository (read the 'LICENSE' file), see <http://www.gnu.org/licenses/>.

import os
import pytest

from click_hotoffthehamster.testing import CliRunner

import dob.dob as dob  # for dob.run


@pytest.fixture
def runner(tmpdir):
    """Provide a convenient fixture to simulate execution of (sub-) commands."""
    def runner(args=[], keep_paths=False, **kwargs):
        # Override environments that AppDirs (thankfully) hooks. Ref:
        #   ~/.virtualenvs/dob/lib/python3.8/site-packages/appdirs.py

        # Override paths: (1) if caller running multiple command test
        # (keep_paths=True); or (2) if user wants theirs (DOB_KEEP_PATHS).
        if keep_paths or os.environ.get('DOB_KEEP_PATHS', False):
            XDG_CONFIG_HOME = os.environ['XDG_CONFIG_HOME']
            XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
        else:
            path = tmpdir.strpath
            XDG_CONFIG_HOME = '{}/.config'.format(path)
            XDG_DATA_HOME = '{}/.local/share'.format(path)
        os.environ['XDG_CONFIG_HOME'] = XDG_CONFIG_HOME
        os.environ['XDG_DATA_HOME'] = XDG_DATA_HOME

        env = {
            'XDG_CONFIG_HOME': XDG_CONFIG_HOME,
            'XDG_DATA_HOME': XDG_DATA_HOME,
            # Do not overwrite ~/.cache/dob path, where dob.log lives,
            # so DEV tail sees test output, too:
            #   'XDG_CACHE_HOME': '{}/.cache'.format(path),
            # It should not be necessary to set the state directory:
            #   'XDG_STATE_HOME': '{}/.local/state'.format(path),
            # AppDirs also checks 2 other environs, generally set
            # to system paths, and also you'll find already existing
            # for your user, probably:
            #   'XDG_DATA_DIRS': '/usr/local/share' or '/usr/share',
            #   'XDG_CONFIG_DIRS': '/etc/xdg',
        }
        return CliRunner().invoke(dob.run, args, env=env, **kwargs)
    return runner

