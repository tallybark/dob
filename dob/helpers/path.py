# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

from gettext import gettext as _

import time

from dob_bright.termio import dob_in_user_warning

__all__ = (
    'compile_and_eval_source',
)


def compile_and_eval_source(py_path):
    """"""
    def _compile_and_eval_source(py_path):
        with open(py_path, 'r') as py_text:
            eval_globals = compile_and_eval_module(py_text, py_path)
        return eval_globals

    def compile_and_eval_module(py_text, py_path):
        code = source_compile(py_text, py_path)
        if code is None:
            return set()
        eval_globals = globals()
        eval_source_code(code, eval_globals, py_path)
        return eval_globals

    def source_compile(py_text, py_path):
        try:
            code = compile(py_text.read(), py_path, 'exec')
        except Exception as err:
            code = None
            msg = _(
                'ERROR: Could not compile source file at "{}": {}'
            ).format(py_path, str(err))
            dob_in_user_warning(msg)
            time.sleep(2.666)
        return code

    def eval_source_code(code, eval_globals, py_path):
        try:
            # Pass py_path to code being eval'd, so it can orientate.
            # (lb): I tried passing `locals()` for second argument, but
            # then plugins complain `name 'ConfigRoot' is not defined`.
            eval_globals['__file__'] = py_path
            eval(code, eval_globals, eval_globals)
        except Exception as err:
            msg = _(
                'ERROR: Could not eval compiled source at "{}": {}'
            ).format(py_path, str(err))
            dob_in_user_warning(msg)
            time.sleep(2.666)

    return _compile_and_eval_source(py_path)

