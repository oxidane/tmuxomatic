

# tmuxomatic

An altogether better way to do session management with tmux.

* Install: `pip install tmuxomatic`
* Release: [https://pypi.python.org/pypi/tmuxomatic](https://pypi.python.org/pypi/tmuxomatic)
[![Version](https://pypip.in/v/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic)
[![Downloads](https://pypip.in/d/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic)
* Development: [https://github.com/oxidane/tmuxomatic](https://github.com/oxidane/tmuxomatic)
* Thread: [Version 1.0.12 @ HN](https://news.ycombinator.com/item?id=8063459)



## Introduction

Existing tmux session managers are needlessly complex and inflexible.  From the ridiculous list of commands with pages of documentation, to panes defined as a complicated nesting of splits and sizings.  What's needed is a session manager that's flexible and powerful, yet so easy anybody could use it after one example.  Something that empowers and gets out of the way.

Enter tmuxomatic.  It uses the **windowgram**, a new approach to tmux sessions.  The windowgram is a rectangle comprised of alphanumeric characters (0-9, a-z, A-Z).  Each character identifies the position, size, and shape of a pane (up to 62 panes per window).  It should take only one example to illustrate all the simplicity and flexibility the windowgram has to offer:

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

That's a sample window from the file `session_example`.  Run with `tmuxomatic session_example`.  Here's the result:

![](https://github.com/oxidane/tmuxomatic/blob/master/img/example.png)

With tmuxomatic, you'll never have to manually split, position, or size a pane again.  Linking the panes to actions is so logically simple that you won't forget it.  There are no extra file format rules to remember, and typically no command line arguments will be necessary.  It's so easy, you can probably begin using tmuxomatic right now.

Run `tmuxomatic --help` for the list of command-line options that may be of use to demanding users.  Most notably, it has a windowgram scaling feature.  With it, you can scale a windowgram to be larger or smaller -- by any multiplier, on either axis -- to help with fine-tuning your session layouts.  This is especially useful if you want very small panes on a window.

**Support for YAML session files coming soon.**



## Requirements

* [Python 3 +](http://www.python.org/getit/)
* [tmux 1.8 +](http://tmux.sourceforge.net/)



## Usage

The example shown above may be reproduced with: `tmuxomatic session_example`.

To reattach after a disconnection, simply run again: `tmuxomatic session_example`.

To force a session recreation, add `-r` or `--recreate`: `tmuxomatic session_example -r`.

For easier expansion of window layouts, use the scale option: `tmuxomatic session_example --scale 1 3x 2x`.

Finally, run `tmuxomatic --help` to get a full list of command line options.



## Examples

This project includes a few examples.  The most useful is `session_practical`, as it demonstrates how you might configure tmuxomatic in a real-world environment.



## Notes

To use tmuxomatic, you don't have to know everything about [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/), but the knowledge is useful for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These features are extraneous to tmuxomatic, and they typically go into your personal `.tmux.conf` file.



## Copyright and License

Copyright 2013-2014, Oxidane.
All rights reserved.

Distributed under the [BSD 3-Clause license](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution of the source.  See the license for details.

