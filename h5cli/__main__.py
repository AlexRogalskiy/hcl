"""
CLI for interactive exploration of
"""
from argparse import ArgumentParser
import logging

from .cli import Cli
from .commands import Ls, Pwd, Cd, Exit

logger = logging.getLogger(__name__)

COMMANDS = [Ls, Pwd, Cd, Exit]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("file", help="HDF5 file to explore")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    args = parser.parse_args()

    log_level = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}.get(
        args.verbose, logging.DEBUG
    )

    logging.basicConfig(level=log_level)

    with Cli(args.file, commands=COMMANDS) as cli:
        cli.run()


if __name__ == "__main__":
    main()
