#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##----------------------------------------------------------------------------------------------------------------------
##
## Installer for tmuxomatic
##
## The distutils is the only standard packaging library included with Python 3.x
##
##----------------------------------------------------------------------------------------------------------------------

from distutils.core import setup
from distutils import sysconfig
import re, os, sys

lines = open("tmuxomatic", "r").read().split("\n")
extract = lambda what: [re.search(r'"([^"]*)"', line).group() for line in lines if line.startswith(what)][0][1:-1]
def fullfile(filename): f = open(filename, "r") ; text = f.read() ; f.close() ; return text

version = extract("VERSION")
homepage = extract("HOMEPAGE")
hashtags = "#tmux"
description = extract("DESCRIPTION") + " ... " + hashtags
long_description = fullfile("README.rst")

KEYWORDS = "tmux, session manager, screen, shell, command line, iterm, xterm, split, windowgram"
keywords = [ key.strip() for key in KEYWORDS.split(",") ] # "1, 2, 3" -> ["1", "2", "3"]

# Maybe someone could help get this sorted out properly.  I don't want to use a subdirectory or a manifest file.  When
# the user installs, I want tmuxomatic to go into the user's bin directory.  I have been able to accomplish this by
# using the data_files parameter, which seems to work except for setup() imposing chmod 644.  So afterwards, if setup
# was called with "install", we search for tmuxomatic in the user's path, and then chmod 755.  If you happen know of a
# way to do this install without a chmod step, or in a more correct manner, please send a pull request with the changes.

packages = [ "windowgram" ]
package_dir = {}
package_data = {}
data_files = [
	( "bin", [ "tmuxomatic" ] ),
	( sysconfig.get_python_lib() + "/tmuxomatic", [ "README.rst" ] ),
# TODO: Add example sessions after install has been sorted out
#	( sysconfig.get_python_lib() + "/tmuxomatic",
#		[ "session_example", "session_practical", "session_unsupported", "session_yaml" ] ),
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

	description=description,
	long_description=long_description,
	license="BSD 3-Clause (tmuxomatic), Other (windowgram)",
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

# This is necessary to make tmuxomatic an executable on install, see notes above

if "install" in sys.argv:
	for path in os.environ["PATH"].split(os.pathsep):
		path = path.strip('"')
		exe_file = os.path.join(path, "tmuxomatic")
		if os.path.isfile(exe_file):
			os.chmod( exe_file, 0o755 )

