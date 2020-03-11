from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent

long_description = (here / "README.md").read_text()

install_requires = ["h5py", "prompt-toolkit", "tabulate"]

setup(
    name="h5cli",
    version="0.1.0",
    description="Interactive CLI for exploring HDF5 files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clbarnes/h5cli",
    author="Chris L. Barnes",
    author_email="chrislloydbarnes@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(include="h5cli"),
    python_requires=">=3.8, <4",
    install_requires=install_requires,
    entry_points={"console_scripts": ["h5cli=h5cli.__main__:main"]},
)
