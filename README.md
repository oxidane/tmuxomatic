

# tmuxomatic [![Version](http://img.shields.io/pypi/v/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic) [![Downloads](http://img.shields.io/pypi/dd/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic)

The other tmux session managers are doing it wrong.  From unnecessary options requiring pages of documentation, to windows defined by a complicated nesting of pane splits.  Instead, session management should be more flexible and more powerful, yet so easy that anybody could use it after just one example.

At the heart of tmuxomatic is the **windowgram**, a better way of defining tmux windows.  The windowgram is a rectangle comprised of alphanumeric characters (0-9, a-z, A-Z).  Each character identifies the position, size, and shape of a pane.  It should take only one short example to demonstrate the flexibility and power of the windowgram.

Compare this window from `session_example`, with its screenshot from `tmuxomatic session_example`:

	window example_one        # <-- A new window begins like this, spaces in names are allowed

	AAAAAAvvvvvXXXXXTTTT      # <-- The windowgram, it defines the shapes and positions of panes
	jjjQQQQQQQuuuuuuTTTT      # <-- Make your own, of any size and arrangement, 62 panes maximum
	jjjQQQQQQQuuuuuuTTTT
	jjjQQQQQQQuuuuuuTTTT
	0000llllllllllaaaaaa
	1234llllllllllaaaaaa

	  foc                     # <-- Three 3-letter commands to remember: Focus, Directory, Run
	  dir ~                   # <-- Unlinked directory, becomes default for all undefined panes
	A run figlet "A"          # <-- Linked to pane A, this command prints "A" in large lettering
	Q run figlet "Q"
	A foc

![](https://github.com/oxidane/tmuxomatic/blob/master/img/example.png)

With tmuxomatic, you'll never have to manually split, position, or size a pane again.  And linking the panes to actions is so simple and logical that you probably won't forget it.  There are no extra file format rules to remember, and typically no command line arguments will be necessary.

For additional features, run `tmuxomatic --help`.  For example, there's a feature to scale your windowgram larger or smaller -- by any multiplier, on either axis -- to help with fine-tuning.  This is useful if you need very small panes on a window.



## Installation

This application requires:

* [Python 3](http://www.python.org/getit/) +
* [tmux 1.8](http://tmux.sourceforge.net/) +

There are three ways to install tmuxomatic, in order of convenience:

**Automatically** using pip

* `pip-python3 install tmuxomatic`

**Manually** using python

* Download and extract the archive file from https://pypi.python.org/pypi/tmuxomatic
* In the tmuxomatic directory, run `python3 setup.py install`

**Development**

* Visit https://github.com/oxidane/tmuxomatic for up-to-date installation instructions
* `git clone git://github.com/oxidane/tmuxomatic.git`
* `cp -a tmuxomatic/tmuxomatic /usr/bin`



## Notes

To use tmuxomatic, you don't have to know everything about [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/), but the knowledge is useful for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These are tmux user preferences, and typically placed in a personal `.tmux.conf` file.



## Copyright and License

Copyright 2013-2014, Oxidane.
All rights reserved.

Distributed under the [BSD 3-Clause license](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution of the source.  See the license for details.

