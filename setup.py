from distutils.core import setup
import py2exe

setup(console=["./server.py"], data_files=[('.', ['./config.ini'])])
