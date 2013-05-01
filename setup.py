import os
from setuptools import setup

def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(path):
        return open(path, 'r').read()
    return ''


setup(
    name='deconf',
    version="0.1.1",
    py_modules=['deconf'],
    provides=['deconf'],
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/deconf",
    description="An object system for building declarative configurations in Python.",
    long_description=read('README.md'),
)
