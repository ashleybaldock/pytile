#!/usr/bin/python
# Development of the rendered grounds system
# Test 1, Mk.2 - merging textures
# Test 1, Mk.3 - PIL tranforms to map rgb maps onto tiles

import os, sys
import pygame
import random
import Image

#paksize
p = 64

#tile height difference
ph = 8

# Value of transparent
TRANSPARENT = (231,255,255)

class Texture:
    """Texture surfaces:
        these are the textures we will apply to the lightmap tiles
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
    """Blending RGB images, to blend together two textures"""
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
    """Lightmap tiles"""
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

        self.output = []
        for i in range(4):
            self.output.append(self.MergeRGB((self.RGBtoTile(RGBmap.maps[i])), Texture.textures[0], Texture.textures[1]))

        self.output2 = []
        for i in range(15):
            self.output2.append(self.TextureTile(Lightmap.lightmap_tiles[i] ,Texture.textures[1]))

        self.output3 = []
        self.output3.append(self.RGBtoTile(RGBmap.maps[1]))

    def MainLoop(self):
        """This is the Main Loop of the Game"""

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
                
            self.background.blit(self.output3[0], ((5 * p),(p * i)))
            
            self.screen.blit(self.background, (0, 0))

            pygame.display.flip()

            pygame.time.wait(100)

    def RGBtoTile(self, rgbmap, tile=0):
        """Deforms a square rgb map image to the shape of a tile,
           tile shape is given by a bitmask representing the heights
           at the corners of a tile, in order top, right, bottom, left"""
        
        # First transfer image data to PIL format
        rgbmap_pil = Image.fromstring("RGBX", (p,p), pygame.image.tostring(rgbmap, "RGBX"))


        root2 = 1.4142135623730950488016887242097
        

        
        # Now use transform to fuck around with it
##        rgbmap_changed = rgbmap_pil.transform((p,p), Image.AFFINE, ((root2), (1/-root2), ((p/2) - (p/root2)), 1/root2, root2, -p))
##        rgbmap_changed = rgbmap_pil.transform((p,p), Image.AFFINE, (root2, (1/-root2), ((p/2) - (p/root2)), 1/(2 * root2), 2 * root2, -p/4))
##        rgbmap_changed = rgbmap_pil.transform((p,p), Image.AFFINE, ((1/root2), (-1/root2), p/2 - p/root2, 1/root2, 1/root2, -p/2))


        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.QUAD, (0,0, 0,p, p + p/4,p, p,0))


        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.QUAD, (-p/4,0, 0,p, p,p, p,-p/4))

                                                                    #a,b,c, d,e,f, g,h
        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.PERSPECTIVE, (11.0/36.0, 7.0/36.0, 0, -1.0/3.0,1.0/4.0,p/3.0, -1.0/(12*p),-5.0/(12.0*p)))
##        rgbmap_pil = rgbmap_pil.transform((p,p), Image.PERSPECTIVE, (168.0/61.0, -84.0/61.0, 28.0*p/61.0,
##                                                                     132.0/61.0, 132.0/61.0, -44.0*p/61.0,
##                                                                     69.0/(61*p),48.0/(61.0*p)))

        rgbmap_pil = rgbmap_pil.transform((p,p), Image.PERSPECTIVE, (1, 2, -(3.0*p)/2.0,
                                                                     -1, 2, -p/2.0,
                                                                     0,0))

        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.AFFINE, (1, -2, 3.0/2*p, 1, 2, -3.0/2*p))
        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.AFFINE, (1/root2, -1/root2, p/2 + p/(2*root2), 1/root2, 1/root2, p/2 + p/(2*root2)))


        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.AFFINE, (1/root2,-1/root2,0, 1/root2,1/root2,0))

        #rgbmap_pil = rgbmap_pil.transform((p,p), Image.AFFINE, (1, 0, 0, 0, 1, -p/root2))

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















