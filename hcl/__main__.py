"""
CLI for interactive exploration of HDF5 files.
"""
from argparse import ArgumentParser
import logging
import shlex
from importlib import import_module
import sys

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
    parser.add_argument(
        "file",
        nargs="?",
        help="HDF5 file to explore. Add ':/path/to/group' to start in a specific group.",
    )
    parser.add_argument(
        "-c",
        "--command",
        help="Run a single command and exit. Output can be redirected but not piped.",
    )
    parser.add_argument(
        "-p",
        "--plugin",
        action="append",
        help="Import path for additional commands. Imported object can be a Command subclass, an iterable of them, or a callable returning either. Format '{absolute_module}:{object}'. Can be used multiple times.",
        default=(),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase logging verbosity, up to -vvv for debug.",
    )
    parser.add_argument(
        "--mode", "-m", default="r", help="Mode in which to open the file. "
        "'r' (default): Readonly, file must exist. "
        "'r+': Read/write, file must exist. "
        "'w': Create file, truncate if exists. "
        "'w-' or 'x': Create file, fail if exists. "
        "'a': Read/write if exists, create otherwise."
    )
    args = parser.parse_args()

    log_level = {
        0: logging.CRITICAL,
        1: logging.WARN,
        2: logging.INFO,
        3: logging.DEBUG,
    }.get(args.verbose, logging.DEBUG)

    logging.basicConfig(level=log_level)

    if not args.file:
        parser.print_help()
        sys.exit()

    fpath_gpath = args.file.split(":")
    els = len(fpath_gpath)
    if els == 1:
        fpath = fpath_gpath[0]
        gpath = "/"
    elif els == 2:
        fpath, gpath = fpath_gpath
    else:
        raise ValueError(f"Got more than one group path from argument '{args.file}'")

    for import_path in args.plugin:
        COMMANDS.extend(get_plugin_commands(import_path))

    with Cli(fpath, gpath=gpath, commands=COMMANDS) as cli:
        if args.command:
            cli.run_command(shlex.split(args.command))
        else:
            try:
                cli.run()
            except EOFError:
                cli.commands["exit"]()


if __name__ == "__main__":
    main()