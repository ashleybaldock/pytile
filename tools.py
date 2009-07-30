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
    aoe = []
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
        self.aoe = []
    def process_key(self, key):
        """Process a keystroke during a drag operation"""
        keyname = pygame.key.name(key)
        if keyname == "[":
            Test.xdims += 1
        elif keyname == "]":
            Test.xdims -= 1
            if Test.xdims < 1:
                Test.xdims = 1
        elif keyname == "o":
            Test.ydims += 1
        elif keyname == "p":
            Test.ydims -= 1
            if Test.ydims < 1:
                Test.ydims = 1
        elif keyname == "s":
            Test.smooth = not(Test.smooth)
        if keyname in ["o","p","[","]"]:
            self.set_highlight(self.find_highlight(self.tile.xWorld, self.tile.yWorld, self.subtile))
            self.set_highlight_changed(True)
        print pygame.key.name(key)
        return True
    def active(self):
        """Return true if tool currently being used and screen needs updating"""
        # Used to test whether the tiles being returned need to be updated
        if self.start:
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
        """Clear the area of effect, changes will only be drawn if has_aoe_changed returns True"""
        self.aoe = []
        return True

    # Highlight related access functions
    # External
    def get_highlight(self):
        """Return the current highlight area for this tool"""
        return self.highlight
    def get_last_highlight(self):
        """Return the previous highlight"""
        return self.last_highlight
    def has_highlight_changed(self):
        """Return True if the area of effect of this tool has changed since last call to update()"""
        return self.highlight_changed
    # Internal
    def set_highlight(self, value):
        """Set the current highlight for this tool"""
        self.last_highlight = self.highlight
        self.highlight = value
    def set_highlight_changed(self, v):
        """When highlight changes (e.g. mouse cursor moves) set this to have the appropriate bit of the screen refreshed"""
        self.highlight_changed = v
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

    def begin(self, start):
        """Reset the start position for a new operation"""
        self.start = start
        self.addback = 0
    def end(self, final):
        """End of application of tool"""
        self.current = final
        self.tiles = []
        self.start = None
    def update(self, current, collisionlist):
        """Tool updated, current cursor position is newpos"""
        # If start is None, then there's no dragging operation ongoing, just update the position of the highlight
        self.current = current
        if self.start == None:
            tile = self.collide_locate(self.current, collisionlist)
            if tile and not tile.exclude:
                subtile = self.subtile_position(self.current, tile)
                # Only update the highlight if the cursor has changed enough to require it
                if tile != self.tile or subtile != self.subtile:
                    self.set_highlight(self.find_highlight(tile.xWorld, tile.yWorld, subtile))
                    self.set_highlight_changed(True)
                else:
                    self.set_highlight_changed(False)
                self.tile = tile
                self.subtile = subtile
                
        # Otherwise a drag operation is on-going, do usual tool behaviour
        else:
##            addback = 0
            # If we don't already have a list of tiles to use as the primary area of effect
            if not self.tiles:
                tile = self.collide_locate(self.current, collisionlist)
                if tile and not tile.exclude:
                    subtile = self.subtile_position(self.current, tile)
                    self.tiles = self.find_rect_aoe(tile.xWorld, tile.yWorld)
                    # Tiles now contains the primary area of effect for this operation
                    self.tile = tile
                    self.subtile = subtile


            diff = (self.current[1] - self.start[1]) / ph
            self.start = (self.start[0], self.start[1] + diff * ph)

##            adiff = diff - self.addback
##
##            invdiff = -diff + self.addback

##        if diff != 0:
##            invdiff = - diff
##            totalchange, realchange = self.modify_tile(self.tile, self.subtile, invdiff)
##            print "invdiff: %s, realchange: %s, totalchange: %s, addback: %s" % (invdiff, realchange, totalchange, addback)

            invdiff = -diff

            if diff != 0:
                if len(self.tiles) > 1:
                    self.modify_tiles(self.tiles, invdiff, soft=Test.smooth)
                else:
                    r = self.modify_tile(self.tiles[0], self.subtile, invdiff, soft=Test.smooth)
                # Addback is calcuated as the total requested height change minus the *actual* height change. The remainder is the
                # amount of cursor movement which doesn't actually do anything.
                # for example, if the cursor moves down (lowering the terrain) and hits the "0" level of the terrain we can't continue
                # to lower the terrain. The cursor keeps moving however and the addback value keeps track of this so that when the
                # cursor starts to move up again it won't start raising the terrain again until it hits the "0" level again
##                self.addback = invdiff - r
                # Set this so that the changed portion of the map is updated on screen
                self.set_aoe_changed(True)
                # Must also re-draw the highlight if we're changing the map
                self.set_highlight_changed(True)

    def modify_tiles(self, tiles, amount, soft=False):
        """Raise or lower a region of tiles"""
        self.aoe = []
        # This will always be a whole tile raise/lower
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
                    for p in vertices:
                        if p[0] == maxval:
                            p[0] -= 1
                            tgrid = World.get_height(p[1])
                            tgrid.lower_face()
                            World.set_height(tgrid, p[1])
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
                        tgrid = World.get_height(p[1])
                        tgrid.raise_face()
                        World.set_height(tgrid, p[1])
            if soft:
                # Soften around the modified tiles
                self.soften(self.aoe, soften_up=True)


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

    def modify_tile(self, t, subtile, amount, soft=False):
        """Raise (or lower) a tile based on the subtile"""
        x = t[0]
        y = t[1]
        # r measures the total amount of raising/lowering *actually* done
        # This can then be compared with the amount requested to calculate the cursor offset
        r = 0
        if amount > 0:
            step = 1
            for i in range(0, amount, step):
                # Whole tile raise
                if subtile == 9:
                    tgrid = World.get_height(x,y)
                    tgrid.raise_face()
                    World.set_height(tgrid, (x,y))
                    self.aoe = [(x,y)]
                # Edge raise
                elif subtile in [5,6,7,8]:
                    st1 = subtile - 5
                    st2 = st1 + 1
                    tgrid = World.get_height(x,y)
                    tgrid.raise_edge(st1, st2)
                    World.set_height(tgrid, (x,y))
                    self.aoe = [(x,y)]
                # Vertex raise
                elif subtile in [1,2,3,4]:
                    tgrid = World.get_height(x,y)
                    tgrid.raise_vertex(subtile - 1)
                    World.set_height(tgrid, (x,y))
                    self.aoe = [(x,y)]
            if subtile == 9 and soft:
                self.soften(self.aoe, soften_up=True)
        else:
            step = -1
            for i in range(0, amount, step):
                # Whole tile lower
                if subtile == 9:
                    tgrid = World.get_height(x,y)
                    r += tgrid.lower_face()
                    World.set_height(tgrid, (x,y))
                    self.aoe = [(x,y)]
                # Edge lower
                elif subtile in [5,6,7,8]:
                    st1 = subtile - 5
                    st2 = st1 + 1
                    tgrid = World.get_height(x,y)
                    tgrid.lower_edge(st1, st2)
                    World.set_height(tgrid, (x,y))
                # Vertex lower
                elif subtile in [1,2,3,4]:
                    tgrid = World.get_height(x,y)
                    tgrid.lower_vertex(subtile - 1)
                    World.set_height(tgrid, (x,y))
                    self.aoe = [(x,y)]
            if subtile == 9 and soft:
                self.soften(self.aoe, soften_down=True)
        return r
