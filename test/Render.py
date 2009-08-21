#!/usr/bin/python
# Render.py - Tile rendering module

# V.0.1.5 - Split from render-test1-5

# Development of the rendered grounds system
# Test 1, Mk.2 - merging textures
# Test 1, Mk.3 - PIL tranforms to map rgb maps onto tiles
# Test 1, Mk.4 - Using perspective transforms now
# Test 1, Mk.5 - Tweaking transforms, and extending the system to different height tiles

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

class Render:
    """All functions related to tile rendering"""
    #paksize
    p = 64

    #tile height difference
    ph = 8

    # Value of transparent
    TRANSPARENT = (231,255,255)
    def __init__(self):
        self.p = 64
        self.transform_values = []

        # The input values for the perspective transform are stored in the
        # transform_values array, so they don't have to be computed each time
        
        for tileheight in range(3):
            a = []
            for tile in range(15):
                # First, find out the corner-height map
                h1, h2, h3, h4 = self.GetHeights(tile)
                
                # Next define the variables we're going to be using as floats
                hh = float(tileheight + 1) * ph
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
                a.append(sol)
            self.transform_values.append(a)

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



    def MakeTile2(self, mode, tile, tileheight, tex1, lmap, rgbmap=None, tex2=None, tex3=None, transparency=255):
        """Combines a lightmap, rgbmap and a number of textures to make a tile
            Required:
                mode        - The operational mode for the funtion:
                    0: - (Default) merges rgbmap with texture, then transforms both
                         to the tile shape
                    1: - Transforms rgbmap first, then maps textures onto it
                tile number - The standard tile number of the tile to be rendered,
                              this is used to work out the transforms required
                tileheight  - The height offset of the tile, multiple of ph between 1 and 4
                              used to work out the transform
                lightmap    - The tile lightmap used to mask the transformed texture
                              and to apply shading to it
                tex1        - Texture to map onto the tile
                lmap    - array of all defined lightmaps
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
        if tileheight not in [0,1,2,3]:
            # Tileheight is not good, again, error should be thrown here...
            tileheight = 0     # But we will just ignore it and assume default value
        if tex1 == None:
            # Should fail here!
            print "no texture!"
        if rgbmap != None:
            if tex2 == None and tex3 == None:
                # If no second/third texture supplied, then we won't use the rgbmap 
                # even if supplied
                rgbmap = None

        lightmap = lmap[tile + (tileheight * 15)]

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

            # Lookup the transformation matrix in the transformation matrix array
            sol = self.transform_values[tileheight][tile]

            # Now use that solution to perform the transformation
            trans_im = trans_im.transform((p,p), Image.PERSPECTIVE, (sol[0][0],sol[1][0],sol[2][0],
                                                                     sol[3][0],sol[4][0],sol[5][0],
                                                                     sol[6][0],sol[7][0],1))

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
                    output = self.TextureTile(lightmap, tex1, tex2, tex3, rendered_tile)
                else:
                    output = self.TextureTile(lightmap, tex1, tex2, rgb=rendered_tile)
            else:
                output = self.TextureTile(lightmap, rendered_tile)


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

