from typing import Sequence, Type
import shlex
from pathlib import Path
import logging

from h5py import File, Group, Dataset
from prompt_toolkit import prompt, print_formatted_text

from .utils import H5Path, normalise_path, Signal
from .commands import Command


logger = logging.getLogger(__name__)


class Cli:
    def __init__(self, fpath, gpath="/", commands: Sequence[Type[Command]] = ()):
        self.fpath = Path(fpath)
        self.gpath = H5Path(gpath)
        self.commands = dict()
        for cmd_cls in commands:
            c = cmd_cls(self)
            self.commands[c.name()] = c

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

    def run(self):
        prefix = f"{self.fpath}:{{}} $ "
        while True:
            text = prompt(prefix.format(self.gpath))
            argv = shlex.split(text)
            if not argv:
                continue
            cmd = argv[0]

            try:
                fn = self.commands[cmd]
            except KeyError:
                print_formatted_text(f"Not a known command: {cmd}")
                continue

            try:
                out = fn(argv[1:])
            except Exception:
                logger.exception(f"Uncaught exception in command: {cmd}")
                continue

            if out == Signal.QUIT:
                break

    def change_group(self, path: H5Path):
        new_path = normalise_path(path, self.gpath)
        new_obj = self.file[str(new_path)]
        if isinstance(new_obj, Dataset):
            raise ValueError(f"Object at path is a dataset: {new_path}")
        self.gpath = new_path
        self.group = self.file[str(new_path)]
