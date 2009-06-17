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

# Size of the world in tiles
xWorld = 6
yWorld = 6

TILE_SIZE = 200

class World(object):
    """Global world object for all Tiles to reference"""
    init = True
    def __init__(self):
        if World.init:
            World.xWorld = xWorld
            World.yWorld = yWorld
            # Starting offsets, these will center the map by default
            World.offx = WINDOW_WIDTH / 2 - World.xWorld * TILE_SIZE / 2
            World.offy = WINDOW_HEIGHT / 2 - World.yWorld * TILE_SIZE / 2

class Bezier(object):
    """Bezier curve related methods"""
    def calculate_bezier(self, p, steps = 30):
        """
        Calculate a bezier curve from 4 control points and return a 
        list of the resulting points.
        
        The function uses the forward differencing algorithm described here: 
        http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
        """

        # This bypasses the generation of a bezier curve, and returns a straight line in a form which should still work with all the functions that depend on this
        if len(p) == 2:
            return ([p[1], p[0]], [p[1] - p[0],p[1] - p[0]])

        t = 1.0 / steps
        temp = t*t
        
        f = p[0]
        fd = 3 * (p[1] - p[0]) * t
        fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
        fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t
        
        fddd = fddd_per_2 + fddd_per_2
        fdd = fdd_per_2 + fdd_per_2
        fddd_per_6 = fddd_per_2 * (1.0 / 3)
        
        points = []
        tangents = []
        for x in range(steps):
            points.append(f)
            tangents.append(fd)
            f = f + fd + fdd_per_2 + fddd_per_6
            fd = fd + fdd + fddd_per_2
            fdd = fdd + fddd
            fdd_per_2 = fdd_per_2 + fddd_per_2
        points.append(f)
        tangents.append(fd)
        return (points, tangents)

    def get_at_width(self, point, tangent, width):
        newpoint = point + tangent.perpendicular_normal() * width
        return newpoint

    def get_point_at_width(self, a, b, width):
        a_to_b = b - a
        c = a + a_to_b.perpendicular_normal() * width
        d = b + a_to_b.perpendicular_normal() * width
        return d

    def find_midpoint(self, a, b):
        """"""
        a_to_b = b - a
        return a + a_to_b / 2.0


class TextSprite(pygame.sprite.Sprite):
    """Subclass of sprite to draw text to the screen"""
    def __init__(self, position, textstring, font, fg=(0,0,0), bg=None,
                 borderwidth=0, bordercolour=(0,0,0),
                 bold=False, italic=False, underline=False,
                 line_spacing=3, padding=5):
        pygame.sprite.Sprite.__init__(self)

        self.position = position
        self.font = font
        self.fg = fg
        self.bg = bg
        self.borderwidth = borderwidth
        self.bordercolour = bordercolour
        self.line_spacing = line_spacing
        self.padding = padding
        self.font.set_bold(bold)
        self.font.set_italic(italic)
        self.font.set_underline(underline)

        self.text = textstring
        self.update()

    def update(self):
        """"""
        textimages = []
        # Render all lines of text
        for t in self.text:
            textimages.append(self.font.render(t, False, self.fg, self.bg))

        # Find the largest width line of text
        debug(str(textimages))
        maxwidth = max(textimages, key=lambda x: x.get_width()).get_width()
        debug(str(maxwidth))
        # Produce an image to hold all of the text strings
        self.image = pygame.Surface((maxwidth + 2 * (self.borderwidth + self.padding),
                                     textimages[0].get_height() * len(textimages) \
                                     + self.line_spacing * (len(textimages) - 1) \
                                     + 2 * (self.borderwidth + self.padding)))

        self.image.fill(self.bg)
        if self.borderwidth > 0:
            pygame.draw.rect(self.image, self.bordercolour,
                             (0, 0, self.image.get_width(), self.image.get_height()), self.borderwidth)
        for n, t in enumerate(textimages):
            self.image.blit(t, (self.borderwidth + self.padding,
                                self.borderwidth + self.padding + (self.line_spacing + t.get_height()) * n))

        self.rect = (self.position[0], self.position[1], self.image.get_width(), self.image.get_height())



class Tile(pygame.sprite.Sprite):
    """A tile containing tracks, drawn in layers"""
    init = False
    def __init__(self, position, type, track_width=10, curve_factor=60):
        pygame.sprite.Sprite.__init__(self)
        if not Tile.init:
            Tile.bezier = Bezier()
            tex = pygame.image.load("ballast_texture.png")
            Tile.ballast_texture = tex.convert()
            Tile.init = True
            Tile.size = TILE_SIZE
            Tile.font = pygame.font.SysFont("Arial", 12)
            Tile.bezier_steps = 30
            # Setup constants
            track_width = Tile.size * 0.05
            Tile.track_spacing = track_width * 2.0
            Tile.sleeper_spacing = track_width * 0.75
            Tile.sleeper_width = track_width * 0.3
            Tile.sleeper_length = track_width * 1.5
            Tile.rail_spacing = track_width
            Tile.rail_width = track_width * 0.2
            Tile.ballast_width = track_width * 2.3
            Tile.curve_factor = curve_factor
            Tile.curve_multiplier = curve_factor * 0.02

        # Position of the tile in tile coordinates from which the world coordinates are derived
        self.position = position

        # Type determines which part of the image this sprite draws (rails, sleepers, ballast or hints)
        self.type = type

        # Init variables
        self.paths = []
        self.paths_changed = False
        self.highlight_changed = False
        self.control_hint = None

        self.box = [vec2d(Tile.size, Tile.size),
                    vec2d(0, Tile.size),
                    vec2d(0, 0),
                    vec2d(Tile.size, 0)]

        self.calc_rect()

        self.box_midpoints = []
        self.box_allmidpoints = []
        for p in range(len(self.box)):
            self.box_midpoints.append(self.bezier.find_midpoint(self.box[p-1], self.box[p]))
        for p in range(len(self.box_midpoints)):
            self.box_allmidpoints.append([self.box_midpoints[p-1], (self.box[p-1] - self.box[p-2]).normalized()])
            self.box_allmidpoints.append([self.bezier.find_midpoint(self.box_midpoints[p-1], self.box_midpoints[p]), (self.box_midpoints[p] - self.box_midpoints[p-1]).normalized()])
        self.box_endpoints = []
        for p in range(len(self.box_allmidpoints)):
            self.box_endpoints.append([self.box_allmidpoints[p][0] - self.box_allmidpoints[p][1] * Tile.track_spacing, self.box_allmidpoints[p][1].perpendicular()])
            self.box_endpoints.append([self.box_allmidpoints[p][0], self.box_allmidpoints[p][1].perpendicular()])
            self.box_endpoints.append([self.box_allmidpoints[p][0] + self.box_allmidpoints[p][1] * Tile.track_spacing, self.box_allmidpoints[p][1].perpendicular()])

        self.endpoints = []
        screen_pos = vec2d(self.xpos, self.ypos)
        for p in range(len(self.box_allmidpoints)):
            self.endpoints.append(screen_pos + self.box_allmidpoints[p][0] - self.box_allmidpoints[p][1] * Tile.track_spacing)
            self.endpoints.append(screen_pos + self.position + self.box_allmidpoints[p][0])
            self.endpoints.append(screen_pos + self.position + self.box_allmidpoints[p][0] + self.box_allmidpoints[p][1] * Tile.track_spacing)

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(black)
        self.image.set_colorkey(black, pygame.RLEACCEL)
        self.paths_changed = True
        self.init_box = True
        self.update()

    def add_path(self, path):
        """Add another path to this tile
        Only add a path if that path does not already exist
        Only add a path if it passes the bounds checks for this track type"""
        debug("add_path - add: %s to existing: %s" % (path, self.paths))
        if path in self.paths or path[::-1] in self.paths:
            # Trying to add duplicate path
            return False
        else:
            # Path is not a duplicate, check if it is allowed
            # Divide by the number of paths per side, then find "angle" (in number of sides) between the two
            # sides being compared. If this is in the allowed "angles" permit drawing of this path
            side1, subside1 = divmod(path[0], 3)
            side2, subside2 = divmod(path[1], 3)
            # K determines the allowed "angle" between two endpoints
            # 0 is endpoint to itself, 1 is endpoint to immediate neighbour etc. 4 is endpoint to its opposite
            # Disallow values of K to restrict endpoints
##            K = [0,1,2,3,4]
            K = [3,4]
            L = [0,1,2,3,4,3,2,1]
            for i in range(side1):
                L.insert(0, L.pop())
            debug("add_path - transform: %s, result: %s, lookup: %s, result: %s" % (side1, L, side2, L[side2]))
            if L[side2] in K:
                self.paths.append(path)
                self.paths_changed = True
                self.update()
                return True
            else:
                return False
    def remove_path(self, path):
        """Remove a path from this tile
        Return True if path removed, False if path doesn't exist"""
        print "remove_path - self.paths: %s" % self.paths
        if path in self.paths or path[::-1] in self.paths:
            print   self.paths
            self.paths.remove(path)
            print self.paths
            self.paths_changed = True
            self.update()
            return True
        else:
            return False


    def set_control_hint(self, endpoint_number):
        """Add a control hint to this sprite, used to indicate which endpoints are active
        Pass None as endpoint_number to clear the control hint"""
        self.control_hint = endpoint_number
        self.highlight_changed = True
        self.update()

    def return_endpoints(self):
        """Return the absolute control points for this tile"""
        return self.endpoints
                
    def calc_rect(self):
        """Calculate the current rect of this tile"""
        x = self.position[0]
        y = self.position[1]
        p = self.size
        p2 = self.size / 2
        # Global screen positions
        self.xpos = xWorld*p2 - (x * p2) + (y * p2) - p2
##        self.ypos = (x * p4) + (y * p4) - (z * ph)
        self.ypos = (x * p2) + (y * p2)
        # Rect position takes into account the offset
        self.rect = (self.xpos + World.offx, self.ypos + World.offy, p, p)
        return self.rect

    def update(self):
        """Draw the image this tile represents"""
        # Draw a track for every entry in paths
        if self.paths_changed and self.type in ["rails", "sleepers", "ballast"]:
            # Reset image
            self.image.fill(black)
            # Only update the image once when first drawn, can be persistent after that (redrawn when the paths change only)
            self.paths_changed = False
            paths_to_draw = []
            paths_to_draw2 = []
            for p in self.paths:
                a = self.box_endpoints[p[0]][0]
                d = self.box_endpoints[p[1]][0]
                # If this tile is a straight line no need to use a bezier curve
                if p[0] + p[1] in [32,26,20,14]:
                    paths_to_draw.append([a,d])
                    paths_to_draw2.append([a,d])
                else:
                    p0 = p[0]
                    p1 = p[1]
                    # This gets us +1, +0 or -1, to bring the real value of the end point up to the midpoint
                    p03 = -1 * ((p0 % 3) - 1)
                    p13 = -1 * ((p1 % 3) - 1)
##                    print "p0: %s, p03: %s, p1: %s, p13: %s" % (p0, p03, p1, p13)
                    # Curve factor dictates the length between the two endpoints of each of the two curve control points
                    # By varying the length of these control points, we can make the curve smoother and sharper
                    # Taking two control points which make up a path, for each one multiply curve factor by either + or - of the
                    # offset location of the other point
                    # Find midpoint to real point vectors
                    x = (self.box_endpoints[p[1]][1] * Tile.track_spacing).length
                    y = (self.box_endpoints[p[0]][1] * Tile.track_spacing).length

                    b1 = self.box_endpoints[p[0]][0] + self.box_endpoints[p[0]][1] * (self.curve_factor + p13 * x * self.curve_multiplier)
                    c1 = self.box_endpoints[p[1]][0] + self.box_endpoints[p[1]][1] * (self.curve_factor + p03 * y * self.curve_multiplier)
                    b = self.box_endpoints[p[0]][0] + self.box_endpoints[p[0]][1] * self.curve_factor
                    c = self.box_endpoints[p[1]][0] + self.box_endpoints[p[1]][1] * self.curve_factor

                    paths_to_draw.append([a,b,c,d])
                    paths_to_draw2.append([a,b1,c1,d])
            if self.type == "rails":
                for p, q in zip(paths_to_draw, paths_to_draw2):
                    self.draw_rails(p, q)
            elif self.type == "sleepers":
                for p in paths_to_draw:
                    self.draw_sleepers(p)
            elif self.type == "ballast":
                self.draw_ballast(paths_to_draw)
        # Box never changes, draw once only
        if self.init_box and self.type == "box":
            self.init_box = False
            self.draw_box()
        # Highlight can change on its own
        if self.highlight_changed and self.type == "highlight":
            # Reset the image to blank
            self.image.fill(black)
            self.draw_highlight()
        self.calc_rect()

    def draw_highlight(self):
        """Draw the highlight which indicates the selected tile endpoint"""
        # Draw control hints for this tile
        if self.control_hint:
            pygame.draw.circle(self.image, green, self.box_endpoints[self.control_hint][0], 7)

    def draw_box(self):
        # Draw the outline of the box
        pygame.draw.lines(self.image, True, darkblue, self.box_midpoints)
        # Draw the remaining box endpoints
        for p in self.box_endpoints:
            # Draw red circles indicating the path endpoints
            pygame.draw.circle(self.image, red, (int(p[0][0]),int(p[0][1])), 3)
            # Draw normal lines indicating the path endpoints
##            pygame.draw.line(self.image, darkblue, p[0], p[0] + 20 * p[1])
            # Draw text indicating which path endpoint the dot is
            s = Tile.font.render(str(self.box_endpoints.index(p)), False, green)
            x,y = s.get_size()
            x = x/2
            y = y/2
            self.image.blit(s, p[0] + 8 * p[1] - (x,y))

    def draw_sleepers(self, control_points):
        """Draw the sleeper component of the track"""
        # Calculate bezier curve points and tangents
        cps, tangents = self.bezier.calculate_bezier(control_points, 30)
        overflow = Tile.sleeper_spacing * -0.5
        sleeper_points = []
        start = True
        # Calculate total length of this curve section based on the straight lines which make it up
        total_length = 0
        for p in range(1, len(cps)):
            # Find gradient of a->b
            b = cps[p]
            a = cps[p-1]
            a_to_b = b - a
            ab_n = a_to_b.normalized()
            total_length += a_to_b.get_length() / ab_n.get_length()
        # Number of sleepers is length, (minus one interval to make the ends line up) divided by interval length
        num_sleepers = float(total_length) / float(Tile.sleeper_spacing)
        true_spacing = float(total_length) / float(math.ceil(num_sleepers))
##        print "base spacing: %s, calculated spacing: %s\n(length: %s, number of sleepers: %s)" % (Tile.sleeper_spacing,true_spacing,total_length,num_sleepers,)
        
        for p in range(1, len(cps)):
            # Find gradient of a->b
            b = cps[p]
            a = cps[p-1]
            a_to_b = b - a
            ab_n = a_to_b.normalized()
            # Vector to add to start vector, to get offset start location
            start_vector = overflow * ab_n
            # Number of sleepers to draw in this section
            n_sleepers, overflow = divmod((a_to_b + start_vector).get_length(), (ab_n * true_spacing).get_length())
            n_sleepers = int(n_sleepers)
            # Loop through n_sleepers, draw a sleeper at the start of each sleeper spacing interval
            if start:
                s = 0
                start = False
            else:
                s = 1
            for n in range(s, n_sleepers+1):
                sleeper_points.append([self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing - ab_n*0.5*Tile.sleeper_width, a_to_b, -Tile.sleeper_length),
                                       self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing - ab_n*0.5*Tile.sleeper_width, a_to_b, Tile.sleeper_length),
                                       self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing + ab_n*0.5*Tile.sleeper_width, a_to_b, Tile.sleeper_length),
                                       self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing + ab_n*0.5*Tile.sleeper_width, a_to_b, -Tile.sleeper_length)])
        # Finally draw all the sleeper points
        for p in sleeper_points:
            pygame.draw.polygon(self.image, brown, p, 0)

    def draw_ballast(self, points_to_draw):
        """Draw the ballast component of the track"""
        # Draw out to the image
        surface = pygame.Surface((self.size, self.size))
        # Black surface, draw onto it in white, then set colourkey to white so only black parts drawn over the final texture,
        surface.fill(black)
        for control_points in points_to_draw:
            # Calculate bezier curve points and tangents
            cps, tangents = self.bezier.calculate_bezier(control_points, 30)
            # Draw the ballast under the track, this will be a polygon in the rough shape of the trackwork which will then be replaced with a texture
            # Polygon defined by the two lines at either side of the track
            ballast_points = []
            # Add one side
            for p in range(0, len(cps)):
                ballast_points.append(self.bezier.get_at_width(cps[p], tangents[p], Tile.ballast_width))
            ballast_points.reverse()
            for p in range(0, len(cps)):
                ballast_points.append(self.bezier.get_at_width(cps[p], tangents[p], -Tile.ballast_width))
            pygame.draw.polygon(surface, white, ballast_points, 0)
        # Set mask key to white, so only the outline parts drawn
        surface.set_colorkey(white, pygame.RLEACCEL)
        # Blit in the texture
        self.image.blit(self.ballast_texture, (0,0), (0,0,self.image.get_width(), self.image.get_height()))
        # Blit in the mask to obscure invisible parts of the texture with black
        self.image.blit(surface, (0,0))
        # Then set colourkey of the final surface to black to remove the mask
        self.image.set_colorkey(black)


    def draw_rails(self, control_points, control_points2):
        """Draw the rails component of the track"""
        # Calculate bezier curve points and tangents
        cps, tangents = self.bezier.calculate_bezier(control_points, 30)
        cps2, tangents2 = self.bezier.calculate_bezier(control_points2, 30)
        if DEBUG:
            pygame.draw.lines(self.image, red, False, cps, 1)
            pygame.draw.lines(self.image, silver, False, cps2, 1)
##        return True
##        softness = 50
##        for s in [1, -1]:
##            for q in range(0, rail_width*softness):
##                points = []
##                for p in range(0, len(cps)):
##                    points.append(Bezier.get_at_width(cps[p], tangents[p], s*rail_spacing+s*q/softness))
##                pygame.draw.aalines(self.image, silver, False, points, True)
        for s in [1, -1]:
            points1 = []
            points2 = []
            points3 = []
            for p in range(0, len(cps)):
                points1.append(self.bezier.get_at_width(cps[p], tangents[p], s*Tile.rail_spacing))
                points2.append(self.bezier.get_at_width(cps[p], tangents[p], s*Tile.rail_spacing - Tile.rail_width/2.0))
                points3.append(self.bezier.get_at_width(cps[p], tangents[p], s*Tile.rail_spacing + Tile.rail_width/2.0))
            pygame.draw.lines(self.image, silver, False, points1, Tile.rail_width)
##            pygame.draw.aalines(self.image, silver, False, points2, True)
##            pygame.draw.aalines(self.image, silver, False, points3, True)

    def draw_controls(self, control_points):
        """Draw the controls component of the track"""
        # Calculate bezier curve points and tangents
        cps, tangents = Bezier.calculate_bezier(control_points, 30)
        # Draw bezier curve control points
        for p in control_points:
            pygame.draw.circle(screen, blue, p, 4)
        # Draw out to the image
        pygame.draw.lines(self.image, lightgray, False, [control_points[0],control_points[1]])
        pygame.draw.lines(self.image, lightgray, False, [control_points[2],control_points[3]])
        # Draw the base bezier curve
        pygame.draw.lines(self.image, red, False, cps)



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

        self.world = World()

    def control_locate(self, mousepos, tolerance=7):
        """Locate all control points close to the mouse position"""
        x = mousepos[0] - World.offx
        y = mousepos[1] - World.offy
        control_points = []
        for a in range(xWorld):
            for b in range(yWorld):
                for n, c in enumerate(self.map[a][b]["controls"]):
                    # Rough tolerance check
                    if abs(x - c[0]) < tolerance and abs(y - c[1]) < tolerance:
                        xx = abs(x - c[0])
                        yy = abs(y - c[1])
                        # Expensive tolerance check if rough passes
                        if math.sqrt(xx * xx + yy * yy) <= tolerance:
                            control_points.append([a, b, n])
        return control_points

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

        self.instructions = ["Click on a pair of red dots to:",
                             "A - Add a track between them",
                             "D - Delete the track between them",
                             ]

        # Layers to draw, first listed drawn first
        layers = [
                  "ballast",
                  "sleepers",
                  "rails",
                  "highlight",
                  "box",
                  ]

        # 2D array, [x][y]
        self.sprites = pygame.sprite.LayeredUpdates()

        # Can look up in self.map:
        #   self.map[x][y]["paths"] -> List of paths for this tile
        #   self.map[x][y]["layers"] -> List of all the tile sprites making up this tile by layer

        # Map, used to look up all the tiles
        self.map = []
        for x in range(xWorld):
            a = []
            for y in range(yWorld):
                b = {"paths": [], "layers": {}, "controls": []}
                for c, d in enumerate(layers):
                    b["layers"][d] = Tile((x,y), d)
                    self.sprites.add(b["layers"][d], layer=c)
                b["controls"] = b["layers"]["box"].return_endpoints()
                a.append(b)
            self.map.append(a)

        # Set up instructions font
        font_size = 16
        instructions_offx = 10
        instructions_offy = 10
        instructions_font = pygame.font.SysFont("Arial", font_size)
        # Make a text sprite for all lines in
##        for n, t in enumerate(self.instructions):
##            self.sprites.add(TextSprite((instructions_offx, instructions_offy + font_size * n),
##                                        t, instructions_font, fg=black, bg=darkgreen, bold=True), layer=100)
        self.sprites.add(TextSprite((10,10), self.instructions, instructions_font,
                                    fg=black, bg=green, bold=True), layer=100)


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
                    if event.key == pygame.K_d:
                        self.mode = "delete"
                        print "set mode: delete"
                    if event.key == pygame.K_a:
                        self.mode = "add"
                        print "set mode: add"
                if event.type == MOUSEMOTION:
                    if event.buttons[2] == 1:
                        rmbpos = event.pos
                        if rmbpos != self.last_rmbpos:
                            World.offx -= self.last_rmbpos[0] - rmbpos[0]
                            World.offy -= self.last_rmbpos[1] - rmbpos[1]
                        print "offx: %s, offy: %s" % (World.offx, World.offy)
                        self.last_rmbpos = rmbpos
                        self.sprites.update()
                        self.refresh_screen = True
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.last_rmbpos = event.pos
                        self.refresh_screen = True
                if event.type == MOUSEBUTTONUP:
##                    if event.button == 3:
##                        self.drag_start = None
                    if event.button == 1:
                        print "Mouse button event starts"
                        if self.start_positions:
                            print "existing operation in progress..."
                            end_positions = self.control_locate(event.pos)
                            if end_positions:
                                for e in end_positions:
                                    for s in self.start_positions:
                                        if e[0] == s[0] and e[1] == s[1]:
                                            if self.mode == "add":
                                                # Paths should be added to the map, rather than the tiles in future!
                                                print "adding path: %s->%s to tile: (%s,%s)" % (s[2], e[2],s[0],s[1])
                                                self.map[s[0]][s[1]]["layers"]["rails"].add_path([s[2], e[2]])
                                                self.map[s[0]][s[1]]["layers"]["sleepers"].add_path([s[2], e[2]])
                                                self.map[s[0]][s[1]]["layers"]["ballast"].add_path([s[2], e[2]])
                                            if self.mode == "delete":
                                                # Paths should be added to the map, rather than the tiles in future!
                                                print "removing path: %s->%s from tile: (%s,%s)" % (s[2], e[2],s[0],s[1])
                                                self.map[s[0]][s[1]]["layers"]["rails"].remove_path([s[2], e[2]])
                                                self.map[s[0]][s[1]]["layers"]["sleepers"].remove_path([s[2], e[2]])
                                                self.map[s[0]][s[1]]["layers"]["ballast"].remove_path([s[2], e[2]])
                                            # Since this track drawing operation is complete, clear the highlights
                                            clear = True
                                            self.dirty.append(self.map[s[0]][s[1]]["layers"]["highlight"].rect)
                                if clear:
                                    # Second loop, if we found something first time around remove all the highlights
                                    print "removing control hints from all tiles"
                                    for s in self.start_positions:
                                        print "removing control hint: %s from tile (%s,%s)" % (s[2], s[0], s[1])
                                        self.map[s[0]][s[1]]["layers"]["highlight"].set_control_hint(None)
                                        self.dirty.append(self.map[s[0]][s[1]]["layers"]["highlight"].rect)
                                        print "...done"
                                    self.start_positions = None
                        else:
                            debug("new operation...")
                            self.start_positions = self.control_locate(event.pos)
                            debug("start positions: %s")
                            if self.start_positions:
                                for s in self.start_positions:
                                    debug("adding control hint: %s to tile (%s,%s)" % (s[2], s[0], s[1]))
                                    self.map[s[0]][s[1]]["layers"]["highlight"].set_control_hint(s[2])
                                    self.dirty.append(self.map[s[0]][s[1]]["layers"]["highlight"].rect)
                                    debug("...done")
                            debug("end operation")


            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                pygame.display.set_caption("FPS: %i" %
                                           (self.clock.get_fps()))

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
