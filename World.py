# coding: UTF-8
#
# This file is part of the pyTile project
#
# http://entropy.me.uk/pytile
#
## Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.
##
## Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
##
## 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
##
## 3. The name of the author may not be used to endorse or promote products derived from this software without specific prior written permission from the author.
##
## 4. Products derived from this software may not be called "pyTile" nor may "pyTile" appear in their names without specific prior written permission from the author.
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 



import os, sys
import pygame
import random

import Tools

# Pre-compute often used multiples
p = 64
p2 = p / 2
p4 = p / 4
p4x3 = p4 * 3
p8 = p / 8
p16 = p / 16

#tile height difference
ph = 8


class World:
    """Holds all world-related variables and methods"""

    # Constants
    SEA_LEVEL = 0
                    # Display variables (need moving to world class?)
    dxoff = 0       # Horizontal offset position of displayed area
    dyoff = 0       # Vertical offset (from top)

    # Hitboxes for subtile selection
    # 0 = Nothing
    # 1 = Left vertex
    # 2 = Bottom vertex
    # 3 = Right vertex
    # 4 = Top vertex
    # 5 = Bottom-left edge
    # 6 = Bottom-right edge
    # 7 = Top-right edge
    # 8 = Top-left edge
    # 9 = Face

    type_lookup = [[0,0,0,0],[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1],[1,1,1,1]]

    type = {}

    # Flat tile
    type["0000"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,8,8,9,9,7,7,0],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Left vertex
    type["1000"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,8,4,4,0,0,0],
                    [1,1,8,4,4,7,0,0],
                    [1,1,8,9,9,7,7,0],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,9,3,3],
                    [0,0,5,9,9,6,6,0],
                    [0,0,0,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Bottom vertex
    type["0100"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,8,8,9,9,7,7,0],
                    [1,1,9,9,9,9,3,3],
                    [1,1,5,2,2,6,3,3],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Right vertex
    type["0010"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,7,0,0],
                    [0,0,8,4,4,7,3,3],
                    [0,8,8,9,9,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,6,6,0],
                    [0,5,5,9,9,6,0,0],
                    [0,0,5,2,2,0,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Top vertex
    type["0001"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,1,8,9,9,7,3,0],
                    [1,1,8,9,9,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Bottom-Left edge
    type["1100"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,8,4,4,0,0,0],
                    [1,1,8,4,4,7,0,0],
                    [1,1,8,9,9,7,7,0],
                    [1,1,5,9,9,9,3,3],
                    [0,5,5,2,2,6,3,3],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Bottom-Right edge
    type["0110"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,7,0,0],
                    [0,0,8,4,4,7,3,3],
                    [0,8,8,9,9,7,3,3],
                    [1,1,9,9,9,6,3,3],
                    [1,1,5,2,2,6,6,0],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Top-Right edge
    type["0011"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,0,8,9,9,7,3,3],
                    [0,8,8,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,6,6,0],
                    [0,5,5,9,9,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Top-Left edge
    type["1001"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,0,8,4,4,7,0,0],
                    [1,1,8,9,9,7,0,0],
                    [1,1,9,9,9,7,7,0],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,9,3,3],
                    [0,5,5,9,9,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Right vertex down
    type["1101"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,8,8,9,9,7,7,0],
                    [1,1,9,9,9,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,5,9,9,6,3,3],
                    [0,5,5,2,2,6,3,3],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,0,0,0,0,0],]
    # Top vertex down
    type["1110"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,8,8,4,4,7,7,0],
                    [1,8,8,4,4,7,7,3],
                    [1,1,8,4,4,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,5,9,9,6,3,3],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,0,0,0,0,0],]
    # Left vertex down
    type["0111"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,8,8,9,9,7,7,0],
                    [1,1,8,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,5,9,9,6,3,3],
                    [1,1,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,0,0,0,0,0],]
    # Bottom vertex down
    type["1011"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,8,8,9,9,7,7,0],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,6,6,0],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Left vertex two-up
    type["2101"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,8,4,4,0,0,0],
                    [1,1,8,4,4,7,7,0],
                    [1,1,8,4,4,7,7,3],
                    [1,1,8,4,4,7,3,3],
                    [1,1,5,9,9,9,3,3],
                    [0,5,5,9,9,6,3,3],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,0,0,0,0,0],]
    # Bottom vertex two-up
    type["1210"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,8,8,4,4,7,7,0],
                    [1,8,8,4,4,7,7,3],
                    [1,1,8,4,4,7,3,3],
                    [1,1,5,9,9,6,3,3],
                    [1,1,5,2,2,6,3,3],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,0,0,0,0,0],]
    # Right vertex two-up
    type["0121"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,7,0,0],
                    [0,8,8,4,4,7,3,3],
                    [1,8,8,4,4,7,3,3],
                    [1,1,8,4,4,7,3,3],
                    [1,1,9,9,9,6,3,3],
                    [1,1,5,9,9,6,6,0],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,0,0,0,0,0],]
    # Top vertex two-up
    type["1012"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,8,8,9,9,7,7,0],
                    [1,1,8,9,9,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,6,6,0],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Left & Right vertices up
    type["1010"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [1,1,8,4,4,7,3,3],
                    [1,1,8,9,9,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [0,5,5,9,9,6,6,0],
                    [0,0,5,9,9,6,0,0],
                    [0,0,0,2,2,0,0,0],
                    [0,0,0,2,2,0,0,0],]
    # Bottom & Top vertices up
    type["0101"] = [[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,4,4,0,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,0,8,4,4,7,0,0],
                    [0,1,8,9,9,7,3,0],
                    [1,1,8,9,9,7,3,3],
                    [1,1,9,9,9,9,3,3],
                    [1,1,5,2,2,6,3,3],
                    [0,5,5,2,2,6,6,0],
                    [0,0,5,2,2,6,0,0],
                    [0,0,0,2,2,0,0,0],]



    def __init__(self):
        World.dxoff = 0
        World.dyoff = 0
        World.array = self.MakeArray()
        World.WorldX = len(self.array)
        World.WorldY = len(self.array[0])

        # Width and Height of the world, in pixels
        World.WorldWidth = (World.WorldX + World.WorldY) * p2
        World.WorldWidth2 = World.WorldWidth / 2
        World.WorldHeight = ((World.WorldX + World.WorldY) * p4) + p2
        # Width and Height of the world, in pixels
        World.WorldWidth = (World.WorldX + World.WorldY) * p2
        World.WorldWidth2 = World.WorldWidth / 2
        World.WorldHeight = ((World.WorldX + World.WorldY) * p4) + p2

    # Tile structure [height, vertexheight[left, bottom, right, top]]


    def MakeArray(self):
##        TileMap = []
##        for i in range(30):
##            t = []
##            for j in range(30):
##                t.append([random.randint(0, 2),[0,0,0,0]])
##            TileMap.append(t)
##        print len(TileMap), len(TileMap[0])

        TileMap = [[[2,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[2,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[4,[0,0,0,0]],[3,[0,0,0,0]],[2,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[6,[0,0,0,0]],[6,[0,0,0,0]],[6,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[3,[0,0,0,0]],[3,[0,0,0,0]],[2,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,0,0]],[0,[1,1,0,0]],[0,[1,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[6,[0,0,0,0]],[12,[0,0,0,0]],[6,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[2,[0,0,0,0]],[2,[0,0,0,0]],[1,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,0,0]],[0,[1,2,1,0]],[1,[1,1,0,0]],[0,[2,1,0,1]],[0,[1,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[6,[0,0,0,0]],[6,[0,0,0,0]],[6,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,1,0]],[1,[0,1,1,0]],[2,[0,0,0,0]],[1,[1,0,0,1]],[0,[1,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[5,[0,0,1,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,1,0]],[0,[0,1,2,1]],[1,[0,0,1,1]],[0,[1,0,1,2]],[0,[0,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[4,[0,0,1,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,1,0]],[0,[0,0,1,1]],[0,[0,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[3,[0,0,1,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[2,[0,0,1,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[1,[0,0,1,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,0,0]],[0,[1,1,0,0]],[0,[1,1,0,0]],[0,[1,1,0,0]],[0,[1,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,1,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,1,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[0,[1,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,0,0]],[0,[1,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,1,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[0,[1,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,1,0]],[0,[0,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,1,1,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[1,[0,0,0,0]],[0,[1,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,1,0]],[0,[0,0,1,1]],[0,[0,0,1,1]],[0,[0,0,1,1]],[0,[0,0,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[1,1,1,0]],[0,[0,0,0,0]],[0,[0,1,1,1]],[0,[0,0,0,0]],[0,[1,0,1,1]],[0,[0,0,0,0]],[0,[1,1,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[1,1,0,0]],[0,[0,0,0,0]],[0,[0,1,1,0]],[0,[0,0,0,0]],[0,[0,0,1,1]],[0,[0,0,0,0]],[0,[1,0,0,1]],[0,[0,0,0,0]],[0,[1,0,1,0]],[0,[0,0,0,0]],[0,[0,1,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[1,0,0,0]],[0,[0,0,0,0]],[0,[0,1,0,0]],[0,[0,0,0,0]],[0,[0,0,1,0]],[0,[0,0,0,0]],[0,[0,0,0,1]],[0,[0,0,0,0]],[0,[1,2,1,0]],[0,[0,0,0,0]],[0,[0,1,2,1]],[0,[0,0,0,0]],[0,[1,0,1,2]],[0,[0,0,0,0]],[0,[2,1,0,1]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],
                   [[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],[0,[0,0,0,0]],],]
                   
        return(TileMap)


# Terrain can be modified in several ways
# Easiest is a one-tile approach, this affects only one vertex/edge/face of a tile and has no effect on neighbouring tiles
# Next is one-tile approach which does affect neighbours, this is a "smooth" modification
# Finally multi-tile smooth/sharp deformations

# Functions in World are hooked into by functions in the GUI of the main program

    def set_height(self, tgrid, x, y=None):
        """Sets the height of a tile"""
        if y is None:
            x, y = x
        self.array[x][y][0] = tgrid.height
        self.array[x][y][1] = tgrid.array

    def get_height(self, x, y=None):
        """Get height of a tile, return as TGrid object"""
        if y is None:
            x, y = x
        return Tools.TGrid(self.array[x][y][0], self.array[x][y][1])

    def modify_tiles(self, array, tiles, action, softedges):
        """array=world array, tiles=list of tiles to alter, action=raise,lower,smooth, softedges=True,False"""
        # Multi-tile/single-tile are essentially the same internally
        # On multi-tile, we lower from the highest point, raise from the lowest point, affecting any slopes first
        #  smoothing is a click'n'drag operation, all tiles in tiles will be smoothed to the value of the first entry
        #  if the first entry is a slope, then this will be smoothed flat, to its baseline level, smoothing can be soft or hard in application
























# The following functions are not used anymore, and are kept for reference from an earlier version

    def LowerTile(self, array, x, y):
        """Decreases height of a single tile, taking care
        of changes to landscape caused by this"""
        
        # Must ensure that tiles surrounding one lowered end up the
        # same height as the one which has been lowered, so, firstly
        # lower the tile in question...
        # But only if the tile is flat, if it's a slope nothing needs to be done
        if array[x][y][1] == 14:
            array[x][y][0] = array[x][y][0] - 1

        # Now, check 8 surrounding tiles, if they are higher than
        # the tile we just lowered, we need to make them the same height,
        # if they are lower we can leave them alone (I think?)
        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) >= 0 and (x+xx) < len(array[0]):
                    if (y+yy) >= 0 and (y+yy) < len(array):
                        if array[x][y][0] < array[x+xx][y+yy][0]:
                            array[x+xx][y+yy][0] = array[x][y][0]
                            
        # Now proceed as for RaiseTile
        # May need additional work to ensure that all tiles touched by previous
        # process are added to stack at the beginning?

        # Next, initialise a stack for iterating through tiles affected by this lowering
        # Will be initialised with the 8 tiles surrounding the lowered tile
        # As well as the tile itself
        # If the tiles fall outside the map, don't add them to the stack...
        stack = []
        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) >= 0 and (x+xx) < len(array[0]):
                    if (y+yy) >= 0 and (y+yy) < len(array):
                        if array[x][y][0] < array[x+xx][y+yy][0]:
                            array[x+xx][y+yy][0] = array[x][y][0]
                            
                        for xxx in range(-1,2):
                            for yyy in range(-1,2):
                                if (x+xx+xxx) >= 0 and (x+xx+xxx) < len(array[0]):
                                    if (y+yy+yyy) >= 0 and (y+yy+yyy) < len(array):
                                        stack.append([(x+xx+xxx), (y+yy+yyy)])
##                        else:
##                            stack.append([(x+xx), (y+yy)])
                        #ret = world.Test9(self.array, x + xx, y + yy)

        # Now, for all the members of the stack, run the Test9 algorythm on them
        # If Test9 returns a set of coords, add them to the stack, continue until
        # Nothing is left in the stack
        while len(stack) != 0:
            h = stack.pop(0)
            ret = self.Test9(array, h[0], h[1], 0)
            if ret != 0:

                #stack.append([ret[0], ret[1]])
                for xx in range(-1,2):
                    for yy in range(-1,2):
                        if (ret[0]+xx) >= 0 and (ret[0]+xx) < len(array[0]):
                            if (ret[1]+yy) >= 0 and (ret[1]+yy) < len(array):
                                stack.append([(ret[0]+xx), (ret[1]+yy)])
                                #ret = world.Test9(self.array, x + xx, y + yy)

        return 0

    def RaiseTile(self, array, x, y):
        """Increase height of a single tile, and take care
        of changes to landscape caused by this"""
        
        # Firstly, raise the height of the selected tile
        array[x][y][0] = array[x][y][0] + 1

        # Next, initialise a stack for iterating through tiles affected by this raise
        # Will be initialised with the 8 tiles surrounding the raised tile
        # As well as the tile itself
        # If the tiles fall outside the map, don't add them to the stack...
        stack = []
        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) >= 0 and (x+xx) < len(array[0]):
                    if (y+yy) >= 0 and (y+yy) < len(array):
                        stack.append([(x+xx), (y+yy)])
                        #ret = world.Test9(self.array, x + xx, y + yy)

        # Now, for all the members of the stack, run the Test9 algorythm on them
        # If Test9 returns a set of coords, add them to the stack, continue until
        # Nothing is left in the stack
        while len(stack) != 0:
            h = stack.pop(0)
            ret = self.Test9(array, h[0], h[1], 1)
            if ret != 0:
                # May need changing to be all surrounding actually...
                #stack.append([ret[0], ret[1]])
                for xx in range(-1,2):
                    for yy in range(-1,2):
                        if (ret[0]+xx) >= 0 and (ret[0]+xx) < len(array[0]):
                            if (ret[1]+yy) >= 0 and (ret[1]+yy) < len(array):
                                stack.append([(ret[0]+xx), (ret[1]+yy)])
                                #ret = world.Test9(self.array, x + xx, y + yy)

        return 0


    def TestZdiff(self, array, x, y, updown):
        """Function to test the tile height difference between
        the specified tile and its neighbours, if height difference
        doesn't exceed 1, then return 0, else return height difference
        (this can be negative, to indicate direction of height difference)"""

    #--------------This function needs rewriting for speed--------------#


        # Check all surrounding tiles, if:
        #   First, if there's no 2+ difference, do nothing... Else:
        #   1) This tile is taller/same size than all surrounding:
        #       a) If updown = 1, do nothing
        #       b) If updown = 0, lower tile by 1 & recalc
        #   2) This tile is smaller/same size than all surrounding:
        #       a) If updown = 1, raise tile by 1 & recalc
        #       b) If updown = 0, do nothing
        #   3) Else:
        #       a) If updown = 1, raise tile by 1 & recalc
        #       b) If updown = 0, lower tile by 1 & recalc
        
        diff = 0
        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) >= 0 and (x+xx) < len(array[0]):
                    if (y+yy) >= 0 and (y+yy) < len(array):

                        # Tile is in array, continue with tests...
                        # First, is there a 2+ difference anywhere?
                        if array[x][y][0] != array[x+xx][y+yy][0]:
                            aa = array[x][y][0] - array[x+xx][y+yy][0]
                            if aa > 1 or aa < -1:
                                diff = 1
        # If no difference, nothing needs to be done
        if diff == 0:                                
            return 0

        diff = 0
        diffpos = 0
        diffneg = 0
        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) >= 0 and (x+xx) < len(array[0]):
                    if (y+yy) >= 0 and (y+yy) < len(array):

                        # Tile is in array, continue with tests...
                        # Second, check all diffs, if all +ve or all -ve,
                        # then use last rule
                        if array[x][y][0] != array[x+xx][y+yy][0]:
                            aa = array[x][y][0] - array[x+xx][y+yy][0]
                            if aa > 1:
                                diffpos = 1
                            elif aa < -1:
                                diffneg = 1
                                
        # If only one is 1, then nothing needs to be done...
        if diffpos == 1 and diffneg == 0:
            if updown == 0:
                array[x][y][0] = array[x][y][0] - 1
                return 1
            else:
                return 0
        elif diffpos == 0 and diffneg == 1:
            if updown == 0:
                #array[x][y][0] = array[x][y][0] - 1
                return 0
            else:
                array[x][y][0] = array[x][y][0] + 1
                return 1
        else:
            if updown == 0:
                array[x][y][0] = array[x][y][0] - 1
                return 1
            else:
                array[x][y][0] = array[x][y][0] + 1
                return 1



    def Test9(self, array, x, y, updown=1):
        """Determines the slope or height change of a tile
        based on the characteristics of the 8 surrounding tiles
        will return either 0, indicating no further action, or
        will return the inputted coords (for another iteration),
        this happens only if the height of a tile is changed by
        a rule
        updown specifies whether terrain is being raised or lowered
        (for level gap calculation)"""
        # Straight slopes (high)
        # Needs some sort of more generic system for this really...

        # Rules to deal with cases where land needs to be raised
        # in these cases we need to re-do all the calcs for the
        # surrounding tiles, to give a degree of recursivity

        # First, check a tile's neighbours to see if there are any
        # height differences greater than 1, if so raise/lower the
        # tile based on whatever action will remove the large gap
        # (again, needs to be recursive, but this will be handled
        # the same way most likely)

        if self.TestZdiff(array, x, y, updown) == 1:
            return (x, y)
            

        #Could be made more efficient if rule can specify only 90 degrees...            
        q = self.TestRule(self.TileSiblings(array, x, y), [2,2,2,
                                                           1,0,1,
                                                           2,2,2,], 2)
        if q != 0:
            array[x][y][0] = array[x][y][0] + 1
            array[x][y][1] = 14
            return (x, y)
        q = self.TestRule(self.TileSiblings(array, x, y), [1,0,0,
                                                           0,0,1,
                                                           0,1,2,], 2)
        if q != 0:
            array[x][y][0] = array[x][y][0] + 1
            array[x][y][1] = 14
            return (x, y)

        # Rules for straight slopes
        q = self.TestRule(self.TileSiblings(array, x, y), [2,0,0,
                                                           1,0,0,
                                                           2,0,0,], 2)
        if q == 1:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 0
            return 0
        elif q == 2:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 1
            return 0
        elif q == 3:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 2
            return 0
        elif q == 4:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 3
            return 0
        
        # Rules for "outside" curves
        q = self.TestRule(self.TileSiblings(array, x, y), [1,0,0,
                                                           0,0,0,
                                                           0,0,0,], 2)
        if q == 1:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 5
            return 0
        elif q == 2:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 6
            return 0
        elif q == 3:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 7
            return 0
        elif q == 4:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 4
            return 0

        # Rules for "inside" curves
        q = self.TestRule(self.TileSiblings(array, x, y), [2,1,2,
                                                           1,0,0,
                                                           2,0,0,], 2)
        if q == 1:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 8
            return 0
        elif q == 2:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 10
            return 0
        elif q == 3:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 12
            return 0
        elif q == 4:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 9
            return 0
        q = self.TestRule(self.TileSiblings(array, x, y), [2,1,0,
                                                           0,0,0,
                                                           0,0,1,], 2)
        if q == 4:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 8
            return 0
        elif q == 1:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 10
            return 0
        elif q == 2:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 12
            return 0
        elif q == 3:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 9
            return 0
        q = self.TestRule(self.TileSiblings(array, x, y), [0,1,2,
                                                           0,0,0,
                                                           1,0,0,], 2)
        if q == 1:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 8
            return 0
        elif q == 2:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 10
            return 0
        elif q == 3:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 12
            return 0
        elif q == 4:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 9
            return 0

        # Rules for double curves at corner of two mountains
        q = self.TestRule(self.TileSiblings(array, x, y), [1,0,0,
                                                           0,0,0,
                                                           0,0,1,], 2)
        if q == 1:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 13
            return 0
        elif q == 2:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 11
            return 0

        else:
            array[x][y][0] = array[x][y][0]
            array[x][y][1] = 14
            return 0

## Check:
## (x-1),(y-1)
## (x-1),y
## (x-1),(y+1)
## x,(y-1)
## x,y
## x,(y+1)
## (x+1),(y-1)
## (x+1),y
## (x+1),(y+1)

    def TestRule(self, test, rule, rot=0):
        """Takes 3 args, test, rule and rot
        test = pattern to test for match
        rule = rule to test pattern against
        rot = what rotations should be used:
              0 - no rotations
              1 - 180 degree rotation only
              2 - all 4 rotations
        returns:
        0 - no rot matches
        1 - 0 degrees matches (what's passed in)
        2 - 90 degrees matches
        3 - 180 degrees matches
        4 - 270 degrees matches"""

        # First, test the rule as passed in
        fail = 0
        for i in range(len(test)):
            # If entry is 2, don't bother testing
            if rule[i] != 2:
                # If they are not the same, mark it for failure
                if rule[i] == test[i]:
                    complete = 1
                else:
                    # If the rule doesn't match on any particular point,
                    # set fail to 1 and this rule varient isn't passed
                    fail = 1

        if fail == 0:
            return complete
        
        if rot >= 1:
        #Could probably save some time here by doing 180 degree case seperately, needs speed testing
            fail = 0
            complete = 0

            rule_rot90 = []
            a = []
            a = rule[:]
            rule_rot90.append(a[6])
            rule_rot90.append(a[3])
            rule_rot90.append(a[0])
            rule_rot90.append(a[7])
            rule_rot90.append(a[4])
            rule_rot90.append(a[1])
            rule_rot90.append(a[8])
            rule_rot90.append(a[5])
            rule_rot90.append(a[2])

            if rot != 1:        # If 1 then we're only testing 180 degrees, so skip this
                for i in range(len(test)):
                    # If entry is 2, don't bother testing
                    if rule_rot90[i] != 2:
                        # If they are not the same, mark it for failure
                        if rule_rot90[i] == test[i]:
                            complete = 2
                        else:
                            # If the rule doesn't match on any particular point,
                            # set fail to 1 and this rule varient isn't passed
                            fail = 1
                if fail == 0:
                    return complete
                fail = 0
                complete = 0

            rule_rot180 = []
            a = []
            a = rule_rot90[:]
            rule_rot180.append(a[6])
            rule_rot180.append(a[3])
            rule_rot180.append(a[0])
            rule_rot180.append(a[7])
            rule_rot180.append(a[4])
            rule_rot180.append(a[1])
            rule_rot180.append(a[8])
            rule_rot180.append(a[5])
            rule_rot180.append(a[2])

            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_rot180[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_rot180[i] == test[i]:
                        complete = 3
                    else:
                        # If the rule doesn't match on any particular point,
                        # set fail to 1 and this rule varient isn't passed
                        fail = 1

            if fail == 0:
                return complete
            if rot == 1:
                return 0
            else:
                fail = 0
                complete = 0

            if rot != 1:        # If 1 then we're only testing 180 degrees, so skip this

                rule_rot270 = []
                a = []
                a = rule_rot180[:]
                rule_rot270.append(a[6])
                rule_rot270.append(a[3])
                rule_rot270.append(a[0])
                rule_rot270.append(a[7])
                rule_rot270.append(a[4])
                rule_rot270.append(a[1])
                rule_rot270.append(a[8])
                rule_rot270.append(a[5])
                rule_rot270.append(a[2])

                for i in range(len(test)):
                    # If entry is 2, don't bother testing
                    if rule_rot270[i] != 2:
                        # If they are not the same, mark it for failure
                        if rule_rot270[i] == test[i]:
                            complete = 4
                        else:
                            # If the rule doesn't match on any particular point,
                            # set fail to 1 and this rule varient isn't passed
                            fail = 1
                if fail == 0:
                    return complete
                else:
                    return 0

        elif fail == 1:
            return 0


    def TileSiblings(self, array, x, y):
        """Returns a 9x9 heightmap for slope testing"""
        #x, y = xy

        siblings = []

        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) < 0 or (x+xx) > (len(array[0])-1):
                    siblings.append(0)
                elif (y+yy) < 0 or (y+yy) > (len(array)-1):
                    siblings.append(0)
                else:
                    if array[x+xx][y+yy][0] > array[x][y][0]:
                        siblings.append(1)
                    elif array[x+xx][y+yy][0] < array[x][y][0]:
                        siblings.append(0)
                    elif array[x+xx][y+yy][0] == array[x][y][0]:
                        siblings.append(0)

        return siblings
