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




# Issues
# BUG - clicking on cliff tile causes crash (needs checks for non-interactable tile type) - Fixed
# BUG - crash when nothing is on screen?



import os, sys
import pygame
import random, math
from copy import copy


import world
World = world.World()

import Tools


import logger
debug = logger.Log()

# Pre-compute often used multiples
p = 64
p2 = p / 2
p4 = p / 4
p4x3 = p4 * 3
p8 = p / 8
p16 = p / 16

#tile height difference
ph = 8

FPS_REFRESH = 500
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class HighlightSprite(pygame.sprite.Sprite):
    """Sprites for displaying ground selection highlight"""
    image = None
    rect = None
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        if HighlightSprite.image is None:
            groundImage = pygame.image.load("ground.png")
            HighlightSprite.image = groundImage.convert()
            # Tile images will be composited using rendering later, for now just read them in
            HighlightSprite.tile_images = {}
            # Each tile's highlight image composited from 1-4 edge images
            # Set for bottom-left edge
            HighlightSprite.tile_images["00XX"] = HighlightSprite.image.subsurface((0*p,4*p,p,p))
            HighlightSprite.tile_images["01XX"] = HighlightSprite.image.subsurface((1*p,4*p,p,p))
            HighlightSprite.tile_images["10XX"] = HighlightSprite.image.subsurface((2*p,4*p,p,p))
            HighlightSprite.tile_images["11XX"] = HighlightSprite.image.subsurface((3*p,4*p,p,p))
            HighlightSprite.tile_images["12XX"] = HighlightSprite.image.subsurface((4*p,4*p,p,p))
            HighlightSprite.tile_images["21XX"] = HighlightSprite.image.subsurface((5*p,4*p,p,p))
            HighlightSprite.tile_images["22XX"] = HighlightSprite.image.subsurface((6*p,4*p,p,p))
            # Set for bottom-right edge
            HighlightSprite.tile_images["X00X"] = HighlightSprite.image.subsurface((0*p,5*p,p,p))
            HighlightSprite.tile_images["X01X"] = HighlightSprite.image.subsurface((1*p,5*p,p,p))
            HighlightSprite.tile_images["X10X"] = HighlightSprite.image.subsurface((2*p,5*p,p,p))
            HighlightSprite.tile_images["X11X"] = HighlightSprite.image.subsurface((3*p,5*p,p,p))
            HighlightSprite.tile_images["X12X"] = HighlightSprite.image.subsurface((4*p,5*p,p,p))
            HighlightSprite.tile_images["X21X"] = HighlightSprite.image.subsurface((5*p,5*p,p,p))
            HighlightSprite.tile_images["X22X"] = HighlightSprite.image.subsurface((6*p,5*p,p,p))
            # Set for top-right edge
            HighlightSprite.tile_images["XX00"] = HighlightSprite.image.subsurface((0*p,6*p,p,p))
            HighlightSprite.tile_images["XX01"] = HighlightSprite.image.subsurface((1*p,6*p,p,p))
            HighlightSprite.tile_images["XX10"] = HighlightSprite.image.subsurface((2*p,6*p,p,p))
            HighlightSprite.tile_images["XX11"] = HighlightSprite.image.subsurface((3*p,6*p,p,p))
            HighlightSprite.tile_images["XX12"] = HighlightSprite.image.subsurface((4*p,6*p,p,p))
            HighlightSprite.tile_images["XX21"] = HighlightSprite.image.subsurface((5*p,6*p,p,p))
            HighlightSprite.tile_images["XX22"] = HighlightSprite.image.subsurface((6*p,6*p,p,p))
            # Set for top-left edge
            HighlightSprite.tile_images["0XX0"] = HighlightSprite.image.subsurface((0*p,7*p,p,p))
            HighlightSprite.tile_images["1XX0"] = HighlightSprite.image.subsurface((1*p,7*p,p,p))
            HighlightSprite.tile_images["0XX1"] = HighlightSprite.image.subsurface((2*p,7*p,p,p))
            HighlightSprite.tile_images["1XX1"] = HighlightSprite.image.subsurface((3*p,7*p,p,p))
            HighlightSprite.tile_images["2XX1"] = HighlightSprite.image.subsurface((4*p,7*p,p,p))
            HighlightSprite.tile_images["1XX2"] = HighlightSprite.image.subsurface((5*p,7*p,p,p))
            HighlightSprite.tile_images["2XX2"] = HighlightSprite.image.subsurface((6*p,7*p,p,p))
            # Nothing
            HighlightSprite.tile_images["None"] = HighlightSprite.image.subsurface((0,3*p,p,p))
            for i in HighlightSprite.tile_images:
                HighlightSprite.tile_images[i].convert()
                HighlightSprite.tile_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)
        self.image = pygame.Surface((p,p))
        self.image.set_colorkey((0,0,0))
        self.exclude = True
    def changepos(self, type, tiletype, xpos, ypos, xoff, yoff, xWorld, yWorld):
        """Set highlight to appear on a different tile"""
        self.image.fill((0,0,0))
        if type == 0:
            # Empty Image
            pass
        # Corner bits, made up of two images
        elif type == 1:
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0), (0,0,p4,p))
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0), (0,0,p4,p))
        elif type == 2:
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (p4,0), (p4,0,p2,p))
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (p4,0), (p4,0,p2,p))
        elif type == 3:
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (p4x3,0), (p4x3,0,p4,p))
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (p4x3,0), (p4x3,0,p4,p))
        elif type == 4:
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (p4,0), (p4,0,p2,p))
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (p4,0), (p4,0,p2,p))
        # Edge bits, made up of one image
        elif type == 5:
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
        elif type == 6:
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
        elif type == 7:
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
        elif type == 8:
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        else:
            # Otherwise highlight whole tile (4 images)
            self.image.fill((0,0,0))
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        self.xpos = xpos
        self.ypos = ypos
        if type == 0:
            self.rect = (self.xpos - xoff, self.ypos - yoff, 1, 1)
        else:
            self.rect = (self.xpos - xoff, self.ypos - yoff, p, p)
        self.type = type
        self.xWorld = xWorld
        self.yWorld = yWorld
        self.layer = xWorld + yWorld
    def update(self, xoff, yoff):
        """Update position of sprite with new offsets"""
        self.rect = (self.xpos - xoff, self.ypos - yoff, p, p)

class TileSprite(pygame.sprite.Sprite):
    """Ground tiles"""
    image = None
    kind = "tile"
    def __init__(self, type, xWorld, yWorld, zWorld, exclude=False):
        pygame.sprite.Sprite.__init__(self)
        if TileSprite.image is None:
            groundImage = pygame.image.load("ground.png")
            TileSprite.image = groundImage.convert()
            # Tile images will be composited using rendering later, for now just read them in
            TileSprite.tile_images = {}
            # Left and Right cliff images
            TileSprite.tile_images["CL11"] = TileSprite.image.subsurface((p*0,p*2,p,p))
            TileSprite.tile_images["CL10"] = TileSprite.image.subsurface((p*1,p*2,p,p))
            TileSprite.tile_images["CL01"] = TileSprite.image.subsurface((p*2,p*2,p,p))
            TileSprite.tile_images["CR11"] = TileSprite.image.subsurface((p*3,p*2,p,p))
            TileSprite.tile_images["CR10"] = TileSprite.image.subsurface((p*4,p*2,p,p))
            TileSprite.tile_images["CR01"] = TileSprite.image.subsurface((p*5,p*2,p,p))
            # Flat tile
            TileSprite.tile_images["0000"] = TileSprite.image.subsurface((0,0,p,p))
            # Corner tile (up)
            TileSprite.tile_images["1000"] = TileSprite.image.subsurface((p*1,0,p,p))
            TileSprite.tile_images["0100"] = TileSprite.image.subsurface((p*2,0,p,p))
            TileSprite.tile_images["0010"] = TileSprite.image.subsurface((p*3,0,p,p))
            TileSprite.tile_images["0001"] = TileSprite.image.subsurface((p*4,0,p,p))
            # Slope tile
            TileSprite.tile_images["1001"] = TileSprite.image.subsurface((p*5,0,p,p))
            TileSprite.tile_images["1100"] = TileSprite.image.subsurface((p*6,0,p,p))
            TileSprite.tile_images["0110"] = TileSprite.image.subsurface((p*7,0,p,p))
            TileSprite.tile_images["0011"] = TileSprite.image.subsurface((p*8,0,p,p))
            # Corner tile (down)
            TileSprite.tile_images["1101"] = TileSprite.image.subsurface((p*9,0,p,p))
            TileSprite.tile_images["1110"] = TileSprite.image.subsurface((p*10,0,p,p))
            TileSprite.tile_images["0111"] = TileSprite.image.subsurface((p*11,0,p,p))
            TileSprite.tile_images["1011"] = TileSprite.image.subsurface((p*12,0,p,p))
            # Two height corner
            TileSprite.tile_images["2101"] = TileSprite.image.subsurface((p*13,0,p,p))
            TileSprite.tile_images["1210"] = TileSprite.image.subsurface((p*14,0,p,p))
            TileSprite.tile_images["0121"] = TileSprite.image.subsurface((p*15,0,p,p))
            TileSprite.tile_images["1012"] = TileSprite.image.subsurface((p*16,0,p,p))
            # "furrow" tiles
            TileSprite.tile_images["1010"] = TileSprite.image.subsurface((p*17,0,p,p))
            TileSprite.tile_images["0101"] = TileSprite.image.subsurface((p*18,0,p,p))
            for i in TileSprite.tile_images:
                TileSprite.tile_images[i].convert()
                TileSprite.tile_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)

            # Now add the highlight_images
            TileSprite.highlight_images = {}
            TileSprite.highlight_images["00XX"] = TileSprite.image.subsurface((0*p,4*p,p,p))
            TileSprite.highlight_images["01XX"] = TileSprite.image.subsurface((1*p,4*p,p,p))
            TileSprite.highlight_images["10XX"] = TileSprite.image.subsurface((2*p,4*p,p,p))
            TileSprite.highlight_images["11XX"] = TileSprite.image.subsurface((3*p,4*p,p,p))
            TileSprite.highlight_images["12XX"] = TileSprite.image.subsurface((4*p,4*p,p,p))
            TileSprite.highlight_images["21XX"] = TileSprite.image.subsurface((5*p,4*p,p,p))
            TileSprite.highlight_images["22XX"] = TileSprite.image.subsurface((6*p,4*p,p,p))
            # Set for bottom-right edge
            TileSprite.highlight_images["X00X"] = TileSprite.image.subsurface((0*p,5*p,p,p))
            TileSprite.highlight_images["X01X"] = TileSprite.image.subsurface((1*p,5*p,p,p))
            TileSprite.highlight_images["X10X"] = TileSprite.image.subsurface((2*p,5*p,p,p))
            TileSprite.highlight_images["X11X"] = TileSprite.image.subsurface((3*p,5*p,p,p))
            TileSprite.highlight_images["X12X"] = TileSprite.image.subsurface((4*p,5*p,p,p))
            TileSprite.highlight_images["X21X"] = TileSprite.image.subsurface((5*p,5*p,p,p))
            TileSprite.highlight_images["X22X"] = TileSprite.image.subsurface((6*p,5*p,p,p))
            # Set for top-right edge
            TileSprite.highlight_images["XX00"] = TileSprite.image.subsurface((0*p,6*p,p,p))
            TileSprite.highlight_images["XX01"] = TileSprite.image.subsurface((1*p,6*p,p,p))
            TileSprite.highlight_images["XX10"] = TileSprite.image.subsurface((2*p,6*p,p,p))
            TileSprite.highlight_images["XX11"] = TileSprite.image.subsurface((3*p,6*p,p,p))
            TileSprite.highlight_images["XX12"] = TileSprite.image.subsurface((4*p,6*p,p,p))
            TileSprite.highlight_images["XX21"] = TileSprite.image.subsurface((5*p,6*p,p,p))
            TileSprite.highlight_images["XX22"] = TileSprite.image.subsurface((6*p,6*p,p,p))
            # Set for top-left edge
            TileSprite.highlight_images["0XX0"] = TileSprite.image.subsurface((0*p,7*p,p,p))
            TileSprite.highlight_images["1XX0"] = TileSprite.image.subsurface((1*p,7*p,p,p))
            TileSprite.highlight_images["0XX1"] = TileSprite.image.subsurface((2*p,7*p,p,p))
            TileSprite.highlight_images["1XX1"] = TileSprite.image.subsurface((3*p,7*p,p,p))
            TileSprite.highlight_images["2XX1"] = TileSprite.image.subsurface((4*p,7*p,p,p))
            TileSprite.highlight_images["1XX2"] = TileSprite.image.subsurface((5*p,7*p,p,p))
            TileSprite.highlight_images["2XX2"] = TileSprite.image.subsurface((6*p,7*p,p,p))
            # Nothing
            TileSprite.highlight_images["None"] = TileSprite.image.subsurface((0,3*p,p,p))
            for i in TileSprite.highlight_images:
                TileSprite.highlight_images[i].convert()
                TileSprite.highlight_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)

        self.exclude = exclude
        # x,y,zdim are the global 3D world dimensions of the object
        self.xdim = 1.0
        self.ydim = 1.0
        # Slope tiles need to have a height so that they appear correctly
        # in front of objects behind them
        # x,y,zWorld are the global 3D world coodinates of the object
        self.xWorld = xWorld
        self.yWorld = yWorld
        self.zWorld = zWorld
        self.zdim = 0
        self.type = type
        self.update()
    def calc_rect(self):
        """Calculate the current rect of this tile"""
        x = self.xWorld
        y = self.yWorld
        z = self.zWorld
        # Global screen positions
        self.xpos = World.WorldWidth2 - (x * p2) + (y * p2) - p2
        self.ypos = (x * p4) + (y * p4) - (z * ph)
        # Rect position takes into account the offset
        self.rect = (self.xpos - World.dxoff, self.ypos - World.dyoff, p, p)
        return self.rect
    def update_xyz(self):
        """Update xyz coords to match those in the array"""
        self.zWorld = World.array[self.xWorld][self.yWorld][0]
        return self.calc_rect()
    def update_type(self):
        """Update type to match those in the array"""
        self.type = self.array_to_string(World.array[self.xWorld][self.yWorld][1])
##        self.update()
    def update(self):
        """Update sprite's rect and other attributes"""
        # What tile type should this tile be?
        self.image = TileSprite.tile_images[self.type]
        self.calc_rect()
    def change_highlight(self, type):
        """Update this tile's image with a highlight"""
        image = pygame.Surface((p,p))
        image.fill((231,255,255))
        image.blit(TileSprite.tile_images[self.type], (0,0))
        tiletype = self.type
        if type == 0:
            # Empty Image
            pass
        # Corner bits, made up of two images
        elif type == 1:
            image.blit(TileSprite.highlight_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0), (0,0,p4,p))
            image.blit(TileSprite.highlight_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0), (0,0,p4,p))
        elif type == 2:
            image.blit(TileSprite.highlight_images["%s%sXX" % (tiletype[0], tiletype[1])], (p4,0), (p4,0,p2,p))
            image.blit(TileSprite.highlight_images["X%s%sX" % (tiletype[1], tiletype[2])], (p4,0), (p4,0,p2,p))
        elif type == 3:
            image.blit(TileSprite.highlight_images["X%s%sX" % (tiletype[1], tiletype[2])], (p4x3,0), (p4x3,0,p4,p))
            image.blit(TileSprite.highlight_images["XX%s%s" % (tiletype[2], tiletype[3])], (p4x3,0), (p4x3,0,p4,p))
        elif type == 4:
            image.blit(TileSprite.highlight_images["XX%s%s" % (tiletype[2], tiletype[3])], (p4,0), (p4,0,p2,p))
            image.blit(TileSprite.highlight_images["%sXX%s" % (tiletype[0], tiletype[3])], (p4,0), (p4,0,p2,p))
        # Edge bits, made up of one image
        elif type == 5:
            image.blit(TileSprite.highlight_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
        elif type == 6:
            image.blit(TileSprite.highlight_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
        elif type == 7:
            image.blit(TileSprite.highlight_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
        elif type == 8:
            image.blit(TileSprite.highlight_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        else:
            # Otherwise highlight whole tile (4 images)
            image.blit(TileSprite.highlight_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
            image.blit(TileSprite.highlight_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
            image.blit(TileSprite.highlight_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
            image.blit(TileSprite.highlight_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        image.set_colorkey((231,255,255), pygame.RLEACCEL)
        self.image = image
        return self.rect
    def array_to_string(self, array):
        """Convert a heightfield array to a string"""
        return "%s%s%s%s" % (array[0], array[1], array[2], array[3])



class DisplayMain(object):
    """This handles the main initialisation
    and startup for the display"""
    def __init__(self, width, height):
        # Initialize PyGame
        pygame.init()
        
        # Set the window Size
        self.screen_width = width
        self.screen_height = height
        
        # Create the Screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))#, pygame.RESIZABLE)

        #tell pygame to keep sending up keystrokes when they are held down
        pygame.key.set_repeat(500, 30)

        # Setup fonts
        self.font = pygame.font.Font(None, 12)

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        # Initiate the clock
        self.clock = pygame.time.Clock()

##        background = pygame.Surface([self.screen_width, self.screen_height])
##        background.fill([0, 0, 0])

        self.orderedSprites = pygame.sprite.LayeredUpdates()
        self.orderedSpritesDict = {}

        self.paint_world()

        # Sprite used to find what the cursor is selecting
        self.mouseSprite = None
        # Settings for FPS counter
        self.fps_refresh = FPS_REFRESH
        self.fps_elapsed = 0
        # Associated with user input
        self.last_mouse_position = pygame.mouse.get_pos()

        # Tools have some global settings/properties, like x/ydims (which determine working area)
        # When tool isn't actually being used it's still updated, to provide highlighting info
        # Most basic tool is the "inspection tool", this will highlight whatever it's over including tiles
        # Terrain raise/lower tool, live preview of affected area
        # Terrain leveling tool, click and drag to select area
        self.lmb_tool = Tools.Test()
        self.rmb_tool = Tools.Move()

        # Array of tiles which should have highlighting applied to them
        
        while True:
            self.clock.tick(0)
            # If there's a quit event, don't bother parsing the event queue
            if pygame.event.peek(pygame.QUIT):
                pygame.display.quit()
                sys.exit()

            # Clear the stack of dirty tiles
            self.dirty = []

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()
                    if not self.lmb_tool.process_key(event.key):
                        # process_key() will always return False if it hasn't processed the key,
                        # so that keys can be used for other things if a tool doesn't want them
                        pass

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # LMB
                    if event.button == 1:
                        self.lmb_tool.begin(event.pos)
                    # RMB
                    if event.button == 3:
                        self.rmb_tool.begin(event.pos)
                if event.type == pygame.MOUSEBUTTONUP:
                    # LMB
                    if event.button == 1:
                        self.lmb_tool.end(event.pos)
                    # RMB
                    if event.button == 3:
                        self.rmb_tool.end(event.pos)
                if event.type == pygame.MOUSEMOTION:
                    # LMB is pressed, update all the time to keep highlight working
##                    if event.buttons[0] == 1:
                    self.lmb_tool.update(event.pos, self.orderedSprites)
                    # RMB is pressed, only update while RMB pressed
                    if event.buttons[2] == 1:
                        self.rmb_tool.update(event.pos)
                    # No buttons are pressed
##                    else:
##                        pass


            if self.lmb_tool.has_aoe_changed():
                # Update the screen to reflect changes made by tools
                self.update_world(self.lmb_tool.get_aoe())
                self.lmb_tool.set_aoe_changed(False)
##                self.lmb_tool.clear_aoe()

            if self.rmb_tool.active():
                # Repaint the entire screen for now until something better is implemented
                self.paint_world()
                self.refresh_screen = 1

            # Add all highlighted tiles to the dirty sprites list to redraw them
            if self.lmb_tool.has_highlight_changed():
                # Remove the old highlight from the screen
                for t in self.lmb_tool.get_last_highlight():
                    self.dirty.append(self.orderedSpritesDict[t[0]][0].change_highlight(0))
                # Add the new highlight
                for t in self.lmb_tool.get_highlight():
                    self.dirty.append(self.orderedSpritesDict[t[0]][0].change_highlight(t[1]))


            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                hl = self.lmb_tool.get_highlight()
                if hl:
                    ii = self.orderedSpritesDict[hl[0][0]][0]
                    layer = self.orderedSprites.get_layer_of_sprite(ii)
                    pygame.display.set_caption("FPS: %i | Tile: (%s,%s) of type: %s, layer: %s | dxoff: %s dyoff: %s" %
                                               (self.clock.get_fps(), ii.xWorld, ii.yWorld, ii.type, layer, World.dxoff, World.dyoff))
                else:
                    pygame.display.set_caption("FPS: %i | dxoff: %s dyoff: %s" %
                                               (self.clock.get_fps(), World.dxoff, World.dyoff))

            # Draw the sprite group to the screen (doesn't necessarily refresh the screen)
            rectlist = self.orderedSprites.draw(self.screen)

            # If land height has been altered, or the screen has been moved
            # we need to refresh the entire screen
            if self.refresh_screen == 1:
                pygame.display.update()
                self.screen.fill((0,0,0))
                self.refresh_screen = 0
            else:
                pygame.display.update(self.dirty)


    def array_to_string(self, array):
        """Convert a heightfield array to a string"""
        return "%s%s%s%s" % (array[0], array[1], array[2], array[3])

    def update_world(self, tiles):
        """Instead of completely regenerating the entire world, just update certain tiles"""
        checked_nearby = []
        # Add all the items in tiles to the checked_nearby hash table
        # There must be a more elegant way to do this!
        for t in tiles:
            print "t is: %s" % str(t)
            checked_nearby.append(t[0])
        tiles2 = []
        for t in tiles:
            x, y = t
            # Also need to look up tiles at (x-1,y) and (x,y-1) and have them re-evaluate their cliffs too
            # This needs to check that a) that tile hasn't already been re-evaluated and that
            # b) that tile isn't one of the ones which we're checking, i.e. not in tiles
            tiles2.append(t)
            if not (x-1,y) in checked_nearby:
                checked_nearby.append((x-1,y))
                tiles2.append([(x-1,y), 2])
            if not (x,y-1) in checked_nearby:
                checked_nearby.append((x,y-1))
                tiles2.append([(x,y-1), 2])
        tiles = tiles2
        for t in tiles:
            x, y = t
            # Look the tile up in the group using the position, this will give us the tile and all its cliffs
            if self.orderedSpritesDict.has_key((x, y)):
                tileset = self.orderedSpritesDict[(x, y)]
                t = tileset[0]
                # Add old positions to dirty rect list
                self.dirty.append(t.rect)

                # Calculate layer
                l = x + y

                # Update the tile type
                t.update_type()
                # Update the tile image
                t.update()
                self.dirty.append(t.update_xyz())
                
                self.orderedSprites.remove(tileset)
                # Recreate the cliffs
                cliffs = self.make_cliffs(x, y)
                cliffs.insert(0, t)
                self.orderedSpritesDict[(x, y)] = cliffs
                self.orderedSprites.add(cliffs, layer=l)

    def paint_world(self):
        """Paint the world as a series of sprites
        Includes ground and other objects"""
        self.refresh_screen = 1
        self.orderedSprites.empty()     # This doesn't necessarily delete the sprites though?
        self.orderedSpritesDict = {}
        # Top-left of view relative to world given by self.dxoff, self.dyoff
        # Find the base-level tile at this position
        topleftTileY, topleftTileX = self.screen_to_iso((World.dxoff, World.dyoff))
        for x1 in range(self.screen_width / p + 1):
            for y1 in range(self.screen_height / p4):
                x = int(topleftTileX - x1 + math.ceil(y1 / 2.0))
                y = int(topleftTileY + x1 + math.floor(y1 / 2.0))
                add_to_dict = []
                # Tile must be within the bounds of the map
                if (x >= 0 and y >= 0) and (x < World.WorldX and y < World.WorldY):
                    l = x + y
                    # Add the main tile
                    tiletype = self.array_to_string(World.array[x][y][1])
                    t = TileSprite(tiletype, x, y, World.array[x][y][0], exclude=False)
                    add_to_dict.append(t)
                    self.orderedSprites.add(t, layer=l)
                    # Add vertical surfaces (cliffs) for this tile (if any)
                    for t in self.make_cliffs(x, y):
                        add_to_dict.append(t)
                        self.orderedSprites.add(t, layer=l)
                    self.orderedSpritesDict[(x,y)] = add_to_dict

    def make_cliffs(self, x, y):
        """Produce a set of cliff sprites to go with a particular tile"""
        returnvals = []
        # A1/A2 are top and right vertices of tile in front/left of the one we're testing
        if x == World.WorldX - 1:
            A1 = 0
            A2 = 0
        else:
            A1 = World.array[x+1][y][1][3] + World.array[x+1][y][0]
            A2 = World.array[x+1][y][1][2] + World.array[x+1][y][0]
        # B1/B2 are left and bottom vertices of tile we're testing
        B1 = World.array[x][y][1][0] + World.array[x][y][0]
        B2 = World.array[x][y][1][1] + World.array[x][y][0]
        while B1 > A1 or B2 > A2:
            if B1 > B2:
                B1 -= 1
                tiletype = "CL10"
            elif B1 == B2:
                B1 -= 1
                B2 -= 1
                tiletype = "CL11"
            else:
                B2 -= 1
                tiletype = "CL01"
            returnvals.append(TileSprite(tiletype, x, y, B1, exclude=True))
        # A1/A2 are top and right vertices of tile in front/right of the one we're testing
        if y == World.WorldY - 1:
            A1 = 0
            A2 = 0
        else:
            A1 = World.array[x][y+1][1][3] + World.array[x][y+1][0]
            A2 = World.array[x][y+1][1][0] + World.array[x][y+1][0]
        # B1/B2 are left and bottom vertices of tile we're testing
        B1 = World.array[x][y][1][2] + World.array[x][y][0]
        B2 = World.array[x][y][1][1] + World.array[x][y][0]
        while B1 > A1 or B2 > A2:
            if B1 > B2:
                B1 -= 1
                tiletype = "CR10"
            elif B1 == B2:
                B1 -= 1
                B2 -= 1
                tiletype = "CR11"
            else:
                B2 -= 1
                tiletype = "CR01"
            returnvals.append(TileSprite(tiletype, x, y, B1, exclude=True))
        return returnvals



    def screen_to_iso(self, (wx,wy)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        TileRatio = 2.0
        # Convert coordinates to be relative to the position of tile (0,0)
        dx = wx - World.WorldWidth2
        dy = wy - (p2)
        # Do some maths
        x = int((dy + (dx / TileRatio)) / (p2))
        y = int((dy - (dx / TileRatio)) / (p2))
##        if x < 0 or y < 0:
##            return (0,0)
##        if x >= (World.WorldX) or y >= (World.WorldY):
##            return (0,0)
        return (x,y)


if __name__ == "__main__":
    sys.stderr = debug
    sys.stdout = debug
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()








    
