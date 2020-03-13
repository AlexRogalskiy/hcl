from pathlib import PurePosixPath as H5Path
from typing import List, Union, Iterable
from enum import Enum, auto
from collections import deque

from h5py import File, Group, Dataset

from prompt_toolkit.completion import Completion, Completer

ObjectType = Union[File, Group, Dataset]


def normalise_path(
    path: H5Path, current_gpath: H5Path = None, relative=False
) -> H5Path:
    path = H5Path(path)
    if current_gpath is not None:
        current_gpath = H5Path(current_gpath)
        path = current_gpath / path

    if not path.is_absolute():
        raise ValueError("Path must be absolute")

    parts: List[str] = []
    for part in path.parts:
        if set(part) == {"."}:
            for _ in part[1:]:
                try:
                    parts.pop()
                    if len(parts) == 0:
                        raise IndexError()
                except IndexError:
                    raise ValueError("Tried to traverse beyond root")
        else:
            parts.append(part)

    out = H5Path(*parts)
    if relative and current_gpath:
        out = out.relative_to(current_gpath)
    return out


def obj_name(obj: ObjectType, parent_name=None) -> str:
    if isinstance(obj, File) or obj.name == "/":
        return "/"

    p_name = parent_name or obj.parent.name
    if not p_name.endswith("/"):
        p_name += "/"
    return obj.name[len(p_name) :]


# TODO: consider replacing with OS signals
class Signal(Enum):
    QUIT = auto()


class H5PathCompleter(Completer):
    """
    Complete for Path variables.
    :param get_paths: Callable which returns a list of directories to look into
                      when the user enters a relative path.
    :param file_filter: Callable which takes a filename and returns whether
                        this file should show up in the completion. ``None``
                        when no filtering has to be done.
    :param min_input_len: Don't do autocompletion when the input string is shorter.
    """

    def __init__(
        self,
        context,
        include_groups: bool = True,
        include_datasets: bool = True,
    ) -> None:
        self.context = context
        self.include_groups = include_groups
        self.include_datasets = include_datasets

    @property
    def gpath(self):
        return self.context.gpath

    @property
    def group(self):
        return self.context.group

    def get_completions(
        self, document, complete_event
    ) -> Iterable[Completion]:
        text = document.text_before_cursor

        curr_path = H5Path(text)
        if text.endswith("/"):
            parent = curr_path
            prefix = ""
        else:
            parent = curr_path.parent
            prefix = curr_path.name

        try:
            parent_obj = self.group[str(normalise_path(parent, self.gpath))]
        except KeyError:
            return

        for name, obj in parent_obj.items():
            if not name.startswith(prefix):
                continue

            if (self.include_groups and isinstance(obj, Group)) or (self.include_datasets and isinstance(obj, Dataset)):
                yield Completion(name[len(prefix) :], 0, display=name)
