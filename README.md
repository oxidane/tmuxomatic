

# tmuxomatic [![](http://img.shields.io/pypi/v/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic) [![](http://img.shields.io/pypi/dm/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic)

Other tmux session managers define windows as a complicated nesting of pane splits and require pages of documentation.

Instead, tmuxomatic is so easy that anyone could use it after just one example, yet it's more flexible and more powerful than other tmux session managers.

At the heart of tmuxomatic is the **windowgram**, a better way of defining tmux windows.  The windowgram is a rectangle comprised of alphanumeric characters (0-9, a-z, A-Z).  Each character grouping identifies the name, position, size, and shape of a pane.  It should take only one example to demonstrate the flexibility and power of the windowgram.



## Learn by example

Compare this window from `session_example`, with its screenshot from `tmuxomatic session_example`:

	window example_one        # A new window begins like this, spaces in names allowed

	AAAAAAvvvvvXXXXXTTTT      # The windowgram, defines the shapes and positions of panes
	jjjQQQQQQQuuuuuuTTTT      # Make your own, any size and arrangement, 62 panes maximum
	jjjQQQQQQQuuuuuuTTTT
	jjjQQQQQQQuuuuuuTTTT
	0000llllllllllaaaaaa
	1234llllllllllaaaaaa

	  foc                     # Only three 3-letter commands: Focus, Directory, Run
	  dir ~                   # Unlinked directory is the default for all undefined panes
	A run figlet "A"          # Linked command to pane A, in this case prints a large "A"
	Q run figlet "Q"
	A foc

![](https://github.com/oxidane/tmuxomatic/blob/master/img/example.png)

With tmuxomatic, you'll never have to manually split, position, or size a pane again.  And linking the panes to actions is so simple and logical that you probably won't forget it.  There are no extra file format rules to remember, and typically no command line arguments will be necessary.

For a list of command line options, run `tmuxomatic --help`.

For additional features, see the included example sessions.



## Flex your windowgrams

Windowgrams are a neat way of arranging workspaces.  For simpler layouts, a windowgram is typed up quickly.  But if you need detail, you may find yourself doing a lot of ASCII art.  In tmuxomatic 2, *flex* was added to automate windowgram manipulation.

Flex is an object-oriented windowgram editor.  It is visually expressive, naturally worded, logically ordered, minimal, and powerful.  Its short command set may be combined to make any conceivable windowgram -- likely more quickly and more easily than crafting by hand.  Flex is intended for power users who desire detailed windowgrams without the tedium of manual entry.

Key concepts used by flex commands:

* **Pane**: Single character pane identifier representing one pane in a windowgram
* **Group**: String of one or more panes (usually in the form of a rectangle without gaps)
* **Edge**: String of panes that together border one or more edges (the imaginary line between panes)
* **Size**: Sizes are expressed in exact characters, or contextually as percentages or multipliers
* **Direction**: Cardinal directions (up, down, left, right), also used for windowgram and group edges

In the following demonstrations, the flex shell is represented by a simpler `flex>` prompt.

For a detailed list of commands, type `help` from the flex shell.



#### Flex demonstration #1 -- Create a new windowgram

Let's use flex to build a windowgram that would otherwise require a lot of typing.

This windowgram is intended for managing cryptocurrency nodes, specifically bitcoin, litecoin, and namecoin.  We'll have panes for: a general use shell (`1`), a disk monitor (`z`); and for each currency: a title with keep-alive loop on top (`B`, `L`, `N`), and blockchain information on bottom (`b`, `l`, `n`).

This the windowgram we will be creating:

	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn

Begin by opening the flex shell on the session file `session_flexample`.  Flex will create the session file for you if it does not already exist.

	% tmuxomatic session_flexample --flex

	flex>

First use the `new` command to create a new window named `wallets`.  By default, it will create a single pane window represented by the single character `1`.

	flex> new wallets

	1

From here it takes only four flex commands to complete the envisioned windowgram.

To make the window easier to work with, let's `scale` this windowgram to `25` characters wide, by `10` characters high.  Many flex parameters are flexible, instead of characters we could have used multipliers or percentages.

	flex> scale 25x10

	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111
	1111111111111111111111111

Now let's `add` a new pane on the `right` edge, and make it `50%` of the size of the base windowgram (or `12` characters, if you prefer).

	flex> add right 50%

	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000
	1111111111111111111111111000000000000

There are only two commands left to complete this.  And two ways to do it: one uses `split` and `break`, the other uses `break` and `join`.  We'll use break and join, because split is shown in the second demonstration.

So let's `break` pane `0` into a grid, `3` panes wide by `5` panes high.  For readability, we'll make use of the optional parameter so that new panes to start at `A`.

	flex> break 0 3x5 A

	1111111111111111111111111AAAABBBBCCCC
	1111111111111111111111111AAAABBBBCCCC
	1111111111111111111111111DDDDEEEEFFFF
	1111111111111111111111111DDDDEEEEFFFF
	1111111111111111111111111GGGGHHHHIIII
	1111111111111111111111111GGGGHHHHIIII
	1111111111111111111111111JJJJKKKKLLLL
	1111111111111111111111111JJJJKKKKLLLL
	1111111111111111111111111MMMMNNNNOOOO
	1111111111111111111111111MMMMNNNNOOOO

Finally we complete the envisioned layout using just one `join` command.  Each parameter represents a group of panes to be joined together.  By default, the joined name is that of the first pane in the group.  But we'll be using the optional rename, by appending `.` followed by the new pane id.

	flex> join ABC.z DG.B EH.L FI.N JM.b KN.l LO.n

	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn

That's it, our windowgram is ready for use.

Either type `done` and flex will open this session file in tmux, or type `exit` add some directions to the session file.  The directions specify run commands, home directories, and focus state.  For more information on directions, see the example session at the introduction of this readme.



#### Flex demonstration #2 -- Modify a windowgram

In this demonstration is presented in summary form.  It modifies the windowgram from the previous demonstration, using a different set of flex commands.

> Open the windowgram that we created in the above demonstration

	flex> use wallets

	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn
	1111111111111111111111111bbbbllllnnnn

> On pane `1`, split along `vertical` axis, `3` characters from the bottom, name the new panes `1` and `s`

	flex> split 1 vertical -3 1s

	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111BBBBLLLLNNNN
	1111111111111111111111111bbbbllllnnnn
	sssssssssssssssssssssssssbbbbllllnnnn
	sssssssssssssssssssssssssbbbbllllnnnn
	sssssssssssssssssssssssssbbbbllllnnnn

**NOTE: Flex is still in development, more will be added in future releases**

**TODO: rename, drag, swap, insert, clone, delete, mirror, flip**



## Installation

This application requires:

* [Python 3](http://www.python.org/getit/) +
* [tmux 1.8](http://tmux.sourceforge.net/) +

There are three ways to install tmuxomatic, in order of convenience:

  * **Automatically** (pip)

    * `pip-python3 install tmuxomatic`

  * **Manually** (python)

    * Download and extract the archive file from https://pypi.python.org/pypi/tmuxomatic
    * In the tmuxomatic directory, run `python3 setup.py install`

  * **From Development** (git)

    * Visit https://github.com/oxidane/tmuxomatic for up-to-date installation instructions
    * `git clone git://github.com/oxidane/tmuxomatic.git`
    * `cp -a tmuxomatic/tmuxomatic /usr/bin`

Verify that you have the current version installed: [![](http://img.shields.io/pypi/v/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic)

* `tmuxomatic -V`

On some systems pip may not upgrade properly, try clearing the pip cache prior to upgrade:

* `rm -rf /tmp/pip-build-root/tmuxomatic`
* `pip-python3 install tmuxomatic --upgrade --force`

Optional packages:

* `pip-python3 install pyyaml` ... For YAML session file support



## Notes

To use tmuxomatic, you don't have to know everything about [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/), but the knowledge is useful for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These are tmux user preferences, and typically placed in a personal `.tmux.conf` file.



## Copyright and License

Copyright 2013-2014, Oxidane.  All rights reserved.

Distributed under the [BSD 3-Clause License](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution of the source.  See the license for details.

