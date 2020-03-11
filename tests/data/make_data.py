#!/usr/bin/env python
import h5py
import numpy as np


with h5py.File("data.hdf5", "w") as f:
    g1 = f.create_group("g1")
    g1_1 = g1.create_group("g1_1")

    g2 = f.create_group("g2")

    ds = f.create_dataset("ds", data=np.ones((5, 8)))
    ds1 = g1.create_dataset("ds1", data=np.ones((5, 5)))
    ds1_1 = g1_1.create_dataset("ds1_1", data=np.ones((10, 15)) * 2)
    ds2 = g2.create_dataset("ds2", data=np.ones((3, 4, 5)) * 4)
