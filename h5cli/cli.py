from typing import Sequence, Type
import shlex
from pathlib import Path
import logging
from functools import wraps
import sys

from h5py import File, Group, Dataset
from prompt_toolkit import print_formatted_text, PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import to_formatted_text

from .utils import H5Path, normalise_path, Signal
from .commands import Command


logger = logging.getLogger(__name__)


class Cli:
    def __init__(
        self,
        fpath,
        gpath="/",
        commands: Sequence[Type[Command]] = (),
        session_kwargs=None,
        print_kwargs=None,
    ):
        self.fpath = Path(fpath)
        self.gpath = H5Path(gpath)
        self.print_kwargs = print_kwargs or dict()

        self.commands = dict()
        completers = dict()
        for cmd_cls in commands:
            c = cmd_cls(self)
            self.commands[c.name()] = c
            completers[c.name()] = c.completer()

        self.session_kwargs = {"completer": NestedCompleter(completers)}
        self.session_kwargs.update(session_kwargs or dict())

        self.session = None
        self.file = None
        self.group = None

    def __enter__(self):
        self.file = File(self.fpath, mode="r")
        self.group = self.file[str(self.gpath)]
        if not isinstance(self.group, Group):
            raise ValueError(f"Not a group: {self.H5Path}")
        return self

    def __exit__(self, exc_type, value, traceback):
        self.file.close()
        self.file = None
        self.group = None

    def run_command(self, argv):
        if not argv:
            return
        cmd, *args = argv

        try:
            fn = self.commands[cmd]
        except KeyError:
            self.print(f"Not a known command: {cmd}", file=sys.stderr)
            return

        try:
            return fn(argv[1:])
        except Exception as e:
            logger.exception()
            self.print(f"Uncaught exception: {e}", file=sys.stderr)
            return

    def run(self):
        prefix = f"{self.fpath}:{{}} $ "
        if not self.session:
            self.session = PromptSession(**self.session_kwargs)

        while True:
            text = self.session.prompt(prefix.format(self.gpath))
            argv = shlex.split(text)
            out = self.run_command(argv)
            if out == Signal.QUIT:
                break

    def change_group(self, path: H5Path):
        new_path = normalise_path(path, self.gpath)
        new_obj = self.file[str(new_path)]
        if isinstance(new_obj, Dataset):
            raise ValueError(f"Object at path is a dataset: {new_path}")
        self.gpath = new_path
        self.group = self.file[str(new_path)]

    @wraps(print_formatted_text)
    def print(self, *args, **kwargs):
        kwargs = {**self.print_kwargs, **kwargs}
        text = to_formatted_text(*args, **kwargs)
        if kwargs.get("file", sys.stdout).isatty():
            print_formatted_text(text)
        else:
            keep = {"sep", "end", "file"}
            print(*(tup[1] for tup in text), **{k: v for k, v in kwargs.items()if k in keep})
