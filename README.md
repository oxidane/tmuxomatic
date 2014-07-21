

# tmuxomatic

Automated window layout and session management for tmux, with a simple definition file that is powerful and flexible.

<!-- [![Version](https://pypip.in/v/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic) [![Downloads](https://pypip.in/d/tmuxomatic/badge.png)](https://pypi.python.org/pypi/tmuxomatic) -->



## Requirements

* [Python 3](http://www.python.org/getit/)
* [tmux 1.8](http://tmux.sourceforge.net/) ... *Some earlier versions may work*



## Introduction

All it takes is a single two-window example session to know what tmuxomatic is and how it works.

From the file `session_example` (included in project):

	window a_simple_layout_of_3_panes
	112
	333
	333
	
	  dir ~
	1 run tail --follow=name /var/log/messages
	3 foc
	3 dir /tmp
	
	window a_complex_layout_of_25_panes
	AAAAAAAAAAAAVVVzz
	11200000000XXOozz
	34400000000XXIiyy
	55500000000YYYYyy
	abc00000000YYYYxx
	ddeeffqqqqqqqqZxx
	
	  foc
	  dir ~
	0 foc
	0 dir /tmp
	0 run ls -la
	Y run echo "boom"

Run the above session with `tmuxomatic session_example`.  The resulting screnshots:

TODO

If you've ever worked with tmux sessions, either manually or using some other tmux-related program, the simplicity and flexibility of tmuxomatic should now be obvious.



## Usage

The above example may be reproduced with: `tmuxomatic session_example`.

To reattach after a disconnection, simply run again: `tmuxomatic session_example`.

To force a session recreation, add `-r` or `--recreate`: `tmuxomatic session_example -r`.

For easier expansion of window layouts, use the scale option: `tmuxomatic session_example --scale 1 3x 2x`.

Finally, run `tmuxomatic --help` to get a full list of command line options.



## Examples

Many session examples are included.  The most practical is `session_practical`.  Other examples were created for testing purposes, or to demonstrate the limitations of tmux.  A complete description of the session file format may be found in `session_description`.



## Notes

Although you don't have to know [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/) to use tmuxomatic, it is essential for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These features are extraneous to tmuxomatic and are typically added to your personalized `.tmux.conf` file.

Latest version may be found here: [https://github.com/oxidane/tmuxomatic](https://github.com/oxidane/tmuxomatic).



## Copyright and License

Copyright 2013-2014, Oxidane
All rights reserved

Distributed under the [BSD 3-Clause license](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution of the source.  See the license for details.

