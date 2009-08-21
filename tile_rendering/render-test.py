#!/usr/bin/python
# Development of the rendered grounds system
# Test 1, Mk.2 - merging textures
# Test 1, Mk.3 - PIL tranforms to map rgb maps onto tiles
# Test 1, Mk.4 - Using perspective transforms now

import os, sys
import pygame
import random
import Image
import numpy
import numpy.linalg as linalg

#paksize
p = 64

#tile height difference
ph = 8

# Value of transparent
TRANSPARENT = (231,255,255)

class Texture:
    """Textures - these are blended using RGBmaps and then rendered to tile shapes
        Any number of textures should be defineable, but we will start
        with a limited number, we need to render a full set of tiles for each
        texture, as well as transitions both ways between this texture and all
        the other textures (though this could be user-definable to cut down on
        the number of permutations)
        """
    image = None

    def __init__(self):

        if Texture.image is None:
            Texture.image = pygame.image.load("texture.png")
            Texture.image.set_alpha(None)
            Texture.image = Texture.image.convert()
            Texture.textures = []
            # Now load the individual textures into the textures array
            for i in range(0,3):
                Texture.textures.append(pygame.Surface((p,p)))
                Texture.textures[i].blit(Texture.image, (0,0), (((i + 1) * p), 0, p,p))
                #Texture.textures[i].set_colorkey(TRANSPARENT, pygame.RLEACCEL)

class RGBmap:
    """RGBmaps - these define how textures should be blended together
        These can be either 2 or 3 channel, 2-channel use only R and B,
        3-channel use R, G and B. First set is for normal transitions,
        second set is for shoreline transitions, third set is for snow
        overlay transitions (normal transition with "speckled" snow effect"""
    image = None

    def __init__(self):
        if RGBmap.image is None:
            RGBmap.image = pygame.image.load("texture.png")
            RGBmap.image.set_alpha(None)
            RGBmap.image = Texture.image.convert()
            RGBmap.maps = []
            # Now load the individual textures into the textures array
            for i in range(0,4):
                RGBmap.maps.append(pygame.Surface((p,p)))
                RGBmap.maps[i].blit(RGBmap.image, (0,0), ((i * p), (2 * p), p,p))
                #RGBmap.maps[i].set_colorkey(TRANSPARENT, pygame.RLEACCEL)


    
class Lightmap:
    """Lightmap tiles - these define the shape of the ground tiles
        In the single-height system there are three sets, one for each possible
        height difference, 8px, 16px ad 24px, the order of the lightmap tiles
        is important"""
    image = None
    
    def __init__(self):

        if Lightmap.image is None:
            # First, load image with all the tiles in
            Lightmap.image = pygame.image.load("ground.png")
            Lightmap.image.set_alpha(None)
            Lightmap.image = Lightmap.image.convert()
            #Tile.image.set_alpha(128)
            #Tile.image.set_colorkey((231,255,255), pygame.RLEACCEL)
            # Second, prepare the array to hold all the tiles
            Lightmap.lightmap_tiles = []

            for i in range(0,15):
                # Load all the basic ground tiles
                Lightmap.lightmap_tiles.append(pygame.Surface((p,p)))
                Lightmap.lightmap_tiles[i].blit(Lightmap.image, (0,0), ((i * p), p, p,p))
                #Lightmap.lightmap_tiles[i].set_colorkey(TRANSPARENT, pygame.RLEACCEL)

        # As this is just a repository for images, nothing much more needs
        # to be done


class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

    x_dist = 20     # Distance to move the screen when arrow keys are pressed
    y_dist = 20     # in x and y dimensions

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
        Texture()
        RGBmap()
        Lightmap()

        # Merge RGB maps with textures
        self.output = []
        for i in range(4):
            self.output.append(self.MergeRGB((RGBmap.maps[i]), Texture.textures[0], Texture.textures[1]))

        # Merge tile lightmaps with a texture
        self.output2 = []
        for i in range(15):
            self.output2.append(self.TextureTile(Lightmap.lightmap_tiles[i] ,Texture.textures[1]))

##        # Transform RGB maps to tiles
##        self.output3 = []
##        for i in range(15):
##        #self.output3.append(self.MakeTile(RGBmap.maps[1]))
##            bleh = RGBmap.maps[1]
##            self.output3.append(self.TextureTile(Lightmap.lightmap_tiles[i] ,self.MakeTile(bleh, i)))
####            self.output3.append(self.TextureTile(Lightmap.lightmap_tiles[i] ,self.MakeTile(self.MergeRGB((RGBmap.maps[1]), Texture.textures[0], Texture.textures[1]), i)))


        # New system test
        self.output3 = []
        for i in range(15):
            #MakeTile2(self, mode, tile, tileheight, tex1, rgbmap=None, tex2=None, tex3=None, transparency=255)
            self.output3.append(self.MakeTile2(0, i, ph, Texture.textures[1], RGBmap.maps, Texture.textures[0]))

    def MainLoop(self):
        """This is a testing loop to display the output of the rendering tests"""

        """Create the background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        #self.background.set_colorkey((231,255,255))
        #self.background.fill((0,0,0))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                    
            self.background.blit(Texture.textures[0], (0,0))
            self.background.blit(Texture.textures[1], (0,p))
            for i in range(4):
                self.background.blit(RGBmap.maps[i], (p,(p * i)))
                self.background.blit(self.output[i], ((2 * p),(p * i)))
            for i in range(8):
                self.background.blit(self.output2[i], ((3 * p),(p * i)))
            for i in range(7):
                self.background.blit(self.output2[(i + 8)], ((4 * p),(p * i)))
                
            for i in range(8):
                self.background.blit(self.output3[i], ((5 * p),(p * i)))
            for i in range(7):
                self.background.blit(self.output3[(i + 8)], ((6 * p),(p * i)))
            self.screen.blit(self.background, (0, 0))

            pygame.display.flip()

            pygame.time.wait(100)

    def GetMapType(self, tile):
        """Returns the type of RGB map which should be used for this tile
            along with a tuple describing the rotation needed for the
            particular tile type:
            returns: (map_to_use, rotation)"""

        if tile == 0:
            return (1,0)
        # straight rgbmap
        elif tile == 3:
            return (0,0)
        elif tile == 6:
            return (0,90)
        elif tile == 9:
            return (0,270)
        elif tile == 12:
            return (0,180)
        # corner rgbmap
        elif tile == 1:
            return (1,0)
        elif tile == 2:
            return (1,90)
        elif tile == 4:
            return (1,180)
        elif tile == 8:
            return (1,270)
        # inverse corner rgbmap
        elif tile == 7:
            return (2,90)
        elif tile == 11:
            return (2,0)
        elif tile == 13:
            return (2,270)
        elif tile == 14:
            return (2,180)
        # double corner rgbmap (only 2!)
        elif tile == 5:
            return (3,0)
        elif tile == 10:
            return (3,90)
        else:
            return -1
        

    def GetHeights(self, tile):
        """Converts a tile's height bitmap into a tuple of height values,
        currently works with one-height only"""

        if tile == 0:
            return (0,0,0,0)
        elif tile == 1:
            return (1,0,0,0)
        elif tile == 2:
            return (0,1,0,0)
        elif tile == 3:
            return (1,1,0,0)
        elif tile == 4:
            return (0,0,1,0)
        elif tile == 5:
            return (1,0,1,0)
        elif tile == 6:
            return (0,1,1,0)
        elif tile == 7:
            return (1,1,1,0)
        elif tile == 8:
            return (0,0,0,1)
        elif tile == 9:
            return (1,0,0,1)
        elif tile == 10:
            return (0,1,0,1)
        elif tile == 11:
            return (1,1,0,1)
        elif tile == 12:
            return (0,0,1,1)
        elif tile == 13:
            return (1,0,1,1)
        elif tile == 14:
            return (0,1,1,1)
        else:
            return 0

    def MakeTile2(self, mode, tile, tileheight, tex1, rgbmap=None, tex2=None, tex3=None, transparency=255):
        """Combines a lightmap, rgbmap and a number of textures to make a tile
            Required:
                mode        - The operational mode for the funtion:
                    0: - (Default) merges rgbmap with texture, then transforms both
                         to the tile shape
                    1: - Transforms rgbmap first, then maps textures onto it
                tile number - The standard tile number of the tile to be rendered,
                              this is used to work out the transforms required
                tileheight  - The height offset of the tile, either ph, 2ph or 3ph,
                              used to work out the transform
                lightmap    - The tile lightmap used to mask the transformed texture
                              and to apply shading to it
                tex1        - Texture to map onto the tile
            Optional:
                rgbmap      - Allows blending of two textures, should be an array of 4
                              rgbmaps, in order:
                                  straight, corner, inverse corner, double corner
                tex2        - Second texture, will use the BLUE channel of the rgbmap
                tex3        - Third texture, will use the GREEN channel of the rgbmap
                transparency- Optional overall transparency for this tile, if set to 255
                              no transparency will be set for the tile, else the value 
                              supplied will be used"""
        # Firstly, check what's been passed in
        if mode not in [0,1]:
            # No mode supplied, default to 0
            mode = 0
        if tile not in range(0,15):
            # No tile supplied, should throw error here!
            tile = 0    # but for now, just assume tile=0
        if tileheight not in [ph,(2*ph),(3*ph)]:
            # Tileheight is not good, again, error should be thrown here...
            tileheight = ph     # But we will just ignore it and assume default value
        if tex1 == None:
            # Should fail here!
            print "no texture!"
        if rgbmap != None:
            if tex2 == None and tex3 == None:
                # If no second/third texture supplied, then we won't use the rgbmap 
                # even if supplied
                rgbmap = None

        lightmap = Lightmap.lightmap_tiles[tile]

        # Now determine from the tile value what transforms need to be performed
        # First, find out the corner-height map
        h1, h2, h3, h4 = self.GetHeights(tile)

        # If we are using an rgbmap, we must deal with that now
        if rgbmap != None:
            # Next, find the rgbmap type
            maptype, rotation = self.GetMapType(tile)
            rgbmap_touse = rgbmap[maptype]

            # First we need to rotate the rgbmap by the specified amount
            # First transfer image data to PIL format
            rgbmap_pil = Image.fromstring("RGBX", (p,p), pygame.image.tostring(rgbmap_touse, "RGBX"))
            # Then do a rotation transform on it...
            rgbmap_pil = rgbmap_pil.rotate(rotation)
            # Now convert back to pygame format
            rgbmap_touse = pygame.image.frombuffer((rgbmap_pil.tostring()), (p,p), "RGBX")

            # Now, if we are in mode 0 combine the textures with the rgbmap
            if mode == 0:
                if tex3 == None:
                    texmerged = self.MergeRGB(rgbmap_touse, tex1, tex2)
                else:
                    texmerged = self.MergeRGB(rgbmap_touse, tex1, tex2, tex3)
            # Otherwise, simply make the rgbmap be the input for the transform
            else:
                texmerged = rgbmap_touse
        # If we are not using an rgbmap, then...
        else:
            if mode == 0:
                texmerged = tex1
            else:
                # If mode 1 being used with no rgbmap, then nothing needs to be transformed
                # instead we just use the lightmap to mask the texture
                texmerged = None

        # So now we're ready to do the transform...
        if texmerged != None:
            # First transfer image data to PIL format
            trans_im = Image.fromstring("RGBX", (p,p), pygame.image.tostring(texmerged, "RGBX"))
            # Next define the variables we're going to be using as floats
            hh = float(tileheight)
            pp = 64.0
            # These were already found earlier...
            # h1, h2, h3, h4 = self.GetHeights(tile)

            # h values are multiples of the ph value, up to 3 times (for ph value of 8, up to 2 times for ph value of 16)
            h1 = float(h1) * hh
            h2 = float(h2) * hh
            h3 = float(h3) * hh
            h4 = float(h4) * hh

            # First define the variables which represent the "input" image
            # Need to add/subtract one from all these values, to ensure the output
            # image is larger than the lightmap mask
            # Could be corrected by fine-tuning input values so that output
            # tiles are perfect... but that'd be really hard
            xx1 = 0.0 + 1
            xx2 = 0.0 + 1
            xx3 = pp - 1
            xx4 = pp - 1
            
            yy1 = 0.0 + 1
            yy2 = pp - 1
            yy3 = pp - 1
            yy4 = 0.0 + 1

            # Next define the variables which represent the "output" image
            x1 = pp/2.0
            x2 = 0.0
            x3 = pp/2.0
            x4 = pp

            y1 = pp/2.0 - h1
            y2 = (3.0*pp)/4.0 - h2
            y3 = pp - h3
            y4 = (3.0*pp)/4.0 - h4

            # Now, enter all of these variables into the big matrix
            big_matrix = numpy.array([[x1,y1,1,0,0,0,(-xx1*x1),(-xx1*y1)],
                                      [0,0,0,x1,y1,1,(-yy1*x1),(-yy1*y1)],
                                      [x2,y2,1,0,0,0,(-xx2*x2),(-xx2*y2)],
                                      [0,0,0,x2,y2,1,(-yy2*x2),(-yy2*y2)],
                                      [x3,y3,1,0,0,0,(-xx3*x3),(-xx3*y3)],
                                      [0,0,0,x3,y3,1,(-yy3*x3),(-yy3*y3)],
                                      [x4,y4,1,0,0,0,(-xx4*x4),(-xx4*y4)],
                                      [0,0,0,x4,y4,1,(-yy4*x4),(-yy4*y4)],
                                      ])

            # And enter the values into the small matrix...
            small_matrix = numpy.array([[xx1],
                                        [yy1],
                                        [xx2],
                                        [yy2],
                                        [xx3],
                                        [yy3],
                                        [xx4],
                                        [yy4],
                                        ])

            # Now, do a linear solve based on these two arrays, to find the transform matrix
            sol = linalg.solve(big_matrix, small_matrix)

            # Now use that solution to perform the transformation
            trans_im = trans_im.transform((p,p), Image.PERSPECTIVE, (sol[0][0],sol[1][0],sol[2][0],
                                                                     sol[3][0],sol[4][0],sol[5][0],
                                                                     sol[6][0],sol[7][0],1))

            # Debugging info
##            print str(sol[0][0]) + ", " + str(sol[1][0]) + ", " + str(sol[2][0]) + "\n"
##            print str(sol[3][0]) + ", " + str(sol[4][0]) + ", " + str(sol[5][0]) + "\n"
##            print str(sol[6][0]) + ", " + str(sol[7][0])

            # Now convert back to pygame format
            rendered_tile = pygame.image.frombuffer((trans_im.tostring()), (p,p), "RGBX")
        else:
            # If we're using mode 1 without an rgbmap, need to set
            # the tile we'll be masking to just be texture 1...
            rendered_tile = tex1

        # Now we simply need to use the lightmap as a mask for whatever rendered_tile
        # happens to be, and we're done

        # If using mode 0, then pass rendered_tile and the lightmap
        if mode == 0:
            output = self.TextureTile(lightmap, rendered_tile)
        elif mode == 1:
            if tex2 != None:
                if tex3 != None:
                    output = TextureTile(lightmap, tex1, tex2, tex3, rendered_tile)
                else:
                    output = TextureTile(lightmap, tex1, tex2, rgb=rendered_tile)
            else:
                output = TextureTile(lightmap, rendered_tile)


        return output












    def MakeTile(self, rgbmap, tile=0):
        """Deforms a square rgb map image to the shape of a tile,
           tile shape is given by a bitmask representing the heights
           at the corners of a tile, in order top, left, bottom, right"""
        
        # First transfer image data to PIL format
        rgbmap_pil = Image.fromstring("RGBX", (p,p), pygame.image.tostring(rgbmap, "RGBX"))

        # Standard flat tile                                          a,b,c, d,e,f, g,h
##        rgbmap_pil = rgbmap_pil.transform((p,p), Image.PERSPECTIVE, (1, 2, -(3.0*p)/2.0,
##                                                                     -1, 2, -p/2.0,
##                                                                     0,0))
        hh = float(ph)
        pp = 64.0

        h1, h2, h3, h4 = self.GetHeights(tile)

        # h values are multiples of the ph value, up to 3 times (for ph value of 8, up to 2 times for ph value of 16)
        h1 = float(h1) * hh
        h2 = float(h2) * hh
        h3 = float(h3) * hh
        h4 = float(h4) * hh

        # First define the variables which represent the "input" image
        # Need to add/subtract one from all these values, to ensure the output
        # image is larger than the lightmap mask
        # Could be corrected by fine-tuning input values so that output
        # tiles are perfect... but that'd be really hard
        xx1 = 0.0 + 1
        xx2 = 0.0 + 1
        xx3 = pp - 1
        xx4 = pp - 1
        
        yy1 = 0.0 + 1
        yy2 = pp - 1
        yy3 = pp - 1
        yy4 = 0.0 + 1

        # Next define the variables which represent the "output" image
        x1 = pp/2.0
        x2 = 0.0
        x3 = pp/2.0
        x4 = pp

        y1 = pp/2.0 - h1
        y2 = (3.0*pp)/4.0 - h2
        y3 = pp - h3
        y4 = (3.0*pp)/4.0 - h4

        # Now, enter all of these variables into the big matrix
        big_matrix = numpy.array([[x1,y1,1,0,0,0,(-xx1*x1),(-xx1*y1)],
                                  [0,0,0,x1,y1,1,(-yy1*x1),(-yy1*y1)],
                                  [x2,y2,1,0,0,0,(-xx2*x2),(-xx2*y2)],
                                  [0,0,0,x2,y2,1,(-yy2*x2),(-yy2*y2)],
                                  [x3,y3,1,0,0,0,(-xx3*x3),(-xx3*y3)],
                                  [0,0,0,x3,y3,1,(-yy3*x3),(-yy3*y3)],
                                  [x4,y4,1,0,0,0,(-xx4*x4),(-xx4*y4)],
                                  [0,0,0,x4,y4,1,(-yy4*x4),(-yy4*y4)],
                                  ])

        # And enter the values into the small matrix...
        small_matrix = numpy.array([[xx1],
                                    [yy1],
                                    [xx2],
                                    [yy2],
                                    [xx3],
                                    [yy3],
                                    [xx4],
                                    [yy4],
                                    ])

        # Now, do a linear solve based on these two arrays, to find the transform matrix
        sol = linalg.solve(big_matrix, small_matrix)

        # Now use that solution to perform the transformation
        rgbmap_pil = rgbmap_pil.transform((p,p), Image.PERSPECTIVE, (sol[0][0],sol[1][0],sol[2][0],
                                                                     sol[3][0],sol[4][0],sol[5][0],
                                                                     sol[6][0],sol[7][0],1))

        # Debugging info
##        print str(sol[0][0]) + ", " + str(sol[1][0]) + ", " + str(sol[2][0]) + "\n"
##        print str(sol[3][0]) + ", " + str(sol[4][0]) + ", " + str(sol[5][0]) + "\n"
##        print str(sol[6][0]) + ", " + str(sol[7][0])

        # Now convert back to pygame format
        output = pygame.image.frombuffer((rgbmap_pil.tostring()), (p,p), "RGBX")

        # Return the output
        return output

    def MergeRGB(self, map, redtex, bluetex, greentex=None):
        """Merges together two or three textures based on the rgb values of the
           specified RGB mask, if two textures passed then they use red and blue,
           the third texture uses the green"""
        # Lock all the surfaces
        redtex.lock()
        bluetex.lock()
        if greentex != None:
            greentex.lock()
            
        map.lock()
        
        # Create the output surface
        output = pygame.Surface((p,p))
        output.lock()
        
        # Now go through all pixels, compare values and merge them in the output surface

        if greentex == None:
            for x in range(p):
                for y in range(p):
                    rt_r, rt_g, rt_b, rt_a = redtex.get_at((x, y))
                    bt_r, bt_g, bt_b, bt_a = bluetex.get_at((x, y))
                    #
                    red, green, blue, alpha = map.get_at((x, y))
                    # Remove this!
                    if red == 0 and blue == 0:
                        output.set_at((x, y), TRANSPARENT)
                    else:
                        #
                        # Calc % values
                        percent_red = (float(red) / 255.0)
                        percent_blue = (float(blue) / 255.0)
                        # Calc red value
                        red_out = int(((float(rt_r) * percent_red) + (float(bt_r) * percent_blue)) / (percent_red + percent_blue))
                        # Calc green value
                        green_out = int(((float(rt_g) * percent_red) + (float(bt_g) * percent_blue)) / (percent_red + percent_blue))
                        # Calc blue value
                        blue_out = int(((float(rt_b) * percent_red) + (float(bt_b) * percent_blue)) / (percent_red + percent_blue))

                        # Set output surface pixel to this value
                        output.set_at((x, y), (red_out, green_out, blue_out, 255))
                    
        # Finally, unlock all and return output
        redtex.unlock()
        bluetex.unlock()
        if greentex != None:
            greentex.unlock()
        map.unlock()
        output.unlock()
        return output


    def TextureTile(self, lightmap, tex1, tex2=None, tex3=None, rgb=None):
        """Applies a texture to a tile based on a lightmap, rgb mask and up to 3 textures
           If only one texture supplied, just apply that to the lightmap
           If two or three textures supplied, use the optional rgb mask to merge them together
           on the tile"""
            
        # Create the output surface
        output = pygame.Surface((p,p))
        output.lock()
        
        # Lock all the surfaces
        lightmap.lock()
        tex1.lock()
        if tex2 != None:
            tex2.lock()
        if tex3 != None:
            tex3.lock()
        if rgb != None:
            rgb.lock()

        # This function maps pixels on the texture to pixels on the lightmap
        # It assumes that both texture and lightmap are square, and of the same size
        # First, get the pixel values at a point (x,y), then combine those values
        # with the greyscale value of the lightmap for shading, if the rgb value of
        # the lightmap pixel is the transparent colour (231,255,255) then ignore that
        # tile entirely.
        for x in range(p):
            for y in range(p):
                lm_r, lm_g, lm_b, lm_a = lightmap.get_at((x, y))
                if (lm_r, lm_g, lm_b) == TRANSPARENT:
                    # Simply make this pixel the transparent colour
                    red_out, blue_out, green_out = TRANSPARENT
                else:
                    t1_r, t1_g, t1_b, t1_a = tex1.get_at((x, y))
                    lm_percent_red = (float(lm_r - 127) / 127.0)
                    lm_percent_green = (float(lm_g - 127) / 127.0)
                    lm_percent_blue = (float(lm_b - 127) / 127.0)

                    # Calculate the output value
                    red_out = t1_r + int(t1_r * lm_percent_red)
                    green_out = t1_g + int(t1_g * lm_percent_green)
                    blue_out = t1_b + int(t1_b * lm_percent_blue)

                    # Ensure output values are in the correct range
                    if red_out > 255:
                        red_out = 255
                    elif red_out < 0:
                        red_out = 0
                    if green_out > 255:
                        green_out = 255
                    elif green_out < 0:
                        green_out = 0
                    if blue_out > 255:
                        blue_out = 255
                    elif blue_out < 0:
                        blue_out = 0


                # Set output surface pixel to this value
                output.set_at((x, y), (red_out, green_out, blue_out, 255))

        # Finally, unlock all and return output
        tex1.unlock()
        if tex2 != None:
            tex2.unlock()
        if tex3 != None:
            tex3.unlock()
        if rgb != None:
            rgb.unlock()
        lightmap.unlock()
        output.unlock()

        # Set surface transparent colour before returning it
        output.set_colorkey(TRANSPARENT, pygame.RLEACCEL)
        return output

if __name__ == "__main__":

    MainWindow = DisplayMain()
    MainWindow.MainLoop()















