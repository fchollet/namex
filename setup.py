from setuptools import find_packages
from setuptools import setup

setup(
    name="namex",
    version="0.0.7",
    description=(
        "A simple utility to separate "
        "the implementation of your Python package "
        "and its public API surface."
    ),
    author="Francois Chollet",
    author_email="francois.chollet@gmail.com",
    license="Apache License 2.0",
    packages=find_packages(),
)
