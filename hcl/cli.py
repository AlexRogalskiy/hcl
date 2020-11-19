from typing import Sequence, Type
import shlex
from pathlib import Path
import logging
from functools import wraps
import sys

from h5py import File
from prompt_toolkit import print_formatted_text, PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import to_formatted_text

from .utils import H5Path, normalise_path, Signal, is_dataset, is_group
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
        mode="r",
        interactive=True,
    ):
        self.fpath = Path(fpath) if fpath else None
        if not gpath:
            gpath = "/"
        elif not gpath.startswith("/"):
            gpath = "/" + gpath
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
        self.mode = mode
        self.interactive = interactive

        self.session = None
        self.file = None
        self.group = None

    def __enter__(self):
        if self.fpath:
            self.file = File(self.fpath, mode=self.mode)
            self.group = self.file[str(self.gpath)]
            if not is_group(self.group):
                raise ValueError(f"Not a group: {self.H5Path}")
        return self

    def __exit__(self, exc_type, value, traceback):
        if self.file:
            self.file.close()
        self.file = None
        self.group = None

    def run_line(self, s):
        out = Signal.SUCCESS
        for cmd in s.split(";"):
            argv = shlex.split(cmd.strip())
            out = self.run_command(argv)
            if out != Signal.SUCCESS:
                break
        return out

    def run_command(self, argv):
        if not argv:
            return
        cmd, *args = argv

        try:
            fn = self.commands[cmd]
        except KeyError:
            self.print(f"Not a known command: {cmd}", file=sys.stderr)
            return Signal.FAILURE

        return fn(argv[1:])

    def run(self):
        prefix = f"{self.fpath}:{{}} $ "
        if not self.session:
            self.session = PromptSession(**self.session_kwargs)

        while True:
            line = self.session.prompt(prefix.format(self.gpath))
            result = self.run_line(line)
            if result == Signal.QUIT:
                break

    def change_group(self, path: H5Path):
        if self.file is None:
            raise RuntimeError("File not open")
        new_path = normalise_path(path, self.gpath)
        new_obj = self.file[str(new_path)]
        if is_dataset(new_obj):
            raise ValueError(f"Object at path is a dataset: {new_path}")
        self.gpath = new_path
        self.group = self.file[str(new_path)]

    @wraps(print_formatted_text)
    def print(self, *args, **kwargs):
        kwargs = {**self.print_kwargs, **kwargs}
        if kwargs.get("file", sys.stdout).isatty():
            print_formatted_text(*args, **kwargs)
        else:
            keep = {"sep", "end", "file", "flush"}
            if self.interactive:
                formatted_items = [tup[1] for tup in to_formatted_text(args)]
            else:
                formatted_items = args
            print(
                *formatted_items,
                **{k: v for k, v in kwargs.items() if k in keep},
            )
