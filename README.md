

# tmuxomatic

Automated window layout and session management for tmux, with a simple definition file that is powerful and flexible.

Quickstart: `pip install tmuxomatic`

* Release: [https://pypi.python.org/pypi/tmuxomatic](https://pypi.python.org/pypi/tmuxomatic)
[![Version](https://pypip.in/v/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic)
[![Downloads](https://pypip.in/d/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic)
* Development: [https://github.com/oxidane/tmuxomatic](https://github.com/oxidane/tmuxomatic)
* Discussions: [Version 1.0.12 @ HN](https://news.ycombinator.com/item?id=8063459)



## Introduction

Not long after I installed tmux, I became frustrated with the needless complexity and inflexibility of existing session managers.  From the ridicuous amounts of documentation and interface options, to the expectation that panes should be defined by a complicated nesting of splits and sizing.  I wanted something simple, flexible, and so easy that anybody could use it to tremendous advantage after seeing just one example.  Something that empowers me and gets out of my way.

Enter tmuxomatic.  It uses the **windowgram**, a totally new approach to tmux sessions.  The windowgram is a rectangle comprised of alphanumeric characters (0-9, a-z, A-Z).  Each character identifies the shape and position of one pane (up to 62 panes per window).  It should take only one example to illustrate the tremendous simplicity and flexibility the windowgram has to offer:

	window my_example       # <-- A new window begins like this, spaces in names are acceptable

	HHHOOOOOVVVVXXXXAAAA    # <-- This is a windowgram, it defines shapes and positions of panes
	HHHOOOOOTTTTXXXXAAAA    # <-- You make your own, any size and arrangement, 62 panes maximum
	HHHqqqqqqqqkkkkkAAAA
	jjjqqqqqqqqkkkkkAAAA
	jjjqqqqqqqqkkkkk1234
	jjjqqqqqqqqkkkkk5678
	0000llllllllllaaaaaa
	tmuxllllllllllaaaaaa

	  foc                   # <-- 3 three letter commands to remember: Focus, Directory, Run
	  dir ~                 # <-- An unlinked command becomes the default for all panes
	a run echo "pane a"     # <-- A linked command to run on pane a
	a run pwd
	q run echo "pane q"
	q foc
	A dir /tmp
	A run pwd

The above comes from the file `session_example`.  Run the session with `tmuxomatic session_example`.  Here you have the result:

![](https://github.com/oxidane/tmuxomatic/blob/master/img/example.png)

The advantages of the windowgram should be obvious now.  With tmuxomatic, you'll never have to manually split, position, or size a pane again.  If you change your window dimensions, tmuxomatic scales it to fit, just as you would expect.  Because pane definition (commands and attributes) is similarly easy, you'll rarely need to look at documentation.

A windowgram scale feature is built into the tmuxomatic command line.  With it, you may scale a windowgram up or down as needed to fine-tune your session layouts.  This is really helpful if you want very small panes.  See `--help` for details on the `--scale` feature.

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

This project includes a few more examples.  The most notable is `session_practical` that shows how someone might really use tmuxomatic.



## Notes

Although you don't have to know [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/) to use tmuxomatic, it is essential for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These features are extraneous to tmuxomatic and are typically added to your personalized `.tmux.conf` file.



## Copyright and License

Copyright 2013-2014, Oxidane.
All rights reserved.

Distributed under the [BSD 3-Clause license](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution of the source.  See the license for details.

