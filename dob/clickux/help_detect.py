# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import sys
from functools import update_wrapper

import click

from .echo_assist import click_echo

__all__ = (
    'show_help_finally',
)


def show_help_finally(func):
    """Click command callback decorator to show help if requested.
    This changes the behavior of option parsing: The old behavior
    of `dob --help command` would show the general help, i.e., it
    would show the same help as `dob --help`. By telling Click to
    cool it, we can show the help for the specified sub-command
    instead, i.e., `dob --help command` will now show the help for
    command."""

    # (lb): I'll admit this might be the "hard way" to do this.
    # In run_cli.py, rather than passing help_option_names to
    # the Context, we could add our own click.option for -h/--help,
    # add a 'help' param to the run() method, and set the flag that
    # way. However, then each command would need to set the help
    # option, e.g., `dob --help command` sets help on the root Context
    # (via the run_cli.run() callback), whereas `dob command --help`
    # sets the help option on the command's context. Not that this
    # would be hard to do -- in addition to adding the show_help_finally
    # decorator to every Click command in dob.py, we could also add a
    # new click.option decorator to each of those commands... but then
    # we'd also have to add the 'help' param to every command method in
    # dob.py... and you see right there what a colossal pain using a
    # normal Click option to handle --help would be. So I guess it is
    # not the "hard way" having Click specially handle -h/--help.

    @click.pass_context
    def check_help(ctx, *args, **kwargs):
        if ctx.find_root().help_option_spotted:
            click_echo(ctx.get_help())
            ctx.exit()
        func(*args, **kwargs)

    return update_wrapper(check_help, func)

