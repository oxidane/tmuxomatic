

# tmuxomatic

Other tmux session managers are doing it wrong.  From the ridiculous list of unnecessary options requiring pages of documentation, to windows defined by a complicated nesting of panes with rigid splits and sizings.  Let's fix this, and make session management more flexible and more powerful, yet so easy that anybody could use it after just one example.  Session management that gets out of the way.

At the heart of tmuxomatic is the **windowgram**, a better way of defining tmux windows.  The windowgram is a rectangle comprised of alphanumeric characters (0-9, a-z, A-Z).  Each character identifies the position, size, and shape of a pane (up to 62 panes per window).  It should take only one short example to demonstrate all the powers of the windowgram.  Compare this definition from `session_example`, with its screenshot from `tmuxomatic session_example`:

	window an_example         # <-- A new window begins like this, spaces in names are acceptable

	HHHOOOOOVVVVXXXXAAAA      # <-- This is a windowgram, it defines shapes and positions of panes
	HHHOOOOOTTTTXXXXAAAA      # <-- You make your own, any size and arrangement, 62 panes maximum
	HHHqqqqqqqqkkkkkAAAA
	jjjqqqqqqqqkkkkkAAAA
	jjjqqqqqqqqkkkkk1234
	jjjqqqqqqqqkkkkk5678
	0000llllllllllaaaaaa
	tmuxllllllllllaaaaaa

	  foc                     # <-- Only 3 three-letter commands to remember: Focus, Directory, Run
	  dir ~                   # <-- An unlinked command becomes the default for all following panes
	a run figlet "a"          # <-- Here is a linked command to print a large "a" on pane a
	q run figlet "q"
	q foc
	A run figlet "A"

![](https://github.com/oxidane/tmuxomatic/blob/master/img/example.png)

With tmuxomatic, you'll never have to manually split, position, or size a pane again.  And linking the panes to actions is so logical that you probably won't forget it.  There are no extra file format rules to remember, and typically no command line arguments will be necessary.

For a list of additional features, run `tmuxomatic --help`.  For example, tmuxomatic can scale your windowgram larger or smaller -- by any multiplier, on either axis -- to help with fine-tuning.  This will be especially useful if you want very small panes on a window.

**Support for YAML session files coming soon.**



## Installation

This application requires:

* [Python 3 +](http://www.python.org/getit/)
* [tmux 1.8 +](http://tmux.sourceforge.net/)

Install with `pip install tmuxomatic`, or download the latest release or development version:

* Release: [https://pypi.python.org/pypi/tmuxomatic](https://pypi.python.org/pypi/tmuxomatic) [![Version](https://pypip.in/v/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic) [![Downloads](https://pypip.in/d/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic)
* Development: [https://github.com/oxidane/tmuxomatic](https://github.com/oxidane/tmuxomatic)



## Notes

To use tmuxomatic, you don't have to know everything about [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/), but the knowledge is useful for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These are tmux user preferences, and typically placed in a personal `.tmux.conf` file.



## Copyright and License

Copyright 2013-2014, Oxidane.
All rights reserved.

Distributed under the [BSD 3-Clause license](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution of the source.  See the license for details.

