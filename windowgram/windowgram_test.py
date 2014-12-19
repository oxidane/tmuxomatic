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

def UnitTests():
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
            for method in methods: method[0]()
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
        wg = Windowgram( "1" ) # Specified in case the default changes
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

    def test_Windowgram_Convert_Purify(self):
        data_i = "\n\n1135      \n1145 # etc\n2245\n\n"
        data_o = "1135\n1145\n2245\n"
        data_x = Windowgram_Convert.Purify( data_i )
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

    ## Enforces the use of scale core v1, and will fail if v2 is reactivated.  See notes in scale core.

    def test_ScaleCoreDifference_CaseOne(self): # Created in flex using "new unittest ScaleCoreDifference_CaseOne"
        # break 1 2x2 ; scale 3x3 ; scale 2x2
        wg_i = "01\n23\n"
        wg_o = scalecore( wg_i, 3, 3 )
        wg_o = scalecore( wg_o, 2, 2 )
        self.assertTrue( wg_o == wg_i )

    ## Tests the scale core multiple resizing that's necessary in some situations.  See notes in scale core.
    ## TODO: Move this into the unit testing for the break command

    def test_ScaleCoreDifference_CaseTwo(self): # Created in flex using "new unittest ScaleCoreDifference_CaseTwo"
        # scale 42x42 ; break 1 6x6 ; break 1 3x3
        self.assertFlexSequence( [
            "scale 42x42 ; break 1 6x6 ; break 1 3x3",
        ], """
            000000000111AAABBB222222222333333333444444444555555555
            000000000111AAABBB222222222333333333444444444555555555
            000000000111AAABBB222222222333333333444444444555555555
            000000000CCCDDDEEE222222222333333333444444444555555555
            000000000CCCDDDEEE222222222333333333444444444555555555
            000000000CCCDDDEEE222222222333333333444444444555555555
            000000000FFFGGGHHH222222222333333333444444444555555555
            000000000FFFGGGHHH222222222333333333444444444555555555
            000000000FFFGGGHHH222222222333333333444444444555555555
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            666666666777777777888888888999999999aaaaaaaaabbbbbbbbb
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            cccccccccdddddddddeeeeeeeeefffffffffggggggggghhhhhhhhh
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            iiiiiiiiijjjjjjjjjkkkkkkkkklllllllllmmmmmmmmmnnnnnnnnn
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            ooooooooopppppppppqqqqqqqqqrrrrrrrrrsssssssssttttttttt
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
            uuuuuuuuuvvvvvvvvvwwwwwwwwwxxxxxxxxxyyyyyyyyyzzzzzzzzz
        """ )

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
                if not axis: parsedpane = Windowgram_Convert.Transpose_Pane( parsedpane )
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
## Unit Testing :: Flex Modifier :: Drag
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifier_Drag(SenseTestCase):

    def test_Drag_EdgeMorphing(self): # Created in flex using "new unittest Drag_EdgeMorphing"
        self.assertFlexSequence( [
            "break 1 6x5 a ; join Au.0 Bvp.1 Cwqk.2 Dxrlf.3 s.w t.Q mn.x o.R ghi.y j.S abcd.z e.T y.X z.Y",
        ], """
            zzzzT3
            yyyS23
            xxR123
            wQ0123
            XY0123
        """ )

    # Ignore notices
    def test_Drag_EdgeModify_Example1(self): # Created in flex using "new unittest Drag_EdgeModify_Example1"
        self.assertFlexSequence( [
            "break 1 6x5 a ; join Au.0 Bvp.1 Cwqk.2 Dxrlf.3 s.w t.Q mn.x o.R ghi.y j.S abcd.z e.T y.X z.Y",
            "drag XY right 5",
        ], """
            zzzzT3 zzzzTT
            yyyS23 yyySSS
            xxR123 xxRRRR
            wQ0123 wQQQQQ
            XY0123 XXXXXX
        """, True )

    # Ignore notices
    def test_Drag_EdgeModify_Example2(self): # Created in flex using "new unittest Drag_EdgeModify_Example2"
        self.assertFlexSequence( [
            "break 1 6x5 a ; join Au.0 Bvp.1 Cwqk.2 Dxrlf.3 s.w t.Q mn.x o.R ghi.y j.S abcd.z e.T y.X z.Y",
            "drag right XY right 4",
        ], """
            zzzzT3 zzzzTT
            yyyS23 yyySSS
            xxR123 xxRRRR
            wQ0123 wQQQQQ
            XY0123 XXXYYY
        """, True )

    # Ignore notices
    def test_Drag_EdgeModify_WithScale(self): # Created in flex using "new unittest Drag_EdgeModify_WithScale"
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
        """, True )

    # Ignore notices
    def test_Drag_EdgeModify_NoScale(self): # Created in flex using "new unittest Drag_EdgeModify_NoScale"
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
        """, True )

    # Ignore notices
    def test_Drag_Expansion_Right(self): # Created in flex using "new unittest Drag_Expansion_Right"
        self.assertFlexSequence( [
            "break 1 2x3 o ; scale 2x:1x",
            "drag right q right 5",
        ], """
            oopp ooppppp
            qqrr qqqqqqq
            sstt ssttttt
        """, True )



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
## Unit Testing :: Flex Modifier Combination :: AddBreakJoin
##
## This asserts the underlying pane order of [0-9a-zA-Z] through default name assignment of the Add command.  It must
## follow the commands it depends upon: add, break, and join.
##
##----------------------------------------------------------------------------------------------------------------------

class Test_FlexModifierCombination_AddBreakJoin(SenseTestCase):

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
        """ )



