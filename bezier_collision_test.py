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
from tools import Tool, MouseSprite

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

nothing = (0,0,0,0)
opaque = (0,0,0,255)

FPS_REFRESH = 500
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

class ControlMover(Tool):
    """"""
    def __init__(self):
        """First time this tool is used"""
        super(ControlMover, self).__init__()
        self.dragsprite = pygame.sprite.GroupSingle()
    # Find all sprites collided with this point on the screen
    # Draw their control points, and collide detect against those to find
    # the one which we need to modify
    # Once the control point and the sprite are determined, use sprite's
    # control_point_modify method to change them
    # This returns a rect area, which should be set as the tool's aoe
    # This in turn will be used to update the screen
    def collide_control_points(self, mousepos, sprites):
        """Collide invisible mouseSprite against invisible control_points
        for all sprites, to find control_point we're interacting with"""
        allsprites = pygame.sprite.Group()

        for s in sprites:
            allsprites.add(s.CPGroup.sprites())
        colsprite = self.collide_locate(mousepos, allsprites)
        if colsprite:
            print "colsprite.label = %s" % colsprite.label
            print "colsprite.parent = %s" % colsprite.parent
        return colsprite
    def mouse_move(self, position, collisionlist):
        """Tool updated, current cursor position is newpos"""
        if len(self.dragsprite) > 0:
            # Move current control point
            # Get dragsprite's parent, and label
            parentsprite = self.dragsprite.sprite.parent
            label = self.dragsprite.sprite.label
            # Call update_endpoint method of parent with label as argument
            # This will update the parent sprite and all its children
            parentsprite.update_endpoint(label, vec2d(position))
            return True
    def mouse_down(self, position, collisionlist):
        """"""
        colsprite = self.collide_control_points(position, collisionlist)
        if colsprite is not None:
            self.dragsprite.add(colsprite)
    def mouse_up(self, position, collisionlist):
        """"""
        # Stop dragging
        self.dragsprite.empty()
    def active(self):
        """"""
        if len(self.dragsprite) > 0:
            return True
        else:
            return False
        


class CPSprite(pygame.sprite.Sprite):
    """Invisible sprite to represent control points of sprites"""
    # This sprite never gets drawn, so no need to worry about what it looks like
    image = None
    #mask = None
    radius = 10
    def __init__(self, position, parent, label=None):
        pygame.sprite.Sprite.__init__(self)
        if CPSprite.image is None:
            CPSprite.image = pygame.Surface((CPSprite.radius*2, CPSprite.radius*2))
            CPSprite.image.fill(black)
            pygame.draw.circle(CPSprite.image, white, 
                               (CPSprite.radius, CPSprite.radius), 
                               CPSprite.radius)
            CPSprite.image.set_colorkey(black)
        self.image = CPSprite.image
        self.rect = pygame.Rect(position.x - CPSprite.radius, 
                                position.y - CPSprite.radius, 
                                CPSprite.radius*2, 
                                CPSprite.radius*2)
        if label is None:
            self.label = "No Label"
        else:
            self.label = label
        self.position = position
        self.parent = parent
        self.exclude = False
    def update(self):
        position = self.position
        self.rect = pygame.Rect(position.x - CPSprite.radius, 
                                position.y - CPSprite.radius, 
                                CPSprite.radius*2, 
                                CPSprite.radius*2)

class ScreenMover(Tool):
    """"""
    def __init__(self):
        """First time this tool is used"""
        super(ScreenMover, self).__init__()
    def active(self):
        return False



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

        # Circles defined by radius
        self.radius = radius
        # Control points, one in center, one for radius
        # Control points are relative to the position
        self.control_points = [vec2d(self.radius,
                                     self.radius), 
                               vec2d(self.radius * 2,
                                     self.radius)]
        # CPGroup, sprite group containing all control points for quick access
        self.CPGroup = pygame.sprite.Group()
        # CPDict, dict containing keyed control points for easy access to modify
        self.CPDict = {}
        sp = CPSprite(self.position + vec2d(self.radius, self.radius), self)
        self.CPGroup.add(sp)
        self.CPDict["move"] = sp
        # Calculate the sprite's rect
        self.calc_rect()
        # Add CP for middle of shape to move it
        sp = CPSprite(self.position + vec2d(self.radius * 2, self.radius), self)
        self.CPGroup.add(sp)
        self.CPDict["radius"] = sp
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
        # Draw circle conntrol points
        for p in self.control_points:
            pygame.draw.circle(self.image, red, p, 2)

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

        self.eps = ["e0","e1","e2","e3"]

        # 4 Control points defining the curve
        # Also needs a control point to move the shape
        # but probably better to build this into a different item
        # e.g. move_control_point, which is always at the center
        # of the shape
        self.control_points = control_points
        # CPGroup, sprite group containing all control points for quick access
        self.CPGroup = pygame.sprite.Group()
        # CPDict, dict containing keyed control points for easy access to modify
        self.CPDict = {}
        for cp, key in zip(self.control_points, self.eps):
            sp = CPSprite(cp + self.position, self, label=key)
            self.CPGroup.add(sp)
            self.CPDict[key] = sp
        # Calculate the sprite's rect
        self.calc_rect()
        # Add CP for middle of shape to move it
        sp = CPSprite(self.position + vec2d(self.width / 2, self.height / 2), 
                      self, label="move")
        self.CPGroup.add(sp)
        self.CPDict["move"] = sp
        # Must modify control points in two ways:
        #  Update control_points value
        #  Update CPDict value
        self.update()

    def calc_rect(self):
        """Calculate the current rect of this tile"""
        # Rect must completely bound all of the control points
        # Since a bezier curve is completely bounded by the convex hull of its 
        # control points we can simply find the smallest rect which contains them all
        cps = self.CPDict
        xvals = []
        for x in self.eps:
            xvals.append(cps[x].position.x)
        yvals = []
        for y in self.eps:
            yvals.append(cps[y].position.y)
        print xvals, yvals
        minx = min(xvals)
        miny = min(yvals)
        maxx = max(xvals)
        maxy = max(yvals)
        # Rect position takes into account the offset
        self.width = maxx-minx
        self.height = maxy-miny
        self.position = vec2d(minx, miny)
        self.rect = (self.position.x, self.position.y, self.width, self.height)
        return self.rect

    def update_endpoint(self, endpoint, newposition):
        """"""
        if endpoint in self.eps:
            # Move the specified endpoint and recalculate all
            self.CPDict[endpoint].position = newposition
            self.calc_rect()
            self.CPDict["move"].position = self.position + vec2d(self.width/2, self.height/2)
            self.update()
        elif endpoint == "move":
            # Move the entire shape to center on new position
            # Get old position of the center control point
            oldpos = self.CPDict["move"].position
            # Calculate vector from the old to the new
            movepos = oldpos - newposition
            # Apply this movement vector to the rest of the control points
            for p in self.CPDict.values():
                p.position = p.position - movepos
            # This will automatically update the position of the entire shape
            # when we do a calc_rect
            self.calc_rect()
            self.update()

    def update(self, update_type=0):
        """Draw the image this tile represents"""
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(blue)

        # Draw control lines for endpoints
        pygame.draw.line(self.image, green, 
                         self.CPDict[self.eps[0]].position - self.position, 
                         self.CPDict[self.eps[1]].position - self.position)
        pygame.draw.line(self.image, green, 
                         self.CPDict[self.eps[2]].position - self.position, 
                         self.CPDict[self.eps[3]].position - self.position)
        # Draw control handles
        for p in self.CPDict.values():
            q = p.position - self.position
            pygame.draw.circle(self.image, red, (int(q.x), int(q.y)), 2)

        control_points = []
        for p in self.eps:
            control_points.append(self.CPDict[p].position - self.position)

        # Draw the bezier curve itself
        cps, tangents = self.bezier.calculate_bezier(control_points, 30)
        pygame.draw.lines(self.image, white, False, cps, 1)

        for p in self.CPDict.values():
            p.update()



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
        self.lmb_tool = ControlMover()
        self.rmb_tool = ScreenMover()


        self.sprites = pygame.sprite.LayeredUpdates()

        s = BezCurve([vec2d(0,0),vec2d(40,40),vec2d(200,100),vec2d(240,240)], 
                     vec2d(200,200))
        self.sprites.add(s, layer=1)
        #s = Circle(30, vec2d(500,200))
        #self.sprites.add(s, layer=1)

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

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # LMB
                    if event.button == 1:
                        self.lmb_tool.mouse_down(event.pos, self.sprites)
                    # RMB
                    if event.button == 3:
                        self.rmb_tool.mouse_down(event.pos, self.sprites)
                if event.type == pygame.MOUSEBUTTONUP:
                    # LMB
                    if event.button == 1:
                        self.lmb_tool.mouse_up(event.pos, self.sprites)
                    # RMB
                    if event.button == 3:
                        self.rmb_tool.mouse_up(event.pos, self.sprites)
                if event.type == pygame.MOUSEMOTION:
                    # LMB is pressed, update all the time to keep highlight working
##                    if event.buttons[0] == 1:
                    self.lmb_tool.mouse_move(event.pos, self.sprites)
                    # RMB is pressed, only update while RMB pressed
                    if event.buttons[2] == 1:
                        self.rmb_tool.mouse_move(event.pos, self.sprites)

            if self.lmb_tool.has_aoe_changed():
                # Update the screen to reflect changes made by tools
                aoe = self.lmb_tool.get_last_aoe() + self.lmb_tool.get_aoe()
                self.update_world(aoe, self.lmb_tool.get_highlight())
                self.lmb_tool.set_aoe_changed(False)
                self.lmb_tool.clear_aoe()

            if self.rmb_tool.active():
                # Repaint the entire screen until something better is implemented
                self.paint_world()
                self.refresh_screen = 1
            if self.lmb_tool.active():
                # Repaint the entire screen until something better is implemented
                self.paint_world()
                self.refresh_screen = 1

            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                #pygame.display.set_caption("FPS: %i" % (self.clock.get_fps()))

            # Refresh the screen if necessary, or just draw the updated bits
            if self.refresh_screen:
                self.screen.fill(darkgreen)
                rectlist = self.sprites.draw(self.screen)
                #for s in self.sprites.sprites():
                #    s.CPGroup.draw(self.screen)
                pygame.display.update()
                self.refresh_screen = False
            else:
                for a in self.dirty:
                    self.screen.fill(darkgreen, a)
                rectlist = self.sprites.draw(self.screen)
                #for s in self.sprites.sprites():
                #    s.CPGroup.draw(self.screen)
                pygame.display.update(self.dirty)

    def update_world(self):
        """Update necessary sprites in the world"""
        self.sprites.update()
        self.refresh_screen = True

    def paint_world(self):
        """Update the entire world (all sprites)"""
        self.sprites.update()
        self.refresh_screen = True
    
if __name__ == "__main__":
    sys.stderr = debug
    sys.stdout = debug
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()
