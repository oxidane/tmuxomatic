#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Copyright 2013-2014, Oxidane
All rights reserved

This source has NOT yet been licensed for redistribution, modification, or inclusion in other projects.

An exception has been granted to the official tmuxomatic project, originating from the following addresses:

    https://github.com/oxidane/tmuxomatic
    https://pypi.python.org/pypi/tmuxomatic

A proper open source license is expected to be applied sometime after the release of this windowgram module as a
separate project.  Please check this source at a later date for these changes.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

##----------------------------------------------------------------------------------------------------------------------
##
## Name ....... windowgram
## Synopsis ... Module for windowgram flex processing 1.x
## Author ..... Oxidane
## License .... (To Be Determined)
## Source ..... (To Be Announced)
##
##---------------+------------------------------------------------------------------------------------------------------
##     About     |
##---------------+
##
## The windowgram originated as the central concept in the tmuxomatic project.  It has since been expanded to include
## flex, a functional windowgram modification language using natural syntax and spatially oriented objects.
##
## Not ready to reveal the future plans for this project.  Check back for updates.
##
##--------------+-------------------------------------------------------------------------------------------------------
##     TODO     |
##--------------+
##
##      Implement the planned flex modifiers
##
##----------------------------------------------------------------------------------------------------------------------

import sys, argparse, re, math, copy, inspect, operator



##----------------------------------------------------------------------------------------------------------------------
##
## Definitions
##
## TODO: Move these into a class
##
##----------------------------------------------------------------------------------------------------------------------

# Panes Primary

PANE_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" # Official order "[0-9a-zA-Z]"
MAXIMUM_PANES   = len(PANE_CHARACTERS)  # 62 maximum panes (not windows)

# Panes Extended (these characters are never saved to file)

MASKPANE_X      = "."                   # Transparency pane id
MASKPANE_1      = "@"                   # Mask character: One
MASKPANE_0      = ":"                   # Mask character: Zero

PANE_CHAR_ALL   = "*"                   # Used as a windowgram reference in some flex commands
PANE_CHAR_COM   = "#"                   # Cannot be used: Session file stripped
PANE_CHAR_SPA   = " "                   # Cannot be used: Session file stripped

# Reserved panes

PANE_RESERVED   = MASKPANE_X + MASKPANE_1 + MASKPANE_0              # Valid ephemeral characters
PANE_RESERVED_X = PANE_CHAR_SPA + PANE_CHAR_COM + PANE_CHAR_ALL     # Invalid or used as wildcard



##----------------------------------------------------------------------------------------------------------------------
##
## Window splitter logic
##
## This converts a windowgram to a layout with split mechanics (tmux).
##
##----------------------------------------------------------------------------------------------------------------------

def SplitProcessor_SplitWindow( sw, dim, at_linkid, linkid, list_split, list_links, how, of_this ):
    """

    Splits the window 'at_linkid' along axis 'how'

    Variable 'how': 'v' = Vertical (new = below), 'h' = Horizontal (new = right)

    """

    def translate( pane, window, screen ):
        # Returns scaled pane according to windowgram and screen dimensions
        return int( float(pane) / float(window) * float(screen) )

    # Initialize
    at_tmux = ""
    for llit in list_links:
        if llit[0] == at_linkid:
            at_tmux = llit[1]
            break
    if at_tmux == "": return
    for llx, llit in enumerate(list_links):
        if llit[1] > at_tmux:
            list_links[llx] = ( llit[0], llit[1]+1 ) # Shift the index to accommodate new pane
    linkid[0] += 1
    this_ent = {}

    # The dimensions for the newly created window are based on the parent (accounts for the one character divider)
    for ent in list_split:
        if ent['linkid'] == at_linkid:
            this_ent = ent
            break
    if this_ent:
        if how == 'v':
            of_this = translate( of_this, dim['win'][1], dim['scr'][1] ) # From size-in-definition to size-on-screen
            w = this_ent['inst_w']
            h = of_this - 1
            per = str( float(of_this) / float(this_ent['inst_h']) * 100.0 )
            if sw['relative']:
                this_ent['inst_h'] = int(this_ent['inst_h']) - of_this # Subtract split from root pane
        else: # elif how == 'h':
            of_this = translate( of_this, dim['win'][0], dim['scr'][0] ) # From size-in-definition to size-on-screen
            w = of_this - 1
            h = this_ent['inst_h']
            per = str( float(of_this) / float(this_ent['inst_w']) * 100.0 )
            if sw['relative']:
                this_ent['inst_w'] = int(this_ent['inst_w']) - of_this # Subtract split from root pane

    # Split list tracks tmux pane number at the time of split (for building the split commands)
    list_split.append( { 'linkid':linkid[0], 'tmux':at_tmux, 'split':how, 'inst_w':w, 'inst_h':h, 'per':per } )

    # Now the new window's pane id, this is shifted up as insertions below it occur (see above)
    at_tmux += 1
    list_links.append( (linkid[0], at_tmux) )

def SplitProcessor_FindCleanBreak( sw, vertical, pos, list_panes, bx, by, bw, bh ):
    """

    Finds a split on an axis within the specified bounds, if found returns True, otherwise False.

    This shares an edge case with tmux that is an inherent limitation in the way that tmux works.
    For more information on this edge case, look over the example file "session_unsupported".

    Important note about the clean break algorithm used.  The caller scans all qualifying panes,
    then it uses each qualifying side as a base from which it calls this function.  Here we scan
    all qualifying panes to complete a match (see scanline).  If the result is a clean break,
    this function returns True, and the caller has the location of the break.  While there's room
    for optimization (probably best ported to C++, where the scanline technique will be really
    fast), it probably isn't needed since it's likely to be adequate even on embedded systems.

    """

    #-----------------------------------------------------------------------------------------------
    #
    # Outline: Clean Break Algorithm (1.0.1)
    # ~ Establish pointers
    # ~ Initialize scanline, used for detecting a clean break spanning multiple panes
    # ~ For each qualifying pane that has a shared edge
    #   ~ If shared edge overlaps, add it to the scanline
    #   ~ If scanline has no spaces, then a clean break has been found, return True
    # ~ Nothing found, return False
    #
    #-----------------------------------------------------------------------------------------------

    # Notify user
    if sw['scanline'] and sw['verbose'] >= 3:
        sw['print']("(3) Scanline: Find clean " + [ "horizontal", "vertical" ][vertical] + \
            " break at position " + str(pos))

    # ~ Establish pointers
    if vertical: sl_bgn, sl_siz = bx, bw # Vertical split is a horizontal line
    else:        sl_bgn, sl_siz = by, bh # Horizontal split is a vertical line

    # ~ Initialize scanline, used for detecting a clean break spanning multiple panes
    scanline = list(' ' * sl_siz) # Sets the scanline to spaces (used as a disqualifier)

    # ~ For each qualifying pane that has a shared edge
    for pane in list_panes:
        # Disqualifiers
        if 's' in pane: continue # Processed panes are out of bounds, all its edges are taken
        if pane['y'] >= by+bh or pane['y']+pane['h'] <= by: continue # Fully out of bounds
        if pane['x'] >= bx+bw or pane['x']+pane['w'] <= bx: continue # Fully out of bounds
        if     vertical and pane['y'] != pos and pane['y']+pane['h'] != pos: continue # No alignment
        if not vertical and pane['x'] != pos and pane['x']+pane['w'] != pos: continue # No alignment
        #   ~ If shared edge found, add it to the scanline
        if vertical: sl_pos, sl_len = pane['x'], pane['w'] # Vertical split is a horizontal line
        else:        sl_pos, sl_len = pane['y'], pane['h'] # Horizontal split is a vertical line
        if sl_pos < sl_bgn: sl_len -= sl_bgn - sl_pos ; sl_pos = sl_bgn # Clip before
        if sl_pos + sl_len > sl_bgn + sl_siz: sl_len = sl_bgn + sl_siz - sl_pos # Clip after
        for n in range( sl_pos - sl_bgn, sl_pos - sl_bgn + sl_len ): scanline[n] = 'X'
        # Show the scanline in action
        if sw['scanline'] and sw['verbose'] >= 3:
            sw['print']("(3) Scanline: [" + "".join(scanline) + "]: modified by pane " + pane['n'])
        #   ~ If scanline has no spaces, then a clean break has been found, return True
        if not ' ' in scanline: return True

    # ~ Nothing found, return False
    return False

def SplitProcessor_FillerRecursive( sw, dim, linkid, l_split, l_links, l_panes, this_linkid, bx, by, bw, bh ):
    """

    Once the panes have been loaded, this recursive function begins with the xterm dimensions.
    Note that at this point, all sizes are still in characters, as they will be scaled later.

        linkid[]        Single entry list with last assigned linkid number (basically a reference)
        l_split[{}]     List of splits and from which pane at the time of split for recreation
        l_links[()]     List of linkid:tmux_pane associations, updated when split occurs
        l_panes[{}]     List of fully parsed user-defined panes as one dict per pane
        this_linkid     The linkid of the current window
        bx, by, bw, bh  The bounds of the current window

    This algorithm supports all layouts supported by tmux.

    Possible improvement for more accurate positioning: Scan for the best possible split, as
    defined by its closest proximity to the top or left edges (alternatively: bottom or right).
    This has yet to be checked for the intended effect of producing more consistent sizing.

    """

    #-----------------------------------------------------------------------------------------------
    #
    # Outline: Filler Algorithm (1.0.1)
    # ~ If any available pane is a perfect fit, link to linkid, mark as processed, return
    # ~ Search panes for clean break, if found then split, reenter 1, reenter 2, return
    # ~ If reached, user specified an unsupported layout that will be detected by caller, return
    #
    #-----------------------------------------------------------------------------------------------

    def idstr( bx, by, bw, bh ):
        # Print the rectangle for debugging purposes.  Maybe change to use a rectangle class.
        return "Rectangle( x=" + str(bx) + ", y=" + str(by) + ", w=" + str(bw) + ", h=" + str(bh) + " )"

    v = True if sw['verbose'] >= 3 else False
    if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Enter")

    # ~ If any available pane is a perfect fit, link to linkid, mark as processed, return
    for pane in l_panes:
        # Disqualifiers
        if 's' in pane: continue                            # Skip processed panes
        # Perfect fit?
        if pane['x'] == bx and pane['y'] == by and pane['w'] == bw and pane['h'] == bh:
            if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + \
                ": Linking pane " + str(pane['n']) + " to " + str(this_linkid))
            pane['l'] = this_linkid
            pane['s'] = True # Linked to tmux[] / Disqualified from further consideration
            if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Exit")
            return

    # ~ Search panes for clean break, if found then split, reenter 1, reenter 2, return
    # This could be optimized (e.g., skip find_clean_break if axis line has already been checked)
    for pane in l_panes:
        # Disqualifiers
        if 's' in pane: continue # Processed panes are going to be out of bounds
        if pane['y'] >= by+bh or pane['y']+pane['h'] <= by: continue # Fully out of bounds
        if pane['x'] >= bx+bw or pane['x']+pane['w'] <= bx: continue # Fully out of bounds
        at = ""
        # Split at top edge?
        if pane['y'] > by:
            if SplitProcessor_FindCleanBreak( sw, True, pane['y'], l_panes, bx, by, bw, bh ):
                if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Split vert at top of pane " + str(pane['n']))
                at = pane['y']
        # Split at bottom edge?
        if pane['y']+pane['h'] < by+bh:
            if SplitProcessor_FindCleanBreak( sw, True, pane['y']+pane['h'], l_panes, bx, by, bw, bh ):
                if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Split vert at bottom of pane " + str(pane['n']))
                at = pane['y']+pane['h']
        # Perform vertical split
        if at:
            linkid_1 = this_linkid
            SplitProcessor_SplitWindow( sw, dim, this_linkid, linkid, l_split, l_links, 'v', bh-(at-by) )
            linkid_2 = linkid[0]
            SplitProcessor_FillerRecursive(sw, dim, linkid, l_split, l_links, l_panes, linkid_1, bx, by, bw, at-by)
            SplitProcessor_FillerRecursive(sw, dim, linkid, l_split, l_links, l_panes, linkid_2, bx, at, bw, bh-(at-by))
            if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Exit")
            return
        # Split at left edge?
        if pane['x'] < bx:
            if SplitProcessor_FindCleanBreak( sw, False, pane['x'], l_panes, bx, by, bw, bh ):
                if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Split horz at left of pane " + str(pane['n']))
                at = pane['x']
        # Split at right edge?
        if pane['x']+pane['w'] < bx+bw:
            if SplitProcessor_FindCleanBreak( sw, False, pane['x']+pane['w'], l_panes, bx, by, bw, bh ):
                if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Split horz at right of pane " + str(pane['n']))
                at = pane['x']+pane['w']
        # Perform horizontal split
        if at:
            linkid_1 = this_linkid
            SplitProcessor_SplitWindow( sw, dim, this_linkid, linkid, l_split, l_links, 'h', bw-(at-bx) )
            linkid_2 = linkid[0]
            SplitProcessor_FillerRecursive(sw, dim, linkid, l_split, l_links, l_panes, linkid_1, bx, by, at-bx, bh)
            SplitProcessor_FillerRecursive(sw, dim, linkid, l_split, l_links, l_panes, linkid_2, at, by, bw-(at-bx), bh)
            if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": Exit")
            return

    # ~ If reached, user specified an unsupported layout that will be detected by caller, return
    if v: sw['print']("(3) " + idstr(bx, by, bw, bh) + ": No match found, unsupported layout")
    return

def SplitProcessor( sw, wg, iw, ih, list_panes ): # list_split, list_links
    #
    # Split window into panes
    #
    linkid = [ 1001 ]   # Incrementing number for cross-referencing (0 is reserved)
    # The linkid number is a unique identifier used to track the tmux panes and cross-reference them when the
    # window is fully divided to get the final pane index for a particular pane.  This is an essential link
    # because panes are renumbered as splits occur, and before they're assigned to tmuxomatic pane ids.
    # Note: 'inst_w' and 'inst_h' are the dimensions when split, the first pane uses full dimensions.
    # Note: The first pane does not use the entires 'split' or 'tmux'.
    list_split = [ { 'linkid': linkid[0], 'split': "", 'tmux': 65536, 'inst_w': iw, 'inst_h': ih, 'per': "100.0" } ]
    list_links = [ ( linkid[0], 0 ) ]   # List of cross-references (linkid, pane_tmux)
    # Run the recursive splitter
    windowgram_w, windowgram_h = wg.Analyze_WidthHeight() # TODO: Clean up remaining wg inlines
    dim = {}
    dim['win'] = [ windowgram_w, windowgram_h ]
    dim['scr'] = [ iw, ih ]
    SplitProcessor_FillerRecursive( \
        sw, dim, linkid, list_split, list_links, list_panes, linkid[0], 1, 1, windowgram_w, windowgram_h )
    # Return useful elements
    return list_split, list_links



##----------------------------------------------------------------------------------------------------------------------
##
## Windowgram miscellaneous
##
##----------------------------------------------------------------------------------------------------------------------

def SortPanes(layout): # list_panes, layout
    # Sort top to bottom, left to right, move into list (layout[] -> list_panes[])
    list_panes = [] # List of user defined panes (derived from windowgram)
    while len(layout):
        pane = ""
        for it in layout:
            if not pane: pane = it
            elif layout[it]['y'] < layout[pane]['y']: pane = it
            elif layout[it]['y'] == layout[pane]['y'] and layout[it]['x'] < layout[pane]['x']: pane = it
        list_panes.append(layout[pane].copy())  # Add to list
        del layout[pane]                        # Remove from dict
    return list_panes, layout

def PaneOverlap(list_panes): # overlap_pane1, overlap_pane2
    # Finds the first overlap and returns it
    for pane1 in list_panes:
        for pane2 in list_panes:
            if pane1 != pane2:
                # Readability
                p1x1 = pane1['x']
                p1x2 = p1x1 + pane1['w']
                p1y1 = pane1['y']
                p1y2 = p1y1 + pane1['h']
                p2x1 = pane2['x']
                p2x2 = p2x1 + pane2['w']
                p2y1 = pane2['y']
                p2y2 = p2y1 + pane2['h']
                # Overlap detection
                if p1x1 < p2x2 and p1x2 > p2x1 and p1y1 < p2y2 and p1y2 > p2y1:
                    return pane1['n'], pane2['n']
    return None, None



##----------------------------------------------------------------------------------------------------------------------
##
## Windowgram class
##
## Interface for the general-purpose use of windowgram data.  Instances of this class should use the name wg.
##
## Note: Most algorithms do not account for windowgrams of varying widths (e.g., "12\n123\n").  Such windowgrams are
## considered invalid in most cases, and where affective they should be fixed or rejected prior to use.
##
## TODO:
##
##          Update all uses of windowgram to use a wg instance, instead of instantiating to use a method
##          Move splitter code into this library, it's used for windowgram compatibility detection
##          Move flex commands into this class, or an accompanying class, free of shell interface concerns
##          Move this class into a library for use in other applications
##
##----------------------------------------------------------------------------------------------------------------------
##
## Windowgram Formats:
##
##      The user deals with the raw format, all other formats are used internally for processing.
##
##      ------- -------------------------- ------------------ --------------------------------------------------------
##      Data    Example Value              Variable           Description
##      ------- -------------------------- ------------------ --------------------------------------------------------
##      Raw     "12\n34 # etc\n"           windowgram_raw     The file input and output, may have spaces or comments
##      String  "12\n34\n"                 windowgram_string  Stripped lines delimited by "\n", no spaces or comments
##      Lines   [ "12", "34" ]             windowgram_lines   List of lines, pure windowgram data (no delimiters)
##      Chars   [['1', '2'], ['3', '4']]   windowgram_chars   List of chars, pure windowgram data (no delimiters)
##      Parsed  {'a': {'x': 1, ...}, ...}  windowgram_parsed  Processed dictionary of panes with keys: n, x, y, w, h
##      Mosaic  (base, [[ w, m ], ...])    windowgram_mosaic  Pairs of windowgram and mask, ordered bottom to top
##      ------- -------------------------- ------------------ --------------------------------------------------------
##
##----------------------------------------------------------------------------------------------------------------------
##
## Windowgram Groups:
##
##      1                   SPLIT ... 1 windowgram, 1 pane
##
##      112...              TILED ... 1 windowgram, 5 panes, transparency
##      452...
##      433...
##
##      1222 444. ....      LAYERED ... 3 windowgrams, 5 panes, implicit overlaps, explicit overlaps, transparency
##      3333 444. .555
##      3333 .... .555
##
##----------------------------------------------------------------------------------------------------------------------
##
## Pane arrangement types:
##
##      Name                    Example     Description
##      ----------------------- ----------- ------------------------------------------------------------------------
##      Implicit Overlaps       12          Pane 1 overlaps pane 2, this is an implicit overlap
##                              22
##
##      Explicit Overlaps       11 22       Pane 2 overlaps pane 1, explicit implies multiple layers are used
##                              11 22
##
##      Positioned              112         These panes cannot be defined using nested splits, however these are
##                              452         valid in other environments where explicit positioning is possible
##                              433
##      ----------------------- ----------- ------------------------------------------------------------------------
##
##----------------------------------------------------------------------------------------------------------------------
##
## Support analysis types:
##
##      Name     Support        Description
##      -------- -------------- -------------------------------------------------------------------------------------
##      split    tmux, ???, os  Fully split compatible, no overlaps of either kind, no positioned panes
##      tiled    ???, os        No overlaps, supports positioned panes, not bound to a split mechanism for layout
##      layered  os             Has one or more layers with implicit overlaps and/or explicit overlaps
##      -------- -------------- -------------------------------------------------------------------------------------
##
## The "???" represents a hypothetical console-based tmux-like system with more flexible positioning.  Not necessarily
## with overlap like a typical graphical user interface, though if it did it would then by extension support layered
## windowgrams.  Does dvtm support positioning?
##
##----------------------------------------------------------------------------------------------------------------------

linestrip = lambda line: (line[:line.find("#")] if line.find("#") >= 0 else line).strip()

##
## To support masking, an extended set of pseudo-panes must be recognized as valid within windowgram class methods
##

def ValidPane(ch, extend=False): return True if (ch in PANE_CHARACTERS or (extend and ch in PANE_RESERVED)) else False
def ValidPanes(extend=False): return (PANE_CHARACTERS + PANE_RESERVED) if extend else PANE_CHARACTERS
def AllPanes(this, used, extend=False): return "".join(list(set([ch for ch in (this+used) if ValidPane(ch, True)])))

##
## Windowgram Format Conversions
##

class Windowgram_Convert():

    ## String <-> Lines ... windowgram_lines == [ "12", "34", ... ]

    @staticmethod
    def String_To_Lines(windowgram):
        return [ linestrip(line) for line in list(filter(None, (windowgram+"\n").split("\n"))) ] # No blank lines

    @staticmethod
    def Lines_To_String(windowgram_lines):
        return "\n".join([ line for line in windowgram_lines ]) + "\n" # Each line has one \n

    ## String <-> Chars ... windowgram_chars == [ ['1', '2'], ['3', '4'], ... ]

    @staticmethod
    def String_To_Chars(windowgram):
        # A list of lists, each containing one or more single characters representing a line, strips empty runs
        return [ r for r in [ [ ch for ch in list(ln) ] for ix, ln in enumerate(windowgram.split("\n")[:-1]) ] if r ]

    @staticmethod
    def Chars_To_String(windowgram_chars):
        return Windowgram_Convert.Lines_To_String( [ "".join(line_chars) for line_chars in windowgram_chars ] )

    ## String <-> Parsed ... windowgram_parsed == { 'Q': { 'n': 'Q', 'x': 1, 'y': 1, 'w': 1, 'h': 1  }, ... }

    @staticmethod
    def String_To_Parsed(windowgram, extend=False): # windowgram_parsed, error_string, error_line
        windowgram_lines = Windowgram_Convert.String_To_Lines(windowgram)
        windowgram_parsed = {}
        panes_y = 0 # Line number
        try:
            panes_x = panes_y = width = 0
            for ix, line in enumerate(windowgram_lines):
                if not line: continue
                panes_y += 1
                panes_x = 0
                for ch in line:
                    if not ValidPane(ch, extend):
                        raise Exception("Windowgram must contain valid identifiers: [0-9a-zA-Z]")
                if panes_y > 1 and len(line) != width:
                    raise Exception("Windowgram width does not match previous lines")
                else:
                    if width == 0: width = len(line)
                    for ch in line:
                        panes_x += 1
                        if not ValidPane(ch, extend):
                            raise Exception("Windowgram must contain valid identifiers: [0-9a-zA-Z]")
                        # Builds "bounding box" around pane for easy error detection through overlap algorithm
                        if not ch in windowgram_parsed:
                            # New pane
                            windowgram_parsed[ch] = { 'n': ch, 'x': panes_x, 'y': panes_y, 'w': 1, 'h': 1 }
                        else:
                            # Expand width
                            x2 = panes_x - windowgram_parsed[ch]['x'] + 1
                            if x2 > windowgram_parsed[ch]['w']:
                                windowgram_parsed[ch]['w'] = x2
                            # Expand height
                            y2 = panes_y - windowgram_parsed[ch]['y'] + 1
                            if y2 > windowgram_parsed[ch]['h']:
                                windowgram_parsed[ch]['h'] = y2
                            # Update x
                            if windowgram_parsed[ch]['x'] > panes_x:
                                windowgram_parsed[ch]['x'] = panes_x
            if not windowgram_parsed: raise Exception("Windowgram not specified")
        except Exception as error:
            return None, str(error), panes_y
        return windowgram_parsed, None, None

    @staticmethod
    def Parsed_To_String(windowgram_parsed): # windowgram_string
        # TODO: Probably should do error handling
        windowgram_list = []
        for paneid in windowgram_parsed.keys():
            pane = windowgram_parsed[paneid]
            for y in range( pane['y'], pane['y'] + pane['h'] ):
                for x in range( pane['x'], pane['x'] + pane['w'] ):
                    ix = int(x) - 1
                    iy = int(y) - 1
                    while len(windowgram_list) <= iy: windowgram_list.append([])
                    while len(windowgram_list[iy]) <= ix: windowgram_list[iy].append([])
                    windowgram_list[iy][ix] = pane['n']
        windowgram_string = ""
        for line in windowgram_list:
            windowgram_string += "".join(line) + "\n"
        return windowgram_string

    ## String <-> Mosaic ... windowgram_mosaic == ( wg_base, [ [ wg_data, wg_mask ], [ wg_data, wg_mask ], ... ] )

    @staticmethod
    def String_To_Mosaic(windowgram_string, mask_string_list): # windowgram_mosaic
        # Implemented for reference only; actual production cases are custom implementations of flex commands
        windowgram_pairs = []
        wg = Windowgram(windowgram_string)
        for mask_string in mask_string_list:
            pair_w = Windowgram( wg.Export_String() )
            panes = pair_w.Panes_FromMask( mask_string )
            used, unused = pair_w.Panes_GetUsedUnused()
            strip = "".join( [ pane for pane in list(used) if pane not in list(panes) ] )
            used, unused = PaneList_MovePanes( used, unused, strip )
            pair_w.Panes_Renamer( unused, "." )
            windowgram_pairs.append( [ pair_w, Windowgram(mask_string) ] )
        windowgram_mosaic = [ Windowgram(windowgram_string), windowgram_pairs ]
        return windowgram_mosaic

    @staticmethod
    def Mosaic_To_String(windowgram_mosaic): # windowgram_string
        # Merges pairs of [ wg_data, wg_mask ] onto wg_base, ordered bottom to top
        wg_base, pairs = windowgram_mosaic
        s_l = wg_base.Export_Lines()    # Source
        for w, m in pairs:
            t_l = w.Export_Lines()      # Target
            m_l = m.Export_Lines()      # Mask
            w_l, s_l = s_l, []          # Work
            for iy in range(len(w_l)):
                line = ""
                for ix in range(len(w_l[iy])): line += w_l[iy][ix] if m_l[iy][ix] != MASKPANE_1 else t_l[iy][ix]
                s_l.append(line)
        return Windowgram_Convert.Lines_To_String( s_l )

    ## String -> Lines -> String ... Full cycle purification of the windowgram by stripping comments and whitespace

    @staticmethod
    def Purify(windowgram):
        return Windowgram_Convert.Lines_To_String( Windowgram_Convert.String_To_Lines( windowgram ) )

    ## Transpose Chars ... Swaps columns and rows, essentially mirror ccw90

    @staticmethod
    def Transpose_Chars(windowgram_chars):
        windowgram_chars_transposed = []
        for x in range( len(windowgram_chars[0]) ):
            windowgram_chars_transposed += [ [ windowgram_chars[y][x] for y in range( len(windowgram_chars) ) ] ]
        return windowgram_chars_transposed

    ## Transpose Pane ... Swaps [x with y] and [w with h] in a parsed pane (dict entry of windowgram_parsed)

    @staticmethod
    def Transpose_Pane(windowgram_parsedpane):
        windowgram_parsedpane_transposed = copy.deepcopy( windowgram_parsedpane )
        windowgram_parsedpane_transposed['x'], windowgram_parsedpane_transposed['y'] = \
        windowgram_parsedpane_transposed['y'], windowgram_parsedpane_transposed['x']
        windowgram_parsedpane_transposed['w'], windowgram_parsedpane_transposed['h'] = \
        windowgram_parsedpane_transposed['h'], windowgram_parsedpane_transposed['w']
        return windowgram_parsedpane_transposed

##
## Mosaics Equal ... Used for comparison purposes in testing, would not be needed if windowgram_mosaic used strings
##

def Mosaics_Equal(windowgram_mosaic_1, windowgram_mosaic_2): # True if equal else False
    if windowgram_mosaic_1[0] != windowgram_mosaic_2[0]: return False
    for m1, m2 in zip( windowgram_mosaic_1[1], windowgram_mosaic_2[1] ):
        if m1 != m2: return False # Necessitates Windowgram.__eq__()
    return True

##
## Windowgram Group Conversions
##
##      WindowgramGroupPattern      Single string of 1 or more packed windowgrams with arbitrary padding
##                                  This pattern must be horizontally aligned to accommodate differently sized panes
##                                  See flex unit testing for examples of properly constructed objects
##
##      WindowgramGroupList         List of strings, where each string is a windowgram with optional padding
##                                  Basically just a list of windowgram_string objects
##

class WindowgramGroup_Convert():

    ## Pattern <-> List

    @staticmethod
    def Pattern_To_List(windowgramgroup_pattern):
        windowgramgroup_list = []
        first_linewithcol = []
        for line in windowgramgroup_pattern.split("\n"):
            if not line.strip(): first_linewithcol = []
            else:
                # Build list of lines according to starting column of character run
                #       * Discard any out-of-bounds character runs (as defined by first line)
                #       * Insert blank lines where no runs were found
                def colsplit(line): # linewithcol
                    linewithcol = [] # [ (line, col), ... ]
                    for col, ch in enumerate(list(line)): # Never strip the line or this will fail: "1 2\n  2\n"
                        if ch == " " or ch == "\t" or not linewithcol:
                            if not linewithcol or linewithcol[-1][0]: linewithcol.append(["", None])
                        if ch != " " and ch != "\t":
                            if linewithcol[-1][1] is None: linewithcol[-1][1] = col
                            linewithcol[-1][0] += ch
                    return linewithcol
                linewithcol = colsplit(line)
                # Refine list using first line as a guide.  This will insert columns that are missing and remove
                # columns that do not match the title.  Each windowgram line must match the one before it, or it's
                # dropped, so a user must take care in editing windowgramgroup_pattern objects or data disappears.
                # TODO: Slightly more sophisticated matching that will compensate for unaligned windowgrams by
                # snapping to the nearest column; this is just be an estimate, user error loss is still possible.
                if first_linewithcol:
                    # Strip columns with unexpected positions
                    drop = []
                    for ix1, (_, col1) in enumerate(linewithcol):
                        ix2 = [ ix2 for ix2, (_, col2) in enumerate(first_linewithcol) if col2 == col1 ]
                        if not ix2: drop.append(ix1)
                    for ix in reversed(drop): linewithcol.pop(ix)
                    # Insert missing columns
                    for ix1, (_, col1) in enumerate(first_linewithcol):
                        if not [ (ix2, col2) for ix2, (_, col2) in enumerate(linewithcol) if col2 == col1 ]:
                            linewithcol.insert( ix1, ["", col1] )
                # First line expands the collation list
                if not first_linewithcol:
                    first_linewithcol = linewithcol
                    for n in range(len(first_linewithcol)): windowgramgroup_list.append([])
                # Insert lines into the collation list
                linewithcol = linewithcol[:len(first_linewithcol)] # Assure truncation
                for n in range(len(first_linewithcol)):
                    windowgramgroup_list[-(len(first_linewithcol)-n)].append(linewithcol[n][0])
        # Return as list of windowgrams with blank lines removed
        windowgramgroup_list = [ "\n".join([ l2 for l2 in l if l2 ])+"\n" for ix, l in enumerate(windowgramgroup_list) ]
        return [ _ for _ in windowgramgroup_list if _ != "\n" ]

    @staticmethod
    def List_To_Pattern(windowgramgroup_list, maxwidth, lpad=0, mpad=1, testmode=False):
        windowgramgroup_pattern = ""
        windowgram_line_arr = []
        windowgram_width_arr = []
        # Build arrays of lines and widths
        for windowgram_string in windowgramgroup_list:
            windowgram_lines = Windowgram_Convert.String_To_Lines( windowgram_string )
            windowgram_line_arr.append( windowgram_lines )
            windowgram_width_arr.append( list( reversed( sorted( [ len(line) for line in windowgram_lines ] ) ) )[0] )
        spent = 0
        while spent < len(windowgram_width_arr):
            # Determine how many of the remaining windowgrams will fit on this windowgramgroup row
            tmplen = lpad + windowgram_width_arr[spent]
            spending = spent
            spent += 1
            while spent < len(windowgram_width_arr):
                tmplen += mpad + windowgram_width_arr[spent]
                if tmplen > maxwidth: break
                spent += 1
            # Skip line between windowgram runs
            if windowgramgroup_pattern: windowgramgroup_pattern += "\n"
            # Vertically pad the windowgrams for zip iteration
            batch = windowgram_line_arr[spending:spent]
            height = list( reversed( sorted( [ len(lines) for lines in batch ] ) ) )[0]
            batch = [ lines if len(lines) >= height else lines + ([" "]*(height-len(lines))) for lines in batch ]
            # Print this windowgramgroup row
            for ix in range( height ):
                row = [ lines[ix] if len(lines[ix]) >= windowgram_width_arr[spending+ix2] \
                    else lines[ix] + (" "*(windowgram_width_arr[spending+ix2]-len(lines[ix]))) \
                    for ix2, lines in enumerate( batch ) ]
                windowgramgroup_pattern = windowgramgroup_pattern + (" "*lpad) + ((" "*mpad).join(row)) + "\n"
        # Strip blank spaces from end of line
        windowgramgroup_pattern = "\n".join( [ line.rstrip() for line in windowgramgroup_pattern.split("\n") ] )
        # For ease of testing, add newline prefix and padding suffix of specified length
        if testmode is not False:
            windowgramgroup_pattern = "\n" + windowgramgroup_pattern + (" "*testmode)
        return windowgramgroup_pattern

##
## Windowgram
##
## Error handling is done by polling GetErrorPair() after calling an error-generating method
##

class Windowgram():

    def __init__(self, windowgram_raw, extend=False):
        # Mask mode (extend parameter) should only be enabled here to avoid type uncertainty
        self.extend = extend # For masking
        self.change_count = 0
        self.change_query = 0
        self.Import_Raw(windowgram_raw)
        self.NoChange()

    def __eq__(self, other):
        # Needed by Mosaics_Equal()
        return True if self.Export_String() == other.Export_String() else False

    def Reset(self):
        self.windowgram_string = None
        self.error_string = None
        self.error_line = 0
        self.change_count += 1

    def GetErrorPair(self): # Resets error when polled.  Returns: error_string, error_line
        error_string = self.error_string
        error_line = self.error_line
        self.error_string = None
        self.error_line = 0
        return error_string, error_line

    def Is_Extended(self):
        return self.extend

    ##
    ## Loaders
    ##

    def Load_Chars(self, windowgram_chars):
        self.Import_Chars(windowgram_chars)
        return self
    def Load_Parsed(self, windowgram_parsed):
        self.Import_Parsed(windowgram_parsed)
        return self

    ##
    ## Imports
    ##

    def Import_Raw(self, windowgram_raw):
        self.Reset()
        self.windowgram_string = Windowgram_Convert.Purify( windowgram_raw ) # Strip comments and whitespace
        self.Changed()
    def Import_String(self, windowgram_string):
        return self.Import_Raw( windowgram_string )
    def Import_Lines(self, windowgram_lines):
        return self.Import_Raw( Windowgram_Convert.Lines_To_String(windowgram_lines) )
    def Import_Chars(self, windowgram_chars):
        return self.Import_Raw( Windowgram_Convert.Chars_To_String(windowgram_chars) )
    def Import_Parsed(self, windowgram_parsed):
        return self.Import_Raw( Windowgram_Convert.Parsed_To_String(windowgram_parsed) )
    def Import_Mosaic(self, windowgram_mosaic):
        return self.Import_Raw( Windowgram_Convert.Mosaic_To_String(windowgram_mosaic) )
    def Import_Wg(self, wg):
        return self.Import_Raw( wg.Export_String() )

    ##
    ## Exports ... The windowgram is only converted upon request
    ##

    def Export_String(self):
        return self.windowgram_string
    def Export_Lines(self):
        return Windowgram_Convert.String_To_Lines( self.windowgram_string )
    def Export_Chars(self):
        return Windowgram_Convert.String_To_Chars( self.windowgram_string )
    def Export_Parsed(self): # Generates error
        windowgram_parsed, error_string, error_line = \
            Windowgram_Convert.String_To_Parsed( self.windowgram_string, self.extend )
        if error_string:
            windowgram_parsed = {}
            self.error_string = error_string
            self.error_line = error_line
        return windowgram_parsed
    def Export_Mosaic(self): # Generates error
        windowgram_mosaic = []
        self.error_string = "Not implemented"
        self.error_line = 0
        return windowgram_mosaic

    ##
    ## Analyze windowgram for metrics and supportability, performed on demand
    ##

    @staticmethod
    def Analyze_WidthHeight_Static(windowgram_lines):
        return [ (max([ len(line) for line in windowgram_lines ]) if windowgram_lines else 0), len( windowgram_lines ) ]
    def Analyze_WidthHeight(self):
        windowgram_lines = Windowgram_Convert.String_To_Lines( self.windowgram_string )
        return Windowgram.Analyze_WidthHeight_Static( windowgram_lines )
    def Analyze_IsBlank(self):
        return True if not max(self.Analyze_WidthHeight()) else False
    def Analyze_Layers(self):
        return 1 # Fixed for now
    def Analyze_Type(self, relative):
        # Determine compatibility (split, tiled, layered)
        analysis_type = ""
        while True:
            # Detect layered
            windowgram_parsed, error, _ = Windowgram_Convert.String_To_Parsed( self.windowgram_string )
            if error:
                analysis_type = "ERROR"
                break
            list_panes, windowgram_parsed = SortPanes( windowgram_parsed )
            overlap_pane1, overlap_pane2 = PaneOverlap( list_panes )
            if overlap_pane1 or overlap_pane2:
                analysis_type = "layered" # Implicit
                break
            # Detect split
            sw = { 'print': None, 'verbose': 0, 'relative': relative, 'scanline': False } # No print
            list_split, list_links = SplitProcessor( sw, self, 1024, 1024, list_panes ) # Avoid layout errors
            splityes = True
            for split in list_split:
                #
                # Readability
                #
                list_split_linkid = split['linkid']     # 1234          This is for cross-referencing
                ent_panes = ''
                for i in list_panes:
                    if 'l' in i and i['l'] == split['linkid']:
                        ent_panes = i
                        break
                if not ent_panes:
                    splityes = False
                    break
            if splityes:
                analysis_type = "split"
                break
            # Assume tiled
            analysis_type = "tiled"
            break
        return analysis_type

    ##
    ## Change Detection (has change_count been incremented since last query)
    ##

    def Changed(self): self.change_count += 1
    def NoChange(self): self.change_query = self.change_count
    def HasChanged_SenseOnly(self): return True if self.change_count == self.change_query else False
    def HasChanged(self): flag = self.HasChanged_SenseOnly() ; NoChange() ; return flag

    ##
    ## Pane / Panes
    ##

    def Panes_GetUsedUnused(self): # used, unused
        # Mutually exclusive list of pane ids for given windowgram
        windowgram_lines = Windowgram_Convert.String_To_Lines( self.windowgram_string )
        used = "".join( sorted( list(set(list("".join(windowgram_lines)))), 
            key=lambda x: ValidPanes(self.extend).find(x) ) )
        unused = "".join( [ paneid for paneid in ValidPanes(self.extend) if paneid not in used ] )
        return used, unused

    def Panes_GetNewPaneId(self, preferred=None): # newpaneid, error
        # Input preferred: None == First available pane / paneid == Specified if valid
        used, unused = self.Panes_GetUsedUnused()
        if not unused: return None, "All pane identifiers have been used"
        if preferred is None: return unused[0], None
        if preferred not in ValidPanes(self.extend): return None, "Invalid pane identifier"
        if preferred not in unused: return None, "Pane id `" + preferred + "` is in use"
        return preferred, None

    def Panes_HasPane(self, pane):
        for line in Windowgram_Convert.String_To_Lines( self.windowgram_string ):
            for ch in line:
                if ch == pane: return True
        return False

    def Panes_PaneXYXY(self, pane): # x1, y1, x2, y2
        if not self.Panes_HasPane( pane ): return 0, 0, 0, 0
        windowgram_lines = Windowgram_Convert.String_To_Lines( self.windowgram_string )
        x2 = y2 = -1
        x1 = len(windowgram_lines[0])
        y1 = len(windowgram_lines)
        for y, line in enumerate(windowgram_lines):
            for x, char in enumerate(line):
                if char == pane:
                    if x < x1: x1 = x
                    if x > x2: x2 = x
                    if y < y1: y1 = y
                    if y > y2: y2 = y
        return x1+1, y1+1, x2+1, y2+1

    def Panes_PaneXYWH(self, pane): # x, y, w, h
        if not self.Panes_HasPane( pane ): return 0, 0, 0, 0
        x1, y1, x2, y2 = self.Panes_PaneXYXY( pane )
        return x1, y1, x2-x1+1, y2-y1+1

    def Panes_Renamer(self, panes, pane):
        # Supports multiple panes renaming, use only when you know the results will be valid
        new_lines = []
        for line in Windowgram_Convert.String_To_Lines( self.windowgram_string ):
            new_lines.append( "".join( [ (ch if ch not in panes else pane) for ch in line ] ) )
        self.Import_Lines( new_lines )

    def Panes_FromMask(self, mask_string):
        # Returns unique panes covered by specified mask
        lines_w = Windowgram_Convert.String_To_Lines( self.windowgram_string )
        lines_m = Windowgram_Convert.String_To_Lines( mask_string )
        panes = "".join( set( \
            [ ch_w for ch_w, ch_m in zip( "".join(lines_w), "".join(lines_m) ) if ch_m == MASKPANE_1 ] ) )
        return panes

    def Panes_Exist(self):
        # True if any panes exist, including transparency
        return True if Windowgram_Convert.String_To_Lines( self.windowgram_string ) != [] else False

    ##
    ## Edge
    ##

    def Edge_PanesAlong(self, axis, edge):
        # Returns a unique unsorted set of panes that touch the edge on either side
        windowgram_chars = Windowgram_Convert.String_To_Chars( self.windowgram_string )
        if axis == "v": windowgram_chars = Windowgram_Convert.Transpose_Chars( windowgram_chars )
        panes = "".join( set( (windowgram_chars[edge-1] if edge > 0 else []) +
                              (windowgram_chars[edge] if edge+1 < len(windowgram_chars) else []) ) )
        return panes

    @staticmethod
    def Edge_Extract_Static(windowgram_lines, axis, edge, direction):
        # Returns a string of characters that border the one side of the edge that is opposite the direction
        wgw, wgh = Windowgram.Analyze_WidthHeight_Static( windowgram_lines )
        # Note special cases (effectively "drag r * l 1" and "drag l * r 1") return transparency since those edges
        # are completely out of range.  The smudgecore caller translates this transparency into a subtraction.
        if axis == "v":
            if (direction == "" and edge == wgw) or (direction == "-" and edge == 0): return MASKPANE_X * wgh
            return "".join( [ line[edge-1 if direction == "-" else edge] for line in windowgram_lines ] )
        else: # if axis == "h":
            if (direction == "" and edge == wgh) or (direction == "-" and edge == 0): return MASKPANE_X * wgw
            return windowgram_lines[edge-1 if direction == "-" else edge]

    def Edge_Extract(self, axis, edge, direction):
        # Returns a string of characters that border the one side of the edge that is opposite the direction
        windowgram_lines = Windowgram_Convert.String_To_Lines( self.windowgram_string )
        return Windowgram.Edge_Extract_Static( windowgram_lines, axis, edge, direction )

    def Edge_ClipOuterTransparents(self):
        # Any fully transparent lines on any outer edge are clipped entirely
        wgc = self.Export_Chars()
        wgx1, wgy1, (wgx2, wgy2) = 1, 1, self.Analyze_WidthHeight()
        wgx2 -= 1 ; wgy2 -= 1 # Aligns edges so they may be extracted directionally
        while wgx1-1 <= wgx2 and set(Windowgram.Edge_Extract_Static( wgc, "v", wgx1, "-" )) == {MASKPANE_X}:
            wgx1 = wgx1 + 1
        while wgx2 >= wgx1-1 and set(Windowgram.Edge_Extract_Static( wgc, "v", wgx2, ""  )) == {MASKPANE_X}:
            wgx2 = wgx2 - 1
        while wgy1-1 <= wgy2 and set(Windowgram.Edge_Extract_Static( wgc, "h", wgy1, "-" )) == {MASKPANE_X}:
            wgy1 = wgy1 + 1
        while wgy2 >= wgy1-1 and set(Windowgram.Edge_Extract_Static( wgc, "h", wgy2, ""  )) == {MASKPANE_X}:
            wgy2 = wgy2 - 1
        self.Import_Chars( [ [ wgc[iy][ix] for ix in range(wgx1-1, wgx2+1) ] for iy in range(wgy1-1, wgy2+1) ] )

    ##
    ## Copy
    ##

    def Copy(self):
        return Windowgram( self.Export_String(), self.Is_Extended() )

    ##
    ## CopyMasked
    ##
    ##      Minimal enclosing windowgram of the specified mask
    ##      Supports non-rectangular masks
    ##      MASKPANE_1: Window data
    ##      MASKPANE_0: Pane transparency
    ##      Mask dimensions must match windowgram dimensions
    ##

    def CopyMasked_Out(self, wg_mask):
        px, py, pw, ph = wg_mask.Panes_PaneXYWH(MASKPANE_1)
        wgc_self = self.Export_Chars()
        wgc_mask = wg_mask.Export_Chars()
        wgc_new = [ [ "" for _ in range(pw) ] for _ in range(ph) ]
        for ix in range( px, px+pw ):
            for iy in range( py, py+ph ):
                if wgc_mask[iy-1][ix-1] == MASKPANE_1: wgc_new[iy-py][ix-px] = wgc_self[iy-1][ix-1]
                else: wgc_new[iy-py][ix-px] = MASKPANE_X
        return Windowgram("", True).Load_Chars(wgc_new) # May contain extended characters

    def CopyMasked_In(self, wg_mask, wg_data):
        windowgram_chars = self.Export_Chars()
        frame_chars = wg_mask.Export_Chars()
        image_chars = wg_data.Export_Chars()
        fx, fy, fw, fh = wg_mask.Panes_PaneXYWH(MASKPANE_1)
        iw, ih = wg_data.Analyze_WidthHeight()
        if iw and ih:
            for iy in range(ih):
                for ix in range(iw):
                    if frame_chars[fy-1+iy][fx-1+ix] == MASKPANE_1:
                        windowgram_chars[fy-1+iy][fx-1+ix] = image_chars[iy][ix]
        return Windowgram("", self.Is_Extended()).Load_Chars(windowgram_chars)

##
## Windowgram Masking Functions
##

def Windowgram_Mask_Generate(wg, panes): # wg_mask
    # Returns a windowgram with non-standard panes for use with masking: "." for zero, ":" for one
    windowgram_parsed = wg.Export_Parsed()
    width, height = wg.Analyze_WidthHeight()
    # Produce mask
    mask_windowgram_chars = []
    while len(mask_windowgram_chars) < height: mask_windowgram_chars.append( list(MASKPANE_0 * width) )
    for key in list(panes):
        pane = windowgram_parsed[key]
        for y in range( pane['y'], pane['y'] + pane['h'] ):
            for x in range( pane['x'], pane['x'] + pane['w'] ):
                mask_windowgram_chars[y-1][x-1] = MASKPANE_1
    # Return mask as wg instance
    wg_mask = Windowgram("", True) # Create a windowgram for masking
    wg_mask.Import_Chars( mask_windowgram_chars )
    return wg_mask

def Windowgram_Mask_Boolean(wg_mask1, wg_mask2, op):
    # Assumes identical size
    wgc1 = wg_mask1.Export_Chars()
    wgc2 = wg_mask2.Export_Chars()
    wgc3 = []
    for iy in range(len(wgc1)):
        for ix in range(len(wgc1[iy])):
            while len(wgc3) <= iy+1: wgc3.append([])
            while len(wgc3[iy]) <= ix+1: wgc3[iy].append("")
            if op == "and":
                wgc3[iy][ix] = MASKPANE_1 if (MASKPANE_1 == wgc1[iy][ix] == wgc2[iy][ix]) else MASKPANE_0
            else: # Unsupported boolean operation
                wgc3[iy][ix] = MASKPANE_0
    return Windowgram("", True).Load_Chars(wgc3)

##
## Pane List Functions
##

def PaneList_DiffLost(this, that): # lostpanes
    # Parameters are Windowgram instances, aka wg
    used1, _ = this.Panes_GetUsedUnused()
    used2, _ = that.Panes_GetUsedUnused()
    lostpanes, _ = Windowgram( "".join( list(set(used1) - set(used2)) ) ).Panes_GetUsedUnused()
    return lostpanes

def PaneList_MovePanes(list1, list2, panes): # newlist1, newlist2
    # Moves specified batch of panes (if present) from "list1" into "list2" ... Returns new lists in that order
    for pane in list(panes):
        if pane in ValidPanes() and (pane in list1 or pane not in list2):
            # Assert ordering every pass, as in some situations the panes will be unsorted
            list1 = "".join([ch for ch in ValidPanes() if ch in list1 and ch != pane])
            list2 = "".join([ch for ch in ValidPanes() if ch in list2 or ch == pane])
    return list1, list2

def PaneList_AssimilatedSorted(this, that): # this_plus_that_assimilated_and_sorted
    return "".join( sorted( set( this + that ), key=lambda x: ValidPanes().find(x) ) )

##
## Other
##

def ParsedPanes_Add(paneid, parsedpane, windowgram_parsed={}):
    windowgram_parsed[paneid] = dict( list(parsedpane.items()) + list(dict(n=paneid).items()) )
    return windowgram_parsed



##
## Flex: Macros ... See actual usage for examples
##

is_long_axis_vert = lambda axis: True if axis in [ "v", "vertical", "vert" ] else False
is_long_axis_horz = lambda axis: True if axis in [ "h", "horizontal", "horz" ] else False
is_short_axis_vert_vhtblr = lambda axis: True if axis in [ "v", "t", "b" ] else False
is_short_axis_horz_vhtblr = lambda axis: True if axis in [ "h", "l", "r" ] else False

is_true = lambda word, alt=None: \
    True if word.lower() in [ "1", "true", "yes" ] + ([ alt.lower() ] if alt else []) else False

valid_directions = [ # These directions are recognized, the list is ordered 0123 == TBRL || NSEW
    [ "top", "t", "tp",     "north", "n",   "up", "u", "over", "above",     ],  # ix == 0 -> Vertical +
    [ "bottom", "b", "bt",  "south", "s",   "down", "d", "under", "below",  ],  # ix == 1 -> Vertical -
    [ "right", "r", "rt",   "east", "e"                                     ],  # ix == 2 -> Horizontal -
    [ "left", "l", "lt",    "west", "w"                                     ],  # ix == 3 -> Horizontal +
]

def direction_to_axiswithflag(direction, inverse=False): # axis_as_vh, negate_flag | None, None
    for ix, directions_ent in enumerate(valid_directions):
        if True in [True if d.lower().strip() == direction.lower().strip() else False for d in directions_ent]:
            if ix == 0: return "v", False ^ inverse  # Top
            if ix == 1: return "v", True  ^ inverse  # Bottom
            if ix == 2: return "h", True  ^ inverse  # Right
            if ix == 3: return "h", False ^ inverse  # Left
    return None, None

def axiswithflag_to_direction(axis, flag): # direction
    if axis == "v" and flag == False: return "t"
    if axis == "v" and flag == True : return "b"
    if axis == "h" and flag == True : return "r"
    if axis == "h" and flag == False: return "l"
    return None

def resolve_vhtblr(hint): # Either one of list("vhtblr") or None
    if is_long_axis_vert(hint): return "v"
    elif is_long_axis_horz(hint): return "h"
    return axiswithflag_to_direction( *direction_to_axiswithflag( hint ) ) # "t", "b", "l", "r"

def thruvalid_panes(panes, ignore=""): # Return unmodified if valid else None
    if len([ ch for ch in panes if ch not in PANE_CHARACTERS + ignore ]): return None
    return panes

def classify_panes(used, unused, panes): # areused, areunused, invalids
    areused = areunused = invalids = ""
    for paneid in panes:
        if paneid in used: areused += paneid
        elif paneid in unused: areunused += paneid
        else: invalids += paneid
    return areused, areunused, invalids

def resolve_size(size, axis_length, inverse, showinv, restrict=True): # error_or_none, inverse_flag, size_as_characters
    size_as_characters = 0
    try:
        original_size = size # Retain original for error messages
        while size and size[0] == "-": size = size[1:] # Strip negation
        size_type = size_GetType( size )
        if size_type is None:
            raise Exception( "Invalid size parameter: " + original_size )
        if restrict and size_GreaterOrEqualToBaseCharacters( size, axis_length ):
            if size_type == "characters": rep = showinv + str(axis_length)
            elif size_type == "percentage": rep = showinv + "100%"
            else: rep = showinv + "1x" # elif size_type == "multiplier"
            raise Exception( "Specified size (" + original_size + \
                ") is greater or equal to the maximum range (" + rep + ") of this function" )
        size_as_characters = size_ConvertToCharacters( size, axis_length )
        if size_as_characters is None:
            raise Exception( "Invalid size parameter: " + size )
        if restrict and size_as_characters >= axis_length: # Shouldn't happen by now, but if it does
            raise Exception( "Resulting size (" + showinv + str(size_as_characters) + \
                " characters) is greater or equal to the axis length (" + str(axis_length) + ")" )
        if size_as_characters < 1:
            raise Exception( "Resulting size (" + showinv + str(size_as_characters) + \
                " characters) is not valid" )
    except Exception as error:
        return str(error), None, None
    return None, inverse, size_as_characters



##----------------------------------------------------------------------------------------------------------------------
##
## Flex cores
##
## These functions are shared by multiple flex commands.
##
##      +----------------+--------------------------------------------------------------+
##      | Cores          | Used By                                                      |
##      +----------------+--------------------------------------------------------------+
##      | scalecore      | scale break      drag insert clone                           |
##      | groupcore      |             join drag insert clone delete flip mirror rotate |
##      | edgecore       |                  drag insert clone delete                    |
##      | smudgecore     |                  drag insert clone                           |
##      +----------------+--------------------------------------------------------------+
##
##----------------------------------------------------------------------------------------------------------------------

##
## Scale core ... Scales a windowgram
##
## Callers: scale, break, drag
##

def scalecore_v1(windowgram_string, w_chars, h_chars):
    ##
    ## Based on the scale code used in tmuxomatic 1.x
    ## Used until 2.0, then reactivated in 2.3
    ##
    def scale_one(element, multiplier):
        # Scale element using integer rounding, multiplier must be float
        q, r = math.modf( float(element - 1) * multiplier )
        if q >= .5: r += 1
        return int(r) + 1
    def scale_windowgram(list_panes, ax, ay): # lost_count
        # Scales the windowgram
        lost = 0
        for paneid in list_panes.keys():
            pane = list_panes[paneid]
            # The following were conditional prior to 2.4, removed to allow scale to 0 since it's handled by caller
            pane['w'] = scale_one( pane['x'] + pane['w'], ax )
            pane['h'] = scale_one( pane['y'] + pane['h'], ay )
            pane['x'] = scale_one( pane['x'], ax )
            pane['y'] = scale_one( pane['y'], ay )
            pane['w'] -= pane['x']
            pane['h'] -= pane['y']
            if not pane['x'] or not pane['y'] or not pane['w'] or not pane['h']: lost += 1
        return lost
    # Get pane list
    list_panes = Windowgram(windowgram_string).Export_Parsed()
    # Set the multipliers
    ww, wh = Windowgram(windowgram_string).Analyze_WidthHeight()
    ax, ay = float(w_chars) / float(ww), float(h_chars) / float(wh)
    # Perform the scale
    list_panes_scaled = copy.deepcopy( list_panes )
    scale_windowgram( list_panes_scaled, ax, ay )
    windowgram_string_new = Windowgram_Convert.Parsed_To_String( list_panes_scaled )
    return windowgram_string_new

def scalecore_v2(windowgram, w_chars, h_chars):
    ##
    ## Simpler but less accurate scale code added in tmuxomatic 2.0
    ## Used briefly from 2.0 to 2.2
    ##
    from_w, from_h = Windowgram(windowgram).Analyze_WidthHeight()
    x_mul = float(w_chars) / float(from_w)
    y_mul = float(h_chars) / float(from_h)
    windowgram_chars = Windowgram_Convert.String_To_Chars(windowgram)
    windowgram_chars_scaled = []
    for y in range(0, h_chars):
        windowgram_chars_scaled.append( [ windowgram_chars[ int(y/y_mul) ][ int(x/x_mul) ] \
            for x in range(0, w_chars) ] )
    windowgram_new = Windowgram_Convert.Chars_To_String( windowgram_chars_scaled )
    return windowgram_new

def scalecore(windowgram, w_chars, h_chars, retry=None): # TODO: Scale by wg to remove the Windowgram_Convert usage
    ##
    ## Main entry for all scale functions
    ##
    windowgram_scaled = "" # Scope, and reset in case of error
    # Retry with necessary increment and/or decrement until desired pane dimensions are reached.  This is required for
    # commands like "break", which need to scale to a specific pane size.  There's likely a way to derive these metrics
    # directly, but this works.  The following verifies that two resizes are necessary.  This is scale core case two:
    #       "new 1 ; scale 42x42 ; break 1 6x6 ; break 1 3x3"
    tries = 0
    tries_max = 16 # An infinite loop is unlikely, but this maximum will prevent such an occurrence
    paneid = exp_w = exp_h = None
    if retry and type(retry) is tuple and len(retry) == 3:
        paneid, exp_w, exp_h = retry # retry == ( paneid, w, h )
        if Windowgram( windowgram ).Panes_HasPane( paneid ): tries = tries_max
        else: paneid = None
    # Scale until satisfied; this loop is for pane measurement, since the windowgram should always scale on first try.
    if tries < 1: tries = 1
    try_w, try_h = w_chars, h_chars
    while tries:
        # Scale core discrepancy example, note that v2 loses 3 panes, but v1 does not.  This is scale core case one:
        #       "new 1 ; break 1 2x2 ; scale 3x3 ; scale 2x2"
        windowgram_scaled = scalecore_v1( windowgram, try_w, try_h ) # Must be v1, see tests
        if paneid:
            _, _, new_w, new_h = Windowgram( windowgram_scaled ).Panes_PaneXYWH( paneid )
            if new_w == exp_w and new_h == exp_h: break
            try_w += 1 if new_w < exp_w else -1 if new_w > exp_w else 0
            try_h += 1 if new_h < exp_h else -1 if new_h > exp_h else 0
        tries -= 1
    return windowgram_scaled

##
## Group core ... Tests group of panes for contiguity, returns group capability, if panes are missing it suggests them
##
## Callers: join, drag
##

class GroupStatus:
    Success = 1 # Group is valid
    Invalid_Panes = 2 # Panes specified are invalid (not in used, or are in unused)
    Insufficient_Panes = 3 # Panes need to be added, see the accompanying suggestions

def groupcore(wg, panes): # flag_groupstatus, string_suggestions
    ##
    ## Groups the specified panes and returns the findings.  If the panes are valid, but there are gaps in the group,
    ## it recursively detects which panes need to be added to complete the group.  If a group is determined to be valid,
    ## the windowgram may be trivially updated by the caller using a simple search and replace.
    ##
    used, unused = wg.Panes_GetUsedUnused()
    # Pane validity
    for pane in set(panes):
        if pane not in used or pane in unused:
            return GroupStatus.Invalid_Panes, None
    # Function for assembly of panes detected within any gaps of the mask
    def pane_deficit_detection(wg_win, x1, y1, x2, y2, panes):
        # Parameters: windowgram, rectangular bounds of mask, valid panes
        deficient_panes = ""
        wgw_windowgram_chars = wg_win.Export_Chars()
        wgm_windowgram_chars = wg_msk.Export_Chars()
        for y in range( len(wgw_windowgram_chars) ):
            for x in range( len(wgw_windowgram_chars[y]) ):
                w, m = wgw_windowgram_chars[y][x], wgm_windowgram_chars[y][x]
                if x >= x1-1 and x <= x2-1 and y >= y1-1 and y <= y2-1 and w not in set(panes):
                    deficient_panes += w
        return deficient_panes
    # Run deficit detection until none remain (e.g., mask == windowgram)
    suggestions = ""
    while True:
        # Draw mask and yield rectangular bounds
        wg_msk = Windowgram_Mask_Generate( wg, panes )
        x1, y1, x2, y2 = wg_msk.Panes_PaneXYXY( MASKPANE_1 )
        # Find pane content of any existing gaps
        deficient_panes = pane_deficit_detection( wg, x1, y1, x2, y2, panes )
        if not deficient_panes: break
        panes = PaneList_AssimilatedSorted( panes, deficient_panes )
        suggestions = PaneList_AssimilatedSorted( suggestions, deficient_panes )
    # Result by now will be either of these
    if not suggestions: return GroupStatus.Success, ""
    return GroupStatus.Insufficient_Panes, suggestions

##
## Edge core ... Tests group of panes for contiguous edge and if valid reduces it to a common form for processing
##
## Callers: drag
##

class EdgeStatus:
    Valid = 1
    Irrational = 2      # No edge produced from data
    Ambiguous = 3       # One or more edges were found (which may be on one or more axis)
    Noncontiguous = 4   # The produced edge has one or more gaps
    @staticmethod
    def error2string(status):
        if status == EdgeStatus.Valid: return None
        elif status == EdgeStatus.Irrational: return "No edge found (EdgeStatus.Irrational)"
        elif status == EdgeStatus.Ambiguous: return "Edges found on each axis (EdgeStatus.Ambiguous)"
        elif status == EdgeStatus.Noncontiguous: return "Multiple edges found (EdgeStatus.Noncontiguous)"
        else: return "Unknown error (EdgeStatus.Undefined)"

# Required for merging contiguous runs that are likely to be unordered ... Presently SwipeSide produces such runs

def edgecore_merger(runs):
    # Not always needed, but always expected: Strip duplicate runs, as how one would expect list(set(runs)) to work
    runs, scanruns = [], runs
    for run in scanruns:
        match = False
        for setrun in runs:
            if run == setrun: match = True
        if not match: runs += [ run ]
    # Merges neighboring runs where possible
    oruns = sorted( runs, key = operator.itemgetter( 0, 1 ) )
    nruns = []
    run = []
    for (y, x1, x2) in oruns:
        if run == []: run = [y, x1, x2]
        elif run[0] == y and run[2] + 1 == x1: run[2] = x2
        else: nruns += [run] ; run = [y, x1, x2]
    if run != []: nruns += [run]
    return nruns

# SideSwipe and SwipeSide ... Though syllable-swapped, the names are accurate descriptions of the respective algorithms

def edgecore_sideswipe(p1x1, p1x2, p2x1, p2x2, p1y1, p1y2, p2y1, p2y2): # [ axis_opposite, scan_a, scan_b ] or None
    # SideSwipe == Edge bordering panes only if contiguous
    decrement_run = lambda run: [ val-1 for val in run ] # How one might expect run-1 to work
    if p2x1 == p1x2 + 1:
        if p2y1 <= p1y1 and p2y2 <= p1y2 and p1y1 <= p2y2: return decrement_run( [ p2x1, p1y1, p2y2 ] )
        if p1y1 <= p2y1 and p2y2 <= p1y2                 : return decrement_run( [ p2x1, p2y1, p2y2 ] )
        if p2y1 <= p1y1 and p1y2 <= p2y2                 : return decrement_run( [ p2x1, p1y1, p1y2 ] )
        if p1y1 <= p2y1 and p1y2 <= p2y2 and p2y1 <= p1y2: return decrement_run( [ p2x1, p2y1, p1y2 ] )
    if p1x1 == p2x2 + 1:
        if p1y1 <= p2y1 and p1y2 <= p2y2 and p2y1 <= p1y2: return decrement_run( [ p1x1, p2y1, p1y2 ] )
        if p2y1 <= p1y1 and p1y2 <= p2y2                 : return decrement_run( [ p1x1, p1y1, p1y2 ] )
        if p1y1 <= p2y1 and p2y2 <= p1y2                 : return decrement_run( [ p1x1, p2y1, p2y2 ] )
        if p2y1 <= p1y1 and p2y2 <= p1y2 and p1y1 <= p2y2: return decrement_run( [ p1x1, p1y1, p2y2 ] )
    return None

def edgecore_swipeside(top, panedict, group, windowgram_chars): # [ [ axis_opposite, scan_a, scan_b ], ... ]
    # SwipeSide == Edge of specified pane where neighbor is not in group ... TB only, LR use transposition
    p1x1, p1y1 = panedict['x'], panedict['y']
    p1x2, p1y2 = panedict['x'] + panedict['w'] - 1, panedict['y'] + panedict['h'] - 1
    # Runs as [ [ axis_opposite, scan_a, scan_b ], [ axis_opposite, scan_a, scan_b ], ... ]
    runs, run = [], []
    for ix in range( p1x1-1, p1x2 ):
        pair = None
        if top and ( p1y1 == 1 or windowgram_chars[p1y1-2][ix] not in group ):
            pair = [ p1y1-1, ix ]
        if not top and ( p1y2 == len(windowgram_chars) or windowgram_chars[p1y2][ix] not in group ):
            pair = [ p1y2, ix ]
        if pair is not None:
            if run == []: run = [ pair[0], pair[1], pair[1] ]
            elif pair[1] == run[2] + 1: run[2] = pair[1]
            else: runs += [run] ; run = [ pair[0], pair[1], pair[1] ]
    if run != []: runs += [run]
    return runs

# Used in edgecore and elsewhere

def edgecore_buildoptimal(windowgram_parsed, axis, group, minimal): # optimal
    #
    # Derive an optimal run from the produced minimal run
    #
    # The following are examples of minimal ("m"), optimal ("o"), and identical ("=") runs where they overlap entirely.
    # The "|" is just a reminder that this is an illustration of edges (as opposed to panes, as a re typical elsewhere).
    # Dots are for irrelevant areas of the windowgram.  Vertical edges are shown, but of course the same applies to
    # horizontal when the windowgram is transposed.
    #
    #       ......| |......    ......| |......    ......| |......
    #       ......| |......    ...qqq|o|xxx...    ...MMM| |NNN...
    #       ...aaa| |bbb...    ...111|o|xxx...    ...111|o|OOO...
    #       ...111|=|222...    ...111|m|222...    ...111|m|222...
    #       ...zzz| |yyy...    ...111|o|rrr...    ...PPP|o|222...
    #       ......| |......    ...www|o|rrr...    ...QQQ| |RRR...
    #       ......| |......    ......| |......    ......| |......
    #
    #             E.1                E.2                E.3
    #
    #       E.1 : The minimal edge is also the optimal edge.  Typically optimal will be used for mechanics in split and
    #             grid platforms.  However for illustrating the edge, minimal will probably be used, or a combination of
    #             the two.  In this particular case it doesn't matter since they're the same.
    #
    #       E.2 : Example "drag vertical 12 right 1", if minimal is used then there will be shearing on pane "1", this
    #             results in an irregular pane, thus an invalid windowgram.  However if optimal is used, then drag knows
    #             what panes are affected by the drag, and assures a valid windowgram is produced every time.  There are
    #             other concerns with the "drag" function that are outside the scope of this core, see callers.
    #
    #       E.3 : Similar to E.2, "drag vertical 12:MNOPQR".  Note that the scalegroup does not apply to this algorithm,
    #             only the edge group factors into the optimal choice.  Dragging the scalegroup is handled independently
    #             of the edges, by using masking and pasting.
    #
    optimal = copy.deepcopy(minimal)
    affected = group
    # Build a list of qualifying edges that are perpendicular to the run
    qedges = [] # Contains only the full run for the qualifying edge, as [ [ paneid, scan_a, scan_b ], ... ]
    for paneid in windowgram_parsed.keys():
        parsedpane = windowgram_parsed[paneid]
        on_axis = optimal[0][0]
        x1, x2 = parsedpane['x'] - 1, parsedpane['x'] + parsedpane['w'] - 1
        y1, y2 = parsedpane['y'] - 1, parsedpane['y'] + parsedpane['h'] - 1
        if axis == "v" and ( x1 == on_axis or x2 == on_axis ): qedges.append( [ paneid, y1, y2 ] )
        if axis == "h" and ( y1 == on_axis or y2 == on_axis ): qedges.append( [ paneid, x1, x2 ] )
    # Function to merge first overlapping edge into the existing run and remove it from further consideration
    def edgemagnet(qedges, panes, run_as_runs): # changed, qedges, panes, run_as_runs
        # An edge is included if and only if it overlaps at least one character of the existing edge
        run = run_as_runs[0]
        for qedge in qedges:
            # Not the most efficient way to do this, but so easy to code...
            sq = list(range(qedge[1], qedge[2] + 1))
            sr = list(range(run  [1], run  [2] + 1))
            sqr = list(sorted(set(sq + sr)))
            if len(sq) + len(sr) - len(sqr) > 1: # Since these counts are edge-to-edge, +1 is not an actual overlap
                run = [ run[0], sqr[0], sqr[-1] ]
                if not qedge[0] in panes: panes += qedge[0]
                qedges = [ _ for _ in qedges if _[0] != qedge[0] ]
                return True, qedges, panes, [run]
        return False, qedges, panes, run_as_runs
    # One dimensional overlap assimilation loop that halts when no more additions are found
    while True:
        changed, qedges, affected, optimal = edgemagnet( qedges, affected, optimal )
        if not changed: break
    return optimal

# The main entry for producing an edge from a specified group

def edgecore(wg, group, direction=None): # status, axis, minimal, optimal
    ##
    ## An edge may be specified in either form:
    ##
    ##      group               Group of panes defines the edge by fully enclosing it with panes, unambiguously
    ##      group, direction    Direction clarifies the edge by specifying either: 1) cardinal direction, 2) axis
    ##
    ## The return types:
    ##
    ##      status              EdgeStatus.Valid if successful, if unsuccessful other types will be None, see errors
    ##      axis                This is either "h" or "v" for the edge axis
    ##      minimal             A single run in form of [[ on_axis, from_edge, to_edge ]]
    ##      optimal             Same as minimal but edge is extended to be compatible with split/grid windowgrams
    ##
    ## For tmuxomatic, (group, direction) should be used and/or the optimal edge favored, otherwise the result could
    ## produce windowgrams that are incompatible with tmux.
    ##
    ## For difference between minimal and optimal, consider the unittests, or see the upcoming "drag" implementation.
    ##
    used, unused = wg.Panes_GetUsedUnused()
    # Resolve direction to common form ("v", "h", "t", "b", "l", "r") for easier reference
    if direction is not None:
        direction = resolve_vhtblr( direction )
    # Algorithm uses parsed and character formats for edge detection
    windowgram_parsed = wg.Export_Parsed()
    windowgram_chars_yx = wg.Export_Chars()
    windowgram_chars_xy = Windowgram_Convert.Transpose_Chars( windowgram_chars_yx ) # Only used to simplify TBRL
    # Unordered array of edge characters, to be sorted later; defined as right/bottom of N, where left/top origin is N=0
    edgeruns_v = [] # Vertical edges as ..... [ (X, y1, y2), (X, y1, y2), ... ]
    edgeruns_h = [] # Horizontal edges as ... [ (Y, x1, x2), (Y, x1, x2), ... ]
    # Produce the minimal edge
    for paneid1 in windowgram_parsed.keys():
        pane1 = windowgram_parsed[paneid1]
        if paneid1 in group:
            # Side specification (TBLR) treats the group as a contiguous pattern, as if it were a single -- and possibly
            # non-rectangular -- pane.  In other words, when scanning an edge, if the neighbor is within the specified
            # group, that edge is simply ignored.  For example "12": "left 12" ignores the edge between "1" and "2",
            # producing an edge that is identical to "left 1".  Any grouping that is non-contiguous or non-rectangular
            # is permitted here, but will be rejected later due to the ambiguity.  There is no reason to allow such
            # ambiguity for the anticipated callers.  For example "12\n34", some ambiguity occurs: "left 124" produces
            # edges that are equivalent of two separate but combined calls, "left 1" and "left 4".  Multiple edges are
            # not valid for the expected use of edge definitions within the windowgram context, so any panes tangential
            # to the edge definition panes should not be included, as they would interfere with edgecore processing.
            if direction == "t" or direction == "b":
                # Side TB (explicit)
                topleft = True if direction == "t" else False
                parsedpane = pane1
                edgeruns_h += edgecore_swipeside( topleft, parsedpane, group, windowgram_chars_yx )
            elif direction == "l" or direction == "r":
                # Side LR (explicit)
                topleft = True if direction == "l" else False
                parsedpane = Windowgram_Convert.Transpose_Pane(pane1)
                edgeruns_v += edgecore_swipeside( topleft, parsedpane, group, windowgram_chars_xy )
            else: # direction == "v" or direction == "h"
                # Axis VH (implicit or explicit)
                for paneid2 in windowgram_parsed.keys():
                    pane2 = windowgram_parsed[paneid2]
                    if paneid2 in group and paneid1 != paneid2:
                        p1x1, p1y1 = pane1['x'],                  pane1['y']
                        p1x2, p1y2 = pane1['x'] + pane1['w'] - 1, pane1['y'] + pane1['h'] - 1
                        p2x1, p2y1 = pane2['x'],                  pane2['y']
                        p2x2, p2y2 = pane2['x'] + pane2['w'] - 1, pane2['y'] + pane2['h'] - 1
                        if direction == "v" or direction is None:
                            run = edgecore_sideswipe( p1x1, p1x2, p2x1, p2x2, p1y1, p1y2, p2y1, p2y2 )
                        if run is not None: edgeruns_v += [ run ]
                        else:
                            if direction == "h" or direction is None:
                                run = edgecore_sideswipe( p1y1, p1y2, p2y1, p2y2, p1x1, p1x2, p2x1, p2x2 )
                            if run is not None: edgeruns_h += [ run ]
    # Merge runs ... Neighboring runs are possible since panes are processed independently in edgecore_swipeside
    edgeruns_v = edgecore_merger( edgeruns_v ) # Duplicate input runs are possible
    edgeruns_h = edgecore_merger( edgeruns_h ) # Duplicate input runs are possible
    # Select edge ... Resolves implicit axis
    minimal, axis = (edgeruns_v, "v") if edgeruns_v else (edgeruns_h, "h") # Ambiguity is rejected below
    # Drop if invalid, with reason
    if not edgeruns_v and not edgeruns_h: return EdgeStatus.Irrational, None, None, None # Irrational == No results
    if edgeruns_v and edgeruns_h: return EdgeStatus.Ambiguous, None, None, None # Ambiguous == Multiple axis
    if len(minimal) > 1: return EdgeStatus.Noncontiguous, None, None, None # Noncontiguous == Multiple edge | Gaps
    # Up to now the runs are defined as character-to-character, but they must be edge-to-edge from here on
    minimal[0][2] += 1
    # Build an optimal run from the minimal run
    # The optimal run is most likely to be used, and it's convenient to produce at this point
    optimal = edgecore_buildoptimal( windowgram_parsed, axis, group, minimal )
    # Done
    return EdgeStatus.Valid, axis, minimal, optimal

# Located with edgecore, but used in conjunction with smudgecore

def edgecore_edgetoedge(axis, edge, width, height):
    # Returns -1 for top/left edge, +1 for bottom/right edge, 0 otherwise
    if edge[0] == 0: return -1
    if edge[0] == (width if axis == "v" else height): return 1
    return 0

##
## Smudge core ... This copies the border of specified edge in the perpendicular direction of length
##
## Callers: drag
##

def smudgecore(wg, edge, axis, length, direction, run=None): # wg
    # Must handle smudging beyond windowgram dimensions by enlarging the windowgram to accommodate
    wgw, wgh = wg.Analyze_WidthHeight()
    span = wgw if axis == "v" else wgh
    edge_characters = wg.Edge_Extract(axis, edge, "" if direction == "-" else "-") # Extracts the trailing side
    if run is None or set(edge_characters) == {MASKPANE_X} \
    or (edge == 0 and direction == "-") or (edge == span and direction == ""):
        run = [ edge, 0, len(edge_characters) ] # Full edge for expansion, contraction, or default
    fr, to = edge + (-1 if direction == "-" else 0), edge + (-length if direction == "-" else length-1)
    fr, to = min(fr, to), max(fr, to)
    if fr <= 0:      ed, ec, fr = -1, -fr,       0
    elif to >= span: ed, ec, to =  1, to-span+1, span-1
    else:            ed, ec     =  0, 0
    wgout = Windowgram("")
    # Smudge the edge
    windowgram_chars, windowgram_chars_from = [], wg.Export_Chars()
    if axis == "h": windowgram_chars_from = Windowgram_Convert.Transpose_Chars( windowgram_chars_from )
    for iy, line in enumerate(windowgram_chars_from): # Modifications
        windowgram_chars += [[(edge_characters[iy] if ix >= fr and ix <= to and iy >= run[1] and iy < run[2] \
            else ch) for ix, ch in enumerate(line)]]
    for iy, _ in enumerate(windowgram_chars): # Additions
        if ed < 0: windowgram_chars[iy] = [edge_characters[iy] * ec] + windowgram_chars[iy]
        else: windowgram_chars[iy] += [edge_characters[iy] * ec]
    if axis == "h": windowgram_chars = Windowgram_Convert.Transpose_Chars( windowgram_chars )
    wgout.Import_Chars( windowgram_chars )
    # Truncate transparency and return
    wgout.Edge_ClipOuterTransparents()
    return wgout



##----------------------------------------------------------------------------------------------------------------------
##
## Flex (windowgram modification console)
##
##----------------------------------------------------------------------------------------------------------------------
##
## Possible improvements:
##
##      Proportional scale, using the following aliases:
##
##          @   Size of user window proportional to counter axis
##          *   Size of current windowgram (just an alias for 1x/100%)
##
##          scale 20:@          Scale y proportionally according to 20 x (200:100 -> 20:10)
##          scale @:*           Scale x proportionally to current y (200:100, 100:25 -> 50:25)
##          scale @             If @ is specified for both, it's 50% of the window (200:100 -> 100:50)
##
## Possible modifiers:
##
##      breakout <pane> [shapes]                    break with axial concatenated shapes, "2x2; x 2x2 3x1; y 1 3x3 1"
##      shuffle <panegroup1> <panegroup2>           shuffle if all bounding boxes share full edge, or are of equal size
##      move <panes1> <panes2>                      swap if both panes are defined otherwise rename (probably redundant)
##      blockswap <panes1> <panes2>                 swaps one block of panes for another, e.g. `BLDbld` with `1` in demo
##
## Other features:
##
##      Allow for direct windowgram edit mode, this effectively makes flex a modal editor.  Needs ncurses, so it's a
##      feature for 3.x.
##
## Expectations:
##
##      The object (pane, group, edge) should always be the first argument to any command (with exception for qualifier)
##
##      All ordering is in English order: front -> back, top -> bottom, left -> right
##
##----------------------------------------------------------------------------------------------------------------------

describe = lambda kwargs: True if 'menu' in kwargs and kwargs['menu'] is True else False
usage_triplets = lambda cmd_dict: [ cmd_dict['usage'][ix:ix+3] for ix in range( 0, len(cmd_dict['usage']), 3 ) ]

##
## Output controls ... Only flex helpers and selectors should use this directly, others should use warnings queue
##

class FlexNotice(object):
    def __init__(self, level, message): self.level = level ; self.message = message
    def GetLvl(self): return self.level
    def GetMsg(self): return self.message

class FlexWarning(FlexNotice):
    def __init__(self, message): super( FlexWarning, self ).__init__( 0, message )

class FlexError(FlexNotice):
    def __init__(self, message): super( FlexError, self ).__init__( 1, message )

##
## Lists of commands ... Commands are ordered by appearance in source
##

flexmenu_top = []                   # List of all commands and aliases (top: user commands)
flexmenu_bot = []                   # List of all commands and aliases (bottom: modifiers + user commands)
flexmenu_aliases = []               # List of all aliases (recognized but not displayed)
flexmenu_grouped = {}               # List of grouped commands (for the short menus)

##
## Other globals
##

flexmenu_session = None             # Session object in global scope for modification by commands
flexmenu_index = [ 0 ]              # Selected window, list is for reference purposes only

##
## Flex sense (TODO: Make this a class)
##

flexsense_reset = {
    'finished': False,              # User exit
    'restore': False,               # User exit: Restore original
    'execute': False,               # User exit: Run session
    'output': [],                   # Command output
    'notices': [],                  # Command notices: Print and continue (FlexWarning, FlexError)
    'errors': [],                   # Command errors: Print and exit
}

##
## Flex: Conversion of windowgram metrics
## Supports floating point values (example: "2.5x")
##

def arg_is_multiplier(arg):
    if type(arg) is str:
        if arg[:-1] == "".join([ch for ch in arg[:-1] if ch in "0123456789.,"]): # Fixed float support
            if arg[-1:] == "x" or arg[-1:] == "X" or arg[-1:] == "*": return True
    return False

def arg_is_percentage(arg):
    if type(arg) is str:
        if arg[:-1] == "".join([ch for ch in arg[:-1] if ch in "0123456789.,"]): # Fixed float support
            if arg[-1:] == "%": return True
    return False

def arg_is_characters(arg):
    try:
        _ = int(arg)
        return True
    except ValueError:
        return False

def size_GetType(arg):
    # Return type or None if invalid
    if arg_is_multiplier(arg): return "multiplier"
    if arg_is_percentage(arg): return "percentage"
    if arg_is_characters(arg): return "characters"
    return None

def size_GreaterOrEqualToBaseCharacters(arg, base_characters):
    # If the parameter is greater or equal to 100%, 1x, or base_characters
    if size_GetType(arg) is not None:
        if arg_is_multiplier(arg): return True if float(arg[:-1]) >= 1.0 else False
        if arg_is_percentage(arg): return True if float(arg[:-1]) >= 100.0 else False
        if arg_is_characters(arg): return True if int(arg) >= base_characters else False
    return None

def size_ConvertToCharacters(arg, base_characters):
    if size_GetType(arg) is not None:
        if arg_is_multiplier(arg): return int(float(base_characters) * float(arg[:-1]))
        if arg_is_percentage(arg): return int(float(base_characters) * (float(arg[:-1]) / 100.0))
        if arg_is_characters(arg): return int(arg)
    return None

##
## Flex: Handling of newpanes parameter
##

def newpanes_RebuildPaneListsInPreferentialOrder(used, unused, newpanes):
    # Identify last valid pane in list while rebuilding unused pane list in a preferential order
    work, unused = unused, ""
    lastpaneid = ""
    for paneid in list(newpanes):
        if paneid in PANE_CHARACTERS: lastpaneid = paneid # Last valid paneid
        if paneid in work and paneid not in used: unused += paneid # Ignore invalid panes
    work, used = PaneList_MovePanes( work, used, unused )
    # Combine by next highest match
    ix = 0 # In case of empty set
    for chkix, paneid in enumerate(list(work)):
        if PANE_CHARACTERS.find(paneid) >= PANE_CHARACTERS.find(lastpaneid): ix = chkix ; break
    unused += work[ix:] + work[:ix] # Ordered by assignment availability, rooted by lastpaneid
    # Return both (note only unused is preferentially reordered)
    return used, unused

##
## Flex: Other macros
##

def panes_in_use_message_generate(panes_in_use):
    if not panes_in_use:
        return None
    print_panes = "pane" + ("s" if len(panes_in_use) > 1 else "")
    print_isare = "are" if len(panes_in_use) > 1 else "is"
    return "Specified " + print_panes + " (" + panes_in_use + ") " + print_isare + " already in use"

##
## Decorator for building flex commands
##

class flex(object):
    def __init__(self, command="", examples=[], description=None, aliases=[], group="", insert=False):
        self.command_only = command
        self.description = description
        self.examples = examples
        self.aliases = aliases
        self.group = group
        self.insert = insert
    def __call__(self, function):
        # From function build usage
        self.usage = self.command_only
        self.arglens = [ 0, 0 ] # [ Required, Total ]
        spec = inspect.getargspec(function)
        la = len(spec.args) if spec.args else 0
        ld = len(spec.defaults) if spec.defaults else 0
        class NoDefault: pass # Placeholder since None is a valid default argument
        args_with_defaults = [ ( spec.args[ix], (NoDefault if ix < la-ld else spec.defaults[ix-(la-ld)]) ) \
            for ix in range(0, len(spec.args)) ]
        brackets = lambda optional: "[]" if optional else "<>"
        def tagged(arg, tag): return True if tag in arg else False
        def clipped(arg, tags):
            arg = arg
            for tag in tags:
                if arg.find(tag) >= 0: arg = arg[:arg.find(tag)] + arg[arg.find(tag)+len(tag):]
            return arg
        for arg, default in args_with_defaults:
            # Regular argument types (normally required):
            #       _PRIVATE    This argument is never shown to the user
            #       _OPTIONAL   Listed as optional even if a default parameter was not specified
            #       =Default    Listed as optional if a default parameter was specified
            if not tagged(arg, "_PRIVATE"):
                self.arglens[1] += 1
                if default is NoDefault: self.arglens[0] += 1
                optional = True if tagged(arg, "_OPTIONAL") else False
                arg = clipped( arg, ["_OPTIONAL"] ) # Clip markers before printing
                enclosed = brackets( default is not NoDefault or optional )
                self.usage += " " + enclosed[0] + arg + enclosed[1]
        if spec.varargs:
            # Variable argument types (normally optional):
            #       _REQUIRED   Makes the parameter required where it is normally optional
            varargs = spec.varargs
            required = optional = False
            required = True if tagged(varargs, "_REQUIRED") else False
            varargs = clipped( varargs, ["_REQUIRED"] ) # Clip markers before printing
            enclosed = brackets( not required )
            self.usage += " " + enclosed[0] + varargs + "..." + enclosed[1]
            if required: self.arglens[0] += 1 # If required then varargs is [REQ+1, -1] instead of [REQ, -1]
            self.arglens[1] = -1 # Represents use of *args
        # Adds new menu item, or appends usage and examples if it already exists
        # Description is only used on first occurrence of the command, successive commands append without description
        append = False
        for entdict in flexmenu_top + flexmenu_bot:
            if entdict['about'][0] == self.command_only:
                entdict['funcs'] += [ function ]
                entdict['usage'] += [ self.usage, self.examples, self.arglens ]
                entdict['group'] += [ self.group ]
                append = True
        if not append:
            obj = {
                'funcs': [ function ],
                'about': [ self.command_only, self.description ],
                'usage': [ self.usage, self.examples, self.arglens ],
                'group': [ self.group ]
            }
            if self.insert: menu = flexmenu_top
            else: menu = flexmenu_bot
            menu.append( obj )
        # Add aliases if any
        for ix, alias_tup in enumerate(self.aliases):
            if type(alias_tup) is not list:
                print("Flex command indexing error: " + self.command_only + " alias #" + str(1+ix) + " is not a list")
                exit()
            if len(alias_tup) != 2:
                print("Flex command indexing error: " + self.command_only + " alias #" + str(1+ix) + " is not a pair")
                exit()
            flexmenu_aliases.append( alias_tup )
        # Grouped commands
        if not self.group in flexmenu_grouped: flexmenu_grouped[self.group] = []
        if not self.command_only in flexmenu_grouped[self.group]:
            flexmenu_grouped[self.group].append(self.command_only)
        # Function wrapper
        def wrapper(*args):
            return function(*args)
        return wrapper

##
## Flex modifier pointers parameter ... Because modifiers are in a separate module, this pointers parameter is required
##

class FlexPointersParameter(object):
    def __init__(self, flexmenu_session, wg_ptr, flexsense_ptr):
        self.flexmenu_session = flexmenu_session
        self.wg = wg_ptr
        self.flexsense = flexsense_ptr
        return None

##
## Flex automated processor for one or more commands in the flex group "modifiers"
##
##      * Supports multiple commands ("cmd 1 ; cmd 2 ; cmd 3")
##      * Only commands from the flex group "modifiers" are supported
##      * No command ambiguity
##      * No command aliases
##      * Processing halts on flex warning or error
##
## Used by
##
##      * Unit testing
##      * Stack reprocessor (when stack support is added)
##      * Other macroing may use this
##

def flex_processor(wg, commands, noticesok=False): # -> error
    processed = found = False
    for command in commands.split(";"):
        command = command.strip()
        command, arguments = re.split(r"[ \t]+", command)[:1][0], re.split(r"[ \t]+", command)[1:]
        for cmd_dict in flexmenu_top + flexmenu_bot:
            for ix, triplet in enumerate(usage_triplets(cmd_dict)):
                usage, examples, arglens = triplet
                group = cmd_dict['group'][ix]
                if group == "modifiers":
                    funcname = cmd_dict['about'][0]
                    if funcname == command:
                        found = True
                        if len(arguments) >= arglens[0] and (len(arguments) <= arglens[1] or arglens[1] == -1):
                            # Prepare for new command
                            flexsense = copy.deepcopy( flexsense_reset )
                            # Execute
                            args = [ FlexPointersParameter( None, wg, flexsense ) ] + arguments
                            cmd_dict['funcs'][ix]( *args )
                            # Error handler
                            if flexsense['notices'] and not noticesok:
                                output = "There were warnings or errors when processing: " + commands + "\n"
                                output = output + "\n".join([ "* "+warn.GetMsg() for warn in flexsense['notices'] ])+"\n"
                                return output
                            # Processed
                            processed = True
    if not found: return "Command not found: " + commands + "\n"
    if not processed: return "Command argument mismatch: " + commands + "\n"
    return None

##
## Flex: Scale
##
## Analogues:
##
##      Drag * may be used for scale
##

@flex(
    command     = "scale",
    group       = "modifiers",
    examples    = [ "scale 25", "scale 500%", "scale 2x", "scale 64:36", "scale 64x36" ],
    description = "Scale the windowgram.  Valid parameters are multipliers (x), percentages (%), exact character " + \
                  "dimensions, or any combination thereof.  Use a space ( ), colon (:), or times (x) to separate " + \
                  "the x and y axis.  If only one axis is specified then the value will be applied to both x and " + \
                  "y.  When specifying both, any valid combination will work, including mixing multipliers with " + \
                  "the times separator, for example \"2xx2x\", \"200%x2x\", \"2xx200%\", etc.",
    aliases     = [ ["size", "scale "], # Resize conflicts with rename for two character ambiguity, replaced with size
                    ["half", "scale 50%"], ["double", "scale 2x"],
                    ["wider", "scale 200%:100%"], ["thinner", "scale 50%:100%"],
                    ["taller", "scale 100%:200%"], ["shorter", "scale 100%:50%"],
                    ["higher", "scale 100%:200%"], ["lower", "scale 100%:50%"], ],
)
def cmd_scale_1(fpp_PRIVATE, xy_how): # 1 parameter
    # Wrapper for two parameter scale, splits "64:36" and "64x36" into "64 36", works with percentages and multipliers
    if ":" in xy_how:
        if xy_how.count(":") == 1: return cmd_scale_2( fpp_PRIVATE, *xy_how.split(":") )
    elif "x" in xy_how:
        count = xy_how.count("x")
        endwx = xy_how.endswith("x")
        if count == 1 and not endwx:
            return cmd_scale_2( fpp_PRIVATE, *xy_how.split("x") )
        if count == 2:
            if endwx: return cmd_scale_2( fpp_PRIVATE, *xy_how.split("x", 1) )
            else: return cmd_scale_2( fpp_PRIVATE, *xy_how.rsplit("x", 1) )
        if count == 3 and endwx:
            parts = xy_how.split("x", 2)
            return cmd_scale_2( fpp_PRIVATE, parts[0]+"x", parts[2] )
    # All others are simply cloned like "2x" into "2x 2x"
    return cmd_scale_2( fpp_PRIVATE, xy_how, xy_how )

@flex(
    command     = "scale",
    group       = "modifiers",
    examples    = [ "scale 25 15", "scale 200% 50%", "scale 2x .5x" ],
)
def cmd_scale_2(fpp_PRIVATE, x_how, y_how): # 2 parameters
    # Because text is inherently low resolution, fractional scaling may produce unsatisfactory results
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    # Generics
    wg_before = fpp_PRIVATE.wg
    dim_before = wg_before.Analyze_WidthHeight()
    # Convert to common float multipliers for easy scaling
    args = [ dim_before[0], dim_before[1] ] # Default to no scale on error
    for ix, arg in enumerate([x_how, y_how]):
        args[ix] = size_ConvertToCharacters(arg, dim_before[ix])
        if args[ix] is None:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Invalid size parameter: " + arg ) )
    w_chars, h_chars = args
    # Scale the windowgram
    wg_after = Windowgram( scalecore( wg_before.Export_String(), w_chars, h_chars ) )
    # Verify new windowgram (in case of scale error)
    dim_result = wg_after.Analyze_WidthHeight()
    if not dim_result[0] or not dim_result[1]:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Scale produced a blank windowgram, skipping" ) )
    if dim_result[0] != w_chars or dim_result[1] != h_chars:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Scale produced erroneous result, skipping" ) )
    # Alert user to any panes lost
    lost_panes = PaneList_DiffLost( wg_before, wg_after )
    if len(lost_panes):
        fpp_PRIVATE.flexsense['notices'].append(
            FlexWarning( "Lost " + str( len(lost_panes) ) + " panes: " + lost_panes ) )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wg_after )

##
## Flex: Add
##
## TODO: Edge could also represent a combined edge of panes.  The panes would have to be adjacent, but it would
## allow for the insertion of panes into the middle of windows.  Would require scaling the surrounding panes to
## support the insertion, but it could be done.  This is the insert command, and the accommodation logic is the
## same as clone.
##

@flex(
    command     = "add",
    group       = "modifiers",
    examples    = [ "add right 50% A", "add b 3", "add l .5x" ],
    description = "Append pane to windowgram edge.  Edge is identified by name (e.g., right), or a variety of " + \
                  "abbreviations (e.g., r, rt).  The size of the pane may be defined as an exact character size, " + \
                  "a percentage (%), or a multiplier (x).  If a pane id is not specified, lowest available will " + \
                  "be used.",
    aliases     = [ ["append", "add "], ["app", "add "] ],
)
def cmd_add(fpp_PRIVATE, edge, size, newpane=None):
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    wg_work = fpp_PRIVATE.wg
    newpane, error = wg_work.Panes_GetNewPaneId( newpane )
    if error:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Unable to secure a new pane id: " + error ) )
    # Convert axis-flag to ix to avoid rewrite
    axis_as_vh, negate_flag = direction_to_axiswithflag(edge)
    if axis_as_vh == "v" and negate_flag == False: ix = 0   # Top
    elif axis_as_vh == "v" and negate_flag == True: ix = 1  # Bottom
    elif axis_as_vh == "h" and negate_flag == True: ix = 2  # Right
    elif axis_as_vh == "h" and negate_flag == False: ix = 3 # Left
    else: ix = None
    # Process
    if ix is not None:
        # ix = 0123 == TBRL | NSEW
        windowgram_lines = wg_work.Export_Lines()
        axis_length = len(windowgram_lines) if (ix == 0 or ix == 1) else len(windowgram_lines[0])
        axis_width = len(windowgram_lines) if (ix == 2 or ix == 3) else len(windowgram_lines[0])
        size_chars = size_ConvertToCharacters( size, axis_length )
        if size_chars is None:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Invalid size parameter: " + size ) )
        if ix == 0: # Top
            for _ in range( size_chars ): windowgram_lines.insert( 0, newpane * axis_width )
        elif ix == 1: # Bottom
            for _ in range( size_chars ): windowgram_lines.append( newpane * axis_width )
        elif ix == 2: # Right
            windowgram_lines = [ line + (newpane * size_chars) for line in windowgram_lines ]
        elif ix == 3: # Left
            windowgram_lines = [ (newpane * size_chars) + line for line in windowgram_lines ]
        # Detect when addition doesn't register and notify user as warning
        wg_compare_before = wg_work.Export_String()
        wg_work.Import_Lines( windowgram_lines )
        wg_compare_after = wg_work.Export_String()
        if wg_compare_before == wg_compare_after:
            return fpp_PRIVATE.flexsense['notices'].append( FlexWarning( "Addition was too small to register" ) )
        # Replace windowgram
        fpp_PRIVATE.wg.Import_Wg( wg_work )
        # Done
        return
    # Edge not found
    return fpp_PRIVATE.flexsense['notices'].append( FlexError(
        "The edge you specified is invalid, please specify either: top, bottom, left, or right" ) )

##
## Flex: Break
##
## Analogues:
##
##      Break may be used for split 50%
##
## Notes:
##
##      Avoiding unnecessary complexity.  It's easy to incorporate support for group as target.  Such an algorithm would
##      break all panes in the group equally and apply the newpanes linearly.  This becomes complicated if avoiding size
##      explosions from finding the most efficient break sequence (common divisors).  Besides, such situations are more
##      easily managed by the user of flex; simply perform the breaks in a sequence that yields personally satisfactory
##      results.  Since this is already possible with flex, implementing such a feature would not add much practical
##      benefit and only complicate the function.
##

@flex(
    command     = "break",
    group       = "modifiers",
    examples    = [ "break 1 3x3", "break 0 3x1 x", "break z 3x2 IVXLCD" ],
    description = "Break a pane into a grid of specified dimensions.  If the break does not produce even panes at " + \
                  "the specified resolution, it will automatically scale up to the next best fit.  The newpanes " + \
                  "parameter is an optional starting pane id, or pane rename sequence.",
    aliases     = [ ["grid", "break "], ["panes", "break "], ],
)
def cmd_break(fpp_PRIVATE, pane, grid, newpanes=None):
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    # In order to produce a break of even proportions, we have to scale this windowgram up to next best fit.  It
    # could go one step further and find the most optimal size, being a resolution that evenly scales the original
    # windowgram constituent panes, while simultaneously providing a grid of even sizes.  The problem is that common
    # use cases would result in massive sizes to accommodate; though accurate, it would not be very practical.
    wg = fpp_PRIVATE.wg
    used, unused = wg.Panes_GetUsedUnused()
    if pane not in PANE_CHARACTERS:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The pane you specified is invalid" ) )
    elif pane in unused:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The pane you specified does not exist" ) )
    # Grid analysis and validity check
    gw = gh = panes = 0
    reason = "Grid parameter is invalid: " + grid
    if grid.count("x") == 1:
        gw, gh = grid.split("x")
        if gw.isdigit() and gh.isdigit():
            gw, gh = int(gw), int(gh)
            panes = gw * gh
            len_unused = len(unused) + 1 # The +1 accounts for the target pane that becomes available
            if not panes:
                reason = "Grid you specified results in no panes"
            elif panes > len(PANE_CHARACTERS):
                reason = "Grid is " + str(panes) + " panes, exceeding max of " + str(len(PANE_CHARACTERS))
            elif panes > len_unused:
                reason = "Grid is " + str(panes) + " panes, only " + str(len_unused) + " will be available"
            else:
                reason = None # No error
    if reason is not None:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( reason ) )
    # Extract the dimensions of the pane to determine requisite scale (if any)
    wg_w, wg_h = wg.Analyze_WidthHeight()
    px, py, pw, ph = wg.Panes_PaneXYWH( pane )
    # Perform a scale if needed
    scale_to = lambda r1, r2: (((float(int(r1/r2))+1.0)*r2) if (r1 % r2) else r1) if (r1 > r2) else r2
    scale_to_pane_w = int( scale_to( float(pw), float(gw) ) ) # Pane target x
    scale_to_pane_h = int( scale_to( float(ph), float(gh) ) ) # Pane target y
    stw_w = int(float(wg_w) * float(scale_to_pane_w) / float(pw)) # Window target x
    stw_h = int(float(wg_h) * float(scale_to_pane_h) / float(ph)) # Window target y
    # Scale
    wg_new = Windowgram( scalecore(
        wg.Export_String(), stw_w, stw_h, ( pane, scale_to_pane_w, scale_to_pane_h ) ) )
    _, _, npw, nph = wg_new.Panes_PaneXYWH( pane )
    # Validate
    if (npw != scale_to_pane_w or nph != scale_to_pane_h):
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The result is not the expected pane size" ) )
    # Swap
    wg = wg_new
    # Dimensions must be reloaded in the event that the windowgram was scaled
    wg_w, wg_h = wg.Analyze_WidthHeight()
    px, py, pw, ph = wg.Panes_PaneXYWH( pane )
    # Manually move availability of pane so it may be reused
    used, unused = PaneList_MovePanes( used, unused, pane )
    # Set starting panes.  By default this starts at the lowest unused pane id and iterates forward.  However
    # the user may specify a pane to start the iteration at, for example if it's a 3x2 grid (6 panes produced):
    #   specified == (None)    produces == 012345
    #                A                     ABCDEF
    #                BLN                   BLNOPQ
    #                BLN1                  BLN123
    if newpanes:
        panes_in_use = "".join([ch for ch in newpanes if ch not in unused and ch != pane])
        panes_in_use_message = panes_in_use_message_generate( panes_in_use )
        if panes_in_use_message:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError( panes_in_use_message ) )
        used, unused = newpanes_RebuildPaneListsInPreferentialOrder( used, unused, newpanes )
    # Replace pane with grid
    windowgram_lines = wg.Export_Lines()
    wg.Import_Lines( [
        "".join( [ ch if ch != pane else unused[int((iy-py+1)*gh/ph)*gw+int((ix-px+1)*gw/pw)] \
            for ix, ch in enumerate(list(line)) ] ) for iy, line in enumerate(windowgram_lines)
    ] )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Join
##
## Analogues:
##
##      Join may be used for rename: join <old>.<new>
##      Join may be used for swap: join <one>.<two> <two>.<one>
##
## Notes:
##
##      Join could be seen as a type of rename, and was used for rename and swap prior to those implementations
##

@flex(
    command     = "join",
    group       = "modifiers",
    examples    = [ "join abcd efgh", "join abcd.x efgh.y" ],
    description = "Join a contiguous group of panes into a single pane.  Multiple joins are supported.  The joined " + \
                  "pane is named after the first pane specified, but can be renamed by adding dot (.) followed by " + \
                  "the pane id.",
    aliases     = [ ["group", "join "], ["merge", "join "], ["glue", "join "], ],
)
def cmd_join(fpp_PRIVATE, *groups_REQUIRED):
    groups = groups_REQUIRED # Readability
    argument = lambda ix: str(ix+1) + " (\"" + groups_REQUIRED[ix] + "\")" # Show the group that the user specified
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    wg = fpp_PRIVATE.wg
    # Repackage groups so all have the rename element
    work, groups = groups, []
    for group in work: groups.append( group if "." in group else (group + "." + group[0]) )
    # Walk all groups and build join lists
    panes_clipped = ""
    for ix, group in enumerate(groups):
        try:
            # Make sure group is superficially valid
            if group.count(".") > 1: raise Exception("Argument contains more than one rename delimiter")
            invalids = "".join([ ch for ch in set(group) if ch not in PANE_CHARACTERS and ch != "." ])
            if invalids: raise Exception("Group contains invalid characters: " + invalids)
            # Verify rename and quietly strip duplicate panes
            group_l, group_r = group.split(".")
            if len(group_r) == 0: raise Exception("Rename delimiter used but subsequent pane unspecified")
            if len(group_r) > 1: raise Exception("Only one pane should be specified after the rename delimiter")
            group = "".join( [ ch for ch in sorted(set(group_l), key=lambda x: group.find(x)) ] ) + "." + group_r
            # Build group, simulate clip, test presence
            notfound = ""
            for ch in [ ch for ch in PANE_CHARACTERS if ch in set(group.split(".")[0]) ]: # Ordered set
                if ch in panes_clipped: raise Exception("Pane \"" + ch + "\" was already used by a previous group")
                if not wg.Panes_HasPane( ch ): notfound += ch
                else: panes_clipped += ch
            if notfound:
                raise Exception("Windowgram does not have pane" + ("(s) " if len(notfound)-1 else " ") + notfound)
        except Exception as error:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError(
                "Error with argument " + argument(ix) + ": " + str(error) ) )
    # Test the duplication of target panes by matching them against availability adjusted for panes clipped
    used, unused = wg.Panes_GetUsedUnused()
    used = "".join(list(set(used) - set(panes_clipped)))
    unused = "".join( [ ch for ch in PANE_CHARACTERS if ch in (unused + panes_clipped) ] )
    for ix, group in enumerate(groups):
        try:
            group_l, group_r = group.split(".")
            if group_r in used:
                raise Exception("Attempting to rename to pane " + group_r + " when it's in use")
            used += group_r
        except Exception as error:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError(
                "Error with argument " + argument(ix) + ": " + str(error) ) )
    # Perform the joins, detecting pane gaps in the group, resulting windowgram is paired for later merging
    joins = []
    for group in groups:
        # Join preprocessing
        group_l, group_r = group.split(".")
        result, suggestions = groupcore(wg, group_l)
        if result is GroupStatus.Invalid_Panes: # Occurs if groupcore() panes parameter is invalid
            return fpp_PRIVATE.flexsense['notices'].append( FlexError(
                "Group #" + argument(ix) + " contains invalid panes" ) )
        if result is GroupStatus.Insufficient_Panes:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError(
                "Group #" + argument(ix) + " isn't whole, but it would be if you add: " + suggestions ) )
        # Join ... By now the group is fully vetted: entirely valid, rectangularly whole
        pair_w = Windowgram( wg.Export_String() )
        pair_m = Windowgram_Mask_Generate( pair_w, group_l )
        pair_w.Panes_Renamer( group_l, group_r )
        joins.append( [ pair_w, pair_m ] )
    # A separate merge step is required to prevent name conflicts where the user makes use of the rename option.
    wg.Import_Mosaic( ( wg, joins ) )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Split
##
## Analogues:
##
##      Break may be used for split 50%
##
## Expectations (for testing):
##
##      If any of the specified newpanes are invalid, return error
##      A negative flag for edges (tblr) is ignored, but used for axis (vh)
##
## TODO:
##
##      Possible reordering detection, "split v h" (where "v" is the pane)
##      Senses reordering, e.g. "split horz v", and if unable to determine defaults to pane first
##

@flex(
    command     = "split",
    group       = "modifiers",
    examples    = [ "split 1 bottom 3", "split 1 vertical -3", "split 0 left 25% LR" ],
    description = "Splits one pane on either: an axis (vert, horz), or from an edge (top, left).  For an axis, a " + \
                  "negation of size inverses the split.  Size parameter is optional, the default is 50%.  Optional " + \
                  "newpanes parameter will rename the panes in order of newest to oldest (2 panes maximum).",
)
def cmd_split(fpp_PRIVATE, pane, how, size=None, newpanes=None):
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    wg = fpp_PRIVATE.wg
    used, unused = wg.Panes_GetUsedUnused()
    axis = how # This argument is handled as an axis
    # Set the default size if unspecified
    if size is None: size = "50%"
    # Verify pane
    if pane not in PANE_CHARACTERS:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The pane you specified is invalid" ) )
    elif pane in unused:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The pane you specified does not exist" ) )
    # Verify axis and reduce to "v" or "h"
    inverse = "-" if size[0] == "-" else ""
    showinv = inverse # Show inverse flag by default
    if is_long_axis_vert(axis): axis = "v"
    elif is_long_axis_horz(axis): axis = "h"
    else:
        if size[0] == "-":
            return fpp_PRIVATE.flexsense['notices'].append(
                FlexError( "Negative size only valid if `how` is vert or horz" ) )
        axis, negate_flag = direction_to_axiswithflag(axis)
        if axis is None or negate_flag is None:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The axis you specified is invalid" ) )
        inverse = "-" if negate_flag else ""
        showinv = "" # For TBRL do not show inverse flag
    # Get axis_length
    px, py, pw, ph = wg.Panes_PaneXYWH(pane)
    axis_length = pw if axis == "h" else ph
    # Verify pane is large enough to split
    if pw < 2 and ph < 2: # Single character pane
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Pane is too small to be split" ) )
    if axis_length < 2: # Single character length on the specified axis
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Pane is too small to be split in that way" ) )
    # Verify size
    error, inverse, size_chars = resolve_size(size, axis_length, inverse, showinv)
    if error: return fpp_PRIVATE.flexsense['notices'].append( error )
    if inverse: size_chars = axis_length - size_chars # Flip
    # Verify newpanes ... Set to first available if not specified
    if len(unused) < 1: return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Insufficient panes to split" ) )
    if newpanes is None: newpanes = ""
    if len(newpanes) == 0: newpanes += unused[0] # New pane is first available
    if len(newpanes) == 1: newpanes += pane # Base pane
    if len(newpanes) > 2: return fpp_PRIVATE.flexsense['notices'].append( FlexError(
        "Parameter newpanes exceeds the function maximum of two panes" ) )
    for ch in set(newpanes):
        if not ch in PANE_CHARACTERS: return fpp_PRIVATE.flexsense['notices'].append( FlexError(
            "Invalid pane in newpanes parameter: " + ch ) )
    panes_in_use = "".join([ch for ch in newpanes if ch not in unused and ch != pane])
    panes_in_use_message = panes_in_use_message_generate( panes_in_use )
    if panes_in_use_message: return fpp_PRIVATE.flexsense['notices'].append( FlexError( panes_in_use_message ) )
    used, unused = newpanes_RebuildPaneListsInPreferentialOrder( used, unused, newpanes )
    # Reorder the newpanes to match fill logic expectations
    newpanes = newpanes[:2] if not inverse else newpanes[1::-1]
    # Perform the split
    src_lines, dst_lines = wg.Export_Lines(), []
    sx, sy = px + size_chars if axis == "h" else 0, py + size_chars if axis == "v" else 0
    for iy, line in enumerate(src_lines):
        if axis == "v": line = "".join( [ newpanes[0 if iy < sy-1 else 1] if ch == pane else ch \
            for ch in list(line) ] )
        if axis == "h": line = "".join( [ newpanes[0 if ix < sx-1 else 1] if ch == pane else ch \
            for ix, ch in enumerate(list(line)) ] )
        dst_lines.append( line )
    wg.Import_Lines( dst_lines )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Rename
##
## Analogues:
##
##      Join may be used for rename: join <old>.<new>
##      Rename may be used for swap: rename <old><new> <new><old>
##
## Tests:
##
##      new rename.t1 ; break 1 3x2 ABCabc ; rename AaBb BbAa
##      new rename.t2 ; break 1 3x2 ABCabc ; rename Aa Bb Bb Cc Cc Aa
##      new rename.t3 ; break 1 2x2 1 ; rename 12 21 34 43
##      new rename.t4 ; break 1 2x2 1 ; rename 1 2 2 1 3 4 4 3
##

@flex(
    command     = "rename",
    group       = "modifiers",
    examples    = [ "rename Ff Tt", "rename F T f t" ],
    description = "Rename from one pane or group, to another pane or group, paired as <from> <to>.  Multiple " + \
                  "pairs may be specified.",
)
def cmd_rename(fpp_PRIVATE, panes_from, *panes_to):
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    # This command could have wrapped join, but a native implementation has been made to reduce overhead somewhat
    wg = fpp_PRIVATE.wg
    used, unused = wg.Panes_GetUsedUnused()
    pairs = [ panes_from ] + [ arg for arg in panes_to ]
    if len(pairs)&1:
        return fpp_PRIVATE.flexsense['notices'].append(
            FlexError( "Insufficient data, every <from> must be followed by <to>" ) )
    pairs = [ pairs[i*2:i*2+2] for i in range(len(pairs)>>1) ]
    # Ends parsed separately to allow for any pair ordering, this parallel effect is also supported by the join command
    def proc_list(which): # error or None
        nonlocal save_f, work_f, work_t
        pair = "1"
        for f, t in pairs:
            # Counts must match (1:1)
            if len(f) != len(t):
                return "Pair " + pair + " count error, both <from> and <to> pane counts must be identical"
            # Check for self rename (this could be safely ignored)
            selfrename = [ fi for fi, ti in zip(list(f), list(t)) if fi == ti ]
            if selfrename:
                return "Pane `" + selfrename[0] + "` renames to self in pair " + pair
            # Iterate all panes in this argument and validate
            fort = f if not which else t
            for paneid in fort:
                if not paneid in PANE_CHARACTERS:
                    return "Invalid pane `" + paneid + "` in pair " + pair
                if which == 0: # Only From
                    if paneid in work_f: # The pane must not have been previously freed
                        return "The <from> pane `" + paneid + "` in pair " + pair + " was renamed by another pair"
                    if not paneid in used: # The pane must already be in use
                        return "The <from> pane `" + paneid + "` in pair " + pair + " is not being used"
                if which == 1: # Only To
                    if paneid in work_t: # The pane must not have been previously named
                        return "The <to> pane `" + paneid + "` in pair " + pair + " was already named by another pair"
                    if not paneid in unused + save_f: # The pane must be unavailable
                        return "The <to> pane `" + paneid + "` in pair " + pair + " is already being used"
            # Next
            work_f += f
            work_t += t
            pair = str( int(pair) + 1 )
        return None
    # Validate pair lists in order of: from, to
    work_f = work_t = save_f = ""
    error = proc_list(0) # From
    if error: return fpp_PRIVATE.flexsense['notices'].append( FlexError( error ) )
    save_f, work_f, work_t = work_f, "", "" # Retention required for second pass validation
    error = proc_list(1) # To
    if error: return fpp_PRIVATE.flexsense['notices'].append( FlexError( error ) )
    # Perform the renames independently, result is paired with a mask and stored in a list for use in a mosaic
    renames = []
    for f, t in pairs:
        for pf, pt in zip(f, t):
            # Rename ... By now fully vetted
            pair_w = Windowgram( wg.Export_String() )
            pair_m = Windowgram_Mask_Generate( pair_w, pf )
            pair_w.Panes_Renamer( pf, pt )
            renames.append( [ pair_w, pair_m ] )
    # A separate merge step is required
    wg.Import_Mosaic( ( wg, renames ) )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Swap
##
## Analogues:
##
##      Join may be used for swap: join <one>.<two> <two>.<one>
##      Rename may be used for swap: rename <old><new> <new><old>
##
## Notes:
##
##      This was going to be simple single pane swap, but decided to go for the same flexibility as rename
##      Because of this, much of the code between rename and swap is the same or similar
##

@flex(
    command     = "swap",
    group       = "modifiers",
    examples    = [ "swap A B", "swap Aa Bb 1 2" ],
    description = "Swaps one pane or group, with another pane or group, paired as <from> <to>.  Multiple " + \
                  "pairs may be specified.",
)
def cmd_swap(fpp_PRIVATE, panes_from, *panes_to):
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    # This command could have wrapped join, but a native implementation has been made to reduce overhead somewhat
    wg = fpp_PRIVATE.wg
    used, unused = wg.Panes_GetUsedUnused()
    pairs = [ panes_from ] + [ arg for arg in panes_to ]
    if len(pairs)&1:
        return fpp_PRIVATE.flexsense['notices'].append(
            FlexError( "Insufficient data, every <from> must be followed by <to>" ) )
    pairs = [ pairs[i*2:i*2+2] for i in range(len(pairs)>>1) ]
    # Check for errors
    swaplist = ""
    pair = "1"
    try:
        for f, t in pairs:
            # Pair counts must be equal
            if len(f) != len(t):
                raise Exception("Pair " + pair + " count error, both <from> and <to> pane counts must be identical")
            # Check for duplicates in the same spot of the same pair
            for spot, paneset in [ ("<from>", f), ("<to>", t) ]:
                paneid = ([paneid for paneid in paneset if paneset.count(paneid) > 1]+[None])[0]
                if paneid:
                    raise Exception("Pane `" + paneid + "` specified multiple times in " + spot + " of pair " + pair)
            # Check for self swap (this could be safely ignored)
            for fi, ti in zip(f, t):
                if fi == ti:
                    raise Exception("Pane `" + fi + "` swaps to self in pair " + pair)
            # Iterate all panes in this argument and validate
            for spot, paneid in zip( ["<from>" for _ in f] + ["<to>" for _ in t], f + t):
                if not paneid in PANE_CHARACTERS:
                    raise Exception("Invalid pane `" + paneid + "` in " + spot + " of pair " + pair)
                if paneid in swaplist: # Panes are only permitted to be swapped once
                    raise Exception("The " + spot + " pane `" + paneid + "` in pair " + pair + " is already swapped")
                if not paneid in used: # The pane must already be in use
                    raise Exception("The " + spot + " pane `" + paneid + "` in pair " + pair + " is not being used")
            # Next
            swaplist += f + t
            pair = str( int(pair) + 1 )
    except Exception as error:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( str(error) ) )
    # Merge all arguments into a single unified from and to that contains both, so only one direction (f->t) is needed
    master_f, master_t = "".join([f for f, _ in pairs]), "".join([t for _, t in pairs])
    master_f, master_t = master_f + master_t, master_t + master_f
    # Perform the swaps in a single pass now that we know all panes are referenced only once
    windowgram_lines = wg.Export_Lines()
    wg.Import_Lines( [ "".join(
        [ ch if ch not in master_f else master_t[master_f.find(ch)] for ch in list(line) ]
        ) for line in windowgram_lines ] )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Drag
##
## Analogues:
##
##      Scale may be used for drag *
##
## Notes:
##
##      Dragging up to just before the point where panes disappear is the function of the caller.  This feature will
##      take considerable overhead by honing in on the extreme using multiple calls to drag (similar to Newton's square
##      root approximation).  Making it faster by analyzing the function is only trivial without the scale feature, so
##      this may require refactoring.  The purpose of this technique is to preserve the existing panes and/or to honor
##      neighboring edges.  For now, this feature is not required.
##
##      Pushing neighboring edges was considered, but this would get complicated and is probably unnecessary.
##
## TODO:
##
##      It will be possible to have a parallel-irregular scalegroup.  This is to say it only needs to have the group
##      edge perpendicular to the edge axis to be a single run, the parallel axis doesn't have to line up like this.
##      Adding this check and allowing this exception will add flexibility to the command.  This requires a new or
##      modified scale core that pins the outer parallel edges.  The following examples illustrates the differences
##      between these forms.
##
##                          Rectangular        Irregular         Irregular
##                                           Perpendicular      Parallelism
##
##      Illustrated       ..aaaa1|2bbbb..   ..AA..1|2bb....   ..AAqq1|2bbb...
##      windowgrams       ..aaaa1|2bbbb..   ..AAaa1|2bbBB..   ..AAqq1|2BBBB..
##      drag a vertical   ..aaaa1|2bbbb..   ..AAaa1|2bbBB.. +-....aa1|2BBBB..
##      edge of 1 and 2   ..aaaa1|2bbbb..   ....aa1|2x.BB.. | ..QQaa1|2ss....
##                                                    |     |
## The arrows point to areas where drag is impossible-+ and +-possible.  It will be possible to support irregularity
## on the parallel axis.  Axis is in relation to drag motion, not edge direction, which are opposites.
##

@flex(
    command     = "drag",
    group       = "modifiers",
    examples    = [ "drag 12 r 2", "drag abcd up 25%", "drag 12:abcd l 50%" ],
    description = "Drags an edge in the specified direction.  An edge is defined by the panes that border it.  " + \
                  "sometimes specifying a hint will be necessary to resolve ambiguity.  The hint is an axis or " + \
                  "a direction (VHTBLR).  Supports an optional scalegroup, simply add the panes to the edge " + \
                  "parameter using colon (:) as a separator.  To prevent loss of panes, set limit to \"yes\".",
    aliases     = [ ["move", "drag "], ["slide", "drag "], ],
)
def cmd_drag_1(fpp_PRIVATE, edge, direction, size): # No support for limit without some analysis
    return cmd_drag_2(fpp_PRIVATE, "", edge, direction, size)

@flex(
    command     = "drag",
    group       = "modifiers",
    examples    = [ "drag v 12 r 2", "drag t abcd up 25%", "drag l 12:abcd l 50%" ],
)
def cmd_drag_2(fpp_PRIVATE, hint, edge, direction, size, limit=None):
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    wg = fpp_PRIVATE.wg
    used, unused = wg.Panes_GetUsedUnused()
    # Reduce edge and resolve hint (supports swapping of hint and edge)
    swapped = ""
    res_hint = resolve_vhtblr( hint ) if hint is not "" else ""
    res_edge = thruvalid_panes( edge, "*:" )
    if not res_hint or not res_edge:
        swapped_hint = resolve_vhtblr( edge ) if edge is not "" else ""
        swapped_edge = thruvalid_panes( hint, "*:" )
        if swapped_hint and res_edge:
            res_hint, res_edge = swapped_hint, swapped_edge
            swapped = "swapped "
    hint = edge = None # From here on use res_hint, res_edge
    if res_hint is None: # Only handle None type, blank string for hint is valid
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The " + swapped + "hint is unrecognized" ) )
    if not res_edge: return fpp_PRIVATE.flexsense['notices'].append( FlexError( \
        "The edge contains invalid pane characters" ) )
    areused, areunused, invalids = classify_panes( used+"*:", unused, res_edge )
    if invalids: return fpp_PRIVATE.flexsense['notices'].append( FlexError( \
        "The panes (" + invalids + ") in " + swapped + "edge (" + res_edge + ") are invalid" ) ) # Already ruled out
    if areunused: return fpp_PRIVATE.flexsense['notices'].append( FlexError( \
        "The panes (" + areunused + ") in " + swapped + "edge (" + res_edge + ") are not being used" ) )
    # Separate edge into edge and scalegroup
    res_scalegroup = ""
    if ":" in res_edge:
        res_edge, res_scalegroup = res_edge.split(":", 1)
        if ":" in res_scalegroup: return fpp_PRIVATE.flexsense['notices'].append( FlexError( \
            "Please specify the optional scalegroup in the form: \"<edge>:<scalegroup>\"" ) )
    # Replace character "*" with all panes
    if "*" in res_edge: res_edge = AllPanes( res_edge, used )
    if "*" in res_scalegroup: res_scalegroup = AllPanes( res_scalegroup, used )
    # Resolve direction ... Axis (VH) is valid and like split, is based on TL, and is controlled with size negation
    res_direction, direction = resolve_vhtblr( direction ), None
    if not res_direction: return fpp_PRIVATE.flexsense['notices'].append( FlexError( \
        "The direction parameter is unrecognized" ) )
    # Get edge from res_hint + res_edge; this yields the official edge axis, required to resolve direction and size
    status, res_hint, minimal, optimal = edgecore( wg, res_edge, res_hint )
    status_print = EdgeStatus.error2string( status )
    if status_print: return fpp_PRIVATE.flexsense['notices'].append( FlexError( \
        "Edge specification error: " + status_print ) )
    # Exclude contradiction in axis, this must follow edge core since the hint may not have been specified by the user
    # Note: If they're equal they're opposite, consider that the edge axis and direction axis are different expressions
    if (is_short_axis_vert_vhtblr(res_direction) and is_short_axis_vert_vhtblr(res_hint)) or \
    (is_short_axis_horz_vhtblr(res_direction) and is_short_axis_horz_vhtblr(res_hint)):
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The direction must go against the edge axis" ) )
    # Reduce direction to "v" or "h"
    inverse = "-" if size[0] == "-" else ""
    showinv = inverse # Show inverse flag by default
    if res_direction != "v" and res_direction != "h":
        if size[0] == "-":
            return fpp_PRIVATE.flexsense['notices'].append(
                FlexError( "Negative size only valid if `direction` is vertical or horizontal" ) )
        res_direction, negate_flag = direction_to_axiswithflag(res_direction, True) # Inversed in this context
        if res_direction is None or negate_flag is None:
            return fpp_PRIVATE.flexsense['notices'].append( FlexError( "The hint you specified is invalid" ) )
        inverse = "-" if negate_flag else ""
        showinv = "" # For TBRL do not show inverse flag
    # Get necessary metrics, axis location is required to translate to characters, and possibly limit drag movement
    wgw, wgh = wg.Analyze_WidthHeight()
    axis_length = axis_location = optimal[0][0] # Use optimal since we're dealing with a pane grid
    if inverse != "-": axis_length = (wgw if res_direction == "h" else wgh) - axis_length
    # Resolve size and refine direction by toggling size negation if direction is VH
    restrict = False # If true, restrict dragging beyond the windowgram edge
    (error, res_sizeinv, res_size), size = resolve_size(size, axis_length, inverse, showinv, restrict), None
    if error: return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Size error: " + error ) )
    # Reduce limitation flag
    limit = True if limit is not None and is_true(limit, "limit") else False
    # Produce mutually-exclusive side masks, these are based on the defined edge and the windowgram dimensions
    aa, bb = (wgw, wgh) if res_hint == "v" else (wgh, wgw)
    mask_0 = dict(x=1,               w=axis_location,    y=1, h=bb)
    mask_1 = dict(x=axis_location+1, w=aa-axis_location, y=1, h=bb)
    if res_hint != "v":
        mask_0 = Windowgram_Convert.Transpose_Pane(mask_0)
        mask_1 = Windowgram_Convert.Transpose_Pane(mask_1)
    wgm0 = Windowgram("", True).Load_Parsed(ParsedPanes_Add(MASKPANE_1, mask_0, ParsedPanes_Add(MASKPANE_0, mask_1)))
    wgm1 = Windowgram("", True).Load_Parsed(ParsedPanes_Add(MASKPANE_1, mask_1, ParsedPanes_Add(MASKPANE_0, mask_0)))
    # Produce valid scale masks
    def Generate(panes):
        wgm0x = Windowgram_Mask_Boolean(wgm0, Windowgram_Mask_Generate(wg, panes), "and")
        wgm1x = Windowgram_Mask_Boolean(wgm1, Windowgram_Mask_Generate(wg, panes), "and")
        return wgm0x, wgm1x
    def Validate(wgm1, wgm2):
        def Validate(wgm):
            # (1) Any MASKPANE_1 character touching the specified axis edge
            if wgm.Panes_HasPane(MASKPANE_1) and not MASKPANE_1 in wgm.Edge_PanesAlong(res_hint, axis_location):
                return "Group of panes does not touch the specified edge"
            # (2) That the mask is a rectangular shape (for now; see above notes on irregular parallelism)
            result, suggestions = groupcore(wgm, MASKPANE_1) # GroupStatus.Invalid_Panes means MASKPANE_1 was not found
            if result == GroupStatus.Invalid_Panes or result == GroupStatus.Success: return None
            return "The group of panes is an unsupported irregular shape, try making it rectangular"
        r1 = Validate(wgm1) ; r2 = Validate(wgm2)
        return r1 if r1 else (r2 if r2 else 0)
    wgm0x, wgm1x = Generate( res_scalegroup + res_edge )    # The first mask pair must be "scalegroup + edgegroup".
    error = Validate( wgm0x, wgm1x )                        # Consider [ "12\n34", "right 12:34" ] -> "34" is valid.
    if error:                                               # The combined should test first, then scalegroup alone.
        wgm0x, wgm1x = Generate( res_scalegroup )           # It's always possible to define parameters that fit the
        error = Validate( wgm0x, wgm1x )                    # user's desired effect, if it's otherwise a valid form.
    if error:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Unable to drag: " + error ) )
    # Mask-extract the dynamics (areas to be scaled) from the static (the rest of the windowgram)
    wgm0s, wgm1s = wg.CopyMasked_Out( wgm0x ), wg.CopyMasked_Out( wgm1x ) # Already supports irregular parallelism
    # Drag logic is isolated so it may be reprocessed as necessary
    def drag(count, edgeruns, wg, wgm0s, wgm0x, wgm1s, wgm1x):
        sw0, sh0 = wgm0s.Analyze_WidthHeight() ; sw1, sh1 = wgm1s.Analyze_WidthHeight()
        # Scale the dynamics
        def modifier(which, val, size, inv):
            return (val+(-size if ((True if inv == "-" else False)^(True if which else False)) else size)) if val else 0
        if res_direction == "h" and sw0: sw0 = modifier(0, sw0, count, inverse)
        if res_direction == "h" and sw1: sw1 = modifier(1, sw1, count, inverse)
        if res_direction == "v" and sh0: sh0 = modifier(0, sh0, count, inverse)
        if res_direction == "v" and sh1: sh1 = modifier(1, sh1, count, inverse)
        if wgm0s.Panes_Exist(): wgm0s = Windowgram( scalecore( wgm0s.Export_String(), sw0, sh0 ) )
        if wgm1s.Panes_Exist(): wgm1s = Windowgram( scalecore( wgm1s.Export_String(), sw1, sh1 ) )
        # Smudge the edge across the masks (trivial, default behavior)
        if wgm0x.Panes_Exist(): wgm0x = smudgecore( wgm0x, axis_location, res_hint, count, inverse )
        if wgm1x.Panes_Exist(): wgm1x = smudgecore( wgm1x, axis_location, res_hint, count, inverse )
        # Smudge the edge across the static (simple, but exhaustive stepping process)
        # Basic behavior: with the edge, after each increment of the drag, modify the edge and proceed
        #       (1) Any-Edge-Outward NOT on outer edge      Modifies edgerun until outer edge is reached
        #       (2) Any-Edge-Outward on outer edge          Full run (windowgram expansion)
        #       (3) Outer-Edge-Inward                       Full run (windowgram contraction / transparency overwrite)
        # This behavior should be controlled here, as it's not required by other planned commands
        move = -1 if inverse == "-" else 1
        while count and wg.Panes_Exist():
            wgw, wgh = wg.Analyze_WidthHeight() # Required reload, smudgecore may contract or expand the windowgram
            location = edgecore_edgetoedge(res_hint, edgeruns[0], wgw, wgh) # Detects drag edge touching windowgram edge
            if location == -1 or location == 1: move = move * count # Full run for the remaining drag ... (2), (3)
            wg = smudgecore( wg, edgeruns[0][0], res_hint, abs(move), inverse, edgeruns[0] ) # Full scan if on wg edge
            edgeruns = [ [ edgeruns[0][0] + move, edgeruns[0][1], edgeruns[0][2] ] ] # Move the edge
            windowgram_parsed = wg.Export_Parsed() # Required to rebuild edge
            edgeruns = edgecore_buildoptimal( windowgram_parsed, res_hint, "", edgeruns )
            count -= abs(move)
        # Paste the dynamics over the static
        wg = wg.CopyMasked_In( wgm0x, wgm0s )
        wg = wg.CopyMasked_In( wgm1x, wgm1s )
        # Return result for analysis
        return wg
    # Perform drag.  Result must be valid according to: windowgram must not be zero, no loss of panes if user selects.
    # This basically starts with the full drag, and if that fails it divides down until the maximum valid drag possible
    # has been found.  Prints warning if actual drag differs from the user's specification.
    # TODO: This may be optimized by checking the range on the dynamic masks, and the nearest neighboring panes on the
    # edge for the static, to find a more efficient maximum range.  The scale algorithm does not lend itself to such
    # reasoning, so windowing will still need to be done to assure that no panes are lost, but if there are no scale
    # masks to begin with then the maximum range is trivially discovered.
    wgout = wg.Copy()
    error = None
    chars = res_size
    chars_min = 0
    chars_max = chars + 1
    while True:
        if chars == 0:
            error = "Drag without losing panes is not possible for the given parameters with this windowgram"
            wgout = wg.Copy()
            break
        wgout = drag( chars, copy.deepcopy(optimal), wg.Copy(), wgm0s.Copy(), wgm0x.Copy(), wgm1s.Copy(), wgm1x.Copy() )
        wgw, wgh = wgout.Analyze_WidthHeight()
        zero = (not wgw or not wgh)
        if (limit and PaneList_DiffLost( wg, wgout )) or zero:
            chars_max = chars
        else:
            chars_min = chars
        span = chars_max - chars_min
        if span == 1:
            if chars == chars_min: break
            chars = chars_min
        else:
            chars = chars_min + (span >> 1)
    # Report error
    if error:
        fpp_PRIVATE.flexsense['notices'].append( FlexError( error ) )
    # Warning if lost panes (and not already an error)
    else:
        lostpanes = PaneList_DiffLost( wg, wgout )
        if lostpanes:
            fpp_PRIVATE.flexsense['notices'].append( FlexWarning( \
                "The drag action resulted in " + str(len(lostpanes)) + " lost panes: " + lostpanes ) )
    # Replace windowgram
    fpp_PRIVATE.wg.Import_Wg( wgout )
    # TODO: Send actual drag value back to the caller in some way, required for interactive use

##
## Flex: Insert
##
##          Modifiers insert and clone need to differentiate between a deduced edge (1 parameter), a specified edge (2),
##          and the cardinal edge of a specified group (2).  Each of these is handled by one master function that will
##          infer the intent by the specified arguments and their originating function.  This may even allow some degree
##          of reordering of arguments, e.g., axis-edge and how-group.  Also maybe support as edge:axis and group:how,
##          this would assist the highlighter when it's implemented.
##
##          Both insert and clone uses the <how> parameter as quasi-optional.  If the edge is ambiguous, it requests it
##          for clarification.
##
##          Both insert and clone requires the edge/group parameter to have holes, all that's important is the specified
##          edge and that it's unambiguous.
##
##          Mid-stream optional arguments (e.g. how) is probably not necessary, since the other function without this
##          parameter will cover that application.  There will still need to be two distinct functions, but they will
##          both be wrappers for a single core function.
##
##          An axial expansion favoritism option needs to be added.  For example on the demo, when inserting "1B", does
##          it expand "1", "B", or both.  This could be added as a 3 state toggle in the UI, but for CLI it needs to be
##          specified.  Make both the default (except on windowgram edges, of course), since drag could be used for
##          additional adjusting.  These concerns also apply to clone.
##
##      insert <edge> <size> [newpanes]      insert pane at edge of panes, just like add but with panes
##      insert <how> <group> <size> [newpanes]
##
##          +---------------+---------------------------------------------------------------------------------------+
##          |   original    |       insert 12 2 X       insert r 3 1 X      insert r * 1 X      insert v 1245 1 X   |
##          +---------------+---------------------------------------------------------------------------------------+
##          |   123         |       1XX23               123X                123X                1X23                |
##          |   456         |       44556               4566                456X                4X56                |
##          |   789         |       77889               7899                789X                7789                |
##          +---------------+---------------------------------------------------------------------------------------+
##

# TODO

##
## Flex: Clone
##
##          The clone command takes the first group of panes (forming a full rectangle), and along the specified edge,
##          it stretches (like scale) the surrounding windowgram to accommodate, and inserts it in.  Most useful for
##          rapidly expanding common windowgram patterns.
##
##          The [newpanes] argument follows the same order as the first <group> parameter.
##
##          Clone could be thought of as:
##              1) insert <pane> ...        Axis 1 stretch/scale and insert
##              2) scale ...                Axis 2 scale to fit
##              Then copy the group into the new pane.  This is pretty easy to implement.
##
##          Requires 3 functions: public by edge, public by group, hidden internal that is core of both wrappers
##
##      clone <group> <edge> [newpanes]
##      clone <group> <how> <group> [newpanes]
##

# TODO

##
## Flex: Delete
##
##      delete <pane>                               remove pane from edge of window (del, clip, remove, drop, rm)
##

# TODO

##
## Flex: Mirror
##
##      mirror <group>                              mirrors a group, supports *
##

# TODO: Group

@flex(
    command     = "mirror",
    group       = "modifiers",
    description = "Reverse horizontally (left/right)",
)
def cmd_mirror(fpp_PRIVATE):
    # TODO: Optional pane group mirror
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    wg = fpp_PRIVATE.wg
    windowgram_lines = wg.Export_Lines()
    wg.Import_Lines( [ "".join( [ ch for ch in reversed(list(line)) ] ) for line in windowgram_lines ] )
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Flip
##
##      flip <group>                                flips a group, supports *
##

# TODO: Group

@flex(
    command     = "flip",
    group       = "modifiers",
    description = "Reverse vertically (top/bottom)",
)
def cmd_flip(fpp_PRIVATE):
    # TODO: Optional pane group flip
    if not fpp_PRIVATE.wg:
        return fpp_PRIVATE.flexsense['notices'].append( FlexError( "Please specify a window with use or new" ) )
    wg = fpp_PRIVATE.wg
    windowgram_lines = wg.Export_Lines()
    wg.Import_Lines( reversed(windowgram_lines) )
    fpp_PRIVATE.wg.Import_Wg( wg )

##
## Flex: Rotate
##
##      rotate <how>                                how == cw, ccw, 180, interpret 1..3 and -1..-3 as multiples of 90
##

# TODO



