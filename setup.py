#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Debugging: python3 setup.py

from distutils.core import setup
from distutils import sysconfig
import re

name = "tmuxomatic"

lines = open(name, "r").read().split("\n")
extract = lambda what: [re.search(r'"([^"]*)"', line).group() for line in lines if line.startswith(what)][0][1:-1]

version = extract("VERSION")
homepage = extract("HOMEPAGE")

extras = sysconfig.get_python_lib() + "/" + name

files = [
	("bin", ["tmuxomatic"]),
#	(extras, ["session_example", "session_practical", "session_unsupported", "session_yaml"]),
#	(extras, ["README.md"]),
]

classifiers = [
	"Development Status :: 5 - Production/Stable",
	"Environment :: Console",
	"Environment :: Other Environment",
	"Intended Audience :: Developers",
	"Intended Audience :: End Users/Desktop",
	"Intended Audience :: System Administrators",
	"License :: OSI Approved :: BSD License",
	"Natural Language :: English",
	"Operating System :: MacOS :: MacOS X",
	"Operating System :: POSIX :: BSD",
	"Operating System :: POSIX :: Linux",
	"Operating System :: Unix",
	"Programming Language :: Python",
	"Programming Language :: Python :: 3",
	"Topic :: Desktop Environment",
	"Topic :: Internet",
	"Topic :: Internet :: Log Analysis",
	"Topic :: System",
	"Topic :: System :: Shells",
	"Topic :: System :: Systems Administration",
	"Topic :: System :: System Shells",
	"Topic :: Terminals",
	"Topic :: Terminals :: Terminal Emulators/X Terminals",
	"Topic :: Utilities",
]

setup(

	name="tmuxomatic",
	version=version,

	description="An altogether better way to do session management with tmux",
	license="BSD 3-Clause",
	url=homepage,
	download_url="https://pypi.python.org/pypi/tmuxomatic",

	author="Oxidane",
	author_email="",

	data_files=files,

	classifiers=classifiers,
	packages=[],

)

