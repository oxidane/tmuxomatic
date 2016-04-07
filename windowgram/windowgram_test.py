#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Copyright 2013-2016, Oxidane
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
## Windowgram Unit Testing
##
##----------------------------------------------------------------------------------------------------------------------
##
## These tests are ordered; both the test classes and their test methods are run in the order they appear.  This is
## processed automatically using the wrapper class (see code).
##
##      Classes with names starting with "Test", processed in the order they appear
##
##      From these recognized classes, methods with names starting with "test_", processed in the order they appear
##
##----------------------------------------------------------------------------------------------------------------------
##
## Tests are ordered lowest level to highest level:
##
##      Windowgram Convert
##      WindowgramGroup Convert
##      Flex Cores
##      Flex Modifiers
##      Readme Demonstrations
##
## TODO:
##
##      Windowgram
##      Windowgram_Mask
##      PaneList
##
##----------------------------------------------------------------------------------------------------------------------
##
## Notes:
##
##      Hashes should not be used in place of windowgrams, they're needed for comparison in case of failure in testing.
##
##      A change of indentation of the windowgram groups in this source will cause tests to fail because multiline
##      strings are widely used.
##
##----------------------------------------------------------------------------------------------------------------------

import unittest, io, inspect, sys

from windowgram import *



##----------------------------------------------------------------------------------------------------------------------
##
## Keeps the flex modifier unit test producer and validator in sync
##
##----------------------------------------------------------------------------------------------------------------------

FLEXUNIT_MAXWIDTH = 120
FLEXUNIT_INDENT = 12
FLEXUNIT_SPACE = 1



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Main
##
##----------------------------------------------------------------------------------------------------------------------

def Flex_UnitTests():
    # Sense test classes
    classes = inspect.getmembers(sys.modules[__name__])
    classes = [ classobj for classname, classobj in classes if classname.startswith("Test") ]
    # Pair with line numbers
    classes = [ (classobj, inspect.getsourcelines(classobj)[1]) for classobj in classes ]
    # Sort by line numbers
    classes = sorted(classes, key=lambda tup: tup[1])
    # Run tests in the order they appear
    stream = io.StringIO()
    runner = unittest.TextTestRunner( stream=stream )
    error = ""
    for tup in classes:
        result = runner.run( tup[0]() )
        if not result.wasSuccessful():
            if not error: error = "\n"
            if result.failures: error = error + result.failures[0][1]
            else: error = error + "Unspecified error"
    return error if error else None



##----------------------------------------------------------------------------------------------------------------------
##
## Wrapper class, includes a runTest() that automatically senses tests and executes them
##
##----------------------------------------------------------------------------------------------------------------------

class SenseTestCase(unittest.TestCase):

    def runTest(self):
        try:
            # Sense test methods
            methods = inspect.getmembers(self.__class__(), predicate=inspect.ismethod)
            methods = [ method for method in methods if method[0].startswith("test_") ]
            # Pair with line numbers
            methods = [ (method[1], inspect.getsourcelines(method[1])[1]) for method in methods ]
            # Sort by line numbers
            methods = sorted(methods, key=lambda tup: tup[1])
            # Execute tests in the order they appear
            for method in methods:
                method[0]()
        except AssertionError as e:
            raise e # Forward
        except Exception as e:
            error = "An error occurred during testing: " + repr(e) # Show the error in case of failure during test
            raise AssertionError( e ) # Forward the exception to properly halt because of failure

    ##----------------------------------------------------------------------------------------------------------
    ##
    ##  Performs flex commands and compares the resulting windowgrams with those specified
    ##
    ##  Commands        List of strings, each string may have multiple commands but corresponds to one windowgram
    ##  Pattern         Windowgram pattern, where they are ordered left to right, top to bottom, with first line 1-N
    ##
    ##----------------------------------------------------------------------------------------------------------

    def assertFlexSequence(self, commands, pattern, noticesok=False):
        windowgramgroup_list = WindowgramGroup_Convert.Pattern_To_List( pattern )
        cmdlen, ptnlen = len(commands), len(windowgramgroup_list)
        if cmdlen != ptnlen:
            raise Exception( "Mismatch: commands (" + str(cmdlen) + ") and windowgrams (" + str(ptnlen) + ")" )
        wg = Windowgram( NEW_WINDOWGRAM ) # Specified in case the default changes
        wlist = []
        for ix, (command, windowgram) in enumerate( zip( commands, windowgramgroup_list ) ):
            errors = flex_processor( wg, command, noticesok )
            self.assertTrue( not errors, errors )
            self.assertTrue( wg.Export_String() == windowgram, 
                "The resulting windowgram for sequence #" + str(ix+1) + " does not match: \n\n" + wg.Export_String() )
            wlist.append( wg.Export_String() )
        pattern_produced = WindowgramGroup_Convert.List_To_Pattern( \
            wlist, FLEXUNIT_MAXWIDTH, FLEXUNIT_INDENT, FLEXUNIT_SPACE )
        pattern_produced = pattern_produced.rstrip(" \t\n").lstrip("\n")
        pattern = pattern.rstrip(" \t\n").lstrip("\n")
        self.assertTrue( pattern_produced == pattern,
            "The resulting pattern does not match specification: \n\n" + pattern_produced + "\n!=\n" + pattern )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Windowgram_Convert
##
##----------------------------------------------------------------------------------------------------------------------

class Test_Windowgram_Convert(SenseTestCase):

    ##----------------------------------------------------------------------------------------------------------
    ##
    ## Windowgram_Convert class
    ##
    ##----------------------------------------------------------------------------------------------------------

    def test_Windowgram_Convert_StringToLines(self):
        data_i = "1135\n1145\n2245\n"
        data_o = [ "1135", "1145", "2245" ]
        data_x = Windowgram_Convert.String_To_Lines( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_LinesToString(self):
        data_i = [ "1135", "1145", "2245" ]
        data_o = "1135\n1145\n2245\n"
        data_x = Windowgram_Convert.Lines_To_String( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_StringToChars(self):
        data_i = "1135\n1145\n2245\n"
        data_o = [ [ "1", "1", "3", "5" ], [ "1", "1", "4", "5" ], [ "2", "2", "4", "5" ] ]
        data_x = Windowgram_Convert.String_To_Chars( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_CharsToString(self):
        data_i = [ [ "1", "1", "3", "5" ], [ "1", "1", "4", "5" ], [ "2", "2", "4", "5" ] ]
        data_o = "1135\n1145\n2245\n"
        data_x = Windowgram_Convert.Chars_To_String( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_StringToParsed(self):
        data_i = "1135\n1145\n2245\n"
        data_o = {
            '1': {'y': 1, 'x': 1, 'w': 2, 'n': '1', 'h': 2},
            '2': {'y': 3, 'x': 1, 'w': 2, 'n': '2', 'h': 1},
            '3': {'y': 1, 'x': 3, 'w': 1, 'n': '3', 'h': 1},
            '4': {'y': 2, 'x': 3, 'w': 1, 'n': '4', 'h': 2},
            '5': {'y': 1, 'x': 4, 'w': 1, 'n': '5', 'h': 3}, }
        data_x, error_string, error_line = Windowgram_Convert.String_To_Parsed( data_i )
        self.assertTrue( error_string is None )
        self.assertTrue( error_line is None )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_ParsedToString(self):
        data_i = {
            '1': {'y': 1, 'x': 1, 'w': 2, 'n': '1', 'h': 2},
            '2': {'y': 3, 'x': 1, 'w': 2, 'n': '2', 'h': 1},
            '3': {'y': 1, 'x': 3, 'w': 1, 'n': '3', 'h': 1},
            '4': {'y': 2, 'x': 3, 'w': 1, 'n': '4', 'h': 2},
            '5': {'y': 1, 'x': 4, 'w': 1, 'n': '5', 'h': 3}, }
        data_o = "1135\n1145\n2245\n"
        data_x = Windowgram_Convert.Parsed_To_String( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_StringToMosaic(self):
        data_i = "1135\n1145\n2245\n"
        data_m = [
            "@@::\n@@::\n::::\n",
            "::::\n::::\n@@::\n",
            "::@:\n::::\n::::\n",
            "::::\n::@:\n::@:\n",
            ":::@\n:::@\n:::@\n",
        ]
        data_o = (
            Windowgram("1135\n1145\n2245\n"),
            [
                [ Windowgram("11..\n11..\n....\n"), Windowgram("@@::\n@@::\n::::\n") ],
                [ Windowgram("....\n....\n22..\n"), Windowgram("::::\n::::\n@@::\n") ],
                [ Windowgram("..3.\n....\n....\n"), Windowgram("::@:\n::::\n::::\n") ],
                [ Windowgram("....\n..4.\n..4.\n"), Windowgram("::::\n::@:\n::@:\n") ],
                [ Windowgram("...5\n...5\n...5\n"), Windowgram(":::@\n:::@\n:::@\n") ],
            ],
        )
        data_x = Windowgram_Convert.String_To_Mosaic( data_i, data_m )
        self.assertTrue( Mosaics_Equal( data_x, data_o ) )

    def test_Windowgram_Convert_MosaicToString(self):
        data_i = (
            Windowgram("xxxx\nxxxx\nxxxx\n"), # This will be completely overwritten by the following mask pairs
            [
                [ Windowgram("11..\n11..\n....\n"), Windowgram("@@::\n@@::\n::::\n") ],
                [ Windowgram("....\n....\n22..\n"), Windowgram("::::\n::::\n@@::\n") ],
                [ Windowgram("..3.\n....\n....\n"), Windowgram("::@:\n::::\n::::\n") ],
                [ Windowgram("....\n..4.\n..4.\n"), Windowgram("::::\n::@:\n::@:\n") ],
                [ Windowgram("...5\n...5\n...5\n"), Windowgram(":::@\n:::@\n:::@\n") ],
            ],
        )
        data_o = "1135\n1145\n2245\n"
        data_x = Windowgram_Convert.Mosaic_To_String( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_PurifyString(self):
        data_i = "\n\n1135      \n1145 # etc\n2245\n\n"
        data_o = "1135\n1145\n2245\n"
        data_x = Windowgram_Convert.PurifyString( data_i )
        self.assertTrue( data_x == data_o )

    def test_Windowgram_Convert_TransposeCharacters(self):
        data_i = [  [ "1", "1", "3", "5" ],
                    [ "1", "1", "4", "5" ],
                    [ "2", "2", "4", "5" ] ]
        data_o = [  [ "1", "1", "2" ],
                    [ "1", "1", "2" ],
                    [ "3", "4", "4" ],
                    [ "5", "5", "5" ] ]
        data_x = Windowgram_Convert.Transpose_Chars( data_i )
        self.assertTrue( data_x == data_o )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: WindowgramGroup_Convert
##
##----------------------------------------------------------------------------------------------------------------------

class Test_WindowgramGroup_Convert(SenseTestCase):

    def test_WindowgramGroup_Convert_ListToPattern(self):

        # Inclusion of blank lines
        group_i = ['1\n', '2\n2\n']
        group_o = """
            1 2
              2
        """
        group_x = WindowgramGroup_Convert.List_To_Pattern( group_i, 32, 12, 1, testmode=8 )
        self.assertTrue( group_o == group_x )

        # Fitting pattern #1
        group_i = [ '111\n'*3, '2\n'*2, '3333333333\n'*5, 'aaaaaaaaaaaaaaaaa\n'*10, 'bbbbbbbbbbbbbbbbb\n'*5 ]
        group_o = """
            111    2    3333333333
            111    2    3333333333
            111         3333333333
                        3333333333
                        3333333333

            aaaaaaaaaaaaaaaaa    bbbbbbbbbbbbbbbbb
            aaaaaaaaaaaaaaaaa    bbbbbbbbbbbbbbbbb
            aaaaaaaaaaaaaaaaa    bbbbbbbbbbbbbbbbb
            aaaaaaaaaaaaaaaaa    bbbbbbbbbbbbbbbbb
            aaaaaaaaaaaaaaaaa    bbbbbbbbbbbbbbbbb
            aaaaaaaaaaaaaaaaa
            aaaaaaaaaaaaaaaaa
            aaaaaaaaaaaaaaaaa
            aaaaaaaaaaaaaaaaa
            aaaaaaaaaaaaaaaaa
        """
        group_x = WindowgramGroup_Convert.List_To_Pattern( group_i, 50, 12, 4, testmode=8 )
        self.assertTrue( group_o == group_x )

        # Fitting pattern #2
        group_i = [ '111\n'*3, '2\n'*2, '3333333333\n'*5, 'aaaaaaaaaaaaaaaaa\n'*10, 'bbbbbbbbbbbbbbbbb\n'*5 ]
        group_o = """
            111 2 3333333333 aaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbb
            111 2 3333333333 aaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbb
            111   3333333333 aaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbb
                  3333333333 aaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbb
                  3333333333 aaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbb
                             aaaaaaaaaaaaaaaaa
                             aaaaaaaaaaaaaaaaa
                             aaaaaaaaaaaaaaaaa
                             aaaaaaaaaaaaaaaaa
                             aaaaaaaaaaaaaaaaa
        """
        group_x = WindowgramGroup_Convert.List_To_Pattern( group_i, 100, 12, 1, testmode=8 )
        self.assertTrue( group_o == group_x )

    def test_WindowgramGroup_Convert_PatternToList(self):

        # Test basic height differences
        group_i = """
            1 2
              2
        """
        group_o = ['1\n', '2\n2\n']
        group_x = WindowgramGroup_Convert.Pattern_To_List( group_i )
        self.assertTrue( group_o == group_x )

        # Test special characters like transparency
        group_i = """
            1.. ...
            ... ..2
        """
        group_o = ['1..\n...\n', '...\n..2\n']
        group_x = WindowgramGroup_Convert.Pattern_To_List( group_i )
        self.assertTrue( group_o == group_x )

        # More comprehensive test, including windowgram width mismatch, and '0' as out-of-bounds windowgram
        group_i = """
            1 22 33 aa bb  XX Y ZZ
            1 22    aa bb     Y    0
            1          bb          0
                       bbb
        """
        group_o = ['1\n1\n1\n', '22\n22\n', '33\n', 'aa\naa\n', 'bb\nbb\nbb\nbbb\n', 'XX\n', 'Y\nY\n', 'ZZ\n']
        group_x = WindowgramGroup_Convert.Pattern_To_List( group_i )
        self.assertTrue( group_o == group_x )

        # Test misaligned windowgram lines (second line of second window should be clipped, see expected result)
        group_i = """
            111  222  333
            111   222 333
            111
        """
        group_o = ['111\n111\n111\n', '222\n', '333\n333\n']
        group_x = WindowgramGroup_Convert.Pattern_To_List( group_i )
        self.assertTrue( group_o == group_x )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Cores
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexCores(SenseTestCase):

    ## Scale Core

    def test_ScaleCore(self):
        group_i = """
            111223
            111223
            111223
            xxxyyz
            xxxyyz
            XXXYYZ
        """
        group_o = Windowgram_Convert.Lines_To_String( [ "111111222233", "111111222233", "xxxxxxyyyyzz" ] )
        group_x = scalecore( group_i, 12, 3 )
        self.assertTrue( group_o == group_x )

    ## Enforces the use of scale core v1, and will fail if v2 is reactivated

    def test_ScaleCore_VersionAssert(self):
        # break 1 2x2 ; scale 3x3 ; scale 2x2
        wg_i = "01\n23\n"
        wg_o = scalecore( wg_i, 3, 3 )
        wg_o = scalecore( wg_o, 2, 2 )
        self.assertTrue( wg_o == wg_i )

    ## Tests the need for retries in the scale core

    def test_ScaleCore_ScaleRetries(self):
        # break 1 11x1 ; scale 46 1 ; break 5 7x1
        wg_x = "00000001111111222222222333333344444445555555666666677777778888888889999999aaaaaaa\n"
        wg_o = scalecore( "000011112222233334444555566667777888889999aaaa\n", 80, 1, ( "5", 7, 1 ) )
        self.assertTrue( wg_o == wg_x )

    ## Group Core

    def test_GroupCore_Sufficient(self):
        wg = Windowgram( """
            qqwwee
            qqwwee
            rrttyy
            rrttyy
            uuiioo
            uuiioo
        """ )
        result, suggestions = groupcore( wg, "qwrt" )
        self.assertTrue( result == GroupStatus.Success )
        self.assertTrue( suggestions == "" )

    def test_GroupCore_Insufficient(self):
        wg = Windowgram( """
            1122xx
            1122yy
            33zzzz
            33zzzz
            rrzzzz
            rrsstt
        """ )
        result, suggestions = groupcore( wg, "123" )
        self.assertTrue( result == GroupStatus.Insufficient_Panes )
        self.assertTrue( suggestions == PaneList_AssimilatedSorted( "rstxyz", "" ) )

    ## Edge Core

    def test_EdgeCore_Merger(self):
        #
        # The merger algorithm should be obvious.  Required to merge the results of SwipeSide algorithm.
        #
        self.assertTrue( edgecore_merger( [[3, 3, 5], [9, 0, 2], [9, 3, 5], [9, 6, 8]] ) == [[3, 3, 5], [9, 0, 8]] )
        self.assertTrue( edgecore_merger( [[9, 6, 8], [9, 3, 5], [3, 3, 5], [9, 0, 2]] ) == [[3, 3, 5], [9, 0, 8]] )

    def test_EdgeCore_SideSwipe(self):
        #
        # SideSwipe algorithm (not to be confused with SwipeSide)
        #
        # This algorithm is axis-agnostic; illustrated tests are vertical, i.e., horizontal swaps parameters.
        # To produce new tests, interject the respective windowgram into edgecore(), print the results, then exit.
        #
        # Successful    Successful    Fail    Fail
        # @A @B @C @D   @E @F @G @H   @I @J   @K @L
        # .2 1. .2 1.   .1 2. .1 2.   .2 1.   2. .1
        # .2 1. 12 12   .1 2. 21 21   .2 1.   2. ..
        # 12 1. 12 12   21 2. 21 21   .2 ..   2. 2.
        # 12 12 12 12   21 21 21 21   .2 ..   .1 2.
        # 12 12 12 .2   21 21 21 .1   .2 .2   .1 2.
        # 12 12 .2 .2   21 21 .1 .1   1. .2   .1 2.
        # 1. 1. .2 .2   2. 2. .1 .1   1. .2   .1 2.
        #                                    p1x   p2x   p1y   p2y
        self.assertTrue( edgecore_sideswipe( 1, 1, 2, 2, 3, 7, 1, 6 ) == [ 1, 2, 5 ] )  # @A
        self.assertTrue( edgecore_sideswipe( 1, 1, 2, 2, 1, 7, 4, 6 ) == [ 1, 3, 5 ] )  # @B
        self.assertTrue( edgecore_sideswipe( 1, 1, 2, 2, 2, 5, 1, 7 ) == [ 1, 1, 4 ] )  # @C
        self.assertTrue( edgecore_sideswipe( 1, 1, 2, 2, 1, 4, 2, 7 ) == [ 1, 1, 3 ] )  # @D
        self.assertTrue( edgecore_sideswipe( 2, 2, 1, 1, 1, 6, 3, 7 ) == [ 1, 2, 5 ] )  # @E
        self.assertTrue( edgecore_sideswipe( 2, 2, 1, 1, 4, 6, 1, 7 ) == [ 1, 3, 5 ] )  # @F
        self.assertTrue( edgecore_sideswipe( 2, 2, 1, 1, 1, 7, 2, 5 ) == [ 1, 1, 4 ] )  # @G
        self.assertTrue( edgecore_sideswipe( 2, 2, 1, 1, 2, 7, 1, 4 ) == [ 1, 1, 3 ] )  # @H
        self.assertTrue( edgecore_sideswipe( 1, 1, 2, 2, 6, 7, 1, 5 ) == None )         # @I
        self.assertTrue( edgecore_sideswipe( 1, 1, 2, 2, 1, 2, 5, 7 ) == None )         # @J
        self.assertTrue( edgecore_sideswipe( 2, 2, 1, 1, 4, 7, 1, 3 ) == None )         # @K
        self.assertTrue( edgecore_sideswipe( 2, 2, 1, 1, 1, 1, 3, 7 ) == None )         # @L

    def test_EdgeCore_SwipeSide(self):
        #
        # SwipeSide algorithm (not to be confused with SideSwipe)
        #
        # This algorithm is axis-agnostic; when using X major, the windowgram and pane must be transposed.
        #
        wg = Windowgram( """
            xx000yyyy # xxx111333 (original, transposed)
            xx000yyyy # xxx111333
            xx000yyyy # 000zzz444
            11zzz2222 # 000zzz444
            11zzz2222 # 000zzz444
            11zzz2222 # yyy444555
            334445555 # yyy444555
            334445555 # yyy444555
            334445555 # yyy444555
            """ )
        windowgram_chars_yx = wg.Export_Chars()
        windowgram_chars_xy = Windowgram_Convert.Transpose_Chars( windowgram_chars_yx )
        windowgram_parsed = wg.Export_Parsed()
        group = "012345"
        # For cleaner processing
        def edgescan_q(axis, direction, windowgram_parsed, group, windowgram_chars):
            runs = []
            for pane in list(group):
                parsedpane = windowgram_parsed[pane]
                if not axis: parsedpane = Windowgram_Convert.Transpose_ParsedPane( parsedpane )
                this_runs = edgecore_swipeside( direction, parsedpane, group, windowgram_chars )
                for run in this_runs: runs.append( run )
            return edgecore_merger( runs )
        def edgescan_v(direction):
            return edgescan_q( True, direction, windowgram_parsed, group, windowgram_chars_yx )
        def edgescan_h(direction):
            return edgescan_q( False, direction, windowgram_parsed, group, windowgram_chars_xy )
        # TBLR
        self.assertTrue( edgescan_v( True )  == [[0, 2, 4], [3, 0, 1], [3, 5, 8], [6, 2, 4]] )
        self.assertTrue( edgescan_v( False ) == [[3, 2, 4], [9, 0, 8]] )
        self.assertTrue( edgescan_h( True )  == [[0, 3, 8], [2, 0, 2], [5, 3, 5]] )
        self.assertTrue( edgescan_h( False ) == [[2, 3, 5], [5, 0, 2], [9, 3, 8]] )

    def test_EdgeCore_Invalid(self):
        wg = Windowgram( """
            W11YY
            XX22Z
        """ )
        # Irrational (W does not border Z)
        status, axis, minimal, optimal = edgecore( wg, "WZ" )
        self.assertTrue( status is EdgeStatus.Irrational )
        self.assertTrue( axis is None )
        self.assertTrue( minimal is None )
        self.assertTrue( optimal is None )
        # Ambiguous (vertical edge W1 and X, horizontal edge W and 1)
        status, axis, minimal, optimal = edgecore( wg, "WX1" )
        self.assertTrue( status is EdgeStatus.Ambiguous )
        self.assertTrue( axis is None )
        self.assertTrue( minimal is None )
        self.assertTrue( optimal is None )
        # Noncontiguous (a gap exists in the minimal edge between 1 and 2)
        status, axis, minimal, optimal = edgecore( wg, "WXYZ" )
        self.assertTrue( status is EdgeStatus.Noncontiguous )
        self.assertTrue( axis is None )
        self.assertTrue( minimal is None )
        self.assertTrue( optimal is None )

    def test_EdgeCore_Group_Vertical(self):
        wg = Windowgram( """
            WX
            1X
            12
            Y2
            YZ
        """ )
        status, axis, minimal, optimal = edgecore( wg, "12" ) # Implicit vertical
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis == "v" )
        self.assertTrue( minimal == [ [1, 2, 3] ] )
        self.assertTrue( optimal == [ [1, 0, 5] ] )

    def test_EdgeCore_Group_Horizontal(self):
        wg = Windowgram( """
            1AA22
            1AA22
            33BB4
            33BB4
        """ )
        status, axis, minimal, optimal = edgecore( wg, "AB" ) # Implicit horizontal
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis == "h" )
        self.assertTrue( minimal == [ [2, 2, 3] ] )
        self.assertTrue( optimal == [ [2, 0, 5] ] )

    def test_EdgeCore_GroupDirection_Vertical(self):
        wg = Windowgram( """
            OWbo
            O1Xo
            O12o
            OY2o
            OqZo
        """ )
        status, axis, minimal, optimal = edgecore( wg, "2", "left" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis == "v" )
        self.assertTrue( minimal == [ [2, 2, 4] ] )
        self.assertTrue( optimal == [ [2, 1, 4] ] )
        status, axis, minimal, optimal = edgecore( wg, "X", "right" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis == "v" )
        self.assertTrue( minimal == [ [3, 1, 2] ] )
        self.assertTrue( optimal == [ [3, 0, 5] ] )

    def test_EdgeCore_GroupDirection_Horizontal(self):
        wg = Windowgram( """
            1AA22
            33BB4
        """ )
        status, axis, minimal, optimal = edgecore( wg, "A", "bottom" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis == "h" )
        self.assertTrue( minimal == [ [1, 1, 3] ] )
        self.assertTrue( optimal == [ [1, 0, 5] ] )
        status, axis, minimal, optimal = edgecore( wg, "3", "top" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis == "h" )
        self.assertTrue( minimal == [ [1, 0, 2] ] )
        self.assertTrue( optimal == [ [1, 0, 5] ] )

    def test_EdgeCore_WindowgramEdge(self):
        # All edges here will have equal minimal and optimal since there are no neighboring panes
        wg = Windowgram( """
            011222
            344555
            344555
            677888
            677888
            677888
        """ )
        status, axis, minimal, optimal = edgecore( wg, "5", "right" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "v" )
        self.assertTrue( minimal == [ [6, 1, 3] ] )
        self.assertTrue( optimal == [ [6, 1, 3] ] )
        status, axis, minimal, optimal = edgecore( wg, "0", "left" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "v" )
        self.assertTrue( minimal == [ [0, 0, 1] ] )
        self.assertTrue( optimal == [ [0, 0, 1] ] )
        status, axis, minimal, optimal = edgecore( wg, "8", "bottom" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "h" )
        self.assertTrue( minimal == [ [6, 3, 6] ] )
        self.assertTrue( optimal == [ [6, 3, 6] ] )
        status, axis, minimal, optimal = edgecore( wg, "1", "top" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "h" )
        self.assertTrue( minimal == [ [0, 1, 3] ] )
        self.assertTrue( optimal == [ [0, 1, 3] ] )

    def test_EdgeCore_Nuances(self):
        # This is noncontiguous, for now.  It's possible to support, but callers must be rigorously tested, since they
        # assume a single run in the edgecore result.
        wg = Windowgram( """
            1122AABB
            aabbxxyy
            XXYY3344
        """ )
        status, axis, minimal, optimal = edgecore( wg, "1234", "right" )
        self.assertTrue( status is EdgeStatus.Noncontiguous )
        self.assertTrue( axis is None )
        self.assertTrue( minimal is None )
        self.assertTrue( optimal is None )

    def test_EdgeCore_Examples(self):
        wg = Windowgram( """
            # E.1
            aaabbb #
            111222 # =
            zzzyyy #
        """ )
        status, axis, minimal, optimal = edgecore( wg, "12" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "v" )
        self.assertTrue( minimal == [ [3, 1, 2] ] )
        self.assertTrue( optimal == [ [3, 1, 2] ] )
        wg = Windowgram( """
            # E.2
            qqqxxx # o
            111xxx # o
            111222 # m
            111rrr # o
            wwwrrr # o
        """ )
        status, axis, minimal, optimal = edgecore( wg, "12" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "v" )
        self.assertTrue( minimal == [ [3, 2, 3] ] )
        self.assertTrue( optimal == [ [3, 0, 5] ] )
        wg = Windowgram( """
            # E.3
            MMMNNN #
            111OOO # o
            111222 # m
            PPP222 # o
            QQQRRR #
        """ )
        status, axis, minimal, optimal = edgecore( wg, "12" )
        self.assertTrue( status is EdgeStatus.Valid )
        self.assertTrue( axis is "v" )
        self.assertTrue( minimal == [ [3, 2, 3] ] )
        self.assertTrue( optimal == [ [3, 1, 4] ] )

    ## Smudge Core

    def test_SmudgeCore_Basic(self):
        wg_i = Windowgram( """
            12345 
            abcde 
            fghij 
            ABCDE 
            FGHIJ 
        """ )
        group_o = """
            2345 11345 1234 12355
            bcde aacde abcd abcee
            ghij ffhij fghi fghjj
            BCDE AACDE ABCD ABCEE
            GHIJ FFHIJ FGHI FGHJJ

            abcde 12345 12345 12345 
            fghij 12345 abcde abcde 
            ABCDE fghij fghij fghij 
            FGHIJ ABCDE ABCDE FGHIJ 
                  FGHIJ       FGHIJ 

            345 12345 123 12555
            cde abcde abc abeee
            hij fffij fgh fgjjj
            CDE AAADE ABC ABCDE
            HIJ FFFIJ FGH FGHIJ

            fghij 12345 12345 12345 
            ABCDE ab345 abcde abcde 
            FGHIJ fg345 fghij FGHij 
                  ABCDE       FGHDE 
                  FGHIJ       FGHIJ 
        """
        wg_o_list = WindowgramGroup_Convert.Pattern_To_List( group_o )
        wg_x_list = [
            smudgecore( wg_i, 0, "v", 1, ""  ).Export_String(),
            smudgecore( wg_i, 1, "v", 1, ""  ).Export_String(),
            smudgecore( wg_i, 5, "v", 1, "-" ).Export_String(),
            smudgecore( wg_i, 4, "v", 1, "-" ).Export_String(),
            smudgecore( wg_i, 0, "h", 1, ""  ).Export_String(),
            smudgecore( wg_i, 1, "h", 1, ""  ).Export_String(),
            smudgecore( wg_i, 5, "h", 1, "-" ).Export_String(),
            smudgecore( wg_i, 4, "h", 1, "-" ).Export_String(),
            smudgecore( wg_i, 0, "v", 2, ""  , [0, 1, 4] ).Export_String(), # Edge discarded with transparency
            smudgecore( wg_i, 1, "v", 2, ""  , [1, 2, 5] ).Export_String(),
            smudgecore( wg_i, 5, "v", 2, "-" , [5, 1, 4] ).Export_String(), # Edge discarded with transparency
            smudgecore( wg_i, 4, "v", 2, "-" , [4, 0, 3] ).Export_String(),
            smudgecore( wg_i, 0, "h", 2, ""  , [0, 1, 4] ).Export_String(), # Edge discarded with transparency
            smudgecore( wg_i, 1, "h", 2, ""  , [1, 2, 5] ).Export_String(),
            smudgecore( wg_i, 5, "h", 2, "-" , [5, 1, 4] ).Export_String(), # Edge discarded with transparency
            smudgecore( wg_i, 4, "h", 2, "-" , [4, 0, 3] ).Export_String(),
        ]
        for wg_o, wg_x in zip( wg_o_list, wg_x_list ):
            self.assertTrue( wg_x == wg_o, "\nwg_o\n" + wg_o + "\nwg_x\n" + wg_x )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier :: Reset
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Reset(SenseTestCase):

    def test_Reset(self):
        self.assertFlexSequence( [
            "reset",
        ], """
            1
        """ )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier :: Scale
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Scale(SenseTestCase):

    def test_Scale_One_DupCharacters(self): # Created in flex using "new unittest Scale_One_DupCharacters"
        self.assertFlexSequence( [
            "scale 1",
            "scale 19",
            "scale 3",
            "scale 20",
        ], """
            1 1111111111111111111 111 11111111111111111111
              1111111111111111111 111 11111111111111111111
              1111111111111111111 111 11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
              1111111111111111111     11111111111111111111
                                      11111111111111111111
        """ )

    def test_Scale_One_DupPercentages(self): # Created in flex using "new unittest Scale_One_DupPercentages"
        self.assertFlexSequence( [
            "scale 200%",
            "scale 400%",
            "scale 25%",
            "scale 400%",
            "scale 75%",
            "scale 33.4%",
            "scale 100%",
            "scale 100.99%",
            "scale 50%",
            "scale 1000%",
            "scale 050.000%",
        ], """
            11 11111111 11 11111111 111111 11 11 11 1 1111111111 11111
            11 11111111 11 11111111 111111 11 11 11   1111111111 11111
               11111111    11111111 111111            1111111111 11111
               11111111    11111111 111111            1111111111 11111
               11111111    11111111 111111            1111111111 11111
               11111111    11111111 111111            1111111111
               11111111    11111111                   1111111111
               11111111    11111111                   1111111111
                                                      1111111111
                                                      1111111111
        """ )

    def test_Scale_One_DupMultipliers(self): # Created in flex using "new unittest Scale_One_DupMultipliers"
        self.assertFlexSequence( [
            "scale 2x",
            "scale 1x",
            "scale .5x",
            "scale 5x",
            "scale 2.5x",
            "scale 1.25x",
            "scale .2x",
            "scale 5.34x",
            "scale 0.25x",
            "scale 00000.25000x",
        ], """
            11 11 1 11111 111111111111 111111111111111 111 1111111111111111 1111 1
            11 11   11111 111111111111 111111111111111 111 1111111111111111 1111
                    11111 111111111111 111111111111111 111 1111111111111111 1111
                    11111 111111111111 111111111111111     1111111111111111 1111
                    11111 111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                          111111111111 111111111111111     1111111111111111
                                       111111111111111     1111111111111111
                                       111111111111111     1111111111111111
                                       111111111111111     1111111111111111
                                                           1111111111111111
        """ )

    def test_Scale_One_MixedJoin1(self): # Created in flex using "new unittest Scale_One_MixedJoin1"
        self.assertFlexSequence( [
            "scale 5:10",
            "scale 10:5",
            "scale 2x:2x",
            "scale 50%:50%",
            "scale .5x:5",
            "scale 5:200%",
            "scale 200%:.5x",
        ], """
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
        """ )

    def test_Scale_One_MixedJoin2(self): # Created in flex using "new unittest Scale_One_MixedJoin2"
        self.assertFlexSequence( [
            "scale 5x10",
            "scale 10x5",
            "scale 2xx2x",
            "scale 50%x50%",
            "scale .5xx5",
            "scale 5x200%",
            "scale 200%x.5x",
        ], """
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111 1111111111 11111111111111111111 1111111111 11111 11111 1111111111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
            11111            11111111111111111111                  11111
        """ )

    def test_Scale_Two_Mixed(self): # Created in flex using "new unittest Scale_Two_Mixed"
        self.assertFlexSequence( [
            "scale 5 10",
            "scale 10 5",
            "scale 10 2x",
            "scale 2x 200%",
            "scale 50% 10",
            "scale 50% 1.5x",
            "scale 2.5x 10",
            "scale 10 50%",
        ], """
            11111 1111111111 1111111111 11111111111111111111 1111111111 11111 111111111111 1111111111
            11111 1111111111 1111111111 11111111111111111111 1111111111 11111 111111111111 1111111111
            11111 1111111111 1111111111 11111111111111111111 1111111111 11111 111111111111 1111111111
            11111 1111111111 1111111111 11111111111111111111 1111111111 11111 111111111111 1111111111
            11111 1111111111 1111111111 11111111111111111111 1111111111 11111 111111111111 1111111111
            11111            1111111111 11111111111111111111 1111111111 11111 111111111111
            11111            1111111111 11111111111111111111 1111111111 11111 111111111111
            11111            1111111111 11111111111111111111 1111111111 11111 111111111111
            11111            1111111111 11111111111111111111 1111111111 11111 111111111111
            11111            1111111111 11111111111111111111 1111111111 11111 111111111111
                                        11111111111111111111            11111
                                        11111111111111111111            11111
                                        11111111111111111111            11111
                                        11111111111111111111            11111
                                        11111111111111111111            11111
                                        11111111111111111111
                                        11111111111111111111
                                        11111111111111111111
                                        11111111111111111111
                                        11111111111111111111
        """ )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier :: Add
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Add(SenseTestCase):

    def test_Add_Characters(self): # Created in flex using "new unittest Add_Characters"
        self.assertFlexSequence( [
            "scale 5x2 ; rename 1 0 ; add left 1 L",
            "add right 2 R",
            "add top 3 T",
            "add bottom 4 B",
        ], """
            L00000 L00000RR TTTTTTTT TTTTTTTT
            L00000 L00000RR TTTTTTTT TTTTTTTT
                            TTTTTTTT TTTTTTTT
                            L00000RR L00000RR
                            L00000RR L00000RR
                                     BBBBBBBB
                                     BBBBBBBB
                                     BBBBBBBB
                                     BBBBBBBB
        """ )

    def test_Add_Percentages(self): # Created in flex using "new unittest Add_Percentages"
        self.assertFlexSequence( [
            "scale 5 ; rename 1 0 ; add left 100% L",
            "add right 50% R",
            "add top 20% T",
            "add bottom 17% B",
        ], """
            LLLLL00000 LLLLL00000RRRRR TTTTTTTTTTTTTTT TTTTTTTTTTTTTTT
            LLLLL00000 LLLLL00000RRRRR LLLLL00000RRRRR LLLLL00000RRRRR
            LLLLL00000 LLLLL00000RRRRR LLLLL00000RRRRR LLLLL00000RRRRR
            LLLLL00000 LLLLL00000RRRRR LLLLL00000RRRRR LLLLL00000RRRRR
            LLLLL00000 LLLLL00000RRRRR LLLLL00000RRRRR LLLLL00000RRRRR
                                       LLLLL00000RRRRR LLLLL00000RRRRR
                                                       BBBBBBBBBBBBBBB
        """ )

    def test_Add_Multipliers(self): # Created in flex using "new unittest Add_Multipliers"
        self.assertFlexSequence( [
            "scale 2 ; rename 1 0 ; add left 3x L",
            "add right .25x R",
            "add top .5x T",
            "add bottom 1x B",
        ], """
            LLLLLL00 LLLLLL00RR TTTTTTTTTT TTTTTTTTTT
            LLLLLL00 LLLLLL00RR LLLLLL00RR LLLLLL00RR
                                LLLLLL00RR LLLLLL00RR
                                           BBBBBBBBBB
                                           BBBBBBBBBB
                                           BBBBBBBBBB
        """ )

    def test_Add_DefaultNames(self): # Created in flex using "new unittest Add_DefaultNames"
        self.assertFlexSequence( [
            "add left 1",
            "add right 1",
            "add right 1",
            "add right 1",
            "add right 1",
            "add right 1",
            "add right 1",
            "add right 1",
            "add right 1",
            "add top 1",
            "add bottom 1",
        ], """
            01 012 0123 01234 012345 0123456 01234567 012345678 0123456789 aaaaaaaaaa aaaaaaaaaa
                                                                           0123456789 0123456789
                                                                                      bbbbbbbbbb
        """ )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier :: Break
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Break(SenseTestCase):

    def test_Break_Recursive(self): # Created in flex using "new unittest Break_Recursive"
        self.assertFlexSequence( [
            "break 1 3x2 Q",
            "break R 3x2 q",
            "break r 3x2 1",
            "break 2 2x2 e",
        ], """
            QRS QQQqrsSSS QQQQQQQQQqqq123sssSSSSSSSSS QQQQQQQQQQQQQQQQQQqqqqqq11ef33ssssssSSSSSSSSSSSSSSSSSS
            TUV QQQtuvSSS QQQQQQQQQqqq456sssSSSSSSSSS QQQQQQQQQQQQQQQQQQqqqqqq11gh33ssssssSSSSSSSSSSSSSSSSSS
                TTTUUUVVV QQQQQQQQQtttuuuvvvSSSSSSSSS QQQQQQQQQQQQQQQQQQqqqqqq445566ssssssSSSSSSSSSSSSSSSSSS
                TTTUUUVVV QQQQQQQQQtttuuuvvvSSSSSSSSS QQQQQQQQQQQQQQQQQQqqqqqq445566ssssssSSSSSSSSSSSSSSSSSS
                          TTTTTTTTTUUUUUUUUUVVVVVVVVV QQQQQQQQQQQQQQQQQQttttttuuuuuuvvvvvvSSSSSSSSSSSSSSSSSS
                          TTTTTTTTTUUUUUUUUUVVVVVVVVV QQQQQQQQQQQQQQQQQQttttttuuuuuuvvvvvvSSSSSSSSSSSSSSSSSS
                          TTTTTTTTTUUUUUUUUUVVVVVVVVV QQQQQQQQQQQQQQQQQQttttttuuuuuuvvvvvvSSSSSSSSSSSSSSSSSS
                          TTTTTTTTTUUUUUUUUUVVVVVVVVV QQQQQQQQQQQQQQQQQQttttttuuuuuuvvvvvvSSSSSSSSSSSSSSSSSS
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
                                                      TTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUVVVVVVVVVVVVVVVVVV
        """ )

    def test_Break_Scale(self): # Created in flex using "new unittest Break_Scale"
        self.assertFlexSequence( [
            "break 1 4x2 G ; scale 2x",
            "break G 3x1 a",
            "break H 4x1 d",
            "break I 5x1 h",
            "break J 3x1 m",
            "break K 1x3 x",
            "break L 1x3 X",
            "break a 1x3 Q",
        ], """
            GGHHIIJJ abcHHHIIIJJJ abbcdefgIIIIJJJJ abbbcdeefghijklJJJJJ abbbbcdeeefghijjklmmnnoo
            GGHHIIJJ abcHHHIIIJJJ abbcdefgIIIIJJJJ abbbcdeefghijklJJJJJ abbbbcdeeefghijjklmmnnoo
            KKLLMMNN KKKLLLMMMNNN KKKKLLLLMMMMNNNN KKKKKLLLLLMMMMMNNNNN KKKKKKLLLLLLMMMMMMNNNNNN
            KKLLMMNN KKKLLLMMMNNN KKKKLLLLMMMMNNNN KKKKKLLLLLMMMMMNNNNN KKKKKKLLLLLLMMMMMMNNNNNN

            abbbbcdeeefghijjklmmnnoo abbbbcdeeefghijjklmmnnoo Qbbbbcdeeefghijjklmmnnoo
            abbbbcdeeefghijjklmmnnoo abbbbcdeeefghijjklmmnnoo Rbbbbcdeeefghijjklmmnnoo
            abbbbcdeeefghijjklmmnnoo abbbbcdeeefghijjklmmnnoo Sbbbbcdeeefghijjklmmnnoo
            xxxxxxLLLLLLMMMMMMNNNNNN xxxxxxXXXXXXMMMMMMNNNNNN xxxxxxXXXXXXMMMMMMNNNNNN
            yyyyyyLLLLLLMMMMMMNNNNNN yyyyyyYYYYYYMMMMMMNNNNNN yyyyyyYYYYYYMMMMMMNNNNNN
            zzzzzzLLLLLLMMMMMMNNNNNN zzzzzzZZZZZZMMMMMMNNNNNN zzzzzzZZZZZZMMMMMMNNNNNN
        """ )

    def test_Break_Various(self): # Created in flex using "new unittest Break_Various"
        self.assertFlexSequence( [
            "break 1 7x4 a",
            "break A 3x3 0",
            "break B 5x2 A",
            "break J 1x1 Z",
            "break k 3x2 OQSUWY",
        ], """
            abcdefg aaabbbcccdddeeefffggg aaaaabbbbbcccccdddddeeeeefffffggggg aaaaabbbbbcccccdddddeeeeefffffggggg
            hijklmn aaabbbcccdddeeefffggg aaaaabbbbbcccccdddddeeeeefffffggggg aaaaabbbbbcccccdddddeeeeefffffggggg
            opqrstu aaabbbcccdddeeefffggg aaaaabbbbbcccccdddddeeeeefffffggggg aaaaabbbbbcccccdddddeeeeefffffggggg
            vwxyzAB hhhiiijjjkkklllmmmnnn aaaaabbbbbcccccdddddeeeeefffffggggg aaaaabbbbbcccccdddddeeeeefffffggggg
                    hhhiiijjjkkklllmmmnnn hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn
                    hhhiiijjjkkklllmmmnnn hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn
                    ooopppqqqrrrssstttuuu hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn
                    ooopppqqqrrrssstttuuu hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn hhhhhiiiiijjjjjkkkkklllllmmmmmnnnnn
                    ooopppqqqrrrssstttuuu ooooopppppqqqqqrrrrrssssstttttuuuuu ooooopppppqqqqqrrrrrssssstttttuuuuu
                    vvvwwwxxxyyyzzz012BBB ooooopppppqqqqqrrrrrssssstttttuuuuu ooooopppppqqqqqrrrrrssssstttttuuuuu
                    vvvwwwxxxyyyzzz345BBB ooooopppppqqqqqrrrrrssssstttttuuuuu ooooopppppqqqqqrrrrrssssstttttuuuuu
                    vvvwwwxxxyyyzzz678BBB ooooopppppqqqqqrrrrrssssstttttuuuuu ooooopppppqqqqqrrrrrssssstttttuuuuu
                                          vvvvvwwwwwxxxxxyyyyyzzzzz00122ABCDE vvvvvwwwwwxxxxxyyyyyzzzzz00122ABCDE
                                          vvvvvwwwwwxxxxxyyyyyzzzzz33455ABCDE vvvvvwwwwwxxxxxyyyyyzzzzz33455ABCDE
                                          vvvvvwwwwwxxxxxyyyyyzzzzz33455FGHIJ vvvvvwwwwwxxxxxyyyyyzzzzz33455FGHIZ
                                          vvvvvwwwwwxxxxxyyyyyzzzzz66788FGHIJ vvvvvwwwwwxxxxxyyyyyzzzzz66788FGHIZ

            aaaaaabbbbbbccccccddddddeeeeeeffffffgggggg
            aaaaaabbbbbbccccccddddddeeeeeeffffffgggggg
            aaaaaabbbbbbccccccddddddeeeeeeffffffgggggg
            aaaaaabbbbbbccccccddddddeeeeeeffffffgggggg
            hhhhhhiiiiiijjjjjjOOQQSSllllllmmmmmmnnnnnn
            hhhhhhiiiiiijjjjjjOOQQSSllllllmmmmmmnnnnnn
            hhhhhhiiiiiijjjjjjUUWWYYllllllmmmmmmnnnnnn
            hhhhhhiiiiiijjjjjjUUWWYYllllllmmmmmmnnnnnn
            ooooooppppppqqqqqqrrrrrrssssssttttttuuuuuu
            ooooooppppppqqqqqqrrrrrrssssssttttttuuuuuu
            ooooooppppppqqqqqqrrrrrrssssssttttttuuuuuu
            ooooooppppppqqqqqqrrrrrrssssssttttttuuuuuu
            vvvvvvwwwwwwxxxxxxyyyyyyzzzzzz001122ABCCDE
            vvvvvvwwwwwwxxxxxxyyyyyyzzzzzz334455ABCCDE
            vvvvvvwwwwwwxxxxxxyyyyyyzzzzzz334455FGHHIZ
            vvvvvvwwwwwwxxxxxxyyyyyyzzzzzz667788FGHHIZ
        """ )

    def test_Break_Naming(self): # Created in flex using "new unittest Break_Naming"
        self.assertFlexSequence( [
            "break 1 6x2 Z",
            "break a 13x2",
            "break Z 13x2",
        ], """
            Z01234 ZZZZZZZZZZZZZ00000000000001111111111111222222222222233333333333334444444444444
            56789a ZZZZZZZZZZZZZ00000000000001111111111111222222222222233333333333334444444444444
                   55555555555556666666666666777777777777788888888888889999999999999abcdefghijklm
                   55555555555556666666666666777777777777788888888888889999999999999nopqrstuvwxyz

            ABCDEFGHIJKLM00000000000001111111111111222222222222233333333333334444444444444
            NOPQRSTUVWXYZ00000000000001111111111111222222222222233333333333334444444444444
            55555555555556666666666666777777777777788888888888889999999999999abcdefghijklm
            55555555555556666666666666777777777777788888888888889999999999999nopqrstuvwxyz
        """ )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier :: Drag
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Drag(SenseTestCase):

    def test_Drag_EdgeModify_Example1(self): # Created in flex using "new unittest_ignore Drag_EdgeModify_Example1"
        self.assertFlexSequence( [
            "break 1 6x5 a ; join Au.0 Bvp.1 Cwqk.2 Dxrlf.3 s.w t.Q mn.x o.R ghi.y j.S abcd.z e.T y.X z.Y",
            "drag XY right 5",
        ], """
            zzzzT3 zzzzTT
            yyyS23 yyySSS
            xxR123 xxRRRR
            wQ0123 wQQQQQ
            XY0123 XXXXXX
        """, True ) # Ignore notices

    def test_Drag_EdgeModify_Example2(self): # Created in flex using "new unittest_ignore Drag_EdgeModify_Example2"
        self.assertFlexSequence( [
            "break 1 6x5 a ; join Au.0 Bvp.1 Cwqk.2 Dxrlf.3 s.w t.Q mn.x o.R ghi.y j.S abcd.z e.T y.X z.Y",
            "drag right XY right 4",
        ], """
            zzzzT3 zzzzTT
            yyyS23 yyySSS
            xxR123 xxRRRR
            wQ0123 wQQQQQ
            XY0123 XXXYYY
        """, True ) # Ignore notices

    def test_Drag_EdgeModify_WithScale(self): # Created in flex using "new unittest_ignore Drag_EdgeModify_WithScale"
        self.assertFlexSequence( [
            "break 1 9x6 ; join RIzqh8 QHypg PGxo OFw NE",
            "drag right ABCJKL right 6",
            "drag top * down 100%",
            "drag left * right 100%",
        ], """
            01234567R 012345677 ijklmnnnn m
            9abcdefQR 9abcdefff
            ijklmnPQR ijklmnnnn
            rstuvOPQR rstuvvvvv
            ABCDNOPQR AAABBBCCC
            JKLMNOPQR JJJKKKLLL
        """, True ) # Ignore notices

    def test_Drag_EdgeModify_NoScale(self): # Created in flex using "new unittest_ignore Drag_EdgeModify_NoScale"
        self.assertFlexSequence( [
            "break 1 7x7 ; join 18fm 29g 3a MFyrkd6 LExqjc KDwpi JCvo IBu HA",
            "drag right l right 10",
            "drag bottom * up 100%",
            "drag right * left 100%",
        ], """
            012345M 00000000000 lllllllllll l
            7123bLM 77777777777
            e12hKLM eeeeeeeeeee
            l1nJKLM lllllllllll
            stIJKLM stIIIIIIIII
            zHIJKLM zHIIIIIIIII
            GHIJKLM GHIIIIIIIII
        """, True ) # Ignore notices

    def test_Drag_Expansion_Right(self): # Created in flex using "new unittest_ignore Drag_Expansion_Right"
        self.assertFlexSequence( [
            "break 1 2x3 o ; scale 2x:1x",
            "drag right q right 5",
        ], """
            oopp ooppppp
            qqrr qqqqqqq
            sstt ssttttt
        """, True ) # Ignore notices

    # Released 2.16 without sufficient unit testing; found and fixed the following bugs

    def test_Drag_Fixed1(self): # Created in flex using "new unittest_ignore Drag_Fixed1"
        self.assertFlexSequence( [
            "break 1 2x2 1 ; scale 5x",
            "drag horizontal 1234 down 4",
            "drag horizontal 1234 down 3",
        ], """
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            3333344444 1111122222 1111122222
            3333344444 1111122222 1111122222
            3333344444 1111122222 1111122222
            3333344444 1111122222 1111122222
            3333344444 3333344444 1111122222
                                  1111122222
                                  1111122222
        """, True ) # Ignore notices

    def test_Drag_Fixed2(self): # Created in flex using "new unittest Drag_Fixed2"
        self.assertFlexSequence( [
            "break 1 2x2 1 ; scale 5x",
            "drag horizontal 1234 down 4",
            "drag horizontal 1234 up 2",
        ], """
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            1111122222 1111122222 1111122222
            3333344444 1111122222 1111122222
            3333344444 1111122222 1111122222
            3333344444 1111122222 3333344444
            3333344444 1111122222 3333344444
            3333344444 3333344444 3333344444
        """ )

    def test_Drag_Fixed3(self): # Created in flex using "new unittest Drag_Fixed3"
        self.assertFlexSequence( [
            "scale 36x10 ; break 1 6x2 defghiDEFGHI ; drag r iI l 3",
            "drag bottom ghi down 4",
            "drag horizontal ghiGHI up 1",
        ], """
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII
        """ )

    # Enforce required sorted() of edge overlap in the edgemagnet() function to prevent careless removal

    def test_Drag_Overlap(self): # Created in flex using "new unittest Drag_Overlap"
        self.assertFlexSequence( [
            "scale 36x10 ; break 1 6x2 defghiDEFGHI ; drag r iI l 3",
            "drag bottom ghi down 4",
            "drag bottom ghi up 1",
        ], """
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii ddddddeeeeeeffffffgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFgggggghhhhhhiii
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFgggggghhhhhhiii DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII
            DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII DDDDDDEEEEEEFFFFFFGGGGGGHHHHHHIII
        """ )

    # Mixing edgegroup with scalegroup to make sure the intended edge is dragged when multiple panes factor

    def test_Drag_EdgeScaleMixing(self): # Created in flex using "new unittest Drag_EdgeScaleMixing"
        self.assertFlexSequence( [
            "scale 12x4 ; break 1 4x2 wxyzWXYZ",
            "drag bottom x:yXY down 1",
            "drag top Y:Xxy up 2",
            "drag horizontal XYxy down 2",
            "drag top XY:xy up 1 ; drag left Z:xyzXY right 2",
            "drag right wW:xyXY left 2",
            "drag vertical ZY:ZYxXyz left 2",
            "drag vertical wxWX:wxWXyY right 2",
        ], """
            wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxxyyyyz wxxxxxyyyyyz wxxxxyyyyzzz wwwxxxyyyzzz
            wwwxxxyyyzzz wwwxxxyyyzzz wwwXXXYYYzzz wwwxxxyyyzzz wwwxxxxyyyyz wxxxxxyyyyyz wxxxxyyyyzzz wwwxxxyyyzzz
            WWWXXXYYYZZZ WWWxxxyyyZZZ WWWXXXYYYZZZ WWWxxxyyyZZZ WWWXXXXYYYYZ WXXXXXYYYYYZ WXXXXYYYYZZZ WWWXXXYYYZZZ
            WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXXYYYYZ WXXXXXYYYYYZ WXXXXYYYYZZZ WWWXXXYYYZZZ
        """ )

    # Other tests

    def test_Drag_ExpandAndContract(self): # Created in flex using "new unittest Drag_ExpandAndContract"
        self.assertFlexSequence( [
            "scale 12x4 ; break 1 4x2 wxyzWXYZ",
            "drag bottom X:* down 2",
            "drag right z:* right 4",
            "drag top y:* down 2",
            "drag left w:* right 4",
            "drag bottom * up 2",
            "drag right * left 8",
            "drag top * up 2",
            "drag left * left 8",
        ], """
            wwwxxxyyyzzz wwwxxxyyyzzz wwwwxxxxyyyyzzzz wwwwxxxxyyyyzzzz wwwxxxyyyzzz wwwxxxyyyzzz wxyz wxyz wwwxxxyyyzzz
            wwwxxxyyyzzz wwwxxxyyyzzz wwwwxxxxyyyyzzzz wwwwxxxxyyyyzzzz wwwxxxyyyzzz WWWXXXYYYZZZ WXYZ wxyz wwwxxxyyyzzz
            WWWXXXYYYZZZ wwwxxxyyyzzz wwwwxxxxyyyyzzzz WWWWXXXXYYYYZZZZ WWWXXXYYYZZZ                   WXYZ WWWXXXYYYZZZ
            WWWXXXYYYZZZ WWWXXXYYYZZZ WWWWXXXXYYYYZZZZ WWWWXXXXYYYYZZZZ WWWXXXYYYZZZ                   WXYZ WWWXXXYYYZZZ
                         WWWXXXYYYZZZ WWWWXXXXYYYYZZZZ
                         WWWXXXYYYZZZ WWWWXXXXYYYYZZZZ
        """ )

    def test_Drag_ExpandAndContract_Rel(self): # Created in flex using "new unittest_ignore Drag_ExpandAndContract_Rel"
        self.assertFlexSequence( [
            "scale 12x4 ; break 1 4x2 wxyzWXYZ",
            "drag top y up 100%",
            "drag bottom X down 100%",
            "drag left w left 100%",
            "drag right Z right 100%",
            "drag top y down 25%",
            "drag bottom X up 35%",
            "drag left w right 17%",
            "drag right Z left 25%",
        ], """
            wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wxxxyyyzzz
            wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz wwwxxxyyyzzz WWWXXXYYYZZZ WWWXXXYYYZZZ WXXXYYYZZZ
            WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ
            WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ WWWXXXYYYZZZ

            wxxxyyyz
            WXXXYYYZ
        """, True ) # Ignore notices

    def test_Drag_WithAndWithoutScalegroup(self): # Created in flex using "new unittest Drag_WithAndWithoutScalegroup"
        self.assertFlexSequence( [
            "break 1 4x4 A ; scale 4x",
            "drag left G:* left 4",
            "drag bottom G:* down 4",
            "drag left G left 1",
            "drag bottom G down 1",
            "drag right G right 2",
        ], """
            AAAABBBBCCCCDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD
            AAAABBBBCCCCDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD
            AAAABBBBCCCCDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD
            AAAABBBBCCCCDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD
            EEEEFFFFGGGGHHHH EEFFGGGGGGHHHHHH AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD
            EEEEFFFFGGGGHHHH EEFFGGGGGGHHHHHH AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD AABBCCCCCCDDDDDD
            EEEEFFFFGGGGHHHH EEFFGGGGGGHHHHHH EEFFGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGGGHHHH
            EEEEFFFFGGGGHHHH EEFFGGGGGGHHHHHH EEFFGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGGGHHHH
            IIIIJJJJKKKKLLLL IIJJKKKKKKLLLLLL EEFFGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGGGHHHH
            IIIIJJJJKKKKLLLL IIJJKKKKKKLLLLLL EEFFGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGGGHHHH
            IIIIJJJJKKKKLLLL IIJJKKKKKKLLLLLL EEFFGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGGGHHHH
            IIIIJJJJKKKKLLLL IIJJKKKKKKLLLLLL EEFFGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGHHHHHH EEFGGGGGGGGGHHHH
            MMMMNNNNOOOOPPPP MMNNOOOOOOPPPPPP IIJJKKKKKKLLLLLL IIJJKKKKKKLLLLLL IIFGGGGGGGLLLLLL IIFGGGGGGGGGLLLL
            MMMMNNNNOOOOPPPP MMNNOOOOOOPPPPPP IIJJKKKKKKLLLLLL IIJJKKKKKKLLLLLL IIJJKKKKKKLLLLLL IIJJKKKKKKKKLLLL
            MMMMNNNNOOOOPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP
            MMMMNNNNOOOOPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP MMNNOOOOOOPPPPPP
        """ )

    def test_Drag_AcrossWindowgramEdge(self): # Created in flex using "new unittest_ignore Drag_AcrossWindowgramEdge"
        self.assertFlexSequence( [
            "scale 12 ; break 1 4x4 A",
            "drag right F left 150%",
            "reset ; scale 12 ; break 1 4x4 A ; drag right F right 150%",
            "reset ; scale 12 ; break 1 4x4 A ; drag bottom G up 150%",
            "reset ; scale 12 ; break 1 4x4 A ; drag bottom G down 150%",
        ], """
            AAABBBCCCDDD AAAAAABBBCCCDDD AAABBBCCCDDDDDD AAABBBKKKDDD AAABBBCCCDDD
            AAABBBCCCDDD AAAAAABBBCCCDDD AAABBBCCCDDDDDD AAABBBKKKDDD AAABBBCCCDDD
            AAABBBCCCDDD AAAAAABBBCCCDDD AAABBBCCCDDDDDD AAABBBKKKDDD AAABBBCCCDDD
            EEEFFFGGGHHH GGGGGGGGGGGGHHH EEEFFFFFFFFFFFF AAABBBKKKDDD EEEFFFGGGHHH
            EEEFFFGGGHHH GGGGGGGGGGGGHHH EEEFFFFFFFFFFFF AAABBBKKKDDD EEEFFFGGGHHH
            EEEFFFGGGHHH GGGGGGGGGGGGHHH EEEFFFFFFFFFFFF AAABBBKKKDDD EEEFFFGGGHHH
            IIIJJJKKKLLL IIIIIIJJJKKKLLL IIIJJJKKKLLLLLL EEEFFFKKKHHH IIIJJJGGGLLL
            IIIJJJKKKLLL IIIIIIJJJKKKLLL IIIJJJKKKLLLLLL EEEFFFKKKHHH IIIJJJGGGLLL
            IIIJJJKKKLLL IIIIIIJJJKKKLLL IIIJJJKKKLLLLLL EEEFFFKKKHHH IIIJJJGGGLLL
            MMMNNNOOOPPP MMMMMMNNNOOOPPP MMMNNNOOOPPPPPP IIIJJJKKKLLL MMMNNNGGGPPP
            MMMNNNOOOPPP MMMMMMNNNOOOPPP MMMNNNOOOPPPPPP IIIJJJKKKLLL MMMNNNGGGPPP
            MMMNNNOOOPPP MMMMMMNNNOOOPPP MMMNNNOOOPPPPPP IIIJJJKKKLLL MMMNNNGGGPPP
                                                         MMMNNNOOOPPP MMMNNNGGGPPP
                                                         MMMNNNOOOPPP MMMNNNGGGPPP
                                                         MMMNNNOOOPPP MMMNNNGGGPPP
        """, True ) # Ignore notices

    def test_Drag_Scalegroups(self): # Created in flex using "new unittest Drag_Scalegroups"
        self.assertFlexSequence( [
            "reset ; scale 16x12 ; break 1 4x4 a ; drag ab:efgh:mnop right 3",
            "reset ; scale 16x12 ; break 1 4x4 a ; drag ab:ijkl:mnop:abcd left 3",
            "reset ; scale 16x12 ; break 1 4x4 a ; drag fj:aei:gko:hl up 2",
            "reset ; scale 16x12 ; break 1 4x4 a ; drag gk:abefij:hlp down 2",
        ], """
            aaaaaaabccccdddd abbbbbcccccddddd aaaabbbbccccdddd aaaabbbbccccdddd
            aaaaaaabccccdddd abbbbbcccccddddd aaaabbbbccccdddd aaaabbbbccccdddd
            aaaaaaabccccdddd abbbbbcccccddddd eeeebbbbccccdddd aaaabbbbccccdddd
            eeeeeeefffggghhh eeeeffffgggghhhh eeeeffffgggghhhh aaaabbbbgggghhhh
            eeeeeeefffggghhh eeeeffffgggghhhh iiiijjjjkkkkllll eeeeffffgggghhhh
            eeeeeeefffggghhh eeeeffffgggghhhh iiiijjjjkkkkllll eeeeffffgggghhhh
            iiiijjjjkkkkllll ijjjjjkkkkklllll iiiijjjjkkkkllll eeeeffffgggghhhh
            iiiijjjjkkkkllll ijjjjjkkkkklllll iiiijjjjkkkkllll eeeeffffgggghhhh
            iiiijjjjkkkkllll ijjjjjkkkkklllll iiiijjjjoooollll iiiijjjjkkkkllll
            mmmmmmmnnnoooppp mnnnnnoooooppppp mmmmnnnnoooopppp mmmmnnnnoooollll
            mmmmmmmnnnoooppp mnnnnnoooooppppp mmmmnnnnoooopppp mmmmnnnnoooopppp
            mmmmmmmnnnoooppp mnnnnnoooooppppp mmmmnnnnoooopppp mmmmnnnnoooopppp
        """ )

    def test_Drag_Scalegroups_Empty(self): # Created in flex using "new unittest Drag_Scalegroups_Empty"
        self.assertFlexSequence( [
            "reset ; scale 15x9 ; break 1 3x3 m ; drag pq:mno: right 2",
            "reset ; scale 15x9 ; break 1 3x3 m ; drag pq:: left 2",
            "reset ; scale 15x9 ; break 1 3x3 m ; drag ru: down 2",
            "reset ; scale 15x9 ; break 1 3x3 m ; drag mp::oru up 2",
        ], """
            mmmmmmmnnnnoooo mmmmmnnnnnooooo mmmmmnnnnnooooo mmmmmnnnnnooooo
            mmmmmmmnnnnoooo mmmmmnnnnnooooo mmmmmnnnnnooooo pppppnnnnnrrrrr
            mmmmmmmnnnnoooo mmmmmnnnnnooooo mmmmmnnnnnooooo pppppnnnnnrrrrr
            pppppppqqqrrrrr pppqqqqqqqrrrrr pppppqqqqqrrrrr pppppqqqqqrrrrr
            pppppppqqqrrrrr pppqqqqqqqrrrrr pppppqqqqqrrrrr pppppqqqqqrrrrr
            pppppppqqqrrrrr pppqqqqqqqrrrrr pppppqqqqqrrrrr pppppqqqqquuuuu
            ssssstttttuuuuu ssssstttttuuuuu ssssstttttrrrrr ssssstttttuuuuu
            ssssstttttuuuuu ssssstttttuuuuu ssssstttttrrrrr ssssstttttuuuuu
            ssssstttttuuuuu ssssstttttuuuuu ssssstttttuuuuu ssssstttttuuuuu
        """ )

    def test_Drag_Scalegroups_Errors(self): # Created in flex using "new unittest_ignore Drag_Scalegroups_Errors"
        self.assertFlexSequence( [
            "reset ; scale 15x6 ; break 1 5x2 V ; drag WX:01234z right 1",
            "reset ; scale 15x6 ; break 1 5x2 V ; drag WX:z right 1",
        ], """
            VVVWWWXXXYYYZZZ VVVWWWXXXYYYZZZ
            VVVWWWXXXYYYZZZ VVVWWWXXXYYYZZZ
            VVVWWWXXXYYYZZZ VVVWWWXXXYYYZZZ
            000111222333444 000111222333444
            000111222333444 000111222333444
            000111222333444 000111222333444
        """, True ) # Ignore notices

# This still needs to be implemented: Automatic splitting of scalegroups when they are combined
# At the moment this will work as "drag b D:DdGg:FfIi", but that's already been tested in the above

#    def test_Drag_MultipleEdges(self): # Created in flex using "new unittest Drag_MultipleEdges"
#        self.assertFlexSequence( [
#            "scale 15x8 ; break 1 3x4 defDEFGHIghi",
#            "drag b D:DdGgFfIi down 2",
#        ], """
#            dddddeeeeefffff dddddeeeeefffff
#            dddddeeeeefffff dddddeeeeefffff
#            DDDDDEEEEEFFFFF dddddEEEEEfffff
#            DDDDDEEEEEFFFFF DDDDDEEEEEFFFFF
#            GGGGGHHHHHIIIII DDDDDHHHHHFFFFF
#            GGGGGHHHHHIIIII DDDDDHHHHHFFFFF
#            ggggghhhhhiiiii GGGGGhhhhhIIIII
#            ggggghhhhhiiiii ggggghhhhhiiiii
#        """ )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier :: Insert
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Insert(SenseTestCase):

    def test_Insert_SpreadFavorsTopLeft_50(self): # Created in flex using "new unittest Insert_SpreadFavorsTopLeft_50"
        self.assertFlexSequence( [
            "reset ; break 1 2x2 w",
            "reset ; break 1 2x2 w ; insert xz 1",
            "reset ; break 1 2x2 w ; insert xz 2",
            "reset ; break 1 2x2 w ; insert xz 3",
            "reset ; break 1 2x2 w ; insert xz 4",
            "reset ; break 1 2x2 w ; insert xz 5",
            "reset ; break 1 2x2 w ; insert xz 6",
            "reset ; break 1 2x2 w",
            "reset ; break 1 2x2 w ; insert yz 1",
            "reset ; break 1 2x2 w ; insert yz 2",
            "reset ; break 1 2x2 w ; insert yz 3",
            "reset ; break 1 2x2 w ; insert yz 4",
            "reset ; break 1 2x2 w ; insert yz 5",
            "reset ; break 1 2x2 w ; insert yz 6",
        ], """
            wx wx wx wx wx wx wx wx wwx wwxx wwwxx wwwxxx wwwwxxx wwwwxxxx
            yz w0 w0 w0 w0 w0 w0 yz y0z y00z y000z y0000z y00000z y000000z
               yz y0 w0 w0 w0 w0
                  yz y0 y0 w0 w0
                     yz y0 y0 y0
                        yz y0 y0
                           yz y0
                              yz
        """ )

    def test_Insert_SpreadTests(self): # Created in flex using "new unittest Insert_SpreadTests"
        self.assertFlexSequence( [
            "reset ; break 1 2x2 w",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 0%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 25%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 50%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 75%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 100%",
            "reset ; break 1 2x2 w ; insert vertical wx 10 0 0x",
            "reset ; break 1 2x2 w ; insert vertical wx 10 0 .2x",
            "reset ; break 1 2x2 w ; insert vertical wx 10 0 .5x",
            "reset ; break 1 2x2 w ; insert vertical wx 10 0 .8x",
            "reset ; break 1 2x2 w ; insert vertical wx 10 0 1x",
        ], """
            wx w0000x w0000x w0000x w0000x w0000x w0000000000x w0000000000x w0000000000x w0000000000x w0000000000x
            yz yzzzzz yyzzzz yyyzzz yyyyzz yyyyyz yzzzzzzzzzzz yyyzzzzzzzzz yyyyyyzzzzzz yyyyyyyyyzzz yyyyyyyyyyyz
        """ )

    def test_Insert_SpreadFails(self): # Created in flex using "new unittest_ignore Insert_SpreadFails"
        self.assertFlexSequence( [
            "reset ; break 1 2x2 w",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -0.0001%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -1%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 100.0001%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 101%",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -0.1x",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -1x",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -1.0001x",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -1.1x",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 -1",
            "reset ; break 1 2x2 w ; insert vertical wx 4 0 5",
        ], """
            wx wx wx wx wx wx wx wx wx wx wx
            yz yz yz yz yz yz yz yz yz yz yz
        """, True ) # Ignore notices

    def test_Insert_LockTest_Edge(self): # Created in flex using "new unittest Insert_LockTest_Edge"
        self.assertFlexSequence( [
            "reset ; break 1 3x3 a ; scale 14x:5x ; drag top h:be up 2",
            "insert right g 5 X",
            "reset ; break 1 3x3 a ; scale 14x:5x ; drag right d:ef right 2",
            "insert bottom a 5 X",
        ], """
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaaeeeeeeeeeeeeeecccccccccccccc aaaaaaaaaaaaaaaaaaaeeeeeeeeeeeeeecccccccccccccc
            ddddddddddddddeeeeeeeeeeeeeeffffffffffffff dddddddddddddddddddeeeeeeeeeeeeeeffffffffffffff
            ddddddddddddddeeeeeeeeeeeeeeffffffffffffff dddddddddddddddddddeeeeeeeeeeeeeeffffffffffffff
            ddddddddddddddeeeeeeeeeeeeeeffffffffffffff dddddddddddddddddddeeeeeeeeeeeeeeffffffffffffff
            ddddddddddddddhhhhhhhhhhhhhhffffffffffffff dddddddddddddddddddhhhhhhhhhhhhhhffffffffffffff
            ddddddddddddddhhhhhhhhhhhhhhffffffffffffff dddddddddddddddddddhhhhhhhhhhhhhhffffffffffffff
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ggggggggggggggXXXXXhhhhhhhhhhhhhhiiiiiiiiiiiiii
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ggggggggggggggXXXXXhhhhhhhhhhhhhhiiiiiiiiiiiiii
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ggggggggggggggXXXXXhhhhhhhhhhhhhhiiiiiiiiiiiiii
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ggggggggggggggXXXXXhhhhhhhhhhhhhhiiiiiiiiiiiiii
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ggggggggggggggXXXXXhhhhhhhhhhhhhhiiiiiiiiiiiiii

            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc aaaaaaaaaaaaaabbbbbbbbbbbbbbcccccccccccccc
            ddddddddddddddddeeeeeeeeeeeeefffffffffffff XXXXXXXXXXXXXXbbbbbbbbbbbbbbcccccccccccccc
            ddddddddddddddddeeeeeeeeeeeeefffffffffffff XXXXXXXXXXXXXXbbbbbbbbbbbbbbcccccccccccccc
            ddddddddddddddddeeeeeeeeeeeeefffffffffffff XXXXXXXXXXXXXXbbbbbbbbbbbbbbcccccccccccccc
            ddddddddddddddddeeeeeeeeeeeeefffffffffffff XXXXXXXXXXXXXXbbbbbbbbbbbbbbcccccccccccccc
            ddddddddddddddddeeeeeeeeeeeeefffffffffffff XXXXXXXXXXXXXXbbbbbbbbbbbbbbcccccccccccccc
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ddddddddddddddddeeeeeeeeeeeeefffffffffffff
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ddddddddddddddddeeeeeeeeeeeeefffffffffffff
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ddddddddddddddddeeeeeeeeeeeeefffffffffffff
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ddddddddddddddddeeeeeeeeeeeeefffffffffffff
            gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii ddddddddddddddddeeeeeeeeeeeeefffffffffffff
                                                       gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii
                                                       gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii
                                                       gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii
                                                       gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii
                                                       gggggggggggggghhhhhhhhhhhhhhiiiiiiiiiiiiii
        """ )

    def test_Insert_LockTest_Center(self): # Created in flex using "new unittest Insert_LockTest_Center"
        self.assertFlexSequence( [
            "reset ; break 1 2x2 W ; scale 10x:5x ; drag WY up 1 ; drag XZ down 1",
            "insert XY 4",
            "reset ; break 1 2x2 W ; scale 10x:5x ; drag WY down 1 ; drag XZ up 1",
            "insert WZ 4",
            "reset ; break 1 2x2 W ; scale 10x:5x ; drag WX right 1 ; drag YZ left 1",
            "insert WZ 2",
            "reset ; break 1 2x2 W ; scale 10x:5x ; drag WX left 1 ; drag YZ right 1",
            "insert XY 2",
        ], """
            WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXXXXXX
            WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXXXXXX
            WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXXXXXX
            WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXX WWWWWWWWWWXXXXXXXXXXXXXX
            YYYYYYYYYYXXXXXXXXXX YYYYYYYYYY0000XXXXXXXXXX WWWWWWWWWWZZZZZZZZZZ WWWWWWWWWW0000ZZZZZZZZZZ
            YYYYYYYYYYXXXXXXXXXX YYYYYYYYYY0000XXXXXXXXXX WWWWWWWWWWZZZZZZZZZZ WWWWWWWWWW0000ZZZZZZZZZZ
            YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYYYYYZZZZZZZZZZ
            YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYYYYYZZZZZZZZZZ
            YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYYYYYZZZZZZZZZZ
            YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZZZZZ YYYYYYYYYYZZZZZZZZZZ YYYYYYYYYYYYYYZZZZZZZZZZ

            WWWWWWWWWWWXXXXXXXXX WWWWWWWWWWWXXXXXXXXX WWWWWWWWWXXXXXXXXXXX WWWWWWWWWXXXXXXXXXXX
            WWWWWWWWWWWXXXXXXXXX WWWWWWWWWWWXXXXXXXXX WWWWWWWWWXXXXXXXXXXX WWWWWWWWWXXXXXXXXXXX
            WWWWWWWWWWWXXXXXXXXX WWWWWWWWWWWXXXXXXXXX WWWWWWWWWXXXXXXXXXXX WWWWWWWWWXXXXXXXXXXX
            WWWWWWWWWWWXXXXXXXXX WWWWWWWWWWWXXXXXXXXX WWWWWWWWWXXXXXXXXXXX WWWWWWWWWXXXXXXXXXXX
            WWWWWWWWWWWXXXXXXXXX WWWWWWWWWWWXXXXXXXXX WWWWWWWWWXXXXXXXXXXX WWWWWWWWWXXXXXXXXXXX
            YYYYYYYYYZZZZZZZZZZZ YYYYYYYYY00XXXXXXXXX YYYYYYYYYYYZZZZZZZZZ WWWWWWWWW00ZZZZZZZZZ
            YYYYYYYYYZZZZZZZZZZZ YYYYYYYYY00XXXXXXXXX YYYYYYYYYYYZZZZZZZZZ WWWWWWWWW00ZZZZZZZZZ
            YYYYYYYYYZZZZZZZZZZZ YYYYYYYYYZZZZZZZZZZZ YYYYYYYYYYYZZZZZZZZZ YYYYYYYYYYYZZZZZZZZZ
            YYYYYYYYYZZZZZZZZZZZ YYYYYYYYYZZZZZZZZZZZ YYYYYYYYYYYZZZZZZZZZ YYYYYYYYYYYZZZZZZZZZ
            YYYYYYYYYZZZZZZZZZZZ YYYYYYYYYZZZZZZZZZZZ YYYYYYYYYYYZZZZZZZZZ YYYYYYYYYYYZZZZZZZZZ
                                 YYYYYYYYYZZZZZZZZZZZ                      YYYYYYYYYYYZZZZZZZZZ
                                 YYYYYYYYYZZZZZZZZZZZ                      YYYYYYYYYYYZZZZZZZZZ
        """ )

    def test_Insert_LockTest_Mixed(self): # Created in flex using "new unittest Insert_LockTest_Mixed"
        self.assertFlexSequence( [
            "reset ; break 1 6x4 a ; scale 5x:3x",
            "drag ag:agms up 2 ; drag ou:ouci down 2 ; drag xw:xwv left 2 ; drag jk:jkl right 2",
            "insert ni 1",
            "insert ij 1",
            "insert wp 1",
            "insert mn 1",
            "insert fk 1",
            "insert ba 1",
            "insert gh 1",
            "insert left m 1",
            "insert kr 1",
            "insert right x 1",
        ], """
            aaaaabbbbbcccccdddddeeeeefffff aaaaabbbbbcccccdddddeeeeefffff aaaaabbbbbbcccccdddddeeeeefffff
            aaaaabbbbbcccccdddddeeeeefffff gggggbbbbbcccccdddddeeeeefffff gggggbbbbbbcccccdddddeeeeefffff
            aaaaabbbbbcccccdddddeeeeefffff gggggbbbbbcccccdddddeeeeefffff gggggbbbbbbcccccdddddeeeeefffff
            ggggghhhhhiiiiijjjjjkkkkklllll ggggghhhhhcccccjjjjjjjkkkkllll ggggghhhhhhcccccjjjjjjjkkkkllll
            ggggghhhhhiiiiijjjjjkkkkklllll ggggghhhhhiiiiijjjjjjjkkkkllll ggggghhhhhhiiiiijjjjjjjkkkkllll
            ggggghhhhhiiiiijjjjjkkkkklllll mmmmmhhhhhiiiiijjjjjjjkkkkllll mmmmmhhhhhhiiiiijjjjjjjkkkkllll
            mmmmmnnnnnooooopppppqqqqqrrrrr mmmmmnnnnniiiiipppppqqqqqrrrrr mmmmmnnnnn0iiiiipppppqqqqqrrrrr
            mmmmmnnnnnooooopppppqqqqqrrrrr mmmmmnnnnnooooopppppqqqqqrrrrr mmmmmnnnnnoooooopppppqqqqqrrrrr
            mmmmmnnnnnooooopppppqqqqqrrrrr sssssnnnnnooooopppppqqqqqrrrrr sssssnnnnnoooooopppppqqqqqrrrrr
            ssssstttttuuuuuvvvvvwwwwwxxxxx ssssstttttooooovvvvwwwwxxxxxxx ssssstttttoooooovvvvwwwwxxxxxxx
            ssssstttttuuuuuvvvvvwwwwwxxxxx ssssstttttooooovvvvwwwwxxxxxxx ssssstttttoooooovvvvwwwwxxxxxxx
            ssssstttttuuuuuvvvvvwwwwwxxxxx ssssstttttuuuuuvvvvwwwwxxxxxxx ssssstttttuuuuuuvvvvwwwwxxxxxxx

            aaaaabbbbbbccccccdddddeeeeefffff aaaaabbbbbbccccccdddddeeeeefffff aaaaabbbbbbbccccccdddddeeeeefffff
            gggggbbbbbbccccccdddddeeeeefffff gggggbbbbbbccccccdddddeeeeefffff gggggbbbbbbbccccccdddddeeeeefffff
            gggggbbbbbbccccccdddddeeeeefffff gggggbbbbbbccccccdddddeeeeefffff gggggbbbbbbbccccccdddddeeeeefffff
            ggggghhhhhhccccccjjjjjjjkkkkllll ggggghhhhhhccccccjjjjjjjkkkkllll ggggghhhhhhhccccccjjjjjjjkkkkllll
            ggggghhhhhhiiiii1jjjjjjjkkkkllll ggggghhhhhhiiiii1jjjjjjjkkkkllll ggggghhhhhhhiiiii1jjjjjjjkkkkllll
            mmmmmhhhhhhiiiii1jjjjjjjkkkkllll mmmmmhhhhhhiiiii1jjjjjjjkkkkllll mmmmmhhhhhhhiiiii1jjjjjjjkkkkllll
            mmmmmnnnnn0iiiiippppppqqqqqrrrrr mmmmmnnnnn0iiiiippppppqqqqqrrrrr mmmmm3nnnnn0iiiiippppppqqqqqrrrrr
            mmmmmnnnnnooooooppppppqqqqqrrrrr mmmmmnnnnnooooooppppppqqqqqrrrrr mmmmm3nnnnnooooooppppppqqqqqrrrrr
            sssssnnnnnooooooppppppqqqqqrrrrr sssssnnnnnooooooppppppqqqqqrrrrr ssssssnnnnnooooooppppppqqqqqrrrrr
            ssssstttttoooooovvvvvwwwwxxxxxxx sssssnnnnnoooooovvvvv2qqqqqrrrrr ssssssnnnnnoooooovvvvv2qqqqqrrrrr
            ssssstttttoooooovvvvvwwwwxxxxxxx ssssstttttoooooovvvvvwwwwxxxxxxx sssssstttttoooooovvvvvwwwwxxxxxxx
            ssssstttttuuuuuuvvvvvwwwwxxxxxxx ssssstttttoooooovvvvvwwwwxxxxxxx sssssstttttoooooovvvvvwwwwxxxxxxx
                                             ssssstttttuuuuuuvvvvvwwwwxxxxxxx sssssstttttuuuuuuvvvvvwwwwxxxxxxx

            aaaaabbbbbbbccccccdddddeeeeefffff aaaaa5bbbbbbbccccccdddddeeeeefffff aaaaa5bbbbbbbbccccccdddddeeeeefffff
            gggggbbbbbbbccccccdddddeeeeefffff ggggggbbbbbbbccccccdddddeeeeefffff ggggggbbbbbbbbccccccdddddeeeeefffff
            gggggbbbbbbbccccccdddddeeeeefffff ggggggbbbbbbbccccccdddddeeeeefffff ggggggbbbbbbbbccccccdddddeeeeefffff
            gggggbbbbbbbccccccdddddeeeee4llll ggggggbbbbbbbccccccdddddeeeee4llll ggggggbbbbbbbbccccccdddddeeeee4llll
            ggggghhhhhhhccccccjjjjjjjkkkkllll gggggghhhhhhhccccccjjjjjjjkkkkllll gggggg6hhhhhhhccccccjjjjjjjkkkkllll
            ggggghhhhhhhiiiii1jjjjjjjkkkkllll gggggghhhhhhhiiiii1jjjjjjjkkkkllll gggggg6hhhhhhhiiiii1jjjjjjjkkkkllll
            mmmmmhhhhhhhiiiii1jjjjjjjkkkkllll mmmmmmhhhhhhhiiiii1jjjjjjjkkkkllll mmmmmmmhhhhhhhiiiii1jjjjjjjkkkkllll
            mmmmm3nnnnn0iiiiippppppqqqqqrrrrr mmmmmm3nnnnn0iiiiippppppqqqqqrrrrr mmmmmmm3nnnnn0iiiiippppppqqqqqrrrrr
            mmmmm3nnnnnooooooppppppqqqqqrrrrr mmmmmm3nnnnnooooooppppppqqqqqrrrrr mmmmmmm3nnnnnooooooppppppqqqqqrrrrr
            ssssssnnnnnooooooppppppqqqqqrrrrr sssssssnnnnnooooooppppppqqqqqrrrrr ssssssssnnnnnooooooppppppqqqqqrrrrr
            ssssssnnnnnoooooovvvvv2qqqqqrrrrr sssssssnnnnnoooooovvvvv2qqqqqrrrrr ssssssssnnnnnoooooovvvvv2qqqqqrrrrr
            sssssstttttoooooovvvvvwwwwxxxxxxx ssssssstttttoooooovvvvvwwwwxxxxxxx sssssssstttttoooooovvvvvwwwwxxxxxxx
            sssssstttttoooooovvvvvwwwwxxxxxxx ssssssstttttoooooovvvvvwwwwxxxxxxx sssssssstttttoooooovvvvvwwwwxxxxxxx
            sssssstttttuuuuuuvvvvvwwwwxxxxxxx ssssssstttttuuuuuuvvvvvwwwwxxxxxxx sssssssstttttuuuuuuvvvvvwwwwxxxxxxx

            aaaaaa5bbbbbbbbccccccdddddeeeeefffff aaaaaa5bbbbbbbbccccccdddddeeeeefffff
            gggggggbbbbbbbbccccccdddddeeeeefffff gggggggbbbbbbbbccccccdddddeeeeefffff
            gggggggbbbbbbbbccccccdddddeeeeefffff gggggggbbbbbbbbccccccdddddeeeeefffff
            gggggggbbbbbbbbccccccdddddeeeee4llll gggggggbbbbbbbbccccccdddddeeeee4llll
            ggggggg6hhhhhhhccccccjjjjjjjkkkkllll ggggggg6hhhhhhhccccccjjjjjjjkkkkllll
            ggggggg6hhhhhhhiiiii1jjjjjjjkkkkllll ggggggg6hhhhhhhiiiii1jjjjjjjkkkkllll
            7mmmmmmmhhhhhhhiiiii1jjjjjjjkkkkllll 7mmmmmmmhhhhhhhiiiii1jjjjjjjkkkkllll
            7mmmmmmm3nnnnn0iiiiippppppqqqqqrrrrr 7mmmmmmmhhhhhhhiiiiippppppqqqqq8llll
            7mmmmmmm3nnnnnooooooppppppqqqqqrrrrr 7mmmmmmm3nnnnn0iiiiippppppqqqqqrrrrr
            sssssssssnnnnnooooooppppppqqqqqrrrrr 7mmmmmmm3nnnnnooooooppppppqqqqqrrrrr
            sssssssssnnnnnoooooovvvvv2qqqqqrrrrr sssssssssnnnnnooooooppppppqqqqqrrrrr
            ssssssssstttttoooooovvvvvwwwwxxxxxxx sssssssssnnnnnoooooovvvvv2qqqqqrrrrr
            ssssssssstttttoooooovvvvvwwwwxxxxxxx ssssssssstttttoooooovvvvvwwwwxxxxxxx
            ssssssssstttttuuuuuuvvvvvwwwwxxxxxxx ssssssssstttttoooooovvvvvwwwwxxxxxxx
                                                 ssssssssstttttuuuuuuvvvvvwwwwxxxxxxx

            aaaaaa5bbbbbbbbccccccdddddeeeeeffffff
            gggggggbbbbbbbbccccccdddddeeeeeffffff
            gggggggbbbbbbbbccccccdddddeeeeeffffff
            gggggggbbbbbbbbccccccdddddeeeee4lllll
            ggggggg6hhhhhhhccccccjjjjjjjkkkklllll
            ggggggg6hhhhhhhiiiii1jjjjjjjkkkklllll
            7mmmmmmmhhhhhhhiiiii1jjjjjjjkkkklllll
            7mmmmmmmhhhhhhhiiiiippppppqqqqq8lllll
            7mmmmmmm3nnnnn0iiiiippppppqqqqqrrrrrr
            7mmmmmmm3nnnnnooooooppppppqqqqqrrrrrr
            sssssssssnnnnnooooooppppppqqqqqrrrrrr
            sssssssssnnnnnoooooovvvvv2qqqqqrrrrrr
            ssssssssstttttoooooovvvvvwwwwxxxxxxx9
            ssssssssstttttoooooovvvvvwwwwxxxxxxx9
            ssssssssstttttuuuuuuvvvvvwwwwxxxxxxx9
        """ )

    def test_Insert_LockTest_Small(self): # Created in flex using "new unittest Insert_LockTest_Small"
        self.assertFlexSequence( [
            "reset ; break 1 2x3 1",
            "insert 34 2",
            "reset ; break 1 2x3 1 ; join 24 35 ; rename 6 4",
            "insert 32 2",
            "reset ; break 1 3x2 1 ; join 12 56 ; rename 345 234",
            "insert 14 2",
        ], """
            12 1122 12 1112 112 112
            34 3004 32 3002 344 302
            56 5566 34 3444     302
                                344
        """ )

    def test_Insert_WindowgramEdge_Full(self): # Created in flex using "new unittest Insert_WindowgramEdge_Full"
        self.assertFlexSequence( [
            "break 1 2x2 ; scale 20x10",
            "insert left * 1 L",
            "insert right * 1 R",
            "insert top * 1 T",
            "insert bottom * 1 B",
        ], """
            00000000001111111111 L00000000001111111111 L00000000001111111111R TTTTTTTTTTTTTTTTTTTTTT
            00000000001111111111 L00000000001111111111 L00000000001111111111R L00000000001111111111R
            00000000001111111111 L00000000001111111111 L00000000001111111111R L00000000001111111111R
            00000000001111111111 L00000000001111111111 L00000000001111111111R L00000000001111111111R
            00000000001111111111 L00000000001111111111 L00000000001111111111R L00000000001111111111R
            22222222223333333333 L22222222223333333333 L22222222223333333333R L00000000001111111111R
            22222222223333333333 L22222222223333333333 L22222222223333333333R L22222222223333333333R
            22222222223333333333 L22222222223333333333 L22222222223333333333R L22222222223333333333R
            22222222223333333333 L22222222223333333333 L22222222223333333333R L22222222223333333333R
            22222222223333333333 L22222222223333333333 L22222222223333333333R L22222222223333333333R
                                                                              L22222222223333333333R

            TTTTTTTTTTTTTTTTTTTTTT
            L00000000001111111111R
            L00000000001111111111R
            L00000000001111111111R
            L00000000001111111111R
            L00000000001111111111R
            L22222222223333333333R
            L22222222223333333333R
            L22222222223333333333R
            L22222222223333333333R
            L22222222223333333333R
            BBBBBBBBBBBBBBBBBBBBBB
        """ )

    def test_Insert_WindowgramEdge_Partial(self): # Created in flex using "new unittest Insert_WindowgramEdge_Partial"
        self.assertFlexSequence( [
            "reset ; break 1 4x2 ; scale 40x10",
            "insert left 4 1 L",
            "insert right 3 1 R",
            "insert top 0 1 T",
            "insert bottom 7 1 B",
            "insert top 12 1 t",
            "insert bottom 56 1 b",
        ], """
            0000000000111111111122222222223333333333 00000000000111111111122222222223333333333
            0000000000111111111122222222223333333333 00000000000111111111122222222223333333333
            0000000000111111111122222222223333333333 00000000000111111111122222222223333333333
            0000000000111111111122222222223333333333 00000000000111111111122222222223333333333
            0000000000111111111122222222223333333333 00000000000111111111122222222223333333333
            4444444444555555555566666666667777777777 L4444444444555555555566666666667777777777
            4444444444555555555566666666667777777777 L4444444444555555555566666666667777777777
            4444444444555555555566666666667777777777 L4444444444555555555566666666667777777777
            4444444444555555555566666666667777777777 L4444444444555555555566666666667777777777
            4444444444555555555566666666667777777777 L4444444444555555555566666666667777777777

            00000000000111111111122222222223333333333R TTTTTTTTTTT111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            L44444444445555555555666666666677777777777 00000000000111111111122222222223333333333R
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
                                                       L44444444445555555555666666666677777777777

            TTTTTTTTTTT111111111122222222223333333333R TTTTTTTTTTTtttttttttttttttttttt3333333333R
            00000000000111111111122222222223333333333R TTTTTTTTTTT111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R 00000000000111111111122222222223333333333R
            L44444444445555555555666666666677777777777 00000000000111111111122222222223333333333R
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777 L44444444445555555555666666666677777777777
            L444444444455555555556666666666BBBBBBBBBBB L44444444445555555555666666666677777777777
                                                       L444444444455555555556666666666BBBBBBBBBBB

            TTTTTTTTTTTtttttttttttttttttttt3333333333R
            TTTTTTTTTTT111111111122222222223333333333R
            00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R
            00000000000111111111122222222223333333333R
            L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777
            L44444444445555555555666666666677777777777
            L444444444455555555556666666666BBBBBBBBBBB
            L4444444444bbbbbbbbbbbbbbbbbbbbBBBBBBBBBBB
        """ )

    def test_Insert_ExamplesFromOutline(self): # Created in flex using "new unittest Insert_ExamplesFromOutline"
        self.assertFlexSequence( [
            "reset ; break 1 3x3 1",
            "reset ; break 1 3x3 1 ; insert v 12 2 X",
            "reset ; break 1 3x3 1 ; insert r 3 1 X",
            "reset ; break 1 3x3 1 ; insert r * 1 X",
            "reset ; break 1 3x3 1 ; insert v 1245 1 X",
        ], """
            123 1XX23 123X 123X 1X23
            456 44556 4566 456X 4X56
            789 77889 7899 789X 7789
        """ )

    def test_Insert_Various_1(self): # Created in flex using "new unittest Insert_Various_1"
        self.assertFlexSequence( [
            "break 1 3x3 1",
            "insert 12 4",
            "insert 23 2",
            "insert 58 2",
            "insert 69 1",
            "insert r * 1",
            "insert l * 1",
            "insert t * 1",
            "insert b * 1",
        ], """
            123 1000023 100002aa3 100002aa3 100002aa3 100002aa3d e100002aa3d fffffffffff fffffffffff
            456 4445556 444555566 444555566 444555566 444555566d e444555566d e100002aa3d e100002aa3d
            789 7778889 777888899 444bbbb66 444bbbb66 444bbbb66d e444bbbb66d e444555566d e444555566d
                                  777bbbb99 444bbbbcc 444bbbbccd e444bbbbccd e444bbbb66d e444bbbb66d
                                  777888899 777bbbb99 777bbbb99d e777bbbb99d e444bbbbccd e444bbbbccd
                                            777888899 777888899d e777888899d e777bbbb99d e777bbbb99d
                                                                             e777888899d e777888899d
                                                                                         ggggggggggg
        """ )

    def test_Insert_Various_2(self): # Created in flex using "new unittest Insert_Various_2"
        self.assertFlexSequence( [
            "reset ; break 1 5x4 ; scale 5x:2x",
            "insert vertical 23:567abcfgh 45 A 100%",
            "insert A5 2",
        ], """
            0000011111222223333344444 000001111122222AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3333344444
            0000011111222223333344444 000001111122222AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3333344444
            5555566666777778888899999 5555555555555555555566666666666666666666777777777777777777778888899999
            5555566666777778888899999 5555555555555555555566666666666666666666777777777777777777778888899999
            aaaaabbbbbcccccdddddeeeee aaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbccccccccccccccccccccdddddeeeee
            aaaaabbbbbcccccdddddeeeee aaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbccccccccccccccccccccdddddeeeee
            fffffggggghhhhhiiiiijjjjj ffffffffffffffffffffgggggggggggggggggggghhhhhhhhhhhhhhhhhhhhiiiiijjjjj
            fffffggggghhhhhiiiiijjjjj ffffffffffffffffffffgggggggggggggggggggghhhhhhhhhhhhhhhhhhhhiiiiijjjjj

            000001111122222AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3333344444
            000001111122222AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3333344444
            000001111122222kkkkk66666666666666666666777777777777777777773333344444
            000001111122222kkkkk66666666666666666666777777777777777777778888899999
            5555555555555555555566666666666666666666777777777777777777778888899999
            5555555555555555555566666666666666666666777777777777777777778888899999
            aaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbccccccccccccccccccccdddddeeeee
            aaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbccccccccccccccccccccdddddeeeee
            ffffffffffffffffffffgggggggggggggggggggghhhhhhhhhhhhhhhhhhhhiiiiijjjjj
            ffffffffffffffffffffgggggggggggggggggggghhhhhhhhhhhhhhhhhhhhiiiiijjjjj
        """ )

    def test_Insert_Various_3(self): # Created in flex using "new unittest Insert_Various_3"
        self.assertFlexSequence( [
            "reset ; break 1 4x3 d ; scale 5x:3x",
            "insert vertical hilm 2",
            "insert vertical efij 2",
            "insert vertical jkno 2",
            "insert horizontal deh0i 2",
            "insert horizontal i1jmn 2",
            "insert top fg 2",
            "insert right ko 2",
            "insert bottom mn 2",
            "insert left lh 2",
        ], """
            dddddeeeeefffffggggg ddddddeeeeeefffffggggg ddddddeeeeee11fffffggggg ddddddeeeeee11ffffffgggggg
            dddddeeeeefffffggggg ddddddeeeeeefffffggggg ddddddeeeeee11fffffggggg ddddddeeeeee11ffffffgggggg
            dddddeeeeefffffggggg ddddddeeeeeefffffggggg ddddddeeeeee11fffffggggg ddddddeeeeee11ffffffgggggg
            hhhhhiiiiijjjjjkkkkk hhhhh00iiiiijjjjjkkkkk hhhhh00iiiii11jjjjjkkkkk hhhhh00iiiii11jjjjj22kkkkk
            hhhhhiiiiijjjjjkkkkk hhhhh00iiiiijjjjjkkkkk hhhhh00iiiii11jjjjjkkkkk hhhhh00iiiii11jjjjj22kkkkk
            hhhhhiiiiijjjjjkkkkk hhhhh00iiiiijjjjjkkkkk hhhhh00iiiii11jjjjjkkkkk hhhhh00iiiii11jjjjj22kkkkk
            lllllmmmmmnnnnnooooo lllll00mmmmmnnnnnooooo lllll00mmmmmmnnnnnnooooo lllll00mmmmmmnnnnnn22ooooo
            lllllmmmmmnnnnnooooo lllll00mmmmmnnnnnooooo lllll00mmmmmmnnnnnnooooo lllll00mmmmmmnnnnnn22ooooo
            lllllmmmmmnnnnnooooo lllll00mmmmmnnnnnooooo lllll00mmmmmmnnnnnnooooo lllll00mmmmmmnnnnnn22ooooo

            ddddddeeeeee11ffffffgggggg ddddddeeeeee11ffffffgggggg ddddddeeeeee11555555555555
            ddddddeeeeee11ffffffgggggg ddddddeeeeee11ffffffgggggg ddddddeeeeee11555555555555
            ddddddeeeeee11ffffffgggggg ddddddeeeeee11ffffffgggggg ddddddeeeeee11ffffffgggggg
            33333333333311ffffffgggggg 33333333333311ffffffgggggg ddddddeeeeee11ffffffgggggg
            33333333333311jjjjj22kkkkk 33333333333311jjjjj22kkkkk ddddddeeeeee11ffffffgggggg
            hhhhh00iiiii11jjjjj22kkkkk hhhhh00iiiii11jjjjj22kkkkk 33333333333311ffffffgggggg
            hhhhh00iiiii11jjjjj22kkkkk hhhhh00iiiii11jjjjj22kkkkk 33333333333311jjjjj22kkkkk
            hhhhh00iiiii11jjjjj22kkkkk hhhhh00iiiii11jjjjj22kkkkk hhhhh00iiiii11jjjjj22kkkkk
            lllll00mmmmmmnnnnnn22ooooo hhhhh0044444444444422kkkkk hhhhh00iiiii11jjjjj22kkkkk
            lllll00mmmmmmnnnnnn22ooooo lllll0044444444444422ooooo hhhhh00iiiii11jjjjj22kkkkk
            lllll00mmmmmmnnnnnn22ooooo lllll00mmmmmmnnnnnn22ooooo hhhhh0044444444444422kkkkk
                                       lllll00mmmmmmnnnnnn22ooooo lllll0044444444444422ooooo
                                       lllll00mmmmmmnnnnnn22ooooo lllll00mmmmmmnnnnnn22ooooo
                                                                  lllll00mmmmmmnnnnnn22ooooo
                                                                  lllll00mmmmmmnnnnnn22ooooo

            ddddddeeeeee1155555555555555 ddddddeeeeee1155555555555555 ddddddddeeeeee1155555555555555
            ddddddeeeeee1155555555555555 ddddddeeeeee1155555555555555 ddddddddeeeeee1155555555555555
            ddddddeeeeee11ffffffgggggggg ddddddeeeeee11ffffffgggggggg ddddddddeeeeee11ffffffgggggggg
            ddddddeeeeee11ffffffgggggggg ddddddeeeeee11ffffffgggggggg ddddddddeeeeee11ffffffgggggggg
            ddddddeeeeee11ffffffgggggggg ddddddeeeeee11ffffffgggggggg ddddddddeeeeee11ffffffgggggggg
            33333333333311ffffffgggggggg 33333333333311ffffffgggggggg 3333333333333311ffffffgggggggg
            33333333333311jjjjj22kkkkk66 33333333333311jjjjj22kkkkk66 3333333333333311jjjjj22kkkkk66
            hhhhh00iiiii11jjjjj22kkkkk66 hhhhh00iiiii11jjjjj22kkkkk66 88hhhhh00iiiii11jjjjj22kkkkk66
            hhhhh00iiiii11jjjjj22kkkkk66 hhhhh00iiiii11jjjjj22kkkkk66 88hhhhh00iiiii11jjjjj22kkkkk66
            hhhhh00iiiii11jjjjj22kkkkk66 hhhhh00iiiii11jjjjj22kkkkk66 88hhhhh00iiiii11jjjjj22kkkkk66
            hhhhh0044444444444422kkkkk66 hhhhh0044444444444422kkkkk66 88hhhhh0044444444444422kkkkk66
            lllll0044444444444422ooooo66 lllll0044444444444422ooooo66 88lllll0044444444444422ooooo66
            lllll00mmmmmmnnnnnn22ooooo66 lllll00mmmmmmnnnnnn22ooooo66 88lllll00mmmmmmnnnnnn22ooooo66
            lllll00mmmmmmnnnnnn22ooooo66 lllll00mmmmmmnnnnnn22ooooo66 88lllll00mmmmmmnnnnnn22ooooo66
            lllll00mmmmmmnnnnnn22ooooo66 lllll00mmmmmmnnnnnn22ooooo66 88lllll00mmmmmmnnnnnn22ooooo66
                                         lllll0077777777777722ooooo66 88lllll0077777777777722ooooo66
                                         lllll0077777777777722ooooo66 88lllll0077777777777722ooooo66
        """ )

    def test_Insert_Various_4(self): # Created in flex using "new unittest Insert_Various_4"
        self.assertFlexSequence( [
            "break 1 4x2 1",
            "insert 78:1234 12",
        ], """
            1234 1111222233334444
            5678 5670000000000008
        """ )

    def test_Insert_Various_5(self): # Created in flex using "new unittest Insert_Various_5"
        self.assertFlexSequence( [
            "reset ; break 1 9x2 ; join 0.a 123.b 4.X 567.y 8.z 9a.0 bcdef.1 gh.x ; insert X1 2",
            "reset ; break 1 4x2 ; scale 3xx1x ; drag 56 left 1 ; drag 67 right 1 ; insert horizontal 16 2 x",
        ], """
            abbbXyyyz 000111222333
            abbb2yyyz 00055x222333
            abbb2yyyz 44455x222333
            0011111xx 444556666677
        """ )

    def test_Insert_ThoroughEdgeV1V2(self): # Created in flex using "new unittest Insert_ThoroughEdgeV1V2"
        self.assertFlexSequence( [
            "reset ; break 1 2x1 ; join 0.L 1.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 024.L 3.R 1 5.2 ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 02.L 3.R 1 4.2 5.3 ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 0.1 24.L 3.R 5.2 1.3 ; insert vertical LR 2 x",
            "reset ; break 1 2x3 ; join 2.L 3.R 0 1 4.3 5.4 ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 2.L 35.R 0.1 1.2 4.3 ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 2.L 13.R 0.1 4.2 5.3 ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 2.L 135.R 0.1 4.2 ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 02.L 35.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 02.L 135.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 02.L 13.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 24.L 35.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 24.L 135.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 24.L 13.R ; insert vertical LR 2 z",
            "reset ; break 1 2x3 ; join 024.L 135.R ; insert vertical LR 2 z",
        ], """
            LzzR L111 L111 1133 0011 1122 111R 111R L111 LzzR LzzR 0011 000R 000R LzzR
                 LzzR LzzR LxxR LzzR LzzR LzzR LzzR LzzR LzzR LzzR LzzR LzzR LzzR LzzR
                 L222 2233 L222 3344 333R 2233 222R 444R 444R 4455 LzzR LzzR L555 LzzR
        """ )

    def test_Insert_ThoroughEdgeV3(self): # Created in flex using "new unittest Insert_ThoroughEdgeV3"
        self.assertFlexSequence( [
            "reset ; break 1 2x5 1 ; join 357.L 6.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 35.L 6.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 57.L 6.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 5.L 6.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 5.L 68.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 5.L 46.R ; insert vertical LR 2 x",
            "reset ; break 1 2x5 1 ; join 5.L 468.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 35.L 68.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 35.L 468.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 35.L 46.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 57.L 68.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 57.L 468.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 57.L 46.R ; insert vertical LR 2 z",
            "reset ; break 1 2x5 1 ; join 357.L 468.R ; insert vertical LR 2 z",
        ], """
            1122 1122 1122 1122 1122 1122 1122 1122 1122 1122 1122 1122 1122 1122
            L444 L444 3344 3344 3344 333R 333R L444 LzzR LzzR 3344 333R 333R LzzR
            LzzR LzzR LzzR LzzR LzzR LxxR LzzR LzzR LzzR LzzR LzzR LzzR LzzR LzzR
            L888 7788 L888 7788 777R 7788 777R 777R 777R 7788 LzzR LzzR L888 LzzR
            99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa 99aa
        """ )

    def test_Insert_Scalegroups(self): # Created in flex using "new unittest Insert_Scalegroups"
        self.assertFlexSequence( [
            "reset ; break 1 3x3 1 ; scale 5x 3x ; insert 23:456:789 6",
            "reset ; break 1 3x3 1 ; scale 5x 3x ; insert 78:123:456 6",
            "reset ; break 1 3x3 1 ; scale 5x 3x ; insert top 1:258:369 3",
            "reset ; break 1 3x3 1 ; scale 5x 3x ; insert bottom 9:147:258 3",
        ], """
            111112222200000033333 111111122222223333333 000002222233333 111112222233333
            111112222200000033333 111111122222223333333 000002222233333 111112222233333
            111112222200000033333 111111122222223333333 000002222233333 111112222233333
            444444455555556666666 444444455555556666666 111112222233333 111112222266666
            444444455555556666666 444444455555556666666 111115555566666 444445555566666
            444444455555556666666 444444455555556666666 111115555566666 444445555566666
            777777788888889999999 777770000008888899999 444445555566666 444445555599999
            777777788888889999999 777770000008888899999 444445555566666 444445555599999
            777777788888889999999 777770000008888899999 444448888899999 777778888899999
                                                        777778888899999 777778888800000
                                                        777778888899999 777778888800000
                                                        777778888899999 777778888800000
        """ )



##----------------------------------------------------------------------------------------------------------
##
## Keep this note for adding new unit tests for flex
##
##   flex> new unittest ScaleCommand    # When created, the output switches to a convenient code dump
##   flex> scale 25x10                  # Run commands and the unittest code will be built as you go
##   flex> scale 20x20                  # When finished just paste the generated code into this class
##
##----------------------------------------------------------------------------------------------------------



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex Modifier Combinations
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifierCombination_ScaleCoreDetails(SenseTestCase):

    ## These two tests were already done in a more direct form earlier in the core area

    def test_ScaleCoreDetails_VersionAssert(self): # Created in flex using "new unittest ScaleCoreDetails_VersionAssert"
        # break 1 2x2 ; scale 3x3 ; scale 2x2
        self.assertFlexSequence( [
            "break 1 2x2 ; scale 3x3 ; scale 2x2",
        ], """
            01
            23
        """ )

    def test_ScaleCoreDetails_ScaleRetries(self): # Created in flex using "new unittest ScaleCoreDetails_ScaleRetries"
        # See this commit for the code used to discover this test
        # break 1 11x1 ; scale 46 1 ; break 5 7x1
        self.assertFlexSequence( [
            "break 1 11x1 ; scale 46 1 ; break 5 7x1",
        ], """
            00000001111111222222222333333344444445bcdefg666666677777778888888889999999aaaaaaa
        """ )

class Test_FlexModifierCombination_AddBreakJoin(SenseTestCase):

    ## This asserts the underlying pane order of [0-9a-zA-Z] through default name assignment of the Add command

    def test_AddBreakJoin_DefaultNames(self): # Created in flex using "new unittest AddBreakJoin_DefaultNames"
        self.assertFlexSequence( [
            "break 1 31x2 ; join 210 ba BA YZ",
            "add left 1",
            "add right 1",
            "add top 1",
            "add bottom 1",
            "add top 1",
        ], """
            2223456789bbcdefghijklmnopqrstu 02223456789bbcdefghijklmnopqrstu 02223456789bbcdefghijklmnopqrstu1
            vwxyzBBCDEFGHIJKLMNOPQRSTUVWXYY 0vwxyzBBCDEFGHIJKLMNOPQRSTUVWXYY 0vwxyzBBCDEFGHIJKLMNOPQRSTUVWXYY1

            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
            02223456789bbcdefghijklmnopqrstu1 02223456789bbcdefghijklmnopqrstu1 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
            0vwxyzBBCDEFGHIJKLMNOPQRSTUVWXYY1 0vwxyzBBCDEFGHIJKLMNOPQRSTUVWXYY1 02223456789bbcdefghijklmnopqrstu1
                                              AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0vwxyzBBCDEFGHIJKLMNOPQRSTUVWXYY1
                                                                                AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        """ )



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Readme Demonstrations
##
##----------------------------------------------------------------------------------------------------------------------

class Test_ReadmeDemonstrations(SenseTestCase):

    def test_ReadmeDemonstration1(self): # Created in flex using "new unittest ReadmeDemonstration1"
        self.assertFlexSequence( [
            "scale 25x10",
            "add right 50%",
            "break 0 3x5 A",
            "join ABC.z DG.B EH.L FI.N JM.b KN.l LO.n",
        ], """
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111AAAABBBBCCCC
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111AAAABBBBCCCC
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111DDDDEEEEFFFF
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111DDDDEEEEFFFF
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111GGGGHHHHIIII
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111GGGGHHHHIIII
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111JJJJKKKKLLLL
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111JJJJKKKKLLLL
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111MMMMNNNNOOOO
            1111111111111111111111111 1111111111111111111111111000000000000 1111111111111111111111111MMMMNNNNOOOO

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
        """ )

    def test_ReadmeDemonstration2(self): # Created in flex using "new unittest ReadmeDemonstration2"
        self.assertFlexSequence( [
            "scale 25x10 ; add right 50% ; break 0 3x5 A ; join ABC.z DG.B EH.L FI.N JM.b KN.l LO.n",
            "split 1 bottom 3 s",
            "rename Nn Dd",
            "swap z s Ll Dd",
            "drag left BDLbdl left 50%",
            "insert left s:BDLbdl 6",
        ], """
            1111111111111111111111111zzzzzzzzzzzz 1111111111111111111111111zzzzzzzzzzzz
            1111111111111111111111111zzzzzzzzzzzz 1111111111111111111111111zzzzzzzzzzzz
            1111111111111111111111111BBBBLLLLNNNN 1111111111111111111111111BBBBLLLLNNNN
            1111111111111111111111111BBBBLLLLNNNN 1111111111111111111111111BBBBLLLLNNNN
            1111111111111111111111111BBBBLLLLNNNN 1111111111111111111111111BBBBLLLLNNNN
            1111111111111111111111111BBBBLLLLNNNN 1111111111111111111111111BBBBLLLLNNNN
            1111111111111111111111111bbbbllllnnnn 1111111111111111111111111bbbbllllnnnn
            1111111111111111111111111bbbbllllnnnn sssssssssssssssssssssssssbbbbllllnnnn
            1111111111111111111111111bbbbllllnnnn sssssssssssssssssssssssssbbbbllllnnnn
            1111111111111111111111111bbbbllllnnnn sssssssssssssssssssssssssbbbbllllnnnn

            1111111111111111111111111zzzzzzzzzzzz 1111111111111111111111111ssssssssssss
            1111111111111111111111111zzzzzzzzzzzz 1111111111111111111111111ssssssssssss
            1111111111111111111111111BBBBLLLLDDDD 1111111111111111111111111BBBBDDDDLLLL
            1111111111111111111111111BBBBLLLLDDDD 1111111111111111111111111BBBBDDDDLLLL
            1111111111111111111111111BBBBLLLLDDDD 1111111111111111111111111BBBBDDDDLLLL
            1111111111111111111111111BBBBLLLLDDDD 1111111111111111111111111BBBBDDDDLLLL
            1111111111111111111111111bbbblllldddd 1111111111111111111111111bbbbddddllll
            sssssssssssssssssssssssssbbbblllldddd zzzzzzzzzzzzzzzzzzzzzzzzzbbbbddddllll
            sssssssssssssssssssssssssbbbblllldddd zzzzzzzzzzzzzzzzzzzzzzzzzbbbbddddllll
            sssssssssssssssssssssssssbbbblllldddd zzzzzzzzzzzzzzzzzzzzzzzzzbbbbddddllll

            1111111111111ssssssssssssssssssssssss 1111111111111000000ssssssssssssssssssssssss
            1111111111111ssssssssssssssssssssssss 1111111111111000000ssssssssssssssssssssssss
            1111111111111BBBBBBBBDDDDDDDDLLLLLLLL 1111111111111BBBBBBBBBBDDDDDDDDDDLLLLLLLLLL
            1111111111111BBBBBBBBDDDDDDDDLLLLLLLL 1111111111111BBBBBBBBBBDDDDDDDDDDLLLLLLLLLL
            1111111111111BBBBBBBBDDDDDDDDLLLLLLLL 1111111111111BBBBBBBBBBDDDDDDDDDDLLLLLLLLLL
            1111111111111BBBBBBBBDDDDDDDDLLLLLLLL 1111111111111BBBBBBBBBBDDDDDDDDDDLLLLLLLLLL
            1111111111111bbbbbbbbddddddddllllllll 1111111111111bbbbbbbbbbddddddddddllllllllll
            zzzzzzzzzzzzzbbbbbbbbddddddddllllllll zzzzzzzzzzzzzbbbbbbbbbbddddddddddllllllllll
            zzzzzzzzzzzzzbbbbbbbbddddddddllllllll zzzzzzzzzzzzzbbbbbbbbbbddddddddddllllllllll
            zzzzzzzzzzzzzbbbbbbbbddddddddllllllll zzzzzzzzzzzzzbbbbbbbbbbddddddddddllllllllll
        """ )



