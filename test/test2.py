#!/usr/bin/python
# Test 2 - 2

# Second series test program using a surface to display tiles
# rather than using sprites

# Test 2, Mk.2 - Merge with tile rendering system, renderer
#                in seperate module "Render"
#              - Also repair all ground-affecting functions
#                which rely on tile-type values so that they
#                use the new bitmask tile descriptors
#              - World can now be rectangular
# Test 3, Mk.3 - Test rgb merged grounds

import os, sys
import pygame
import random

import World
import Render

#paksize
p = 64

#tile height difference
ph = 8


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
            # First load the beach texture
            Texture.textures.append(pygame.Surface((p,p)))
            Texture.textures[0].blit(Texture.image, (0,0), ((1 * p), 0, p,p))

            # Now load the grass texture
            Texture.textures.append(pygame.Surface((p,p)))
            Texture.textures[1].blit(Texture.image, (0,0), ((2 * p), 0, p,p))

            # Now load the mountain texture
            Texture.textures.append(pygame.Surface((p,p)))
            Texture.textures[2].blit(Texture.image, (0,0), ((6 * p), 0, p,p))

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

            # Tiles 0-14 are for height 1, 15-29 for height 2, 30-44 for height 3
            # and 45-59 for height 4
            # i.e. (height - 1) * 15 + tilevalue
            for i in range(0,15):
                # Load all the basic ground tiles
                Lightmap.lightmap_tiles.append(pygame.Surface((p,p)))
                Lightmap.lightmap_tiles[i].blit(Lightmap.image, (0,0), ((i * p), p, p,p))
                #Lightmap.lightmap_tiles[i].set_colorkey(TRANSPARENT, pygame.RLEACCEL)
            for i in range(0,15):
                Lightmap.lightmap_tiles.append(pygame.Surface((p,p)))
                Lightmap.lightmap_tiles[(i + 15)].blit(Lightmap.image, (0,0), ((i * p), p * 2, p,p))
            for i in range(0,15):
                Lightmap.lightmap_tiles.append(pygame.Surface((p,p)))
                Lightmap.lightmap_tiles[(i + 30)].blit(Lightmap.image, (0,0), ((i * p), p * 3, p,p))

        # As this is just a repository for images, nothing much more needs
        # to be done


class Highlight(pygame.sprite.Sprite):
    """All types of ground tile"""
    image = None
    
    def __init__(self, rect=None, val=0):

        # All sprite classes should extend pygame.sprite.Sprite. This
        # gives you several important internal methods that you probably
        # don't need or want to write yourself. Even if you do rewrite
        # the internal methods, you should extend Sprite, so things like
        # isinstance(obj, pygame.sprite.Sprite) return true on it.
        pygame.sprite.Sprite.__init__(self)
        if Highlight.image is None:
            bb = pygame.image.load("ground.png")
            Highlight.image = bb.convert()
            #Highlight.image.set_colorkey((231,255,255), pygame.RLEACCEL)
            #Tile.image.convert_alpha()
            Highlight.tile_images = []
            
            Highlight.tile_images.append(pygame.Surface((p,p), pygame.HWSURFACE, Highlight.image))
            Highlight.tile_images[0].blit(Highlight.image, (0,0), ((0 * p), (2 * p), p,p))
            Highlight.tile_images[0] = Highlight.tile_images[0].convert()
            Highlight.tile_images[0].set_colorkey((231,255,255), pygame.RLEACCEL)
            Highlight.tile_images[0].set_alpha(130)
        # Pre-load this sprite's image, so that it is only loaded once
        self.image = Highlight.tile_images[val]
        self.image.set_colorkey((231,255,255), pygame.RLEACCEL)
        self.rect = self.image.get_rect()
        
        if rect != None:
            self.rect = rect

            
class Cliff:
    """All types of ground cliff"""
    image = None
    
    def __init__(self):
        if Cliff.image is None:
            # First, load image with all the tiles in
            Cliff.image = pygame.image.load("ground.png")
            Cliff.image.set_alpha(None)
            Cliff.image = Cliff.image.convert()
            #Cliff.image.set_alpha(128)
            #Cliff.image.set_colorkey((231,255,255), pygame.RLEACCEL)
            # Second, prepare the array to hold all the tiles
            
            Cliff.cliff_images = []
            # Now load the cliff components,
            # First set face east
            for i in range(0,5):
                Cliff.cliff_images.append(pygame.Surface((p,p)))
                Cliff.cliff_images[i].blit(Cliff.image, (0,0), ((i * p), (10 * p), p,p))
                Cliff.cliff_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)

            i = 0
            # Now load the south-facing set
            for i in range(0,5):
                Cliff.cliff_images.append(pygame.Surface((p,p)))
                Cliff.cliff_images[(i+5)].blit(Cliff.image, (0,0), ((i * p), (11 * p), p,p))
                Cliff.cliff_images[(i+5)].set_colorkey((231,255,255), pygame.RLEACCEL)

            Cliff.water_images = []
            # Now load the cliff components,
            # First set face east
            for i in range(0,5):
                Cliff.water_images.append(pygame.Surface((p,p)))
                Cliff.water_images[i].blit(Cliff.image, (0,0), ((i * p), (12 * p), p,p))
                Cliff.water_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)
                Cliff.water_images[i].set_alpha(200)

            i = 0
            # Now load the south-facing set
            for i in range(0,5):
                Cliff.water_images.append(pygame.Surface((p,p)))
                Cliff.water_images[(i+5)].blit(Cliff.image, (0,0), ((i * p), (13 * p), p,p))
                Cliff.water_images[(i+5)].set_colorkey((231,255,255), pygame.RLEACCEL)
                Cliff.water_images[(i+5)].set_alpha(200)



class Tile:
    """All ground tiles, includes:
        - Ground tiles and slopes
        - Water tiles (with alpha set)
        - Mountains (eventually)
        - Marker tiles and other misc stuff"""
    image = None
    
    def __init__(self):

        if Tile.image is None:
            # First, load image with all the tiles in
            Tile.image = pygame.image.load("ground.png")
            Tile.image.set_alpha(None)
            Tile.image = Tile.image.convert()
            #Tile.image.set_alpha(128)
            #Tile.image.set_colorkey((231,255,255), pygame.RLEACCEL)
            # Second, prepare the arrays to hold all the tiles
            Tile.tile_images = []
            Tile.water = []
            
            # First load the water tile(s)
            Tile.water.append(pygame.Surface((p,p)))
            Tile.water[0].set_alpha(130)
            Tile.water[0].blit(Tile.image, (0,0), ((0 * p), (6 * p), p,p))
            Tile.water[0].set_colorkey((231,255,255), pygame.RLEACCEL)

            # 0-15 = beach, 15-30 = beach/grass, 30-45 = grass, 45-60 = grass/mountain, 60-75 = mountain

            # beach
            # Load the standard ground tiles first
            for i in range(0,15):
                #Tile.tile_images.append(pygame.Surface((p,p)))
                Tile.tile_images.append(render.MakeTile2(0, i, 1, Texture.textures[0], Lightmap.lightmap_tiles))

            # beach/grass
            # Next, make some which transition between two textures
            for i in range(0,15):
                #Tile.tile_images.append(pygame.Surface((p,p)))
                Tile.tile_images.append(render.MakeTile2(0, i, 1, Texture.textures[1], Lightmap.lightmap_tiles, RGBmap.maps, Texture.textures[0]))

            # grass
            # Load the standard ground tiles first
            for i in range(0,15):
                #Tile.tile_images.append(pygame.Surface((p,p)))
                Tile.tile_images.append(render.MakeTile2(0, i, 1, Texture.textures[1], Lightmap.lightmap_tiles))
                
            # grass/mountain
            # Next, make some which transition between two textures
            for i in range(0,15):
                #Tile.tile_images.append(pygame.Surface((p,p)))
                Tile.tile_images.append(render.MakeTile2(0, i, 1, Texture.textures[2], Lightmap.lightmap_tiles, RGBmap.maps, Texture.textures[1]))

            # mountain
            # Now make some beach tiles
            for i in range(0,15):
                #Tile.tile_images.append(pygame.Surface((p,p)))
                Tile.tile_images.append(render.MakeTile2(0, i, 1, Texture.textures[2], Lightmap.lightmap_tiles))

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
        
        # Init classes
        Texture()
        RGBmap()
        Lightmap()
        # Initialise the tile object (load tile images)
        Tile()
        Cliff()

        self.array = world.MakeArray()   # array of tiles, make or load
        self.WorldX = len(self.array)      #lazy method, needs change
        self.WorldY = len(self.array[0])
        self.WidthX = (self.WorldX + self.WorldY) * (p/2)
        self.HeightY = ((self.WorldX + self.WorldY) * (p/4)) + (p/2)
        
        self.dxoff = 0
        self.dyoff = 0

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        """Load All of our Sprites"""
        # LoadSprites will load actual sprites
        # PaintLand will take care of the ground underneath,
        # which is painted using a surfaces
        self.LoadSprites()
        
        # Create the land surface, onto which the terrain is drawn
        self.landsurface = pygame.Surface(self.screen.get_size())
        self.landsurface = self.landsurface.convert()
        #self.landsurface.set_colorkey((231,255,255))

        # Draw the terrain the first time
        self.PaintLand()

        # Initiate the clock
        self.gameclock = pygame.time.Clock()
        
        """tell pygame to keep sending up keystrokes when they are
        held down"""
        pygame.key.set_repeat(500, 30)
        
        """Create the background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        #self.background.set_colorkey((231,255,255))
        #self.background.fill((0,0,0))
        
        #Must ensure mouse is over screen (needs fixing properly)
        pygame.mouse.set_pos(((self.background.get_width()/2),(self.background.get_height()/2)))

        self.tool = ""

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if ((event.key == pygame.K_RIGHT)
                    or (event.key == pygame.K_LEFT)
                    or (event.key == pygame.K_UP)
                    or (event.key == pygame.K_DOWN)):
                        self.MoveScreen(event.key)
                    else:
##                        b = event.unicode
##                        if pygame.font:
##                            font = pygame.font.Font(None, 24)
##                            self.textitems.append(font.render("Key pressed: " + str(b), 1, (255, 255, 255)))
                        
                        # Need some sort of tool selection system implemented here...
                        self.tool = event.unicode
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If LMB pressed...
                    if (event.button == 1):
                        self.ModifyHeight()


                elif event.type == pygame.MOUSEMOTION:
                    # When the mouse is moved, check to see if...
                    b = event.buttons
                    
##                    if pygame.font:
##                        font = pygame.font.Font(None, 24)
##                        self.textitems.append(font.render("Mouse State: " + str(b), 1, (255, 255, 255)))
                        
                    #pygame.event.event_name()
                        # Is the right mouse button held? If so, do scrolling & refresh whole screen
                    if (event.buttons == (0,0,1)):
                        self.MoveScreen("mouse")
                        # If neither mouse button held, then simply
                        # check which tile is active, and highlight it
                    else:
                        pygame.mouse.get_rel()  #Reset mouse position for scrolling
                        self.HighlightTile()
                        
            self.dirty = []
            
            # Get areas of the screen which have been changed/updated
            self.highlight.clear(self.screen, self.landsurface)

            bb = self.highlight.draw(self.screen)
            for i in range(len(bb)):
                self.dirty.append(bb.pop(0))

            # If land height has been altered, or the screen has been moved
            # we need to refresh the entire screen

            if self.refresh_screen == 1:
                self.screen.blit(self.landsurface, (0, 0))
                self.refresh_screen = 0
                
            pygame.display.update(self.dirty)

            pygame.display.flip()

            pygame.time.wait(100)

    def PaintSprites(self):
        """Adds sprites to sprite groups as needed"""

    def PaintLand(self):
        """Paint the land tiles on the screen - 
            This function has been changed now, the
            land is no longer made up of sprites, but
            from images painted to a surface. This surface
            is called "landsurface", it is the same size
            as the screen and is blitted onto the screen
            and used as a background for sprite repainting"""

        self.refresh_screen = 1
        
        self.landsurface.fill((0, 0, 100))
        #self.landsurface.set_colorkey((231,255,255), pygame.RLEACCEL)
        

        # Check to find the lowest point on the map
        self.lowpoint = 0
        for y in range(self.WorldY):
            for x in range(self.WorldX):
                if self.lowpoint > self.array[x][y][0]:
                    self.lowpoint = self.array[x][y][0]


        # This will be changed to be only tiles within the subset visible on screen
        for y in range(self.WorldY):
            for x in range(self.WorldX):
                xpos = (self.WidthX / 2) + (x * (p/2)) - (y * (p/2)) - (p/2) + self.dxoff
                ypos = (x * (p/4)) + (y * (p/4)) - (self.array[x][y][0] * ph) + self.dyoff
                
                # Draw the right tile image for this tile, check its height to find what
                # rendered texture needs to be used
                # 0-15 = beach, 15-30 = beach/grass, 30-45 = grass, 45-60 = grass/mountain, 60-75 = mountain
                # lvl<0 = beach, lvl=0 = beach/grass, lvl>0&lvl<3 = grass, lvl=3 = grass/mountain, lvl>3 = mountain
                if self.array[x][y][0] < 0:
                    im = Tile.tile_images[self.array[x][y][1]]
                elif self.array[x][y][0] == 0:
                    im = Tile.tile_images[self.array[x][y][1] + 15]
                elif self.array[x][y][0] > 0 and self.array[x][y][0] < 3:
                    im = Tile.tile_images[self.array[x][y][1] + 30]
                elif self.array[x][y][0] == 3:
                    im = Tile.tile_images[self.array[x][y][1] + 45]
                elif self.array[x][y][0] > 3:
                    im = Tile.tile_images[self.array[x][y][1] + 60]


                self.landsurface.blit(im, (xpos, ypos))



                # Take care of the cliffs around the edge of the map,
                # these extend for 8 layers below the lowest point on the map,
                # will eventually be nicely textured and such
                
                # Find the number of layers below sea level by adding 8 to the lowest point of the map
                levels = (0 - self.lowpoint) + 8
                
                # Deals with the right hand side
                if x == (self.WorldX - 1):
                    startlevel = (0 - self.array[x][y][0]) + 1
                    
                    for z in range(startlevel,(levels + 1)):
                        k = 0
                        # If this is a sloped tile...
##                        if self.array[x][y][1] in [0,4,8,11]:
                        if self.array[x][y][1] in [9,8,11,10]:
                            im = Cliff.cliff_images[3]
                            zz = z
                            # If this is the bottom image, also draw the bottom bit
                            if z == levels:
                                im2 = Cliff.cliff_images[1]
                                k = 1
                                zzz = z
                                
                        # If this is a sloped tile...
##                        elif self.array[x][y][1] in [2,7,10,13]:
                        elif self.array[x][y][1] in [6,4,7,5]:
                            im = Cliff.cliff_images[2]
                            zz = z
                            # If this is the bottom image, also draw the bottom bit
                            if z == levels:
                                im2 = Cliff.cliff_images[0]
                                k = 1
                                zzz = z
                            
                        # If this is a flat tile...
                        else:
                            im = Cliff.cliff_images[4]
                            zz = z
                        self.landsurface.blit(im, (xpos, ypos + (ph * (zz + self.array[x][y][0]))))
                        if k == 1:
                            self.landsurface.blit(im2, (xpos, ypos + (ph * (zzz + self.array[x][y][0]))))

                if y == (self.WorldY - 1):
                    startlevel = (0 - self.array[x][y][0]) + 1
                    # Deals with left hand side
                    for z in range(startlevel,(levels + 1)):
                        k = 0
                        # If this is a sloped tile...
##                        if self.array[x][y][1] in [1,6,8,11]:
                        if self.array[x][y][1] in [3,2,11,10]:
                            im = Cliff.cliff_images[7]
                            zz = z
                            # If this is the bottom image, also draw the bottom bit
                            if z == levels:
                                im2 = Cliff.cliff_images[5]
                                k = 1
                                zzz = z
##                        elif self.array[x][y][1] in [3,7,9,13]:
                        elif self.array[x][y][1] in [12,4,13,5]:
                            im = Cliff.cliff_images[8]
                            zz = z
                            # If this is the bottom image, also draw the bottom bit
                            if z == levels:
                                im2 = Cliff.cliff_images[6]
                                k = 1
                                zzz = z
                        # If this is a flat tile...
                        else:
                            im = Cliff.cliff_images[9]
                            zz = z
                        self.landsurface.blit(im, (xpos, ypos + (ph * (zz + self.array[x][y][0]))))
                        if k == 1:
                            self.landsurface.blit(im2, (xpos, ypos + (ph * (zzz + self.array[x][y][0]))))
                            

                # If a tile is below sea level (less than 0 in height) then draw water over it
                if self.array[x][y][0] < world.SEA_LEVEL:
                    im = Tile.water[0]
                    self.landsurface.blit(im, (xpos, ypos + (ph * self.array[x][y][0])))
                    
                    # Then if it's at the edge of the map, draw also the water "cliff" effect
                    # This deals with the right hand side
                    if x == (self.WorldX - 1):
                        # Start level will always be sealevel + 1
                        startlevel = world.SEA_LEVEL + 1
                        levels = (0 - self.array[x][y][0])
                        
                        for z in range(startlevel,(levels + 1)):
                            # If this is a sloped tile...
                            if self.array[x][y][1] in [9,8,11,10]:
                                # If this is the top image, just draw the top part
                                if z == startlevel:
                                    im = Cliff.water_images[1]
                                    zz = z
                                else:
                                    im = Cliff.water_images[3]
                                    zz = z
                                    
                            # If this is a sloped tile...
                            elif self.array[x][y][1] in [6,4,7,5]:
                                # If this is the top image, just draw the top part
                                if z == startlevel:
                                    im = Cliff.water_images[0]
                                    zz = z
                                else:
                                    im = Cliff.water_images[2]
                                    zz = z
                                
                            # If this is a flat tile...
                            else:
                                im = Cliff.water_images[4]
                                zz = z
                                
                            self.landsurface.blit(im, (xpos, ypos + (ph * (zz + self.array[x][y][0]))))
                            
                    # This deals with the left hand side
                    if y == (self.WorldY - 1):
                        # Start level will always be sealevel + 1
                        startlevel = world.SEA_LEVEL + 1
                        levels = (0 - self.array[x][y][0])
                        
                        for z in range(startlevel,(levels + 1)):
                            # If this is a sloped tile...
                            if self.array[x][y][1] in [3,2,11,10]:
                                # If this is the top image, just draw the top part
                                if z == startlevel:
                                    im = Cliff.water_images[5]
                                    zz = z
                                else:
                                    im = Cliff.water_images[7]
                                    zz = z
                                    
                            # If this is a sloped tile...
                            elif self.array[x][y][1] in [12,4,13,5]:
                                # If this is the top image, just draw the top part
                                if z == startlevel:
                                    im = Cliff.water_images[6]
                                    zz = z
                                else:
                                    im = Cliff.water_images[8]
                                    zz = z
                                
                            # If this is a flat tile...
                            else:
                                im = Cliff.water_images[9]
                                zz = z
                                
                            self.landsurface.blit(im, (xpos, ypos + (ph * (zz + self.array[x][y][0]))))







    def LoadSprites(self):
        """Load the sprites that we need"""
        self.highlight = pygame.sprite.RenderUpdates()
        self.tool = pygame.sprite.RenderUpdates()

    def ModifyHeight(self):
        """Raises or lowers the height of a tile"""
        # Raise height of a single tile
        isopos = self.ScreenToIso(pygame.mouse.get_pos())
        x, y = isopos
        #self.array[x][y][0] = self.array[x][y][0] + 1

        if self.tool == "u":
            world.RaiseTile(self.array, x, y)
        elif self.tool == "d":
            world.LowerTile(self.array, x, y)

        self.PaintLand()

    def HighlightTile(self, iso_coords=(0,0)):
        """Highlight a particular tile, takes one argument:
        iso_coords - coords of tile to highlight"""
        isopos = self.ScreenToIso(pygame.mouse.get_pos())
        x, y = isopos
        self.highlight.empty()
        #tohighlight = self.TileSiblings(isopos)

        xpos = (self.WidthX / 2) + (x * (p/2)) - (y * (p/2)) - (p/2) + self.dxoff
        ypos = (x * (p/4)) + (y * (p/4)) - (self.array[x][y][0] * ph) + self.dyoff
        self.highlight.add(Highlight(pygame.Rect(xpos, ypos, p, p), 0))

    def ScreenToIso(self, wxy=(0,0)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        TileRatio = 2
        wx, wy = wxy

        #wx = wx# + self.dxoff
        #wy = wy# + self.dyoff
        #dx = wx - p + self.dxoff
        #dy = wy + (p/2) + self.dyoff
        dx = wx - (self.WidthX/2) - self.dxoff
        dy = wy - (p/2) - self.dyoff
        # Don't really understand how this bit works...
        x = int((dy + dx / TileRatio) * (TileRatio / 2) / (p/2))
        y = int((dy - dx / TileRatio) * (TileRatio / 2) / (p/2))
        if x < 0 or y < 0:
            return (0,0)
        if x >= (self.WorldX) or y >= (self.WorldY):
            return (0,0)
        
        return (x,y)

    def MoveScreen(self, key):
        """Moves the screen"""
        if (key == pygame.K_RIGHT):
            self.dxoff = self.dxoff - self.x_dist
        elif (key == pygame.K_LEFT):
            self.dxoff = self.dxoff + self.x_dist
        elif (key == pygame.K_UP):
            self.dyoff = self.dyoff + self.y_dist
        elif (key == pygame.K_DOWN):
            self.dyoff = self.dyoff - self.y_dist
        if (key == "mouse"):
            b = pygame.mouse.get_rel()
            self.dxoff = self.dxoff + b[0]
            self.dyoff = self.dyoff + b[1]
            
        #pygame.mouse.set_pos(((self.background.get_width()/2),(self.background.get_height()/2)))
        #pygame.mouse.get_rel()
        
        self.PaintLand()
        #self.HighlightTile()


if __name__ == "__main__":
    world = World.World()
    render = Render.Render()
    
    MainWindow = DisplayMain()
    MainWindow.MainLoop()








    
