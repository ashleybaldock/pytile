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




# Issues
# BUG - clicking on cliff tile causes crash (needs checks for non-interactable tile type)   - Fixed
# BUG - crash when previously highlighted tile moves off screen                             - Fixed
# BUG - terrain smoothing is still far too greedy, especially on terrain lowering
# BUG - doesn't draw vertical faces of surrounding tiles                                    - Fixed
# BUG - background isn't blanked to black when raise/lower on the edges of the world        - Fixed
# BUG - resize window, if a tile is highlighted which is then moved off screen by
#       the window being resized the program crashes


# To add tracks - 
#   Need to extend World schema to have slots for the track data on tiles                   - Done
#   Extend world painting to include drawing of tracks                                      - Done
#   Port over the bezier curve drawing system                                               - Done
#   Port over perspective transform for the flat images the bezier curve system produces    - Using perspective mapping of vector points - Done
#   Add Different highlight types (indexable by name)                                       - 
#   Add methods to track tool to actually draw tracks                                       - Done
#       Extend this method with pathfinding to draw more than one tile's worth of track



import os, sys, operator
import pygame
import random, math
from copy import copy

import logger
debug = logger.Log()

import world
World = world.World()

import bezier
from vec2d import *

import tools


# Some useful colours
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

transparent = (231,255,255)

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

        self.rect = None
        self.last_rect = None

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

        # Store the last rect so if the new one is smaller we can update those bits of the screen too
        self.last_rect = self.rect
        self.rect = pygame.Rect(self.position[0], self.position[1], self.image.get_width(), self.image.get_height())

        if self.last_rect is None:
            return self.rect
        else:
            return self.last_rect.union(self.rect)


class TrackSprite(pygame.sprite.Sprite):
    """Railway track sprites"""
    init = True
    image = None
    cache = {}
    bezier = None
    TILE_SIZE = p
    props = {
             "track_width": 0.05,           # Relative to tile size
             "track_spacing": 2.0,
             "sleeper_spacing": 0.75,
             "sleeper_width": 0.3,
             "sleeper_length": 1.5,
             "rail_spacing": 0.9,
             "rail_width": 0.2,
             "ballast_width": 2.3,
             "curve_factor": 0.3,           # Relative to tile size
             "curve_multiplier": 0.02,
             }
    props_lookup = []
    tilemask = None
    for key in props.keys():
        props_lookup.append(key)

    def __init__(self, xWorld, yWorld, zWorld, init_paths=None, 
                 init_neighbour_paths=None, exclude=True):
        """"""
        pygame.sprite.Sprite.__init__(self)
        if TrackSprite.init:
            TrackSprite.init = False
            TrackSprite.bezier = bezier.Bezier()
            tex = pygame.image.load("ballast_texture.png")
            TrackSprite.ballast_texture = tex.convert()
            TrackSprite.size = TrackSprite.TILE_SIZE
            TrackSprite.bezier_steps = 30
            self.update_dimensions()
            self.gen_box()
            TrackSprite.tilemask = self.make_mask()
        self.xWorld = xWorld
        self.yWorld = yWorld
        self.zWorld = zWorld
        self.exclude = exclude
        # Init paths and neighbour_paths for this tile
        # Either init from the World, or, in the case of highlights (and other
        # temporary drawing operations) from an array passed in
        if init_paths == None:
            self.update_paths()
        else:
            self.paths = init_paths
        if init_neighbour_paths == None:
            self.update_neighbour_paths()
        else:
            self.neighbour_paths = init_neighbour_paths
        self.update()

    def make_mask(self):
        """Make a mask image ready for combination with the output image"""
        # Generate a new surface to draw onto
        surface = pygame.Surface((p, p))
        # Fill surface with transparent colour
        surface.fill(transparent)
        pointlist = [(p/2,p),(0,p/4+p/2),(p/2-1,p/2+1),(p/2,p/2+1),(p-1,p/4+p/2),(p/2,p-1)] 
        # Draw the mask in black, transparent background, but this image has its
        # transparency set to black. When blitted over another image the black
        # part won't be drawn, but the transparent colour part will
        pygame.draw.polygon(surface, black, pointlist)
        # Finally ensure surface is set back to correct colourkey for further additions
        surface.set_colorkey(black)
        return surface

    def gen_box(self):
        """Generate the array of box endpoints used for drawing tracks"""
        box = [vec2d(self.size, self.size),
               vec2d(0, self.size),
               vec2d(0, 0),
               vec2d(self.size, 0)]

        box_allmidpoints = []
        box_mids_temp = []
        box_mids_temp2 = []

        TrackSprite.midpoints = []
        TrackSprite.endpoints = []

        for p in range(len(box)):
            TrackSprite.midpoints.append(self.bezier.find_midpoint(box[p-1], box[p]))

        for p in range(len(TrackSprite.midpoints)):
            # Vector from origin to start point, unit vector representing the gradient of this vector
            box_mids_temp.append(self.bezier.find_midpoint(TrackSprite.midpoints[p-1], TrackSprite.midpoints[p]))
            box_mids_temp.append(TrackSprite.midpoints[p])

        # Copy the midpoints array
        for p in box_mids_temp:
            box_mids_temp2.append(p)
        # Offset the midpoints array
        for p in range(4):
            box_mids_temp2.insert(0, box_mids_temp2.pop())

        for p, q in zip(box_mids_temp, box_mids_temp2):
            box_allmidpoints.append([p, (q - p).normalized()])

        for p in box_allmidpoints:
            TrackSprite.endpoints.append([p[0] - p[1].perpendicular() * self.track_spacing, p[1], p[1].perpendicular()])
            TrackSprite.endpoints.append([p[0], p[1], p[1].perpendicular()])
            TrackSprite.endpoints.append([p[0] + p[1].perpendicular() * self.track_spacing, p[1], p[1].perpendicular()])

    def get_dimension(self, key):
        """Lookup and return a dimension value by numbered key"""
        return TrackSprite.props[TrackSprite.props_lookup[key]]
    def change_dimension(self, key, value):
        """Change one of the dimension values, lookup is by key number"""
        TrackSprite.props[TrackSprite.props_lookup[key]] = value
        self.update_dimensions()
        return True
    def update_dimensions(self):
        """Calculate actual dimensions for drawing track from the multiplier values"""
        # Setup constants
        # Track drawing
        track_width = TrackSprite.size * TrackSprite.props["track_width"]
        TrackSprite.track_spacing = track_width * TrackSprite.props["track_spacing"]
        TrackSprite.sleeper_spacing = track_width * TrackSprite.props["sleeper_spacing"]
        TrackSprite.sleeper_width = track_width * TrackSprite.props["sleeper_width"]
        TrackSprite.sleeper_length = track_width * TrackSprite.props["sleeper_length"]
        TrackSprite.rail_spacing = track_width * TrackSprite.props["rail_spacing"]
        TrackSprite.rail_width = track_width * TrackSprite.props["rail_width"]
        if TrackSprite.rail_width < 1:
            TrackSprite.rail_width = 1
        TrackSprite.ballast_width = track_width * TrackSprite.props["ballast_width"]
        # Curve offsets
        TrackSprite.curve_factor = TrackSprite.size * TrackSprite.props["curve_factor"]
        TrackSprite.curve_multiplier = TrackSprite.curve_factor * TrackSprite.props["curve_multiplier"]

    def update_xyz(self):
        """Update xyz coords to match those in the array"""
        self.zWorld = World.array[self.xWorld][self.yWorld][0]
        return self.calc_rect()
    def update_paths(self):
        """Read paths for this tile from World array"""
        self.paths = World.get_paths(self.xWorld, self.yWorld)
        # paths in form [[start, end(, starttype, endtype)], ...]
    def update_neighbour_paths(self):
        """Read neighbouring paths from the World array"""
        self.neighbour_paths = World.get_4_neighbour_paths(self.xWorld, self.yWorld)
        print self.xWorld, self.yWorld, self.paths, self.neighbour_paths
    def update(self):
        """Draw image and return nothing"""
        # Generate a new surface to draw onto
        surface = pygame.Surface((self.size, self.size))
        # Fill surface with transparent colour
        surface.fill(transparent)

        # 1. Look up neighbours to see if this tile needs to have any of their
        #    paths drawn on it too
        outs = World.get_4_overlap_paths(self.neighbour_paths)
        debug("out is: %s" % outs)

        # 2. If so, look up those images in the cache (should be there if
        #    neighbour tile has drawn them, if not generates them
        xdiffs = [ p2,  p2, -p2, -p2]
        ydiffs = [-p4,  p4,  p4, -p4]
        for xdiff, ydiff, out in zip(xdiffs, ydiffs, outs):
            if out != []:
                print out
                im = self.lookup_image(out)
                if not im:
                    print "generating..."
                    im = self.generate_image(out)
                    # Works if we remove this, problem must be with the cache
                    # not storing the correct images
                    #self.add_cache_image(out, im)
                surface.blit(im, (xdiff, ydiff))

        # 3. Lookup & generate (if necessary) own image
        debug("self.paths: %s" % str(self.paths))
        ownim = self.lookup_image(self.paths)
        if not ownim:
            ownim = self.generate_image(self.paths)
            self.add_cache_image(self.paths, ownim)

        # 4. Composit all of these images together
        surface.blit(ownim, (0,0))

        # 5. Blit over the mask image to ensure nothing outside of this tile
        #    gets drawn to interfere with other tiles
        surface.blit(TrackSprite.tilemask, (0,0))
        # Set transparency
        surface.set_colorkey(transparent)

        # 6. Set self.image to the surface we've created
        self.image = surface

        self.calc_rect()

    def lookup_image(self, paths):
        """Try to lookup an image in the cache, returns image or False if it isn't cached"""
        # 
        key = self.make_cache_key(paths)
        if self.cache.has_key(key):
            # debug("Looking up cache key %s succeeded!" % str(key))
            return self.cache[key]
        else:
            debug("Looking up cache key %s failed, key does not exist" % str(key))
            return False

    def make_cache_key(self, paths):
        """Make an imutable string key suitable for doing image cache lookups"""
        # Strip any duplicates (shouldn't be but worth checking)

        # First ensure that all paths are in small->big order, e.g. [13,1,t,t] converts to [1,13,t,t]
        for path in paths:
            if path[0] > path[1]:
                path.insert(1, path.pop(0))
        # Then ensure that list of paths is similarly ordered, e.g. [[10,22,t,t],[1,13,t,t]] converts to [[1,13,t,t],[10,22,t,t]]
        paths.sort(key=operator.itemgetter(slice(0,2)))
        # Convert to a tuple for immutable dict key
        a = []
        for path in paths:
            a.append(tuple(path))
        return tuple(a)

    def add_cache_image(self, paths, surface):
        """Add an image to the cache"""
        # Entries in the cache are of form:
        #   ((1,13,type1,type1),(1,10,type1,type1), ... ) : [combined, layer1, layer2, layer3, ... ]
        # Each layer is an image, combined is the overall result, this is always [0] in the array
        key = self.make_cache_key(paths)
        #self.cache[key] = []
        #for surface in surfaces:
        #    self.cache[key].append(surface)
        debug("Adding cache image with key: %s" % str(key))
        self.cache[key] = surface
        return True

    def generate_image(self, paths):
        """Generate an image and add it to the cache"""
        # Generate a new surface to draw onto
        surface = pygame.Surface((self.size, self.size))
        # Fill surface with transparent colour
        surface.fill(transparent)

        layers = [[],[],[]]
        layer_props = [1,0,0]

        if self.paths != []:
            for path in self.paths:
                cps = self.calc_control_points(path[0:2])
                # When multiple waytypes implemented look up in "type" attribute how many layers, order of layers etc.
                layers[0].append(self.draw_ballast_mask(cps))
                layers[1].append(self.draw_sleepers(cps))
                layers[2].append(self.draw_rails(cps))
            # Merge all layers down
            for n, l in zip(layer_props, layers):
                im = False
                for i in l:
                    if not im:
                        im = i
                    else:
                        im.blit(i, (0, 0))
                # Map texture if required
                if n == 1:
                    im = self.map_ballast_texture(im)
                surface.blit(im, (0, p2))

        debug("Generating image from paths: %s" % paths)

        # Finally ensure surface is set back to correct colourkey for further additions
        surface.set_colorkey(transparent)

        return surface

    def draw_rails(self, control_points):
        """Draw one set of rails using some control points and return a surface"""
        # Generate a new surface to draw onto
        surface = pygame.Surface((self.size, self.size))
        # Fill surface with transparent colour
        surface.fill(transparent)
        # Calculate bezier curve points and tangents
        cps, tangents = self.bezier.calculate_bezier(control_points, 30)
        for s in [1, -1]:
            points1 = []
            for p in range(0, len(cps)):
                points1.append(self.bezier.get_at_width(cps[p], tangents[p], s*self.rail_spacing))
            points1 = self.translate_points(points1)
            pygame.draw.lines(surface, silver, False, points1, self.rail_width)
        # Finally ensure surface is set back to correct colourkey for further additions
        surface.set_colorkey(transparent)
        return surface

    def draw_sleepers(self, control_points):
        """Draw a set of sleepers and return a surface containing them"""
        # Draw out to the image
        surface = pygame.Surface((self.size, self.size))
        # Fill surface with transparent colour
        surface.fill(transparent)
        # Calculate bezier curve points and tangents
        cps, tangents = self.bezier.calculate_bezier(control_points, 30)
        overflow = self.sleeper_spacing * -0.5
        sleeper_points = []
        start = True
        # calculate total length of this curve section based on the straight lines which make it up
        total_length = 0
        for p in range(1, len(cps)):
            # find gradient of a->b
            b = cps[p]
            a = cps[p-1]
            a_to_b = b - a
            ab_n = a_to_b.normalized()
            try:
                total_length += a_to_b.get_length() / ab_n.get_length()
            except ZeroDivisionError:
                total_length += 0
                pass
        # number of sleepers is length, (minus one interval to make the ends line up) divided by interval length
        num_sleepers = float(total_length) / float(TrackSprite.sleeper_spacing)
        try:
            true_spacing = float(total_length) / float(math.ceil(num_sleepers))
        except ZeroDivisionError:
            true_spacing = 0
            pass
        for p in range(1, len(cps)):
            # find gradient of a->b
            b = cps[p]
            a = cps[p-1]
            a_to_b = b - a
            ab_n = a_to_b.normalized()
            # vector to add to start vector, to get offset start location
            start_vector = overflow * ab_n
            # number of sleepers to draw in this section
            try:
                n_sleepers, overflow = divmod((a_to_b + start_vector).get_length(), (ab_n * true_spacing).get_length())
            except ZeroDivisionError:
                n_sleepers = 0
                overflow = 0
                pass
            n_sleepers = int(n_sleepers)
            # loop through n_sleepers, draw a sleeper at the start of each sleeper spacing interval
            if start:
                s = 0
                start = False
            else:
                s = 1
            for n in range(s, n_sleepers+1):
                sleep_p = [self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing - ab_n*0.5*self.sleeper_width, a_to_b, -self.sleeper_length),
                           self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing - ab_n*0.5*self.sleeper_width, a_to_b, self.sleeper_length),
                           self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing + ab_n*0.5*self.sleeper_width, a_to_b, self.sleeper_length),
                           self.bezier.get_at_width(a - start_vector + n*ab_n*true_spacing + ab_n*0.5*self.sleeper_width, a_to_b, -self.sleeper_length)]
                # translate points into iso perspective
                sleeper_points.append(self.translate_points(sleep_p))
        # finally draw all the sleeper points
        for p in sleeper_points:
            pygame.draw.polygon(surface, brown, p, 0)
        # Finally ensure surface is set back to correct colourkey for further additions
        surface.set_colorkey(transparent)
        return surface

    def draw_ballast_mask(self, control_points):
        """Draw the mask used to produce the ballast component of the image"""
        # Draw out to the image
        surface = pygame.Surface((self.size, self.size))
        # Transparent surface, draw mask in white, set colourkey to transparent so blitting these textures
        # onto one another will result in final mask. When final mask obtained, set colourkey
        # to white and blit over the texture, see map_ballast_texture
        # Fill surface with transparent colour
        surface.fill(transparent)
        # Calculate bezier curve points and tangents
        cps, tangents = self.bezier.calculate_bezier(control_points, 30)
        # Polygon defined by the two lines at either side of the track
        ballast_points = []
        # Add one side
        for p in range(0, len(cps)):
            ballast_points.append(self.bezier.get_at_width(cps[p], tangents[p], TrackSprite.ballast_width))
        ballast_points.reverse()
        for p in range(0, len(cps)):
            ballast_points.append(self.bezier.get_at_width(cps[p], tangents[p], -TrackSprite.ballast_width))
        # Translate points into iso space
        ballast_points = self.translate_points(ballast_points)
        # Draw the polygon to the surface
        pygame.draw.polygon(surface, white, ballast_points, 0)
        # Set transparency so these surfaces can be composited
        surface.set_colorkey(transparent)
        return surface

    def map_ballast_texture(self, surface):
        """Take a surface generated by calls to draw_ballast_mask and apply a ballast texture to it"""
        # Set mask key to white, so only the outline parts drawn
        surface.set_colorkey(white, pygame.RLEACCEL)
        outsurface = pygame.Surface((self.size, self.size))
        # Blit in the texture
        outsurface.blit(self.ballast_texture, (0,0), (0, 0, self.size, self.size))
        # Blit in the mask to obscure invisible parts of the texture with black
        outsurface.blit(surface, (0,0))
        # Then set colourkey of the final surface to black to remove the mask
        outsurface.set_colorkey(transparent)
        # Finally ensure surface is set back to correct colourkey for further additions
        surface.set_colorkey(transparent)
        return outsurface

    def calc_control_points(self, p):
        """Calculate control points from a path"""
        a = self.endpoints[p[0]][0]
        d = self.endpoints[p[1]][0]
        # If this tile is a straight line no need to use a bezier curve
        if p[0] + p[1] in [32,26,20,14]:
            return [a,d]
        else:
            p0 = p[0]
            p1 = p[1]
            # This gets us +1, +0 or -1, to bring the real value of the end point up to the midpoint
            p03 = -1 * ((p0 % 3) - 1)
            p13 = -1 * ((p1 % 3) - 1)
            # Curve factor is the length between the two endpoints of each of the two curve control points
            # By varying the length of these control points, we can make the curve smoother and sharper
            # Taking two control points which make up a path, for each one multiply curve factor by 
            # either + or - of the offset location of the other point
            # Find midpoint to real point vectors
            x = (self.endpoints[p[1]][1] * TrackSprite.track_spacing).length
            y = (self.endpoints[p[0]][1] * TrackSprite.track_spacing).length

            b = self.endpoints[p[0]][0] + self.endpoints[p[0]][1] * self.curve_factor
            c = self.endpoints[p[1]][0] + self.endpoints[p[1]][1] * self.curve_factor

            return [a,b,c,d]

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

    def translate_points(self, points):
        """Translate a set of points to convert from world space into iso space"""
        scale = vec2d(1,0.5)
        out = []
        for p in points:
            out.append(p*scale)
        return out



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
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

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
        self.refresh_screen = 1

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
        self.lmb_tool = tools.Terrain()
        self.rmb_tool = tools.Move()


        # overlay_sprites is for text that overlays the terrain in the background
        self.overlay_sprites = pygame.sprite.LayeredUpdates()


        # Set up instructions font
        font_size = 18
        instructions_offx = 10
        instructions_offy = 10
        
        instructions_font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        # Make a text sprite to display the instructions
        self.active_tool_sprite = TextSprite((10,10), ["Terrain modification"], instructions_font, 
                                             fg=(0,0,0), bg=(255,255,255), bold=False)
        self.overlay_sprites.add(self.active_tool_sprite, layer=100)


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
                    if event.key == pygame.K_F12:
                        pygame.image.save(self.screen, "pytile_sc.png")
                    if not self.lmb_tool.process_key(event.key):
                        # process_key() will always return False if it hasn't processed the key,
                        # so that keys can be used for other things if a tool doesn't want them
                        if event.key == pygame.K_t:
                            # Activate track drawing mode
                            debug("Track drawing mode active")
                            self.lmb_tool = tools.Track()
                            self.active_tool_sprite.text = ["Track drawing"]
                            self.dirty.append(self.active_tool_sprite.update())
                        if event.key == pygame.K_h:
                            # Activate terrain modification mode
                            debug("Terrain modification mode active")
                            self.lmb_tool = tools.Terrain()
                            self.active_tool_sprite.text = ["Terrain modification"]
                            self.dirty.append(self.active_tool_sprite.update())
                        # Some tools may use the escape key
                        if event.key == pygame.K_ESCAPE:
                            pygame.display.quit()
                            sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # LMB
                    if event.button == 1:
                        self.lmb_tool.mouse_down(event.pos, self.orderedSprites)
                    # RMB
                    if event.button == 3:
                        self.rmb_tool.mouse_down(event.pos, self.orderedSprites)
                if event.type == pygame.MOUSEBUTTONUP:
                    # LMB
                    if event.button == 1:
                        self.lmb_tool.mouse_up(event.pos, self.orderedSprites)
                    # RMB
                    if event.button == 3:
                        self.rmb_tool.mouse_up(event.pos, self.orderedSprites)
                if event.type == pygame.MOUSEMOTION:
                    # LMB is pressed, update all the time to keep highlight working
##                    if event.buttons[0] == 1:
                    self.lmb_tool.mouse_move(event.pos, self.orderedSprites)
                    # RMB is pressed, only update while RMB pressed
                    if event.buttons[2] == 1:
                        self.rmb_tool.mouse_move(event.pos, self.orderedSprites)
                    # No buttons are pressed
##                    else:
##                        pass
                if event.type == pygame.VIDEORESIZE:
                    debug("Screen resized, new dimensions: (%s, %s)" % (event.w, event.h))
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                    self.paint_world()
                    self.refresh_screen = 1

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

            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                ii = self.lmb_tool.tile
                if ii:
                    layer = self.orderedSprites.get_layer_of_sprite(ii)
                    pygame.display.set_caption("FPS: %i | Tile: (%s,%s) of type: %s, layer: %s | dxoff: %s dyoff: %s" %
                                               (self.clock.get_fps(), ii.xWorld, ii.yWorld, ii.type, layer, World.dxoff, World.dyoff))
                else:
                    pygame.display.set_caption("FPS: %i | dxoff: %s dyoff: %s" %
                                               (self.clock.get_fps(), World.dxoff, World.dyoff))

            # If land height has been altered, or the screen has been moved
            # we need to refresh the entire screen
            if self.refresh_screen == 1:
                self.screen.fill((0,0,0))
                rectlist = self.orderedSprites.draw(self.screen)
                rectlist = self.overlay_sprites.draw(self.screen)
                pygame.display.update()
                self.refresh_screen = 0
            else:
                for r in self.dirty:
                    self.screen.fill((0,0,0), r)
                rectlist = self.orderedSprites.draw(self.screen)
                rectlist = self.overlay_sprites.draw(self.screen)
                pygame.display.update(self.dirty)


    def array_to_string(self, array):
        """Convert a heightfield array to a string"""
        return "%s%s%s%s" % (array[0], array[1], array[2], array[3])

    def update_world(self, tiles, highlight={}):
        """Instead of completely regenerating the entire world, just update certain tiles"""
        # Add all the items in tiles to the checked_nearby hash table
        nearbytiles = []
        for t in tiles:
            x, y = t
            # Also need to look up tiles at (x-1,y) and (x,y-1) and have them re-evaluate their cliffs too
            # This needs to check that a) that tile hasn't already been re-evaluated and that
            # b) that tile isn't one of the ones which we're checking, i.e. not in tiles
            if not (x-1,y) in tiles and not (x-1,y) in nearbytiles:
                nearbytiles.append((x-1,y))
            if not (x,y-1) in tiles and not (x,y-1) in nearbytiles:
                nearbytiles.append((x,y-1))
        # This is a direct reference back to the aoe specified in the tool,
        # need to make a copy to use this!
        tiles.extend(nearbytiles)
        for t in tiles:
            x, y = t
            # If an override is defined in highlight for this tile,
            # update based on that rather than on contents of World
            if highlight.has_key((x,y)):
                tile = highlight[(x,y)]
            else:
                tile = World.array[x][y]
            # Look the tile up in the group using the position, this will give us the tile and all its cliffs
            if self.orderedSpritesDict.has_key((x, y)):
                tileset = self.orderedSpritesDict[(x, y)]
                t = tileset[0]
                # Add old positions to dirty rect list
                self.dirty.append(t.rect)

                # Calculate layer
                l = self.get_layer(x,y)

                # Update the tile type
                t.update_type()
                # Update the tile image
                t.update()
                # Update cursor highlight for tile (if it has one)
                try:
                    tile[3]
                except IndexError:
                    pass
                else:
                    t.change_highlight(tile[3])
                self.dirty.append(t.update_xyz())
                
                self.orderedSprites.remove(tileset)
                # Recreate the cliffs
                cliffs = self.make_cliffs(x, y)
                cliffs.insert(0, t)

                # Add the regenerated sprites back into the appropriate places
                self.orderedSpritesDict[(x, y)] = cliffs
                self.orderedSprites.add(cliffs, layer=l)

                # Improvement: Track sprite doesn't need to be re-added, only updated!
                # If there are tracks on this tile, or overlapping tracks on a 
                # neighbouring tile then add a track sprite
                try:
                    paths = tile[2]
                except IndexError:
                    paths = World.get_paths(x,y)
                if paths == []:
                    npaths = World.get_4_overlap_paths(World.get_4_neighbour_paths(x,y, highlight))
                if paths != [] or npaths != [[],[],[],[]]:
                    t = TrackSprite(x, y, tile[0], init_paths=paths, exclude=True)
                    #t.update_xyz()
                    self.orderedSprites.add(t, layer=l+1)
                    self.orderedSpritesDict[(x, y)].append(t)

    def get_layer(self, x, y):
        """Return the layer a sprite should be based on some parameters"""
        return (x + y) * 10

    def paint_world(self, highlight={}):
        """Paint the world as a series of sprites
        Includes ground and other objects"""
        # highlight defines tiles which should override the tiles stored in World
        # can be accessed in the same way as World
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
                    # If an override is defined in highlight for this tile,
                    # update based on that rather than on contents of World
                    if highlight.has_key((x,y)):
                        tile = highlight[(x,y)]
                    else:
                        tile = World.array[x][y]
                    l = self.get_layer(x,y)
                    # Add the main tile
                    tiletype = self.array_to_string(tile[1])
                    t = TileSprite(tiletype, x, y, tile[0], exclude=False)
                    # Update cursor highlight for tile (if it has one)
                    try:
                        tile[3]
                    except IndexError:
                        pass
                    else:
                        t.change_highlight(tile[3])

                    add_to_dict.append(t)
                    self.orderedSprites.add(t, layer=l)

                    # If there are tracks on this tile, or overlapping tracks on a 
                    # neighbouring tile then add a track sprite
                    paths = World.get_paths(x,y)
                    if paths == []:
                        npaths = World.get_4_overlap_paths(World.get_4_neighbour_paths(x,y))
                    if paths != [] or npaths != [[],[],[],[]]:
                        t = TrackSprite(x, y, tile[0], exclude=True)
                        add_to_dict.append(t)
                        self.orderedSprites.add(t, layer=l+1)

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
#    os.environ["SDL_VIDEO_CENTERED"] = "1"
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()








    
