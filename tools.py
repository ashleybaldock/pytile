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

import world
World = world.World()

import copy

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


class Tool(object):
    """Methods which all tools can access"""
    def __init__(self):
        """"""
        self.mouseSprite = False
    def collide_locate(self, mousepos, collideagainst):
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
                return None
            else:
                # No collision means nothing to select
                return None
        else:
            return None
    def subtile_position(self, mousepos, tile):
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
            tilesubposition = World.type[tile.type][offy16][offx8]
            return tilesubposition
        except IndexError:
            print "offy16: %s, offx8: %s, coltile: %s" % (offy16, offx8, tile.type)
            return None


class Move(Tool):
    """Screen movement tool"""
    def __init__(self):
        """First time the Move tool is used"""
        super(Move, self).__init__()
        self.start = None
    def active(self):
        """Return true if tool currently being used and screen needs updating"""
        if self.start:
            return True
        else:
            return False
    def mouse_down(self, position, collisionlist):
        """"""
        self.start = position
    def mouse_up(self, position, collisionlist):
        """"""
        self.current = position
        self.start = None
    def mouse_move(self, position, collisionlist):
        """"""
        self.current = position
        if self.start:
            self.move_screen(self.start, self.current)
        self.start = self.current
    def move_screen(self, start, end):
        """Move the screen on mouse input"""
        start_x, start_y = start
        end_x, end_y = end
        rel_x = start_x - end_x
        rel_y = start_y - end_y
        World.set_offset(World.dxoff + rel_x, World.dyoff + rel_y)

class Track(Tool):
    """Track drawing tool"""
    start = None
    aoe = []
    width = 1
    active = False
    def __init__(self):
        """"""
        # Call init method of parent
        super(Track, self).__init__()
        # The tile found through collision detection
        self.tile = None
        # The subtile of that tile
        self.subtile = None
        # tiles - all the tiles in the primary area of effect (ones which are modified first)
        self.tiles = []
        # Set start state
        self.startpos = None
        self.endpos = None
        self.active = False
        # Whether to redraw areas of the screen for aoe/highlight
        self.aoe_changed = False
        self.highlight_changed = False
        self.highlight = []
        self.last_highlight = []
        self.aoe = []
    def process_key(self, key):
        """Process keystrokes sent to this tool"""
        keyname = pygame.key.name(key)
        debug("process_key: %s" % keyname)
        ret = False
        if keyname == "1":
            self.width = 1
            ret = True
        elif keyname == "2":
            self.width = 2
            ret = True
        return ret
    def active(self):
        """Return true if tool currently being used and screen needs updating"""
        # Used to test whether the tiles being returned need to be updated
        if self.active:
            return True
        else:
            return False
    def get_aoe(self):
        """Return the current area of effect for this tool"""
        return self.aoe
    def has_aoe_changed(self):
        """Return True if the area of effect of this tool has changed since the last call to this function"""
        return self.aoe_changed
    def set_aoe_changed(self, v):
        """When aoe changes, call this to tell the main program that the area of effect on the screen must be updated"""
        self.aoe_changed = v
    def clear_aoe(self):
        """Clear the area of effect, changes will only be drawn if aoe_changed returns True"""
        self.aoe = []
        return True

    # Highlight related access functions
    # External
    def get_highlight(self):
        """Return the current highlight area for this tool"""
        return self.highlight
    # Internal
    def set_highlight(self, value):
        """Set the current highlight for this tool"""
        self.highlight = value
    def find_highlight(self, x, y, subtile):
        """Find the primary area of effect of the tool, based on tool dimensions
        Return a list of tiles to modify in [(x,y), modifier] form
        Used to specify region which will be highlighted"""
        tiles = []
        if Test.xdims > 1 or Test.ydims > 1:
            for xx in range(Test.xdims):
                for yy in range(Test.ydims):
                    tiles.append([(x + xx, y + yy), 9])
        else:
            tiles = [[(x, y), subtile]]
        return tiles


    def find_rect_aoe(self, x, y):
        """Return a list of tiles for the primary area of effect of the tool based on a box pattern"""
        tiles = []
        for xx in range(Test.xdims):
            for yy in range(Test.ydims):
                tiles.append((x + xx, y + yy))
        return tiles

    def mouse_down(self, position, collisionlist):
        """Mouse button DOWN"""
    def mouse_up(self, position, collisionlist):
        """Mouse button UP"""
        if self.active:
            # First point has already been selected
            tile = self.collide_locate(position, collisionlist)
            if tile and not tile.exclude:
                subtile = self.subtile_position(position, tile)
                self.endpos = [(tile.xWorld,tile.yWorld), self.collide_convert(subtile, end=True)]
                debug("endpos is now: %s" % self.endpos)
                # If we're doing a 2->1 type of track, need to ensure both arrays have same number of items
                if len(self.startpos[1]) > len(self.endpos[1]):
                    self.endpos[1].append(self.endpos[1][0])
                elif len(self.startpos[1]) < len(self.endpos[1]):
                    self.startpos[1].append(self.startpos[1][0])
                # Add a path to the World for each set of start/end positions
                for s, e in zip(self.startpos[1], self.endpos[1]):
                    World.add_path(tile.xWorld, tile.yWorld, [s,e])
                # Set which tiles need updating
                self.aoe = [(tile.xWorld, tile.yWorld)]
                self.set_aoe_changed(True)
                # Reset the tool
                self.endpos = None
                self.startpos = None
                self.active = False
                debug("endpos is now: %s" % self.endpos)
                self.tile = tile
                self.subtile = subtile
            else:
                # Invalid location clicked on, do nothing
                pass
        else:
            # First point selection
            tile = self.collide_locate(position, collisionlist)
            if tile and not tile.exclude:
                subtile = self.subtile_position(position, tile)
                self.startpos = [(tile.xWorld,tile.yWorld), self.collide_convert(subtile, start=True)]
                self.active = True
                debug("startpos is now: %s" % self.startpos)
                self.tile = tile
                self.subtile = subtile
            else:
                # Invalid location clicked on, do nothing
                pass


    def mouse_move(self, position, collisionlist):
        """Mouse position MOVE"""
        # If start is None, then there's no dragging operation ongoing, just update the position of the highlight
        self.current = position
        if self.start == None:
            tile = self.collide_locate(self.current, collisionlist)
            if tile and not tile.exclude:
                subtile = self.subtile_position(self.current, tile)
                # Only update the highlight if the cursor has changed enough to require it
                if tile != self.tile or subtile != self.subtile:
                    self.set_highlight(self.find_highlight(tile.xWorld, tile.yWorld, subtile))
                self.tile = tile
                self.subtile = subtile
            else:
                self.set_highlight(None)
                self.tile = None
                self.subtile = None
 
    def collide_convert(self, subtile, start=False, end=False):
        """Convert subtile edge locations from collide_detect form to track drawing form"""
        a = [5,3,1,7,4,2,0,6]
        b = a[subtile-1]
        # Convert to an endpoint, depends on whether we're drawing single or double track
        if self.width == 1:
            # Single track, return only one endpoint, found by multiplying the side the endpoint is on
            # by three, then adding one (to offset to the middle of the side)
            return [b*3+1]
        else:
            # Double track, return two endpoints, found by multiplying the side the endpoing is on
            # by three, then adding 2 to one (to offset correctly). Which one we add 2 to depends on
            # whether this is the start or end of a segment (since if we did the same on both, the
            # tracks would produce a crossover)
            if start:
                return [b*3,b*3+2]
            elif end:
                return [b*3+2,b*3]







class Test(Tool):
    """Testing tool"""
    xdims = 1
    ydims = 1
    start = None
    aoe = []
    last_aoe = []
    smooth = False
    def __init__(self):
        """First time the Test tool is used"""
        # Call init method of parent
        super(Test, self).__init__()
        # The tile found through collision detection
        self.tile = None
        # The subtile of that tile
        self.subtile = None
        # tiles - all the tiles in the primary area of effect (ones which are modified first)
        self.tiles = []
        # Whether to redraw areas of the screen for aoe/highlight
        self.aoe_changed = False
        self.highlight_changed = False
        self.highlight = []
        self.last_highlight = []
        self.aoe = []
    def process_key(self, key):
        """Process keystrokes sent to this tool"""
        keyname = pygame.key.name(key)
        debug("process_key: %s" % keyname)
        ret = False
        if keyname == "k":
            Test.xdims += 1
            ret = True
        elif keyname == "o":
            Test.xdims -= 1
            if Test.xdims < 1:
                Test.xdims = 1
            ret = True
        elif keyname == "l":
            Test.ydims += 1
            ret = True
        elif keyname == "i":
            Test.ydims -= 1
            if Test.ydims < 1:
                Test.ydims = 1
            ret = True
        elif keyname == "s":
            Test.smooth = not(Test.smooth)
            ret = True
        if keyname in ["i","o","k","l"]:
            self.set_highlight(self.find_highlight(self.tile.xWorld, self.tile.yWorld, self.subtile))
            self.set_aoe_changed(True)
            self.aoe = self.find_rect_aoe(self.tile.xWorld, self.tile.yWorld)
            ret = True
        return ret

    def active(self):
        """Return true if tool currently being used and screen needs updating"""
        # Used to test whether the tiles being returned need to be updated
        if self.start:
            return True
        else:
            return False

    # AOE related access functions
    # External
    def get_aoe(self):
        """Return the current area of effect for this tool"""
        return self.aoe
    def get_last_aoe(self):
        """Return the current area of effect for this tool"""
        return self.last_aoe
    def has_aoe_changed(self):
        """Return True if the area of effect of this tool has changed since the last call to this function"""
        return self.aoe_changed
    def set_aoe_changed(self, v):
        """When aoe changes, call this to tell the main program that the area of effect on the screen must be updated"""
        self.aoe_changed = v
        return True
    def clear_aoe(self):
        """Clear the area of effect, changes only drawn if aoe_changed returns True"""
        self.last_aoe = copy.copy(self.aoe)
        self.aoe = []
        return True
    # Method to find the aoe
    def find_rect_aoe(self, x, y):
        """Return a list of tiles for the primary area of effect of the tool based on a box pattern"""
        tiles = []
        for xx in range(Test.xdims):
            for yy in range(Test.ydims):
                # Tiles in aoe must be within the bounds of the World
                if x+xx < World.WorldX and y+yy < World.WorldY:
                    tiles.append((x + xx, y + yy))
        return tiles

    # Highlight related access functions
    # External
    def get_highlight(self):
        """Return the current highlight area for this tool"""
        return self.highlight
    # Internal
    def set_highlight(self, value):
        """Set the current highlight for this tool"""
        self.highlight = value
        return True
    def find_highlight(self, x, y, subtile):
        """Find the primary area of effect of the tool, based on tool dimensions
        Return a list of tiles to modify in [(x,y), modifier] form
        Used to specify region which will be highlighted"""
        tiles = {}
        if Test.xdims > 1 or Test.ydims > 1:
            for xx in range(Test.xdims):
                for yy in range(Test.ydims):
                    try:
                        World.array[x+xx][y+yy]
                    except IndexError:
                        pass
                    else:
                        t = copy.copy(World.array[x+xx][y+yy])
                        if len(t) == 2:
                            t.append([])
                        t.append(9)
                        tiles[(x+xx,y+yy)] = t
        else:
            t = copy.copy(World.array[x][y])
            if len(t) == 2:
                t.append([])
            t.append(subtile)
            tiles[(x,y)] = t
        return tiles


    def mouse_down(self, position, collisionlist):
        """Reset the start position for a new operation"""
        self.start = position
        self.addback = 0
    def mouse_up(self, position, collisionlist):
        """End of application of tool"""
        self.current = position
        self.tiles = []
        self.start = None
    def mouse_move(self, position, collisionlist):
        """Tool updated, current cursor position is newpos"""
        # If start is None, then there's no dragging operation ongoing, just update the position of the highlight
        self.current = position
        if self.start == None:
            tile = self.collide_locate(self.current, collisionlist)
            if tile and not tile.exclude:
                subtile = self.subtile_position(self.current, tile)
                # Only update the highlight if the cursor has changed enough to require it
                if tile != self.tile or subtile != self.subtile:
                    self.set_highlight(self.find_highlight(tile.xWorld, tile.yWorld, subtile))
                    self.set_aoe_changed(True)
                    self.aoe = self.find_rect_aoe(tile.xWorld, tile.yWorld)
                else:
                    self.set_aoe_changed(False)
                self.tile = tile
                self.subtile = subtile
            else:
                self.set_highlight({})
                self.set_aoe_changed(True)
                self.tile = None
                self.subtile = None
        # Otherwise a drag operation is on-going, do usual tool behaviour
        else:
            # If we don't already have a list of tiles to use as the primary area of effect
            if not self.tiles:
                tile = self.collide_locate(self.current, collisionlist)
                if tile and not tile.exclude:
                    subtile = self.subtile_position(self.current, tile)
                    self.tiles = self.find_rect_aoe(tile.xWorld, tile.yWorld)
                    # Tiles now contains the primary area of effect for this operation
                    self.tile = tile
                    self.subtile = subtile

            # We keep track of the mouse position in the y dimension, as it moves it ticks over in ph size increments
            # each time it does this we remove a ph size increment from the start location, so that next time we start
            # from the right place. If when we actually try to modify the terrain by that number of ticks we find we're
            # unable to (e.g. we've hit a terrain limit) and the modification is less than the requested modification
            # the start position needs to be offset such that we have to "make back" that offset.

            # Coord system is from top-left corner, down = -ve, up = +ve, so do start pos - end pos
            # This gets us the number of units to move up or down by
            diff = (self.start[1] - self.current[1]) / ph
            self.start = (self.start[0], self.start[1] - diff * ph)

            # If diff < 0 we're lowering terrain, if diff > 0 we're raising it
            # If raising, check if addback is positive, if so we need to zero out addback before applying any raising
            # to the terrain
            if diff > 0:
                while self.addback > 0:
                    if diff == 0:
                        break
                    diff -= 1
                    self.addback -= 1

            if diff != 0:
                if len(self.tiles) > 1:
                    r = self.modify_tiles(self.tiles, diff, soft=Test.smooth)
                else:
                    r = self.modify_tiles(self.tiles, diff, subtile=self.subtile, soft=Test.smooth)
                # Addback is calcuated as the actual height change minus the requested height change. The remainder is the
                # amount of cursor movement which doesn't actually do anything.
                # For example, if the cursor moves down (lowering the terrain) and hits the "0" level of the terrain we can't continue
                # to lower the terrain. The cursor keeps moving however and the addback value keeps track of this so that when the
                # cursor starts to move up it won't start raising the terrain until it hits the "0" level again

                # If we're lowering, update addback if necessary
                if diff < 0:
                    self.addback += r - diff

                # Set this so that the changed portion of the map is updated on screen
                self.set_aoe_changed(True)


    def modify_tiles(self, tiles, amount, subtile=9, soft=False):
        """Raise or lower a region of tiles"""
        # r measures the total amount of raising/lowering *actually* done
        # This can then be compared with the amount requested to calculate the cursor offset
        r = 0
        # The area of effect of the tool (list of tiles modified)
        self.aoe = []
        # This will always be a whole tile raise/lower
        # If subtile is None, this is always a whole tile raise/lower
        # If subtile is something, and there's only one tile in the array then this is a single tile action
        # If subtile is something, and there's more than one tile in the array then this is a multi-tile action, but based
        #   off a vertex rather than a face
        vertices = []
        # Lowering terrain, find maximum value to start from
        if amount < 0:
            for t in tiles:
                x = t[0]
                y = t[1]
                tgrid = World.get_height(x,y)
                if tgrid:
                    vertices.append([tgrid.height + max(tgrid.array), (x, y)])
                    self.aoe.append((x,y))
            step = -1
            for i in range(0, amount, step):
                maxval = max(vertices, key=lambda x: x[0])[0]
                if maxval != 0:
                    rr = 0
                    for p in vertices:
                        if p[0] == maxval:
                            p[0] -= 1
                            # Whole tile lower
                            if subtile == 9:
                                tgrid = World.get_height(p[1])
                                rr = tgrid.lower_face()
                                World.set_height(tgrid, p[1])
                            # Edge lower
                            elif subtile in [5,6,7,8]:
                                st1 = subtile - 5
                                st2 = st1 + 1
                                tgrid = World.get_height(p[1])
                                rr = tgrid.lower_edge(st1, st2)
                                World.set_height(tgrid, p[1])
                            # Vertex lower
                            elif subtile in [1,2,3,4]:
                                tgrid = World.get_height(p[1])
                                rr = tgrid.lower_vertex(subtile - 1)
                                World.set_height(tgrid, p[1])
                    # Since we're potentially modifying a large number of individual tiles we only want to know if
                    # *any* of them were lowered for the purposes of calculating the real raise/lower amount
                    # Thus r should only be incremented once per raise/lower level
                    r += rr
            if soft:
                # Soften around the modified tiles
                self.soften(self.aoe, soften_down=True)
        # Raising terrain, find minimum value to start from
        else:
            for t in tiles:
                x = t[0]
                y = t[1]
                tgrid = World.get_height(x,y)
                if tgrid:
                    vertices.append([tgrid.height, (x, y)])
                    self.aoe.append((x,y))
            step = 1
            for i in range(0, amount, step):
                minval = min(vertices, key=lambda x: x[0])[0]
                for p in vertices:
                    if p[0] == minval:
                        p[0] += 1
                        # Whole tile raise
                        if subtile == 9:
                            tgrid = World.get_height(p[1])
                            tgrid.raise_face()
                            World.set_height(tgrid, p[1])
                        # Edge raise
                        elif subtile in [5,6,7,8]:
                            st1 = subtile - 5
                            st2 = st1 + 1
                            tgrid = World.get_height(p[1])
                            tgrid.raise_edge(st1, st2)
                            World.set_height(tgrid, p[1])
                        # Vertex raise
                        elif subtile in [1,2,3,4]:
                            tgrid = World.get_height(p[1])
                            tgrid.raise_vertex(subtile - 1)
                            World.set_height(tgrid, p[1])
            if soft:
                # Soften around the modified tiles
                self.soften(self.aoe, soften_up=True)
        return r

    def soften(self, tiles, soften_up=False, soften_down=False):
        """Soften the tiles around a given set of tiles, raising them to make a smooth slope
        Can be set to either raise tiles to the same height or lower them"""
        # Init stacks
        to_check = {}
        checking = {}
        checked = {}
        # Add all initial tiles to first stack
        for t in tiles:
            to_check[t] = World.get_height(t)

        # Find any neighbours of this tile which have the same vertex height before we raise it
        # Need to compare 4 corners and 4 edges
        # Corners:
        # x+1,y-1 -> 0:2
        # x+1,y+1 -> 1:3
        # x-1,y+1 -> 2:0
        # x-1,y-1 -> 3:1
        # Edges:
        # x,y-1 -> 3:2,0:1
        # x+1,y -> 0:3,1:2
        # x,y+1 -> 1:0,2:3
        # x-1,y -> 2:1,3:0
        c_x = [ 1,       1,        -1,       -1,        0,    1,     0,     -1   ]
        c_y = [-1,       1,         1,       -1,       -1,    0,     1,      0   ]
        c_a = [(0,None), (1,None), (2,None), (3,None), (3,0), (0,1), (1,2), (2,3)]
        c_b = [(2,None), (3,None), (0,None), (1,None), (2,1), (3,2), (0,3), (1,0)]

        while to_check:
            # Checking should be empty from the end of the last loop
            checking = to_check
            # To check should be emptied at this point ready to add values this look
            to_check = {}
            for key, value in checking.iteritems():
                # Find all neighbours which haven't already been added to to_check and which aren't already
                # Needs to be changed so that it checks if this tile has already been checked (will be speedier)
                for x, y, a, b in zip(c_x, c_y, c_a, c_b):
                    x = key[0] + x
                    y = key[1] + y
                    # Check if the potential tile has been checked before, if so use the existing object
                    if checked.has_key((x,y)):
##                        potential = checked[(x,y)]
                        potential = None
                    elif checking.has_key((x,y)):
##                        potential = checking[(x,y)]
                        potential = None
                    elif to_check.has_key((x,y)):
                        potential = to_check[(x,y)]
##                        potential = None
                    # Otherwise create a new tile object for that tile
                    else:
                        potential = World.get_height(x, y)
                    m = 0
                    # If there is a tile to compare to (bounds check) and the comparison tile is lower
                    if potential and soften_up:
                        # Raise vertex to same height as the tile we're comparing against
                        # Do this twice for edges, only once for corners
                        for aa, bb in zip(a, b):
                            while self.compare_vertex_higher(value, potential, aa, bb):
                                potential.raise_vertex(bb)
                                m = 1
                    elif potential and soften_down:
                        # Lower vertex to same height as the tile we're comparing against
                        for aa, bb in zip(a, b):
                            while self.compare_vertex_lower(value, potential, aa, bb):
                                potential.lower_vertex(bb)
                                m = 1
                    elif potential:
                        checked[(x, y)] = potential
                    # Since we've modified this vertex, add it to the list to be checked next time around
                    if m == 1:
                        to_check[(x, y)] = potential
                        self.aoe.append((x,y))

            # Add the last iteration's checked values to the checked stack
            checked.update(checking)
            # Clear the checking stack
            checking = {}

        # Finally modify the world to reflect changes made by this tool
        for k in checked.keys():
            World.set_height(checked[k], k)

    def compare_vertex_higher(self, tgrid1, tgrid2, v1, v2):
        """Return True if specified vertex of tgrid1 is higher than specified vertex of tgrid2"""
        if v1 == None or v2 == None:
            return False
        if tgrid1[v1] + tgrid1.height > tgrid2[v2] + tgrid2.height:
            return True
        else:
            return False
    def compare_vertex_lower(self, tgrid1, tgrid2, v1, v2):
        """Return True if specified vertex of tgrid1 is lower than specified vertex of tgrid2"""
        if v1 == None or v2 == None:
            return False
        if tgrid1[v1] + tgrid1.height < tgrid2[v2] + tgrid2.height:
            return True
        else:
            return False
