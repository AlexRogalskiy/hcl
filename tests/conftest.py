from pathlib import Path

import h5py
import numpy as np

import pytest


@pytest.fixture
def hdf5_path(tmp_path):
    path = Path(tmp_path / "data.hdf5")
    with h5py.File(path, "w") as f:
        g1 = f.create_group("g1")
        g1_1 = g1.create_group("g1_1")

        g2 = f.create_group("g2")

        f.create_dataset("ds", data=np.ones((5, 8)))
        g1.create_dataset("ds1", data=np.ones((5, 5)))
        g1_1.create_dataset("ds1_1", data=np.ones((10, 15)) * 2)
        g2.create_dataset("ds2", data=np.ones((3, 4, 5)) * 4)

    return path
