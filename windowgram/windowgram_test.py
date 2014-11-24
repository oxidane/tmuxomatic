#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Copyright 2013-2014, Oxidane
All rights reserved

This source has NOT yet been licensed for redistribution, modification, or inclusion in other projects.

An exception has been granted to the official tmuxomatic project, originating from the following addresses:

    https://github.com/oxidane/tmuxomatic
    https://pypi.python.org/pypi/tmuxomatic

A proper open source license is expected to be applied on or before the release of this windowgram module as a separate
project.  Please check this source at a later date for these changes.

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
## Unit Testing
##
##      Flex unit testing
##
##      Windowgram unit testing
##
## Hashes should not be used in place of windowgrams, they're needed for comparison in case of failure in testing.
##
## A change in source indentation will cause some tests to fail because multiline strings are widely used.
##
##----------------------------------------------------------------------------------------------------------------------
##
## TODO: The runTest() method should sense tests from its class, ordered by line.  Doing so will eliminate need to add
## the test to that method, which is something that is easy to forget when adding tests at a later date.  Should sense
## only the methods that start with "test_" so the custom assert method is not mistakenly included in the tests.
##
##----------------------------------------------------------------------------------------------------------------------

import unittest, io

from windowgram import *



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Windowgram
##
## TODO: Add support for the other windowgram classes and functions.
##
##----------------------------------------------------------------------------------------------------------------------

class TestWindowgram(unittest.TestCase):

    ##
    ## Tests
    ##

    def test_WindowgramGroupConversions_ListToPattern(self):

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

    def test_WindowgramGroupConversions_PatternToList(self):

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

    ##
    ## Run
    ##

    def runTest(self):
        self.test_WindowgramGroupConversions_ListToPattern()
        self.test_WindowgramGroupConversions_PatternToList()



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Flex
##
## TODO: Test all commands comprehensively.
##
##----------------------------------------------------------------------------------------------------------------------
##
## Keep this note for adding new unit tests for flex
##
##   flex> new unittest ScaleCommand    # When created, the output switches to a convenient code dump
##   flex> scale 25x10                  # Run commands and the unittest code will be built as you go
##   flex> scale 20x20                  # When finished just paste the generated code into this class
##
##----------------------------------------------------------------------------------------------------------------------

class TestFlex(unittest.TestCase):

    ##----------------------------------------------------------------------------------------------------------
    ##
    ##  Performs flex commands and compares the resulting windowgrams with those specified
    ##
    ##  Commands        List of strings, each string may have multiple commands but corresponds to one windowgram
    ##  Pattern         Windowgram pattern, where they are ordered left to right, top to bottom, with first line 1-N
    ##  Build           OPTIONAL: If specified it will add the new windowgram(s) into the existing one and print it
    ##
    ##----------------------------------------------------------------------------------------------------------

    def assertFlexSequence(self, commands, pattern, build=None):
        windowgramgroup_list = WindowgramGroup_Convert.Pattern_To_List( pattern )
        cmdlen, ptnlen = len(commands), len(windowgramgroup_list)
        if cmdlen != ptnlen:
            raise Exception( "Mismatch: commands (" + str(cmdlen) + ") and windowgrams (" + str(ptnlen) + ")" )
        wg = Windowgram( "1" ) # Specified in case the default changes
        for ix, (command, windowgram) in enumerate( zip( commands, windowgramgroup_list ) ):
            errors = flex_processor( wg, command )
            self.assertTrue( not errors, errors )
            self.assertTrue( wg.Export_String() == windowgram, 
                "The resulting windowgram for sequence #" + str(ix+1) + " does not match: \n\n" + wg.Export_String() )

    ##----------------------------------------------------------------------------------------------------------
    ##
    ## Tests
    ##
    ##----------------------------------------------------------------------------------------------------------

    ##
    ## Flex Scale
    ##

    ##
    ## Readme Demonstration
    ##

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

    ##----------------------------------------------------------------------------------------------------------
    ##
    ## Run
    ##
    ##----------------------------------------------------------------------------------------------------------

    def runTest(self):
        self.test_ReadmeDemonstration1()



##----------------------------------------------------------------------------------------------------------------------
##
## Unit Testing :: Main
##
##----------------------------------------------------------------------------------------------------------------------

def UnitTests():

    ##
    ## Unit tests (low level first)
    ##

    units = [
        TestWindowgram(),
        TestFlex(),
    ]

    ##
    ## Iterate
    ##

    stream = io.StringIO()
    runner = unittest.TextTestRunner( stream=stream )
    error = ""
    for unit in units:
        result = runner.run( unit )
        if not result.wasSuccessful():
            if not error: error = "\n"
            error = error + result.failures[0][1]
    return error if error else None



