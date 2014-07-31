#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Debugging: python3 setup.py

from distutils.core import setup
from distutils import sysconfig
import re, os, sys

lines = open("tmuxomatic", "r").read().split("\n")
extract = lambda what: [re.search(r'"([^"]*)"', line).group() for line in lines if line.startswith(what)][0][1:-1]

version = extract("VERSION")
homepage = extract("HOMEPAGE")
keywords = "tmux, screen, awesome"

# Maybe someone could help get this sorted out properly.  I don't want to use a subdirectory or a manifest file for this.
# When the user installs, I want tmuxomatic to go into the user's bin directory.  I have been able to accomplish this by
# using the data_files parameter, which seems to work except for setup() imposing chmod 644.  So afterwards, if setup was
# called with "install", we search for tmuxomatic in the user's path, and then chmod 755.  If you happen know of a way to
# do this install without the chmod step, or in a more correct manner, please send a pull request with the changes.

packages = [] # ["tmuxomatic"]
package_dir = {} # {'tmuxomatic': "/usr/bin"}
package_data = {} # {'tmuxomatic': ["tmuxomatic"]}
data_files = [
	( "bin", [ "tmuxomatic" ] ),
# Add readme after it's ported to pypi+github friendly format, add example sessions after install has been sorted out
#	( sysconfig.get_python_lib() + "/tmuxomatic",
#		[ "README.md", "session_example", "session_practical", "session_unsupported", "session_yaml" ] ),
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

	packages=packages,
	package_dir=package_dir,
	package_data=package_data,
	data_files=data_files,

	keywords=keywords,
	classifiers=classifiers,

)

def which(program):
	"""
	Returns the absolute path of specified executable
	Source: https://stackoverflow.com/a/377028
	"""

	def is_exe(fpath):
		# Return true if file exists (not expected to be executable)
		return os.path.isfile(fpath)

	fpath, _ = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file
	return None

if "install" in sys.argv:
	os.chmod( which("tmuxomatic"), 0o755 )

