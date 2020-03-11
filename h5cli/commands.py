from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
import logging

from prompt_toolkit import print_formatted_text
from h5py import Dataset

from .utils import H5Path, normalise_path, obj_name, Signal


class Command(ABC):
    def __init__(self, context):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.name()}")

    @abstractmethod
    def argument_parser(self) -> ArgumentParser:
        pass

    def __call__(self, argv):
        self.logger.debug("Called with arguments %s", argv)
        parser = self.argument_parser()
        try:
            parsed = parser.parse_args(argv)
        except SystemExit:
            return
        self.logger.debug("Parsed arguments to %s", parsed)
        return self.run(parsed)

    @abstractmethod
    def run(self, parsed_args: Namespace):
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class Ls(Command):
    def name(self):
        return "ls"

    def argument_parser(self):
        parser = ArgumentParser(self.name(), description="List members of a group")
        parser.add_argument(
            "path", nargs="*", help="Paths to list the directories of", type=H5Path
        )

        return parser

    def ls_object(self, path: H5Path):
        obj_path = normalise_path(path, self.context.gpath, True)
        self.logger.debug("Normalised path to %s", obj_path)

        obj = self.context.group[str(obj_path)]
        self.logger.debug("Listing item at %s", obj.name)
        if isinstance(obj, Dataset):
            return str(path)
        else:
            name = obj.name
            rows = sorted(str(obj_path / obj_name(child, name)) for child in obj.values())
            return "\n".join(rows)

    def run(self, parsed_args):
        paths = parsed_args.path
        if not paths:
            paths = [self.context.gpath]

        if len(paths) == 1:
            out = self.ls_object(paths[0])
        else:
            out = "\n".join(f"{path}:\n{self.ls_object(path)}" for path in paths)

        print_formatted_text(out)


class Pwd(Command):
    def name(self):
        return "pwd"

    def argument_parser(self):
        return ArgumentParser(self.name(), description="Get working group")

    def run(self, parsed_args):
        print_formatted_text(str(self.context.gpath))


class Cd(Command):
    def name(self):
        return "cd"

    def argument_parser(self):
        parser = ArgumentParser(self.name(), description="Change working group")
        parser.add_argument("path", nargs="?", help="Path to next working group", type=H5Path)
        return parser

    def run(self, parsed_args):
        path = parsed_args.path
        if not path:
            return
        try:
            self.context.change_group(path)
        except KeyError as e:
            print_formatted_text(str(e))
        except ValueError as e:
            print_formatted_text(str(e))


class Exit(Command):
    def name(self):
        return "exit"

    def argument_parser(self):
        return ArgumentParser(self.name(), description="Quit h5cli")

    def run(self, parsed_args):
        self.logger.debug("Quitting")
        return Signal.QUIT
