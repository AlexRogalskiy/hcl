"""
CLI for interactive exploration of HDF5 files.
"""
from argparse import ArgumentParser
import logging
import shlex
from importlib import import_module

from .cli import Cli
from .commands import Command, all_commands as COMMANDS

logger = logging.getLogger(__name__)


def get_plugin_commands(import_path):
    mod_name, obj_name = import_path.split(":")
    mod = import_module(mod_name)
    obj = getattr(mod, obj_name)
    if hasattr(obj, "__call__"):
        obj = obj()

    if issubclass(obj, Command):
        out = [obj]
    else:
        out = list(obj)

    logger.debug("Got commands from %s : %s", import_path, [c.__name__ for c in out])
    return out


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="HDF5 file to explore")
    parser.add_argument("-c", "--command", help="Run a single command and exit. Not suitable for piping/ redirection.")
    parser.add_argument("-p", "--plugin", action="append", help="Import path for additional commands. Can be a Command subclass, an iterable of them, or a callable returning either. Format '{absolute_module}:{object}'. Can be used multiple times.", default=())
    parser.add_argument(
        "--verbose", "-v", action="count", default=0, help="Increase logging verbosity"
    )
    args = parser.parse_args()

    log_level = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}.get(
        args.verbose, logging.DEBUG
    )

    logging.basicConfig(level=log_level)

    for import_path in args.plugin:
        COMMANDS.extend(get_plugin_commands(import_path))

    with Cli(args.file, commands=COMMANDS) as cli:
        if args.command:
            cli.run_command(shlex.split(args.command))
        else:
            try:
                cli.run()
            except EOFError:
                cli.commands["exit"]()


if __name__ == "__main__":
    main()
