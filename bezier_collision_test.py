#!/usr/bin/python
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

DEBUG = False

import os
import sys
import math

import pygame
from pygame.locals import *

from numpy import *

from bezier import Bezier

import logger
debug = logger.Log()
 
from vec2d import *
 
grey = (100,100,100)
lightgray = (200,200,200)
red = (255,0,0)
darkred = (192,0,0)
green = (0,255,0)
darkgreen = (0,128,0)
blue = (0,0,255)
darkblue = (0,0,192)
brown = (72,64,0)
silver = (224,216,216)
black = (0,0,0)
white = (255,255,255)
yellow = (255,255,0)

FPS_REFRESH = 500
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

class Circle(pygame.sprite.Sprite):
    """A circle graphic"""
    init = True
    def __init__(self, radius, position):
        pygame.sprite.Sprite.__init__(self)
        if BezCurve.init:
            BezCurve.bezier = Bezier()
            BezCurve.init = False

        # Position of this graphic
        self.position = position

        # 4 Control points defining the curve
        self.radius = radius
        self.calc_rect()
        self.update()

    def calc_rect(self):
        """"""
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.rect = (self.position.x, self.position.y, self.width, self.height)
        return self.rect

    def update(self, update_type=0):
        """Draw the image this tile represents"""
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(blue)

        # Draw the circle
        pygame.draw.circle(self.image, white, (self.radius, self.radius), self.radius, 1)
        # Draw circle center control point
        pygame.draw.circle(self.image, red, (self.radius, self.radius), 2)
        # Draw circle radius control point
        pygame.draw.circle(self.image, red, (self.radius*2, self.radius), 2)

        self.calc_rect()

class BezCurve(pygame.sprite.Sprite):
    """A bezier curve graphic"""
    init = True
    def __init__(self, control_points, position):
        pygame.sprite.Sprite.__init__(self)
        if BezCurve.init:
            BezCurve.bezier = Bezier()
            BezCurve.init = False

        # Position of this graphic
        self.position = position

        # 4 Control points defining the curve
        self.control_points = control_points
        self.calc_rect()
        self.update()

    def calc_rect(self):
        """Calculate the current rect of this tile"""
        x = self.position[0]
        y = self.position[1]
        # Rect must completely bound all of the control points
        # Since a bezier curve is completely bounded by the convex hull of its 
        # control points we can simply find the smallest rect which contains all of these
        cps = self.control_points
        xvals = [cps[0].x, cps[1].x, cps[2].x, cps[3].x]
        yvals = [cps[0].y, cps[1].y, cps[2].y, cps[3].y]
        minx = min(xvals)
        miny = min(yvals)
        maxx = max(xvals)
        maxy = max(yvals)
        # Rect position takes into account the offset
        self.width = maxx-minx
        self.height = maxy-miny
        self.rect = (self.position[0], self.position[1], self.width, self.height)
        return self.rect

    def update(self, update_type=0):
        """Draw the image this tile represents"""
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(blue)

        pos = vec2d(self.position)
        cps_adj = []
        for cp in self.control_points:
            cps_adj.append(cp - pos)

        # Draw control lines for endpoints
        pygame.draw.line(self.image, green, cps_adj[0], cps_adj[1])
        pygame.draw.line(self.image, green, cps_adj[2], cps_adj[3])
        # Draw control handles
        for p in cps_adj:
            pygame.draw.circle(self.image, red, (int(p.x), int(p.y)), 2)

        # Draw the bezier curve itself
        cps, tangents = self.bezier.calculate_bezier(cps_adj, 30)
        pygame.draw.lines(self.image, white, False, cps, 1)
        self.calc_rect()



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
        self.screen.fill(darkgreen)

        #tell pygame to keep sending up keystrokes when they are held down
        pygame.key.set_repeat(500, 30)

        # Setup fonts
        self.font = pygame.font.SysFont("Arial", 16)

        # Set up variables
        self.refresh_screen = True

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        # Initiate the clock
        self.clock = pygame.time.Clock()

        self.box_size = 200

        # Settings for FPS counter
        self.fps_refresh = FPS_REFRESH
        self.fps_elapsed = 0

        # The currently selected point
        self.selected = None
        # Array to contain endpoint positions selected during the start of a draw operation
        self.start_positions = []
        # Stores the last recorded drag operation position for world movement
        self.last_rmbpos = (0,0)

        # Current tool mode
        self.mode = "add"
        self.modified = False

        self.sprites = pygame.sprite.LayeredUpdates()

        s = BezCurve([vec2d(200,200),vec2d(240,240),vec2d(400,300),vec2d(340,340)], (200,200))
        self.sprites.add(s, layer=1)
        s = Circle(30, vec2d(500,200))
        self.sprites.add(s, layer=1)

        while True:
            self.clock.tick(0)
            # If there's a quit event, don't bother parsing the event queue
            if pygame.event.peek(pygame.QUIT):
                pygame.display.quit()
                sys.exit()

            # Clear the stack of dirty tiles
            self.dirty = []
            clear = False
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()

                if event.type == MOUSEMOTION:
                    if event.buttons[2] == 1:
                        rmbpos = event.pos
                        if rmbpos != self.last_rmbpos:
                            pass
                        #print "offx: %s, offy: %s" % (World.offx, World.offy)
                        self.last_rmbpos = rmbpos
                        self.modified = 1
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.last_rmbpos = event.pos
                        self.refresh_screen = True
                if event.type == MOUSEBUTTONUP:
                    pass
##                    if event.button == 3:
##                        self.drag_start = None


            if self.modified:
                self.sprites.update(self.modified)
                self.refresh_screen = True
                self.modfied = False

            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                #pygame.display.set_caption("FPS: %i" % (self.clock.get_fps()))

            # Refresh the screen if necessary, or just draw the updated bits
            if self.refresh_screen:
                self.screen.fill(darkgreen)
                rectlist = self.sprites.draw(self.screen)
                pygame.display.update()
                self.refresh_screen = False
            else:
                for a in self.dirty:
                    self.screen.fill(darkgreen, a)
                rectlist = self.sprites.draw(self.screen)
                pygame.display.update(self.dirty)


    
if __name__ == "__main__":
    sys.stderr = debug
    sys.stdout = debug
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()
