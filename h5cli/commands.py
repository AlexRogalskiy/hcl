import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
import logging
import pprint

from h5py import Dataset

from .utils import H5Path, normalise_path, obj_name, Signal


class Command(ABC):
    def __init__(self, context):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.name()}")

    @abstractmethod
    def argument_parser(self) -> ArgumentParser:
        pass

    def __call__(self, argv=()):
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
            rows = sorted(
                obj_name(child, name) for child in obj.values()
            )
            return "\n".join(rows)

    def run(self, parsed_args):
        paths = parsed_args.path
        if not paths:
            paths = [self.context.gpath]

        if len(paths) == 1:
            out = self.ls_object(paths[0])
        else:
            out = "\n".join(f"{path}:\n{self.ls_object(path)}" for path in paths)

        self.context.print(out)


class Pwd(Command):
    def name(self):
        return "pwd"

    def argument_parser(self):
        return ArgumentParser(self.name(), description="Get working group")

    def run(self, parsed_args):
        self.context.print(str(self.context.gpath))


class Cd(Command):
    def name(self):
        return "cd"

    def argument_parser(self):
        parser = ArgumentParser(self.name(), description="Change working group")
        parser.add_argument(
            "path", nargs="?", help="Path to next working group", type=H5Path
        )
        return parser

    def run(self, parsed_args):
        path = parsed_args.path
        if not path:
            return
        try:
            self.context.change_group(path)
        except KeyError as e:
            self.context.print(str(e), file=sys.stderr)
        except ValueError as e:
            self.context.print(str(e), file=sys.stderr)


class Exit(Command):
    def name(self):
        return "exit"

    def argument_parser(self):
        return ArgumentParser(self.name(), description="Quit h5cli")

    def run(self, parsed_args):
        self.logger.debug("Quitting")
        return Signal.QUIT


class Attrs(Command):
    def name(self):
        return "attrs"

    def argument_parser(self):
        parser = ArgumentParser(
            "attrs", description="List attributes or look at one attribute"
        )
        parser.add_argument(
            "path",
            nargs="?",
            type=H5Path,
            help="Path to object whose attributes to check",
        )
        parser.add_argument("attr", nargs="?", help="Attribute to check")
        parser.add_argument(
            "-a", "--all", action="store_true", help="Show all attribute values"
        )
        return parser

    def run(self, parsed_args):
        if not parsed_args.path:
            obj = self.context.group
        else:
            obj = self.context.group[str(parsed_args.path)]

        if parsed_args.all:
            out = []
            for k, v in sorted(obj.attrs.items()):
                out.append(f"{k}:\n{pprint.pformat(v, indent=2)}")
            self.context.print(*out, sep="\n\n")
            return

        if not parsed_args.attr:
            self.context.print(sorted(obj.attrs.keys()))
        else:
            self.context.print(pprint.pformat(obj.attrs[parsed_args.attr]))


class AttributePrint(Command):
    _name = None
    _pprint = False

    def name(self):
        return self._name

    def argument_parser(self):
        parser = ArgumentParser(self._name, description=f"Get object {self._name}")
        parser.add_argument("path", type=H5Path, help="Path to object")
        return parser

    def _format(self, obj):
        if self._pprint:
            return pprint.pformat(obj)
        else:
            return str(obj)

    def run(self, parsed_args):
        obj = self.context.group[str(parsed_args.path)]
        try:
            attr = getattr(obj, self._name)
        except AttributeError as e:
            self.context.print(str(e), file=sys.stderr)
            return

        if attr is not None:
            self.context.print(self._format(attr))


class Filename(AttributePrint):
    _name = "filename"


class Mode(AttributePrint):
    _name = "mode"


class Driver(AttributePrint):
    _name = "driver"


class Libver(AttributePrint):
    _name = "libver"


class UserblockSize(AttributePrint):
    _name = "userblock_size"


class Name(AttributePrint):
    _name = "name"


class Shape(AttributePrint):
    _name = "shape"
    _pprint = True


class Dtype(AttributePrint):
    _name = "dtype"


class Size(AttributePrint):
    _name = "size"


class Maxshape(AttributePrint):
    _name = "maxshape"
    _pprint = True


class Chunks(AttributePrint):
    _name = "chunks"
    _pprint = True


class Compression(AttributePrint):
    _name = "compression"


class CompressionOpts(AttributePrint):
    _name = "compression_opts"
    _pprint = True


class Scaleoffset(AttributePrint):
    _name = "scaleoffset"


class Shuffle(AttributePrint):
    _name = "shuffle"


class Fletcher32(AttributePrint):
    _name = "fletcher32"


class Fillvalue(AttributePrint):
    _name = "fillvalue"


class IsVirtual(AttributePrint):
    _name = "is_virtual"


class Help(Command):
    def name(self):
        return "help"

    def argument_parser(self):
        parser = ArgumentParser(self.name(), description="List available commands")
        parser.add_argument(
            "-s", "--short", action="store_true", help="Just show the names"
        )
        parser.add_argument(
            "-l",
            "--long",
            action="store_true",
            help="Show the full help text for every command",
        )
        return parser

    def run(self, parsed_args):
        commands = sorted(self.context.commands)
        if parsed_args.short:
            self.context.print(*commands, sep="\n")
            return

        if parsed_args.long:
            self.context.print(
                *(
                    self.context.commands[c].argument_parser().format_help()
                    for c in commands
                ),
                sep="\n\n",
            )
            return

        indent = max(len(c) for c in commands) + 4
        out = []
        for c in commands:
            desc = self.context.commands[c].argument_parser().description
            short = desc.split(".")[0] + "."
            out.append(f"{c}{' ' * (indent - len(c))}{short}")

        self.context.print(*out, sep="\n")


all_commands = [
    Ls,
    Pwd,
    Cd,
    Exit,
    Attrs,
    Filename,
    Mode,
    Driver,
    Libver,
    UserblockSize,
    Name,
    Shape,
    Dtype,
    Size,
    Maxshape,
    Chunks,
    Compression,
    CompressionOpts,
    Scaleoffset,
    Shuffle,
    Fletcher32,
    Fillvalue,
    IsVirtual,
    Help,
]
