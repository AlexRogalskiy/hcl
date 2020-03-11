from pathlib import PurePosixPath as H5Path
from typing import List, Union
from enum import Enum, auto

from h5py import File, Group, Dataset

ObjectType = Union[File, Group, Dataset]


def normalise_path(
    path: H5Path, current_gpath: H5Path = None, relative=False
) -> H5Path:
    if current_gpath is not None:
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
    if isinstance(obj, File):
        return "/"

    p_name = parent_name or obj.parent.name
    if not p_name.endswith("/"):
        p_name += "/"
    return obj.name[len(p_name):]


# TODO: consider replacing with OS signals
class Signal(Enum):
    QUIT = auto()
