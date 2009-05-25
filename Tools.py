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

# Pre-compute often used multiples
p = 64
p2 = p / 2
p4 = p / 4
p4x3 = p4 * 3
p8 = p / 8
p16 = p / 16

#tile height difference
ph = 8



class tGrid:
    """Short array which can wrap-around"""
    def __init__(self, value):
        self.array = value
        self.length = len(self.array)
    def __len__(self):
        return self.length
    def __call__(self, array):
        self.array = array
    def __getitem__(self, key):
        while key < 0:
            key += self.length
        while key > self.length - 1:
            key -= self.length
        return self.array[key]
    def __setitem__(self, key, value):
        while key < 0:
            key += self.length
        while key > self.length - 1:
            key -= self.length
        self.array[key] = value
        return
    def __contains__(self, item):
        if item in self.array:
            return True
        else:
            return False
    def __str__(self):
        return str(self.array)

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
                    else:
                        # None of the collided sprites has collision enabled
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



##            if lmb_drags:
##                # Do selection, interaction etc.
##                # First locate collision position of the start and end point of the drag (if these differ)
##                for drag in lmb_drags:
##                    if not drag[2]:
##                        tileposition = self.CollideLocate(drag[0], self.orderedSprites)
##                        if tileposition:
##                            subtileposition = self.SubTilePosition(drag[0], tileposition)
##                        else:
##                            subtileposition = None
##                        drag[2] = (tileposition, subtileposition)
##                    else:
##                        tileposition, subtileposition = drag[2]
##                    # Drag or click must be on a sprite
##                    # If that sprite is a ground tile, and a ground tile altering tool is selected
##                    # then perform ground alteration
##                    if tileposition:
##                        # Set start position
##                        start = drag[0]
##                        # If end position different to start, set end position
##                        if drag[0] != drag[1]:
##                            end = drag[1]
##                        else:
##                            end = None
##                        if end:
##                            # Addback keeps the cursor on the 0 level of the terrain and ensures that the user
##                            # must bring the mouse back up to the 0 level before the raising function will
##                            # work again
##                            addback = 0
##                            # Raise height by y difference / ph
##                            diff = (end[1] - start[1]) / ph
##                            diffrem = (end[1] - start[1]) % ph
##                            if diff != 0:
##                                invdiff = - diff
##                                totalchange, realchange = self.modify_tile(tileposition, subtileposition, invdiff)
##                                x = tileposition.xWorld
##                                y = tileposition.yWorld
##                                # Also raise the height of the stored copy of the tile in the drag object
##                                drag[2][0].ypos += realchange * ph
##                                if invdiff < 0:
##                                    # Moving down
##                                    if totalchange > invdiff:
##                                        # Have moved tile down by less than the total change
##                                        # Thus an additional offset must be made to force the cursor to be
##                                        # brought back up to the level of the terrain
##                                        addback = (invdiff - totalchange) * ph
####                                print "invdiff: %s, realchange: %s, totalchange: %s, addback: %s" % (invdiff, realchange, totalchange, addback)
##                                # This could be optimised to not recreate the entire sprite array
##                                # and only correct the tiles which have been modified
##                                self.paint_world()
##                            if drag == lmb_current_drag:
##                                # If this is a drag operation which is split across multiple frames then
##                                # the start location for the next frame needs to be modified to reflect the bits
##                                # which were processed this frame
##                                lmb_current_drag[0] = (lmb_current_drag[1][0],
##                                                       lmb_current_drag[1][1] - diffrem + addback)
##
##

class ToolSettings(object):
    """Global settings for tools, e.g. size of area of effect"""
    xdims = 1
    ydims = 1


class Move(Tool):
    """Screen movement tool"""
    def __init__(self):
        """First time the Move tool is used"""
        self.start = None
    def active(self):
        """Return true if tool currently being used and screen needs updating"""
        if self.start:
            return True
        else:
            return False
    def begin(self, start):
        """"""
        self.start = start
    def end(self, final):
        """"""
        self.current = final
        self.start = None
    def update(self, current):
        """"""
        self.current = current
        if self.start:
            self.move_screen(self.start, self.current)
        self.start = self.current
        World.blah = "eh"

    def move_screen(self, start, end):
        """Move the screen on mouse input"""
        start_x, start_y = start
        end_x, end_y = end
        rel_x = start_x - end_x
        rel_y = start_y - end_y
        World.set_offset(World.dxoff + rel_x, World.dyoff + rel_y)
        print rel_x, World.dxoff, rel_y, World.dyoff


class Test(Tool):
    """Testing tool"""
    xdims = 1
    ydims = 1
    start = None
    def __init__(self):
        """First time the Test tool is used"""
        # Call init method of parent
        super(Test, self).__init__()
        self.tile = None
        self.tiles = []
    def process_key(self, key):
        """Process a keystroke during a drag operation"""
        keyname = pygame.key.name(key)
        if keyname == "[":
            Test.xdims += 1
        elif keyname == "]":
            Test.xdims -= 1
            if Test.xdims < 1:
                Test.xdims = 1
        if keyname == "o":
            Test.ydims += 1
        elif keyname == "p":
            Test.ydims -= 1
            if Test.ydims < 1:
                Test.ydims = 1
        print pygame.key.name(key)
        return True
    def active(self):
        """Return true if tool currently being used and screen needs updating"""
        # Used to test whether the tiles being returned need to be updated
        if self.start:
            return True
        else:
            return False
    def begin(self, start):
        """Reset the start position for a new operation"""
        self.start = start
        return []
    def end(self, final):
        """End of application of tool"""
        self.current = final
        self.tiles = []
        self.start = None
        # This should return a list of tiles to highlight
        return []
    def get_aoe(self):
        """Return the current area of effect for this tool"""
        return self.tiles
    def get_highlight(self):
        """Return the current highlight area for this tool"""
        return self.tiles
    def find_aoe(self, x, y, subtile):
        """Find the total area of effect of the tool, based on tool dimensions
        Return a list of tiles to modify in [(x,y), subtile] form"""
        tiles = []
        for xx in range(Test.xdims):
            for yy in range(Test.ydims):
                # If this is a multi-tile operation we don't care about the subtile
                # Could be modified to draw a box around the tile area
                # Would be even better if this was intelligent, and drew a line around any demarked area of the selection, e.g. where there are cliffs
                # This function can then be put into the base Tool class to be used by any tool that requires it, can do highlighting based on lots
                #  of different options...
                if x > 1 or y > 1:
                    tiles.append([(x + xx, y + yy), 9])
                else:
                    tiles.append([(x + xx, y + yy), subtile])
        return tiles
    def find_highlight(self, x, y, subtile):
        """Find the primary area of effect of the tool, based on tool dimensions
        Return a list of tiles to modify in [(x,y), subtile] form
        Used to specify region which will be highlighted"""
        tiles = []
        for xx in range(Test.xdims):
            for yy in range(Test.ydims):
                tiles.append([(x + xx, y + yy), subtile])
        return tiles
    def update(self, current, collisionlist):
        """Tool updated, current cursor position is newpos"""
        # If start is None, then there's no dragging operation ongoing
        self.current = current
        if self.start == None:
            self.tile = self.collide_locate(self.current, collisionlist)
            if self.tile and not self.tile.exclude:
                self.subtile = self.subtile_position(self.current, self.tile)
                self.tiles = self.find_aoe(self.tile.xWorld, self.tile.yWorld, self.subtile)
                return self.tiles
            else:
                return []
        # Otherwise a drag operation is on-going, do usual tool behaviour
        else:
            addback = 0
            # This should return a list of tiles to highlight
            # First time update is called store the tile we're interacting with by doing a collision detection search,
            # also store subtile so we know which corner we're modifying
            if not self.tiles:
                self.tile = self.collide_locate(self.current, collisionlist)
                if self.tile and not self.tile.exclude:
                    self.subtile = self.subtile_position(self.current, self.tile)
                    self.tiles = self.find_aoe(self.tile.xWorld, self.tile.yWorld, self.subtile)
                    # Tiles now contains a list of all tiles to modify
                else:
                    return []
            

            diff = (self.current[1] - self.start[1]) / ph
            diffrem = (self.current[1] - self.start[1]) % ph
            self.start = (self.start[0], self.start[1] + diff * ph)

##        if diff != 0:
##            invdiff = - diff
##            totalchange, realchange = self.modify_tile(self.tile, self.subtile, invdiff)
##            print "invdiff: %s, realchange: %s, totalchange: %s, addback: %s" % (invdiff, realchange, totalchange, addback)

            invdiff = -diff

            if diff != 0:
                if len(self.tiles) > 1:
                    self.modify_tiles(self.tiles, 9, invdiff)
                else:
                    self.modify_tile(self.tiles[0][0], self.subtile, invdiff)

            return self.tiles


    def modify_tiles(self, tiles, subtile, amount):
        """Raise or lower a region of tiles"""
        # This will always be a whole tile raise/lower
        vertices = []
        # Lowering terrain, find maximum value to start from
        if amount < 0:
            for t in tiles:
                x = t[0][0]
                y = t[0][1]
                vertices.append([World.array[x][y][0] + max(World.array[x][y][1]), (x, y)])
            step = -1
            for i in range(0, amount, step):
                maxval = max(vertices, key=lambda x: x[0])[0]
                if maxval != 0:
                    for p in vertices:
                        if p[0] == maxval:
                            p[0] -= 1
                            tgrid = World.get_height(p[1])
                            tgrid.lower_face()
                            World.set_height(tgrid, p[1])
        # Raising terrain, find minimum value to start from
        else:
            for t in tiles:
                x = t[0][0]
                y = t[0][1]
                vertices.append([World.array[x][y][0], (x, y)])
            step = 1
            for i in range(0, amount, step):
                minval = min(vertices, key=lambda x: x[0])[0]
                for p in vertices:
                    if p[0] == minval:
                        p[0] += 1
                        tgrid = World.get_height(p[1])
                        tgrid.raise_face()
                        World.set_height(tgrid, p[1])

    def modify_tile(self, t, subtile, amount):
        """Raise (or lower) a tile based on the subtile"""
        x = t[0]
        y = t[1]
        if amount > 0:
            step = 1
            for i in range(0, amount, step):
                # Whole tile raise
                if subtile == 9:
                    tgrid = World.get_height((x,y))
                    tgrid.raise_face()
                    World.set_height(tgrid, (x,y))
                # Edge raise
                elif subtile in [5,6,7,8]:
                    st1 = subtile - 5
                    st2 = st1 + 1
                    tgrid = World.get_height((x,y))
                    tgrid.raise_edge(st1, st2)
                    World.set_height(tgrid, (x,y))
                # Vertex raise
                elif subtile in [1,2,3,4]:
                    tgrid = World.get_height((x,y))
                    tgrid.raise_vertex(subtile - 1)
                    World.set_height(tgrid, (x,y))
        else:
            step = -1
            for i in range(0, amount, step):
                # Whole tile lower
                if subtile == 9:
                    tgrid = World.get_height((x,y))
                    tgrid.lower_face()
                    World.set_height(tgrid, (x,y))
                # Edge lower
                elif subtile in [5,6,7,8]:
                    st1 = subtile - 5
                    st2 = st1 + 1
                    tgrid = World.get_height((x,y))
                    tgrid.lower_edge(st1, st2)
                    World.set_height(tgrid, (x,y))
                # Vertex lower
                elif subtile in [1,2,3,4]:
                    tgrid = World.get_height((x,y))
                    tgrid.lower_vertex(subtile - 1)
                    World.set_height(tgrid, (x,y))

