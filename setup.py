#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

files = [
	("Program", ["tmuxomatic"]),
	("Setup", ["setup.py"]),
#	("Examples", ["session_example", "session_practical", "session_unsupported"]),
#	("Documentation", ["README.md"]),
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
	version="1.0.16", # TODO: Extract this from tmuxomatic

	description="An altogether better way to do session management with tmux",
	license="BSD 3-Clause",
	url="https://github.com/oxidane/tmuxomatic",
	download_url="https://pypi.python.org/pypi/tmuxomatic",

	author="Oxidane",
	author_email="",

	data_files=files,

	classifiers=classifiers,
	packages=[],

)

