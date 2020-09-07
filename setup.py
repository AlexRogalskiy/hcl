#!/usr/bin/env python
from setuptools import setup, find_packages
from pathlib import Path
import runpy

here = Path(__file__).resolve().parent

long_description = (here / "README.md").read_text()
version = runpy.run_path(here / "hcl" / "version.py")["__version__"]

install_requires = ["h5py", "prompt-toolkit", "tree-format"]

setup(
    name="hcl",
    version=version,
    description="Interactive CLI for exploring HDF5 files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clbarnes/hcl",
    author="Chris L. Barnes",
    author_email="chrislloydbarnes@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(include="hcl"),
    python_requires=">=3.8, <4",
    install_requires=install_requires,
    entry_points={"console_scripts": ["hcl=hcl.__main__:main"]},
)
