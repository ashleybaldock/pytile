#!/usr/bin/python
# Development of image quilting algorythm implementation
# Test 2, Mk.1 - Re-write system to output only two tiles
#                which will be fitted together using best-
#                fit algorythm and path of least error
# Test 2, Mk.3 - Implement cut path along two tiles
# Test 2, Mk.4 - Implement minimum error cut along output tiles (partially complete)
# Test 2, Mk.5 - Make method to turn tiles into wang tiles through edge
#                cutting and some sort of transform
# Test 2, Mk.6 - Improve everything so it isn't crap

import os, sys
import pygame
import random
import Image
import math

# paksize   
p = 150
# Width/height of tile fragment
w = 32
# Overlap
v = 6
# Number of tile-fragments (for wang-tile generation)
# X-dimension (left-right)
X = 2
# Y-dimension (top-bottom)
Y = 2
# Error threshold
R = 0.2
# Repitition (number of random tile combos to check)
rep = 500

# Value of transparent
TRANSPARENT = (231,255,255)

# For all possible tiles in the source texture compare X number of tiles
# at the edges, if the overall error is below the error threshold, add
# this set of tiles to the list of possibles.

# Needs addition of code to do the path of least error cut for knitting
# together the images (probably do this by setting pixel transparencies
# before pasting one image onto another)


WangTiles = []
# ((Tile description), tile image number)
# top, left, bottom, right
WangTiles.append(((0,0,0,0), 0))     # 0
WangTiles.append(((1,1,1,1), 1))     # 14
WangTiles.append(((0,0,1,1), 2))     # 12
WangTiles.append(((1,1,0,0), 3))     # 3
WangTiles.append(((0,1,0,1), 4))     # 10
WangTiles.append(((1,0,1,0), 5))     # 5
WangTiles.append(((0,1,1,0), 6))     # 6
WangTiles.append(((1,0,0,1), 7))     # 9


class Node:
    """A square used in pathfinding"""
    def __init__(self, coords, parent, cost):
        # Information contained by the square
        self.coords = coords
        self.parent = parent
        self.cost = cost
        self.path_cost = cost
    def ChangeParent(self, newparent):
        self.parent = newparent
    def ChangePathCost(self, pathcost):
        self.path_cost = pathcost
            

# First, need a class which represents the input texture
class Texture:
    """Texture object for tiling"""    
    def __init__(self, rect=None, val=0):
        self.texture = pygame.image.load("texture3a.png")
        self.texture.set_alpha(None)
        self.texture = self.texture.convert()

        self.tex_x = self.texture.get_width()
        self.tex_y = self.texture.get_height()

        self.texture_pil = Image.fromstring("RGBX", (self.tex_x,self.tex_y), pygame.image.tostring(self.texture, "RGBX"))

    def CutImageEdge2(self, error_surface, image, edge):
        """Uses an error surface to cut the edge of an image"""
        # error_surface in form [x][y]
        # print str(error_surface)
        # swap dimensions of the array if necessary
        image = image.copy()
        esurf = []
        im = image.load()

        closed_list = []
        open_list = []
        # Nodes start off on the node_list, then they are moved to the open
        # or closed lists as required
        node_list = []
        
        size_y = len(error_surface[0])
        size_x = len(error_surface)

        for y in range(size_y):
            for x in range(size_x):
                node_list.append(Node((x,y), (-1,-1), error_surface[x][y]))

        # Move the first node from the node_list to the open_list
        for i in range(len(node_list)-1):
            if node_list[i].coords == (0,0):
                open_list.append(node_list.pop(i))

        j = 0
        # Now onto the main pathfinding loop
        while j == 0:
            if open_list == []:
                # No path is possible (this should never happen!)
                j = 2
            else:
                # Start by finding the lowest pathcost square on the open list
                aa = []
                for i in range(len(open_list)):
                    aa.append(open_list[i].path_cost)

                current_node = open_list[aa.index(min(aa))]
                # Now switch the current node over to the closed_list
                closed_list.append(open_list.pop(aa.index(min(aa))))
                
                if current_node.coords[1] == size_y - 1:
                    # We have found the target, so go no further
                    j = 1
                else:
                    # Now, we have the lowest cost square, we check
                    # each of the squares we can now possibly move to,
                    # these are the touching squares on the row below
                    xx, yy = current_node.coords
                    for i in [(xx-1,yy+1), (xx,yy+1), (xx+1,yy+1)]:
                        # First, check to see if this is in the closed_list
                        # If it is on the closed list, do nothing
                        for aa in range(len(open_list)):
                            if open_list[aa].coords == i:
                                # If it's on the open_list, check to see if this
                                # path to the square is better than its current path
                                # and if so change the parent & path costs
                                if open_list[aa].path_cost > current_node.path_cost + open_list[aa].cost:
                                    open_list[aa].path_cost = current_node.path_cost + open_list[aa].cost
                                    open_list[aa].parent = current_node.coords
                        for aa in range(len(node_list) - 1):
                            if node_list[aa].coords == i:
                                # If it's on the node_list, move it to the
                                # open list and set its parent to be the current
                                # square, then calculate the path cost
                                node_list[aa].parent = current_node.coords
                                node_list[aa].path_cost = current_node.path_cost + node_list[aa].cost
                                open_list.append(node_list.pop(aa))
        path = []
        if j == 1:
            # We have found a path, so now we just need to read out
            # that path and then mask the image
            k = 0
            while k == 0:
                path.insert(0, current_node.coords)
                if current_node.coords == (0,0):
                    # Path is complete
                    k = 1
                else:
                    for aa in range(len(closed_list)):
                        if closed_list[aa].coords == current_node.parent:
                            current_node = closed_list[aa]
        # Now we have our path, so we can use it to mask the output
        # image...

        for y in range(len(path)):
            for x in range(size_x):
                if x < path[y][0]:
                    im[x,y] = (0,0,0,0)

##        apple.append(b)
##        # This uses a very basic pathfinding system,
##        # it searches each row for the lowest value and takes
##        # that to be the next step in the path
##        # This needs to be replaced with a better pathfinding system!
##        if edge in [1,3]:
##            # esurf now in form [y][x]
##            for y in range(len(error_surface[0])):
##                aa = []
##                for x in range(len(error_surface)):
##                    aa.append(error_surface[x][y])
##                esurf.append(aa)
##            
##            # Now do cutting
##            for y in range(len(esurf)):
##                # Find the minimum error value in this row
##                minimum = min(esurf[y])
##                # And find its list index
##                k = esurf[y].index(minimum)
##                
##                for x in range(len(esurf[0])):
##                    if x < k:
##                        im[x,y] = (0,0,0,0)
##        else:
##            esurf = error_surface
##            # Now do cutting
##            for y in range(len(esurf)):
##                # Find the minimum error value in this row
##                minimum = min(esurf[y])
##                # And find its list index
##                k = esurf[y].index(minimum)
##                
##                for x in range(len(esurf[0])):
##                    if x < k:
##                        im[y,x] = (0,0,0,0)


        return image

    def CompareRegionError2(self, regions):
        """Compares two images to find the error between them"""
        reg1, type1, part1, reg2, type2, part2 = regions

        if type1 in [0,2]:
            region1 = self.tiles_X[reg1].copy()
        elif type1 in [1,3]:
            region1 = self.tiles_Y[reg1].copy()
        else:
            region1 = reg1.copy()
        if type2 in [0,2]:
            region2 = self.tiles_X[reg2].copy()
        elif type2 in [1,3]:
            region2 = self.tiles_Y[reg2].copy()
        else:
            region2 = reg2.copy()
        
        # Make pixel access objects
        r1 = region1.load()
        r2 = region2.load()

        # part1 of the form 0: top, 1: left, 2: bottom, 3: right
        if part1 == 0:      # top
            off_x1 = 0
            off_y1 = 0
            width = region1.size[0]
            height = v
        elif part1 == 1:    # left
            off_x1 = 0
            off_y1 = 0
            width = v
            height = region1.size[1]
        elif part1 == 2:    # bottom
            off_x1 = 0
            off_y1 = w - v
            width = region1.size[0]
            height = v
        elif part1 == 3:    # right
            off_x1 = w - v
            off_y1 = 0
            width = v
            height = region1.size[1]

        # part2 of the form 0: top, 1: left, 2: bottom, 3: right
        if part2 == 0:      # top
            off_x2 = 0
            off_y2 = 0
        elif part2 == 1:    # left
            off_x2 = 0
            off_y2 = 0
        elif part2 == 2:    # bottom
            off_x2 = 0
            off_y2 = w - v
        elif part2 == 3:    # right
            off_x2 = w - v
            off_y2 = 0

        # Now go through for all pixels and calculate the difference
        # between the two images
        surf_array = []
        diff_total = 0
        max_total = width * height * 255 * 3.0
        error_surface = []
        for x in range(width):
            surf = []
            for y in range(height):
                r1_r, r1_g, r1_b, r1_a = r1[off_x1 + x, off_y1 + y]
                r2_r, r2_g, r2_b, r2_a = r2[off_x2 + x, off_y2 + y]
                
                if r1_r > r2_r:
                    diff_r = r1_r - r2_r
                elif r1_r == r2_r:
                    diff_r = 0
                else:
                    diff_r = r2_r - r1_r

                if r1_g > r2_g:
                    diff_g = r1_g - r2_g
                elif r1_g == r2_g:
                    diff_g = 0
                else:
                    diff_g = r2_g - r1_g

                if r1_b > r2_b:
                    diff_b = r1_b - r2_b
                elif r1_b == r2_b:
                    diff_b = 0
                else:
                    diff_b = r2_b - r1_b

                # The smaller the value of diff_total, the smaller
                # the overall difference or error
##                diff_total = diff_total + (diff_r + diff_g + diff_b)
                diff = math.sqrt((diff_r * diff_r) + (diff_g * diff_g) + (diff_b * diff_b))
                diff_total = diff_total + diff
                surf.append(diff)
            surf_array.append(surf)
            
        return (diff_total, surf_array)

    def MakeWang(self):
        """Uses the texture to generate a set of wang tiles, by comparing
           the error value along the joins of random subsections from the
           source texture"""
        texture = Image.fromstring("RGBX", (self.texture.get_width(),self.texture.get_height()), pygame.image.tostring(self.texture, "RGBX"))

##        self.tiles_X = []
##        self.tiles_Y = []
        possibles = []


        error_list = []
        possible_list = []
        
        self.tiles_X = []
        self.tiles_X.append(Image.new("RGBA",(w,w)))
        self.tiles_X.append(Image.new("RGBA",(w,w)))

        self.tiles_Y = []
        self.tiles_Y.append(Image.new("RGBA",(w,w)))
        self.tiles_Y.append(Image.new("RGBA",(w,w)))

        for s in range(rep):
            # Generate 4 sets of coordinates for the 4 random patches of texture
            # These are stored each time in the possibles array
            possibles = []
            for i in range(X + Y):
                possibles.append((random.randint(0, self.tex_x - w), random.randint(0, self.tex_y - w)))

            # Now actually crop those sections out of the texture and store them in two lists
            # one for X and one for Y
            for i in range(X):
                a = texture.crop((possibles[i][0], possibles[i][1], possibles[i][0] + w, possibles[i][1] + w))
                self.tiles_X[i].paste(a,(0,0,w,w))

            for i in range(Y):
                a = texture.crop((possibles[i+X][0], possibles[i+X][1], possibles[i+X][0] + w, possibles[i+X][1] + w))
                self.tiles_Y[i].paste(a,(0,0,w,w))


            # Comparisons are added to a list, which keeps track of what has
            # been compared, comparisons are tuples of form:
            #   (X, direction, Y, direction, comp_error)
            # Where X is which X tile it is, Y is which Y tile it is
            # and direction indicates the edge of X and Y which are compared
            # (i.e. 0: top, 1: left, 2: bottom, 3: right
            # comp_error is the comparison error value obtained, this needs to
            # be added to the running total for each instance of this comparison

            # For each WangTile in the WangTiles list, perform all comparisons
            # between the tiles in the relavent arrays (unless this test has
            # already been performed, in which case skip it)


            # Test with just two tiles
            # Optimizing so that the right/left edges match up

            skip_list = []
            skip_error = []
            total_error = 0
            for i in range(len(WangTiles)):

                # top, left, bottom, right
                tile = WangTiles[i][0]
                comparison = []
                # comp AB
                #               tile variant number, X or Y type, comparison type
                comparison.append((tile[0], 0, 2, tile[1], 1, 0))
                # comp BC
                comparison.append((tile[1], 1, 3, tile[2], 2, 1))
                # comp CD
                comparison.append((tile[2], 2, 0, tile[3], 3, 2))
                # comp DA
                comparison.append((tile[3], 3, 1, tile[0], 0, 3))
                for j in range(4):
                    if comparison[j] in skip_list:
                        total_error = total_error + skip_error[skip_list.index(comparison[j])]
                    else:
                        skip_list.append(comparison[j])
                        error, meh = self.CompareRegionError2(comparison[j])
                        total_error = total_error + error
                        skip_error.append(error)

                error_list.append(total_error)
                possible_list.append(possibles)


        sel = min(error_list)
        k = error_list.index(sel)
        possibles = possible_list[k]

        for i in range(X):
            a = texture.crop((possibles[i][0], possibles[i][1], possibles[i][0] + w, possibles[i][1] + w))
            self.tiles_X[i].paste(a,(0,0,w,w))

        for i in range(Y):
            a = texture.crop((possibles[i+X][0], possibles[i+X][1], possibles[i+X][0] + w, possibles[i+X][1] + w))
            self.tiles_Y[i].paste(a,(0,0,w,w))

        # Now produce an array containing the patched together wang tile primitives
        wang_tile_prims = []
        wang_tiles = []
        for i in range(len(WangTiles)):
            wang_tile_prims.append(Image.new("RGBA",(w*2,w*2)))
            wang_tiles.append(Image.new("RGBA",(w*2,w*2)))
            temp1 = Image.new("RGBA",(w*2,w))
            temp2 = Image.new("RGBA",(w*2,w))
            
            tile = WangTiles[i][0]

            # First step, paste the first (top-left) part of the tile
            # into each of the temporary images
            temp1.paste(self.tiles_X[tile[0]],(0,0,w,w))
            temp2.paste(self.tiles_Y[tile[1]],(0,0,w,w))

            # Next, generate an error surface between this tile and the tile to the
            # right of it for both temp. images
            meh, error_surface1 = self.CompareRegionError2((tile[3], 3, 1, tile[0], 0, 3))
            meh, error_surface2 = self.CompareRegionError2((tile[2], 2, 1, tile[1], 1, 3))

            # Then use that error surface to cut the edge of the right-hand tile
            # using a modified Dijkstra's algorythm
            image1 = self.CutImageEdge2(error_surface1, self.tiles_Y[tile[3]], 1)
            image2 = self.CutImageEdge2(error_surface2, self.tiles_X[tile[2]], 1)

            # Now paste the returned image onto the temporary image, at the right position
            temp1.paste(self.tiles_Y[tile[3]],(w-v,0,w*2-v,w),image1)
            temp2.paste(self.tiles_X[tile[2]],(w-v,0,w*2-v,w),image2)

            # Next, we must repeat the process for the two temp images we've obtained
            # So first obtain the error surface
            meh, error_surface3 = self.CompareRegionError2((temp1, 5, 2, temp2, 5, 0))

            # Then use error surface to cut the top edge of the bottom part
            image3 = self.CutImageEdge2(error_surface3, temp2, 0)

            # Now paste the returned image onto the output image, at the right position
            wang_tile_prims[i].paste(temp1,(0,0,w*2,w))
            wang_tile_prims[i].paste(temp2,(0,w-v,w*2,w*2-v),image3)

            # Finally, transform each image to produce a finished tile
            #      top x,       top y,   left x,  left y,      bottom x,    bottom y,          right x,           right y
##            data = (w-(v/2.0)), (v/2.0), (v/2.0), (w-(v/2.0)), (w-(v/2.0)), (2*w - v - (v/2)), (2*w - v - (v/2)), (w-(v/2.0))
            data = (v/2.0), (w-(v/2.0)), (w-(v/2.0)), (2*w - v - (v/2)), (2*w - v - (v/2)), (w-(v/2.0)), (w-(v/2.0)), (v/2.0)

            wang_tiles[i].paste(wang_tile_prims[i].transform((w,w), Image.QUAD, data), (0,0))

            # Now we would repeat the process for the bottom two tiles, pasting them into a
            # temporary container image, which would then be compared (top edge of temp image
            # with "bottom edge" of the image we've built up so far) to generate an error
            # surface. Then we'd cut along that surface on the temp image and paste it in,
            # completing the effect

            # For now though, simply do the first two bits...

        #print "a"
        # Go through blitting all the wang tiles formed by these input tiles
        # to the example output image
        ret = pygame.Surface((w*2*(len(WangTiles)),w*6))
        #print "b"
        for i in range(len(wang_tile_prims)):
            aa = pygame.image.frombuffer((wang_tile_prims[i].tostring()), (w*2,w*2), "RGBA")
            bb = pygame.image.frombuffer((wang_tiles[i].tostring()), (w*2,w*2), "RGBA")
            ret.blit(aa, (w*2*i,0))
            ret.blit(bb, (w*i,w*2))

        aa = pygame.image.frombuffer((self.tiles_X[0].tostring()), (w,w), "RGBA")
        ret.blit(aa, (0, w*4))
        aa = pygame.image.frombuffer((self.tiles_X[1].tostring()), (w,w), "RGBA")
        ret.blit(aa, (w, w*4))
        aa = pygame.image.frombuffer((self.tiles_Y[0].tostring()), (w,w), "RGBA")
        ret.blit(aa, (w*2, w*4))
        aa = pygame.image.frombuffer((self.tiles_Y[1].tostring()), (w,w), "RGBA")
        ret.blit(aa, (w*3, w*4))
        return ret

##            # If the error is below the threshold, return this tile for blitting
##            if total_error < 800000:
##                ret = pygame.Surface((w*2,w*2))
##                aa = pygame.image.frombuffer((self.tiles_X[0].tostring()), (w,w), "RGB")
##                ret.blit(aa, (0,0))
##                aa = pygame.image.frombuffer((self.tiles_Y[0].tostring()), (w,w), "RGB")
##                ret.blit(aa, (0,w-v))
##                aa = pygame.image.frombuffer((self.tiles_Y[1].tostring()), (w,w), "RGB")
##                ret.blit(aa, (w-v,0))
##                aa = pygame.image.frombuffer((self.tiles_X[1].tostring()), (w,w), "RGB")
##                ret.blit(aa, (w-v,w-v))
##
##                return ret

class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

    def __init__(self, width=800,height=600):
        # Initialize PyGame
        pygame.init()
        
        # Set the window Size
        self.width = width
        self.height = height
        
        # Create the Screen
        self.screen = pygame.display.set_mode((self.width
                                               , self.height), pygame.RESIZABLE)
        
        self.dxoff = 0
        self.dyoff = 0
        
        # Init classes
        self.texture = Texture()

    def MainLoop(self):
        """This is a testing loop to display the output of the rendering tests"""

        # Create the background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        #self.background.set_colorkey((231,255,255))
        #self.background.fill((0,0,0))

        
        # Find the width and height of the screen as multiples of w
##        tiles_wide = self.width / (w - v)
##        tiles_high = self.height / (w - v)
        tiles_wide = 4
        tiles_high = 5

        #array = self.MakeTileArray(tiles_high, tiles_wide)

        self.background.blit(self.texture.MakeWang(), (0,0))
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "r":
                        self.background.fill((0,0,0))
                        self.background.blit(self.texture.MakeWang(), (0,0))
                        self.screen.blit(self.background, (0, 0))
                        pygame.display.flip()

                else:
                    self.screen.blit(self.background, (0, 0))

                    pygame.display.flip()

                    pygame.time.wait(100)

if __name__ == "__main__":

    MainWindow = DisplayMain()
    MainWindow.MainLoop()

