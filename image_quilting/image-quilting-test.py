#!/usr/bin/python
# Development of image quilting algorythm implementation
# Test 2, Mk.1 - Re-write system to output only two tiles
#                which will be fitted together using best-
#                fit algorythm and path of least error
# Test 2, Mk.3 - Implement cut path along two tiles
# Test 2, Mk.4 - Implement minimum error cut along output tiles (partially complete)
# Test 2, Mk.5 - Make method to turn tiles into wang tiles through edge
#                cutting and some sort of transform

import os, sys
import pygame
import random
import Image
import math

# paksize   
p = 64
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
rep = 1000

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


# First, need a class which represents the input texture
class Texture:
    """Texture object for tiling"""    
    def __init__(self, rect=None, val=0):
        self.texture = pygame.image.load("texture3.png")
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

        if edge in [1,3]:
            # esurf now in form [y][x]
            for y in range(len(error_surface[0])):
                aa = []
                for x in range(len(error_surface)):
                    aa.append(error_surface[x][y])
                esurf.append(aa)
            
            # Now do cutting
            for y in range(len(esurf)):
                # Find the minimum error value in this row
                minimum = min(esurf[y])
                # And find its list index
                k = esurf[y].index(minimum)
                
                for x in range(len(esurf[0])):
                    if x < k:
                        im[x,y] = (0,0,0,0)
        else:
            esurf = error_surface
            # Now do cutting
            for y in range(len(esurf)):
                # Find the minimum error value in this row
                minimum = min(esurf[y])
                # And find its list index
                k = esurf[y].index(minimum)
                
                for x in range(len(esurf[0])):
                    if x < k:
                        im[y,x] = (0,0,0,0)


        return image


    def CutImageEdge(self, error_surface, image, edge):
        """Uses an error surface to cut the edge of an image"""
        
        # edge of the form 0: top, 1: left, 2: bottom, 3: right
        if edge == 0:      # top
            off_x = 0
            off_y = 0
        elif edge == 1:    # left
            off_x = 0
            off_y = 0
        elif edge == 2:    # bottom
            off_x = 0
            off_y = w - v
        elif edge == 3:    # right
            off_x = w - v
            off_y = 0

        # error_surface is a 2 dimensional array, [x][y],
        # which represents a graph describing the error between
        # the two images. We can move down through the rows, but
        # not back up again
        # For each value in the width (height for horizontal...)
        # we find a path of least error, then we pick the minimum
        # path found and use it to set pixels transparent if they
        # are on the wrong side of that path
        open_list = []
        closed_list = []
        # values on either list are of the form:
        # (a, b, c) where a = (x,y) coords of current square (for lookup
        # in error_surface) and b = (x,y) coords of parent, c = the
        # total error involved in getting to this square
        paths = []
##        for i in range(len(error_surface[0])):
        for i in range(1):
            # First make a copy of the error surface for this path
            esurf = []
            for x in range(len(error_surface[0])):
                a = []
                for y in range(len(error_surface)):
                    a.append(error_surface[y][x])
                esurf.append(a)
                
            # Make open and closed lists
            open_list = []
            closed_list = []
            
            # For each of the potential starting squares in the first row
            # of the error surface
            open_list.append(((0,i), (0,i), esurf[0][i]))
            # Now start the main pathfinding loop
            j = 0
            while j == 0:
                # Find the lowest error square on the open list
                aa = []
                for m in range(len(open_list)):
                    aa.append(open_list[m][2])
                # Set current_square to be the smallest error value in the open list
                bb = min(aa)
                k = aa.index(bb)
                current_square = open_list[k]
                # Move the current square to the closed list
                closed_list.append(open_list.pop(k))
                
                if current_square[0][1] == len(error_surface) - 1:
                    # We have found a target square (at the bottom of the
                    # error surface) so finish up
                    j = 1
                else:
                    # Now, add the squares on the line below current_square to the
                    # open list IF:
                    #   - They are "below" the current square
                    #   - They are not on the closed list
                    # If they are already on the open list
                    n = current_square[0][1] + 1
                    for m in range(len(error_surface[0])):
                        if ((m,n), current_square[0], esurf[m][n]) not in closed_list:
                            # If this square already on the closed list, don't do anything
                            
                            if ((m,n), current_square[0], esurf[m][n]) in open_list:
                                # If this square already on the open list
                                if esurf[m][n] + current_square[2] < open_list[m][n][3]:
                                    # If path error via this parent is lower than path error
                                    # already existing on this square, then change the square
                                    # to go via this parent
                                    open_list[m][n] = ((m,n), current_square[0], esurf[m][n] + current_square[2])
                                #else:
                                    # Otherwise, don't do anything, as this path to that square would be worse
                                
                            else:
                                # If this square isn't on the open or closed lists
                                #       coords of this square, coords of parent square, error of path to this square
                                open_list.append(((m,n), current_square[0], esurf[m][n] + current_square[2]))
            # Now, we need to add this path to the list of paths
            # First find the path...
            this_path = []
            this_path_cost = current_square[2]
            path_costs = []
            j = 0
            print "closed_list" + str(closed_list)
            print "open_list: " + str(open_list)
            while j == 0:
                # If the current square has itself as a parent, this is the origin square
                if current_square[0] == current_square[1]:
                    j = 1
                # Otherwise, add the current square to the path
                else:
                    this_path.insert(0, current_square)
                    # Then make the current square the parent of the current square
                    parents = []
                    for m in range(len(closed_list)):
                        parents.append(closed_list[m][1])

                    k = parents.index((current_square[1][0], current_square[1][1]))
                    current_square = closed_list[k]
            paths.append(this_path)
            path_costs.append(this_path_cost)

        # Now, which of the paths costs the least?
        sel = min(path_costs)
        k = path_costs.index(sel)
        best_path = paths[0]
        print str(best_path)
        # So now we have the best path represented as a list of pixel coords
        # in the best_path variable
        # Make pixel access object
        im = image.load()
        for x in range(len(error_surface) - 1):
            for y in range(len(error_surface[0])):
                # For each row, set all pixels to the left of the pixel
                # in the path to be transparent
                if y < best_path[x][1]:
                    im[x,y] = (0,0,0)
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

