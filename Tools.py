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
from World import World

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




class Test(Tool):
    """Testing tool"""
    xdims = 2
    ydims = 3
    def __init__(self, start):
        """New application of this tool, begins at startpos"""
        # Call init method of parent
        super(Test, self).__init__()
        self.start = start
        self.tile = None
        self.tiles = None
        
    def update(self, current, collisionlist):
        """Tool updated, current cursor position is newpos"""
        self.current = current
        addback = 0
        # This should return a list of tiles to highlight
        # First time update is called store the tile we're interacting with by doing a collision detection search,
        # also store subtile so we know which corner we're modifying
        if not self.tile:
            self.tile = self.collide_locate(self.current, collisionlist)
            self.subtile = self.subtile_position(self.current, self.tile)
        if not self.tiles:
            self.tile = self.collide_locate(self.current, collisionlist)
            x = self.tile.xWorld
            y = self.tile.yWorld
            self.tiles = []
            for xx in range(Test.xdims):
                for yy in range(Test.ydims):
                    self.tiles.append([(x + xx, y + yy), self.subtile])
            # Tiles now contains a list of all tiles to modify
            

        diff = (self.current[1] - self.start[1]) / ph
        diffrem = (self.current[1] - self.start[1]) % ph
        self.start = (self.start[0], self.start[1] + diff * ph)

##        if diff != 0:
##            invdiff = - diff
##            totalchange, realchange = self.modify_tile(self.tile, self.subtile, invdiff)
##            print "invdiff: %s, realchange: %s, totalchange: %s, addback: %s" % (invdiff, realchange, totalchange, addback)

        invdiff = -diff

        if diff != 0:
            self.modify_tiles(self.tiles, 9, invdiff)
##            for t in self.tiles:
##                totalchange, realchange = self.modify_tile(t[0], self.subtile, invdiff)

        return self.tiles

    def end(self, endpos):
        """End of application of tool"""
        self.currentpos = endpos
        # This should return a list of tiles to highlight
        return []

    def modify_tiles(self, tiles, subtile, amount):
        """Raise or lower a region of tiles"""
        # This will always be a whole tile raise/lower

        # Find highest point
        # Reduce those points by 1 each
        # Continue to next iteration
        # 4 points per tile at each vertex, found by summing height with vertexheight
        # These can be represented by [x][y][v] where x and y are the world coords, and v is the vertex coord [0,1,2,3]
        vertices = []
        # Lowering terrain, find maximum value to start from
        if amount < 0:
            for t in tiles:
                x = t[0][0]
                y = t[0][1]
                vertices.append([World.array[x][y][0] + max(World.array[x][y][1]), (x, y)])
            step = -1
            for i in range(0, amount, step):
                print vertices
                maxval = max(vertices, key=lambda x: x[0])[0]
                if maxval != 0:
                    for p in vertices:
                        if p[0] == maxval:
                            p[0] -= 1
                            x = p[1][0]
                            y = p[1][1]
                            grid = [World.array[x][y][1][0], World.array[x][y][1][1], World.array[x][y][1][2], World.array[x][y][1][3]]
                            t = World.array[x][y][0]

                            if 2 in grid:
                                for k in range(len(grid)):
                                    if grid[k] == 2:
                                        grid[k] = 1
                            elif 1 in grid:
                                grid = [0,0,0,0]
                            else:
                                t -= 1

                            # Tile must not be reduced to below 0
                            if t < 0:
                                t = 0
            
                            World.array[x][y][1] = grid
                            World.array[x][y][0] = t
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
                        x = p[1][0]
                        y = p[1][1]
                        grid = [World.array[x][y][1][0], World.array[x][y][1][1], World.array[x][y][1][2], World.array[x][y][1][3]]
                        t = World.array[x][y][0]
                        # Sort the correct tile type
                        if 2 in grid:
                            t += 1
                            for k in range(len(grid)):
                                grid[k] -= 1
                                if grid[k] < 0:
                                    grid[k] = 0
                        elif 1 in grid:
                            t += 1
                            grid = [0,0,0,0]
                        else:
                            t += 1
        
                        World.array[x][y][1] = grid
                        World.array[x][y][0] = t


    def modify_tile(self, t, subtile, amount):
        """Raise (or lower) a tile based on the subtile"""
        x = t[0]
        y = t[1]
        t = World.array[x][y][0]
        tgrid = tGrid(World.array[x][y][1])
##        t = World.array[tile.xWorld][tile.yWorld][0]
        total = 0
        if amount > 0:
            step = 1
            for i in range(0, amount, step):
                # Whole tile raise
                total += 1
                if subtile == 9:
                    if 2 in tgrid:
                        t += 1
                        for k in range(len(tgrid)):
                            tgrid[k] -= 1
                            if tgrid[k] < 0:
                                tgrid[k] = 0
                    elif 1 in tgrid:
                        t += 1
                        tgrid([0,0,0,0])
                    else:
                        t += 1
                # Edge raise
                elif subtile in [5,6,7,8]:
                    st1 = subtile - 5
                    st2 = st1 + 1
##                    print "st1: %s, tgrid[st1]: %s, st2: %s, tgrid[st2]: %s" % (st1, tgrid[st1], st2, tgrid[st2])
                    if tgrid[st1] > tgrid[st2]:
                        # Raise the one which is lower first
                        tgrid, t = self.modify_vertex(tgrid, t, st2, step)
                    elif tgrid[st1] < tgrid[st2]:
                        tgrid, t = self.modify_vertex(tgrid, t, st1, step)
                    else:
                        # Edge is already level, simply raise those vertices
                        tgrid, t = self.modify_vertex(tgrid, t, st1, step)
                        tgrid, t = self.modify_vertex(tgrid, t, st2, step)
                # Vertex raise
                elif subtile in [1,2,3,4]:
                    st = subtile - 1
                    tgrid, t = self.modify_vertex(tgrid, t, st, step)
        else:
            step = -1
            for i in range(0, amount, step):
                if t > 0 or [1,2] in tgrid:
                    total -= 1
                # Whole tile lower
                if subtile == 9:
                    if 2 in tgrid:
                        for k in range(len(tgrid)):
                            if tgrid[k] == 2:
                                tgrid[k] = 1
                    elif 1 in tgrid:
                        tgrid([0,0,0,0])
                    else:
                        t -= 1
                # Edge lower
                elif subtile in [5,6,7,8]:
                    st1 = subtile - 5
                    st2 = st1 + 1
                    if tgrid[st1] > tgrid[st2]:
                        # Lower the one which is higher first
                        tgrid, t = self.modify_vertex(tgrid, t, st1, step)
                    elif tgrid[st1] < tgrid[st2]:
                        tgrid, t = self.modify_vertex(tgrid, t, st2, step)
                    else:
                        # Edge is already level, simply lower those vertices
                        tgrid, t = self.modify_vertex(tgrid, t, st1, step)
                        tgrid, t = self.modify_vertex(tgrid, t, st2, step)
                # Vertex lower
                elif subtile in [1,2,3,4]:
                    st = subtile - 1
                    tgrid, t = self.modify_vertex(tgrid, t, st, step)

        # Tile must not be reduced to below 0
        if t < 0:
            t = 0
        ct = World.array[x][y][0]
        
        World.array[x][y][1] = [tgrid[0],tgrid[1],tgrid[2],tgrid[3]]
        World.array[x][y][0] = t
        # Return the total amount of height change, and the real amount
        return (total, ct - t)

    def modify_vertex(self, tgrid, t, st, step):
        """Raise or lower one corner of a tile"""
        if step > 0:
            if tgrid[st] == 0:
                tgrid[st] += 1
                if not 0 in tgrid:
                    for k in range(len(tgrid)):
                        tgrid[k] -= 1
                    t += 1
                elif 2 in tgrid and not 0 in tgrid:
                    for k in range(len(tgrid)):
                        tgrid[k] -= 1
                    t += 1
            elif tgrid[st] == 1:
                if 2 in tgrid:
                    # If there is a 2 there already increase the tile we're dealing with to 2, then subtract 1
                    # from any remaining 1's and increase the tile's height by 1
                    t += 1
                    tgrid[st] += 1
                    for k in range(len(tgrid)):
                        if tgrid[k] == 2:
                            tgrid[k] = 1
                        elif tgrid[k] == 1:
                            tgrid[k] = 0
                else:
                    # If there isn't already a 2, if neighbours are both 0 and opposite is 1
                    # raise height by 1 and set active corner to 1
                    if tgrid[st + 2] == 1:
                        t += 1
                        tgrid([0,0,0,0])
                        tgrid[st] = 1
                    else:
                        tgrid([0,0,0,0])
                        tgrid[st] = 2
                        # Modify ones either side
                        tgrid[st + 1] = 1
                        tgrid[st - 1] = 1
            elif tgrid[st] == 2:
                # If raising corner is 2, just raise the entire tile by 1
                t += 1
        else:
            if tgrid[st] == 0 and t != 0:
                if 2 in tgrid:
                    # Just reduce the layer
                    t -= 1
                elif 1 in tgrid:
                    # Reduce by 1 and set the others to a 121 configuration, unless opposite is also
                    # 0 in which case set all to 1, then set active corner to 0 and reduce tile by 1
                    if tgrid[st + 2] == 0:
                        t -= 1
                        tgrid([1,1,1,1])
                        tgrid[st] = 0
                    else:
                        t -= 1
                        tgrid([2,2,2,2])
                        tgrid[st] = 0
                        # Modify ones either side
                        tgrid[st + 1] = 1
                        tgrid[st - 1] = 1
                else:
                    t -= 1
                    tgrid([1,1,1,1])
                    tgrid[st] = 0
            elif tgrid[st] == 1:
                if 2 in tgrid:
                # If lowering corner is 1 and there is a 2 reduce the 2 by 1 and reduce
                # the lowering corner by 1
                    for k in range(len(tgrid)):
                        if tgrid[k] == 2:
                            tgrid[k] -= 1
                    tgrid[st] -= 1
                else:
                    # No 2, so just 1's and 0's, so safe to just reduce by 1
                    tgrid[st] -= 1
            elif tgrid[st] == 2:
                # If lowering corner is 2, simply reduce it by 1
                tgrid[st] -= 1
        return tgrid, t


