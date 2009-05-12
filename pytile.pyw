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
# BUG - clicking on cliff tile causes crash (needs checks for non-interactable tile type)



import os, sys
import pygame
import random, math
from copy import copy

from World import World
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

class MouseSprite(pygame.sprite.Sprite):
    """Small invisible sprite to use for mouse/sprite collision testing"""
    # This sprite never gets drawn, so no need to worry about what it looks like
    image = None
    mask = None
    def __init__(self, (mouseX, mouseY)):
        pygame.sprite.Sprite.__init__(self)
        if MouseSprite.image is None:
            MouseSprite.image = pygame.Surface((1,1))
        if MouseSprite.mask is None:
            s = pygame.Surface((1,1))
            s.fill((1,1,1))
            MouseSprite.mask = pygame.mask.from_surface(s, 0)
        self.mask = MouseSprite.mask
        self.image = MouseSprite.image
        self.rect = pygame.Rect(mouseX, mouseY, 1,1)
    def update(self, (x, y)):
        self.rect = pygame.Rect(x, y, 1,1)

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
        self.lmb_current_drag = False
        rmb_current_drag = False

        # Tool currently selected for use
        active_tool = Tools.Test

        # Array of tiles which should have highlighting applied to them
        self.highlight_tiles = []
        
        while True:
            self.clock.tick(0)
            self.dirty = []
            # If there's a quit event, don't bother parsing the event queue
            if pygame.event.peek(pygame.QUIT):
                pygame.display.quit()
                sys.exit()
            lmb_drags = []
            rmb_drags = []

            # Clear all the old highlighted tiles
            for t in self.highlight_tiles:
                self.dirty.append(self.orderedSpritesDict[t[0]][0].change_highlight(0))
            if not self.lmb_current_drag:
                self.highlight_tiles = []

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()

                # Process events, all RMB events are motion commands, all LMB ones get fed into the active tool
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # LMB down - start a new LMB drag
                        if self.lmb_current_drag:
                            self.lmb_current_drag.end(event.pos)
                        self.lmb_current_drag = Tools.Test(event.pos)
                        self.highlight_tiles = self.lmb_current_drag.update(event.pos, self.orderedSprites)
                    if event.button == 3:
                        # RMB down - start a new RMB drag and stop current LMB drag (if present)
                        rmb_current_drag = [event.pos, event.pos]
                        if self.lmb_current_drag:
                            self.lmb_current_drag.end(event.pos)
                            self.lmb_current_drag = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # LMB up - end current LMB drag (if present, could've been ended in other ways)
                        if self.lmb_current_drag:
                            self.highlight_tiles = self.lmb_current_drag.end(event.pos)
                            self.lmb_current_drag = False
                    if event.button == 3:
                        # RMB up - end current RMB drag
                        rmb_drags.append(rmb_current_drag)
                        rmb_current_drag = False
                if event.type == pygame.MOUSEMOTION:
                    self.last_mouse_position = event.pos
                    if event.buttons[2] == 1:
                        # RMB pressed, change rmb_drag endpoint
                        rmb_current_drag[1] = event.pos
                    elif event.buttons[0] == 1:
                        # LMB pressed, change lmb_drag endpoint
                        if self.lmb_current_drag:
                            self.highlight_tiles = self.lmb_current_drag.update(event.pos, self.orderedSprites)




            # Must then end any currently active drags, but leave the mouse button states open for the next
            # frame (e.g. take a snapshot of the current drag progress, but don't delete it
            if rmb_current_drag:
                rmb_drags.append(rmb_current_drag)
            if rmb_drags:
                # Do screen movement
                total_drag = [rmb_drags[0][0], rmb_drags[-1][1]]
                if total_drag[0][0] != total_drag[1][0] or total_drag[0][1] != total_drag[1][1]:
                    self.move_screen(total_drag)
                # As this part of the current drag has been processed, set the start point of the next
                # bit to the end point of this bit
                # Remove this to enable constant drag scrolling (though using it this way would require
                # some kind of modifier based on the framerate, to ensure that it scrolls at a consistent
                # speed on all speeds of platform)
                if rmb_current_drag:
                    rmb_current_drag[0] = rmb_current_drag[1]


            if not self.lmb_current_drag and self.highlight_tiles == []:
                t = self.CollideLocate(self.last_mouse_position, self.orderedSprites)
                if t:
                    subtileposition = self.SubTilePosition(self.last_mouse_position, self.orderedSpritesDict[(t.xWorld, t.yWorld)][0])
                    self.highlight_tiles = [[(t.xWorld, t.yWorld), subtileposition]]

##            print self.highlight_tiles

            if self.lmb_current_drag:
                # Update the screen to reflect changes made by ground altering tools
                self.update_world(self.highlight_tiles)
##                self.paint_world()

            # Find position of cursor relative to the confines of the selected tile
            # Use first item in the list
            for t in self.highlight_tiles:
                self.dirty.append(self.orderedSpritesDict[t[0]][0].change_highlight(t[1]))


            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                if self.highlight_tiles:
                    ii = self.orderedSpritesDict[self.highlight_tiles[0][0]][0]
                    layer = self.orderedSprites.get_layer_of_sprite(ii)
                    pygame.display.set_caption("FPS: %i | Tile: (%s,%s) of type: %s, layer: %s | dxoff: %s dyoff: %s" %
                                               (self.clock.get_fps(), ii.xWorld, ii.yWorld, ii.type, layer, World.dxoff, World.dyoff))
                else:
                    pygame.display.set_caption("FPS: %i | dxoff: %s dyoff: %s" %
                                               (self.clock.get_fps(), World.dxoff, World.dyoff))



            rectlist = self.orderedSprites.draw(self.screen)

            # If land height has been altered, or the screen has been moved
            # we need to refresh the entire screen
##            self.refresh_screen = 1
##            self.paint_world()
            if self.refresh_screen == 1:
                pygame.display.update()
                self.screen.fill((0,0,0))
                self.refresh_screen = 0
            else:
                pygame.display.update(self.dirty)


# Only mark dirty when the cursor position has significantly changed (i.e. new graphic)

# Could also use a mode which maintains the slope of the tile, and simply increases its height
# shift+LMBdrag - preserve slope and move up/down (whole tile only)
# ctrl+LMBdrag  - vertex, modify this vertex and its neighbours
#               - edge, modify this edge, its facing neighbour and the vertices at either end
#               - tile, modify this tile, its surrounding neighbour edges and vertices
#


    def SubTilePosition(self, mousepos, tile):
        """Find the sub-tile position of the cursor"""
        x = tile.xWorld
        y = tile.yWorld
        # Find where this tile would've been drawn on the screen, and subtract the mouse's position
        mousex, mousey = mousepos
        posx = World.WorldWidth2 - (x * (p2)) + (y * (p2)) - p2
        posy = (x * (p4)) + (y * (p4)) - (World.array[x][y][0] * ph)
        offx = mousex - (posx - World.dxoff)
        offy = mousey - (posy - World.dyoff)
        # Then compare these offsets to the table of values for this particular kind of tile
        # to find which overlay selection sprite should be drawn
        # Height in 16th incremenets, width in 8th increments
        offx8 = offx / p8
        offy16 = offy / p16
        # Then lookup the mask number based on this, this should be drawn on the screen
        try:
            tilesubposition = type[tile.type][offy16][offx8]
            return tilesubposition
        except IndexError:
            print "offy16: %s, offx8: %s, tile type: %s" % (offy16, offx8, tile.type)
            return None

    def CollideLocate(self, mousepos, collideagainst):
        """Locates the sprite(s) that the mouse position intersects with"""
        # Draw mouseSprite at cursor position
        if self.mouseSprite:
            self.mouseSprite.sprite.update(mousepos)
        else:
            self.mouseSprite = pygame.sprite.GroupSingle(MouseSprite(mousepos))
        # Find sprites that the mouseSprite intersects with
        collision_list1 = pygame.sprite.spritecollide(self.mouseSprite.sprite, collideagainst, False)#, pygame.sprite.collide_mask)
        if collision_list1:
            collision_list = pygame.sprite.spritecollide(self.mouseSprite.sprite, collision_list1, False, pygame.sprite.collide_mask)
            if collision_list:
                collision_list.reverse()
                for t in collision_list:
                    if t.exclude == False:
                        return t
                    else:
                        # None of the collided sprites has collision enabled
                        return None
            else:
                # No collision means nothing to select
                return None
        else:
            return None

    def array_to_string(self, array):
        """Convert a heightfield array to a string"""
        return "%s%s%s%s" % (array[0], array[1], array[2], array[3])

    def update_world(self, tiles):
        """Instead of completely regenerating the entire world, just update certain tiles
        Returns dirty rects"""
        for t in tiles:
            x = t[0][0]
            y = t[0][1]
            t = self.orderedSpritesDict[(x,y)][0]
            self.dirty.append(t.rect)

            l = x + y
            
            # Look the tile up in the group using the position, this will give us the tile and all its cliffs
            tileset = self.orderedSpritesDict[(x, y)]
            t = tileset[0]
            # Update the tile
            t.update_type()
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

    def move_screen(self, drag):
        """Move the screen on mouse input"""
        start_x, start_y = drag[0]
        end_x, end_y = drag[1]
        rel_x = start_x - end_x
        rel_y = start_y - end_y
        World.dxoff += rel_x
        World.dyoff += rel_y

        self.paint_world()





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

if __name__ == "__main__":
    sys.stderr = debug
    sys.stdout = debug
    print "debug test"
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    world = World()
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()








    
