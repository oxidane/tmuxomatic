

# tmuxomatic [![](http://img.shields.io/pypi/v/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic)



A completely different kind of tmux session manager.

1. [Introduction](https://github.com/oxidane/tmuxomatic#introduction)
2. [Learn by example](https://github.com/oxidane/tmuxomatic#learn-by-example)
3. [Flex](https://github.com/oxidane/tmuxomatic#flex) ... ( i. [Concepts](https://github.com/oxidane/tmuxomatic#flex-concepts), ii. [Demo #1](https://github.com/oxidane/tmuxomatic#flex-demonstration-1----create-a-new-windowgram), iii. [Demo #2](https://github.com/oxidane/tmuxomatic#flex-demonstration-2----extend-the-windowgram) )
4. [Installation](https://github.com/oxidane/tmuxomatic#installation) ... ( i. [Requirements](https://github.com/oxidane/tmuxomatic#installation-requirements), ii. [Guide](https://github.com/oxidane/tmuxomatic#installation-guide), iii. [Optional packages](https://github.com/oxidane/tmuxomatic#optional-packages) )
5. [Notes on tmux](https://github.com/oxidane/tmuxomatic#notes-on-tmux)
6. [Contributor agreement](https://github.com/oxidane/tmuxomatic#contributor-agreement)
7. [Legal](https://github.com/oxidane/tmuxomatic#legal) ... ( i. [Copyright](https://github.com/oxidane/tmuxomatic#copyright), ii. [License](https://github.com/oxidane/tmuxomatic#license) )



## Introduction

Other tmux session managers require pages of documentation for basic use, and define windows as a complicated nesting of pane splits.  Instead, tmuxomatic is so easy that anyone could use it after just one example.  Yet tmuxomatic is more flexible and more powerful than other tmux session managers.

At the heart of tmuxomatic is the **windowgram**, a better way of arranging tmux windows.  The windowgram is a rectangle comprised of alphanumeric characters (0-9, a-z, A-Z).  Each character grouping identifies the name, position, size, and shape of a pane.  It should take only one example to demonstrate the power and flexibility of the windowgram.



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

![](https://raw.githubusercontent.com/oxidane/tmuxomatic/master/screenshots/screenshot_example.png)

With tmuxomatic, you'll never have to manually split, position, or size a pane again.  And linking the panes to actions is so simple and logical that you probably won't forget it.  There are no extra file format rules to remember, and typically no command line arguments will be necessary.

For additional features, see the included example sessions.  Or for a list of command line arguments, run `tmuxomatic --help`.



## Flex

Windowgrams are a neat way of arranging workspaces.  For simpler layouts, a windowgram is typed up quickly.  But if you need detail, you may find yourself doing a lot of ASCII art.

In tmuxomatic 2, **flex** was added to automate the construction and modification of the windowgram itself.

Flex is an object-oriented windowgram editor.  It is visually expressive, naturally worded, logically ordered, minimal, and powerful.  Its short command set may be combined to make any conceivable windowgram -- likely more quickly and more easily than crafting by hand.  Flex is intended for power users who desire detailed windowgrams without the tedium of manual entry.

#### Flex concepts

Before proceeding with the flex demonstration, take a moment to review the following key concepts.

  * **Pane**: Single character pane identifier representing one pane in a windowgram
  * **Group**: String of one or more panes (usually in the form of a rectangle without gaps)
  * **Edge**: String of panes that together border one or more edges (the imaginary line between panes)
  * **Size**: Expressed in exact characters, or contextually as a percentage or multiplier
  * **Direction**: Cardinal directions (up, down, left, right) for movement or to specify object edge

In the demonstrations below, the flex shell is represented by the `flex>` prompt.  For a detailed list of all flex commands, type `help` from the shell at any time.

#### Flex demonstration #1 -- Create a new windowgram

Let's use flex to build a windowgram that would otherwise require a lot of typing.

The following windowgram is what we will be creating in this demonstration.  This windowgram is intended for managing cryptocurrency nodes, specifically bitcoin, litecoin, and namecoin.  There are panes for a general use shell (`1`), a disk monitor (`z`); and for each currency: a title with keep-alive loop on top (`B`, `L`, `N`), and blockchain information on bottom (`b`, `l`, `n`).

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

**Scale**:

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

**Add**:

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

There are only two commands left to complete this, and two ways to do it.  One way uses `split` and `break`, the other uses `break` and `join`.  We'll use break and join, because split is shown in the next demonstration.

**Break**:

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

**Join**:

Finally we complete the envisioned layout using just one `join` command.  Each parameter represents a group of panes to be joined together.  By default, the first pane in the group becomes the joined name.  But we'll be using the optional rename, by appending `.` followed by the new pane id.

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

That's it.  Our windowgram is ready to use.

Either type `done` and flex will open this session file in tmux, or type `exit` and add some directions to the session file.  The directions specify run commands, home directories, and focus state.  For more information on directions, see the example session at the start of this readme.

#### Flex demonstration #2 -- Extend the windowgram

For this demonstration, we modify the windowgram from the previous demonstration, using a different set of flex commands.  The commands in this section are described in summary form.

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

**Split**:

> Split pane `1`, along `bottom`, exactly `3` characters, name the new pane `s`

	flex> split 1 bottom 3 s

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

**Rename**:

> Rename the panes `N` and `n`, to `D` and `d` respectively

	flex> rename Nn Dd

	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111zzzzzzzzzzzz
	1111111111111111111111111BBBBLLLLDDDD
	1111111111111111111111111BBBBLLLLDDDD
	1111111111111111111111111BBBBLLLLDDDD
	1111111111111111111111111BBBBLLLLDDDD
	1111111111111111111111111bbbblllldddd
	sssssssssssssssssssssssssbbbblllldddd
	sssssssssssssssssssssssssbbbblllldddd
	sssssssssssssssssssssssssbbbblllldddd

**Swap**:

> Swap pane `z` with `s`, also swap panes `Ll` with `Dd`.

	flex> swap z s Ll Dd

	1111111111111111111111111ssssssssssss
	1111111111111111111111111ssssssssssss
	1111111111111111111111111BBBBDDDDLLLL
	1111111111111111111111111BBBBDDDDLLLL
	1111111111111111111111111BBBBDDDDLLLL
	1111111111111111111111111BBBBDDDDLLLL
	1111111111111111111111111bbbbddddllll
	zzzzzzzzzzzzzzzzzzzzzzzzzbbbbddddllll
	zzzzzzzzzzzzzzzzzzzzzzzzzbbbbddddllll
	zzzzzzzzzzzzzzzzzzzzzzzzzbbbbddddllll

**Drag**:

> Drag the `left` edge of group `BDLbdl`, to the `left`, about `50%` of the available space.

	flex> drag left BDLbdl left 50%

	1111111111111ssssssssssssssssssssssss
	1111111111111ssssssssssssssssssssssss
	1111111111111BBBBBBBBDDDDDDDDLLLLLLLL
	1111111111111BBBBBBBBDDDDDDDDLLLLLLLL
	1111111111111BBBBBBBBDDDDDDDDLLLLLLLL
	1111111111111BBBBBBBBDDDDDDDDLLLLLLLL
	1111111111111bbbbbbbbddddddddllllllll
	zzzzzzzzzzzzzbbbbbbbbddddddddllllllll
	zzzzzzzzzzzzzbbbbbbbbddddddddllllllll
	zzzzzzzzzzzzzbbbbbbbbddddddddllllllll

**Insert**:

**Clone**:

**Delete**:

**Mirror**:

**Flip**:

**Rotate**:

*Flex is in development, these commands will be added in 2.x*



## Installation

#### Installation Requirements

This application requires the following:

  * [Python 3](http://www.python.org/getit/) +
  * [tmux 1.8](http://tmux.sourceforge.net/) +

#### Installation Guide

There are three ways to install tmuxomatic, in order of convenience:

  * **Automatically** (pip)

    * An upgrade may require an empty pip cache, `rm -rf /tmp/pip-build-root/`
    * `pip-python3 install tmuxomatic --upgrade`

  * **Manually** (python)

    * Download and extract the archive file from https://pypi.python.org/pypi/tmuxomatic
    * `cd tmuxomatic`
    * `python3 setup.py install`

  * **From Development** (git)

    * Visit https://github.com/oxidane/tmuxomatic for up-to-date installation instructions
    * Additional requirement for build [pandoc 1.12](http://johnmacfarlane.net/pandoc/) +
    * `git clone git://github.com/oxidane/tmuxomatic.git`
    * `cd tmuxomatic`
    * `pandoc -f markdown -t rst README.md -o README.rst`
    * `python3 setup.py install`

Verify that the version reported by `tmuxomatic -V` matches the latest release.  [![](http://img.shields.io/pypi/v/tmuxomatic.svg?style=flat)](https://pypi.python.org/pypi/tmuxomatic)

#### Optional Packages

The following packages are optional; install if you want the additional features.

  * `pip-python3 install pyyaml` ... YAML session file support



## Notes on tmux

To use tmuxomatic, you don't have to know everything about [how to use tmux](http://net.tutsplus.com/tutorials/tools-and-tips/intro-to-tmux/), but the knowledge is useful for [customizing the tmux status bar](http://me.veekun.com/blog/2012/03/21/tmux-is-sweet-as-heck/), or [changing the default key bindings](https://wiki.archlinux.org/index.php/tmux#Key_bindings).  These are tmux user preferences, and typically placed in a personal `.tmux.conf` file.



## Contributor agreement

Pull requests must be original source, or properly attributed public domain source.  By submitting, you agree that your contribution will inherit the current copyright and license, and will be subject to future changes in tmuxomatic and any officially-related projects.



## Legal

#### Copyright

Copyright 2013-2014, Oxidane.  All rights reserved.

#### License

The `windowgram` module is presently not licensed for use outside the tmuxomatic project.  For more information, including future plans for an open source license, please see the file `windowgram.py`.

The `tmuxomatic` source is distributed under the [BSD 3-Clause License](http://opensource.org/licenses/BSD-3-Clause).  The copyright and license must be included with any use, modification, or redistribution.  See the license for details.

