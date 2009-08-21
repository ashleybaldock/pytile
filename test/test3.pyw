#!/usr/bin/python
# Test 3 - 3
# Tidy up older examples, change structure of map

# Second series test program using a surface to display tiles
# rather than using sprites

import os, sys
import pygame
import random

import World3 as World

#paksize
p = 64
p2 = p / 2
p4 = p / 4
p8 = p / 8
p16 = p / 16

#tile height difference
ph = 8

class MouseSprite(pygame.sprite.Sprite):
    """Small invisible sprite to use for mouse/sprite collision testing"""
    image = None
    mask = None
    def __init__(self, (mouseX, mouseY)):
        pygame.sprite.Sprite.__init__(self)
        if MouseSprite.image is None:
            MouseSprite.image = pygame.Surface((1,1))
            MouseSprite.image.fill((0,0,0))
            MouseSprite.image.convert()
            MouseSprite.image.set_colorkey((0,0,0), pygame.RLEACCEL)
        if MouseSprite.mask is None:
            s = pygame.Surface((1,1))
            s.fill((1,1,1))
            MouseSprite.mask = pygame.mask.from_surface(s, 0)
        self.mask = MouseSprite.mask
        self.image = MouseSprite.image
        self.rect = pygame.Rect(mouseX, mouseY, 1,1)

# 0 = Nothing
# 1 = Left vertex
# 2 = Bottom vertex
# 3 = Right vertex
# 4 = Top vertex
# 5 = Bottom-left edge
# 6 = Bottom-right edge
# 7 = Top-right edge
# 8 = Top-left edge
# 9 = Face
type0 = [[0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,4,4,0,0,0],
         [0,0,8,4,4,7,0,0],
         [0,8,8,8,7,7,7,0],
         [1,1,8,9,9,7,3,3],
         [1,1,5,9,9,6,3,3],
         [0,5,5,5,6,6,6,0],
         [0,0,5,2,2,6,0,0],
         [0,0,0,2,2,0,0,0],]

class HighlightSprite(pygame.sprite.Sprite):
    """Sprites for displaying ground selection highlight"""
    image = None
    col_exclude = True
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        if HighlightSprite.image is None:
            groundImage = pygame.image.load("ground3.png")
            HighlightSprite.image = groundImage.convert()
            # Tile images will be composited using rendering later, for now just read them in
            HighlightSprite.tile_images = {}

            # Each tile's highlight image composited from 1-4 edge images
            # Set for bottom-left edge
            HighlightSprite.tile_images["00XX"] = HighlightSprite.image.subsurface((0*p,4*p,p,p))
            HighlightSprite.tile_images["01XX"] = HighlightSprite.image.subsurface((1*p,4*p,p,p))
            HighlightSprite.tile_images["10XX"] = HighlightSprite.image.subsurface((2*p,4*p,p,p))
            HighlightSprite.tile_images["11XX"] = HighlightSprite.image.subsurface((3*p,4*p,p,p))
            HighlightSprite.tile_images["12XX"] = HighlightSprite.image.subsurface((4*p,4*p,p,p))
            HighlightSprite.tile_images["21XX"] = HighlightSprite.image.subsurface((5*p,4*p,p,p))
            HighlightSprite.tile_images["22XX"] = HighlightSprite.image.subsurface((6*p,4*p,p,p))
            # Set for bottom-right edge
            HighlightSprite.tile_images["X00X"] = HighlightSprite.image.subsurface((0*p,5*p,p,p))
            HighlightSprite.tile_images["X01X"] = HighlightSprite.image.subsurface((1*p,5*p,p,p))
            HighlightSprite.tile_images["X10X"] = HighlightSprite.image.subsurface((2*p,5*p,p,p))
            HighlightSprite.tile_images["X11X"] = HighlightSprite.image.subsurface((3*p,5*p,p,p))
            HighlightSprite.tile_images["X12X"] = HighlightSprite.image.subsurface((4*p,5*p,p,p))
            HighlightSprite.tile_images["X21X"] = HighlightSprite.image.subsurface((5*p,5*p,p,p))
            HighlightSprite.tile_images["X22X"] = HighlightSprite.image.subsurface((6*p,5*p,p,p))
            # Set for top-right edge
            HighlightSprite.tile_images["XX00"] = HighlightSprite.image.subsurface((0*p,6*p,p,p))
            HighlightSprite.tile_images["XX01"] = HighlightSprite.image.subsurface((1*p,6*p,p,p))
            HighlightSprite.tile_images["XX10"] = HighlightSprite.image.subsurface((2*p,6*p,p,p))
            HighlightSprite.tile_images["XX11"] = HighlightSprite.image.subsurface((3*p,6*p,p,p))
            HighlightSprite.tile_images["XX12"] = HighlightSprite.image.subsurface((4*p,6*p,p,p))
            HighlightSprite.tile_images["XX21"] = HighlightSprite.image.subsurface((5*p,6*p,p,p))
            HighlightSprite.tile_images["XX22"] = HighlightSprite.image.subsurface((6*p,6*p,p,p))
            # Set for top-left edge
            HighlightSprite.tile_images["0XX0"] = HighlightSprite.image.subsurface((0*p,7*p,p,p))
            HighlightSprite.tile_images["1XX0"] = HighlightSprite.image.subsurface((1*p,7*p,p,p))
            HighlightSprite.tile_images["0XX1"] = HighlightSprite.image.subsurface((2*p,7*p,p,p))
            HighlightSprite.tile_images["1XX1"] = HighlightSprite.image.subsurface((3*p,7*p,p,p))
            HighlightSprite.tile_images["2XX1"] = HighlightSprite.image.subsurface((4*p,7*p,p,p))
            HighlightSprite.tile_images["1XX2"] = HighlightSprite.image.subsurface((5*p,7*p,p,p))
            HighlightSprite.tile_images["2XX2"] = HighlightSprite.image.subsurface((6*p,7*p,p,p))

            # Nothing
            HighlightSprite.tile_images["None"] = HighlightSprite.image.subsurface((0,3*p,p,p))
            HighlightSprite.tile_images["0"] = HighlightSprite.image.subsurface((0,3*p,p,p))
            # Vertices
            HighlightSprite.tile_images["1"] = HighlightSprite.image.subsurface((1*p,3*p,p,p))
            HighlightSprite.tile_images["2"] = HighlightSprite.image.subsurface((2*p,3*p,p,p))
            HighlightSprite.tile_images["3"] = HighlightSprite.image.subsurface((3*p,3*p,p,p))
            HighlightSprite.tile_images["4"] = HighlightSprite.image.subsurface((4*p,3*p,p,p))
            # Edges
            HighlightSprite.tile_images["5"] = HighlightSprite.image.subsurface((5*p,3*p,p,p))
            HighlightSprite.tile_images["6"] = HighlightSprite.image.subsurface((6*p,3*p,p,p))
            HighlightSprite.tile_images["7"] = HighlightSprite.image.subsurface((7*p,3*p,p,p))
            HighlightSprite.tile_images["8"] = HighlightSprite.image.subsurface((8*p,3*p,p,p))
            # Whole tile
            HighlightSprite.tile_images["9"] = HighlightSprite.image.subsurface((9*p,3*p,p,p))
            for i in HighlightSprite.tile_images:
                HighlightSprite.tile_images[i].convert()
                HighlightSprite.tile_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)
        self.image = pygame.Surface((p,p))
        self.image.set_colorkey((0,0,0))
    def changepos(self, type, tiletype, xpos, ypos, xoff, yoff, xWorld, yWorld):
        """Set highlight to appear on a different tile"""
        self.image.fill((0,0,0))
        if type == 0:
            # Empty Image
            pass
        # Corner bits, made up of two images
        elif type == 1:
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
        elif type == 2:
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
        elif type == 3:
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
        elif type == 4:
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        # Edge bits, made up of one image
        elif type == 5:
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
        elif type == 6:
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
        elif type == 7:
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
        elif type == 8:
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        else:
            # Otherwise highlight whole tile (4 images)
            self.image.fill((0,0,0))
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0))
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (0,0))
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (0,0))
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0))
        self.xpos = xpos
        self.ypos = ypos
        self.rect = (self.xpos + xoff, self.ypos + yoff, p, p)
        self.type = type
        self.xWorld = xWorld
        self.yWorld = yWorld
        self.layer = xWorld + yWorld
    def update(self, xoff, yoff):
        """Update position of sprite with new offsets"""
        self.rect = (self.xpos + xoff, self.ypos + yoff, p, p)

class TileSprite(pygame.sprite.Sprite):
    """Ground tiles"""
    image = None
    col_exclude = False
    def __init__(self, val, xpos, ypos, xoff, yoff, xWorld, yWorld):
        pygame.sprite.Sprite.__init__(self)
        if TileSprite.image is None:
            groundImage = pygame.image.load("ground3.png")
            TileSprite.image = groundImage.convert()
            # Tile images will be composited using rendering later, for now just read them in
            TileSprite.tile_images = {}
            # Flat tile
            TileSprite.tile_images["0000"] = TileSprite.image.subsurface((0,0,p,p))
            # Corner tile (up)
            TileSprite.tile_images["1000"] = TileSprite.image.subsurface((p*1,0,p,p))
            TileSprite.tile_images["0100"] = TileSprite.image.subsurface((p*2,0,p,p))
            TileSprite.tile_images["0010"] = TileSprite.image.subsurface((p*3,0,p,p))
            TileSprite.tile_images["0001"] = TileSprite.image.subsurface((p*4,0,p,p))
            # Slope tile
            TileSprite.tile_images["1001"] = TileSprite.image.subsurface((p*5,0,p,p))
            TileSprite.tile_images["1100"] = TileSprite.image.subsurface((p*6,0,p,p))
            TileSprite.tile_images["0110"] = TileSprite.image.subsurface((p*7,0,p,p))
            TileSprite.tile_images["0011"] = TileSprite.image.subsurface((p*8,0,p,p))
            # Corner tile (down)
            TileSprite.tile_images["1101"] = TileSprite.image.subsurface((p*9,0,p,p))
            TileSprite.tile_images["1110"] = TileSprite.image.subsurface((p*10,0,p,p))
            TileSprite.tile_images["0111"] = TileSprite.image.subsurface((p*11,0,p,p))
            TileSprite.tile_images["1011"] = TileSprite.image.subsurface((p*12,0,p,p))
            # Two height corner
            TileSprite.tile_images["2101"] = TileSprite.image.subsurface((p*13,0,p,p))
            TileSprite.tile_images["1210"] = TileSprite.image.subsurface((p*14,0,p,p))
            TileSprite.tile_images["0121"] = TileSprite.image.subsurface((p*15,0,p,p))
            TileSprite.tile_images["1012"] = TileSprite.image.subsurface((p*16,0,p,p))
            # "furrow" tiles
            TileSprite.tile_images["1010"] = TileSprite.image.subsurface((p*17,0,p,p))
            TileSprite.tile_images["0101"] = TileSprite.image.subsurface((p*18,0,p,p))
            for i in TileSprite.tile_images:
                TileSprite.tile_images[i].convert()
                TileSprite.tile_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)
        # Pre-load sprite's image
        self.image = TileSprite.tile_images[val]
        self.xpos = xpos
        self.ypos = ypos
        self.rect = (self.xpos + xoff, self.ypos + yoff, p, p)
        self.type = val
        self.xWorld = xWorld
        self.yWorld = yWorld
    def update(self, xoff, yoff):
        """Update position of sprite with new offsets"""
        self.rect = (self.xpos + xoff, self.ypos + yoff, p, p)
        
class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

    x_dist = 20     # Distance to move the screen when arrow keys are pressed
    y_dist = 20     # in x and y dimensions

    def __init__(self, width=800, height=500):
        # Initialize PyGame
        pygame.init()
        
        # Set the window Size
        self.width = width
        self.height = height
        
        # Create the Screen
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                
        self.array = world.MakeArray()   # array of tiles, make or load
        self.WorldX = len(self.array[0])      #lazy method, needs change
        self.WorldY = len(self.array)
        self.WidthX = (self.WorldX + self.WorldY) * (p/2)
        self.HeightY = ((self.WorldX + self.WorldY) * (p/4)) + (p/2)
        
        self.dxoff = 0
        self.dyoff = 0

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        # Initiate the clock
        self.clock = pygame.time.Clock()

        #tell pygame to keep sending up keystrokes when they are held down
        pygame.key.set_repeat(500, 30)
                
        self.tool = ""

        self.font = pygame.font.Font(None, 12)

        background = pygame.Surface([self.width, self.height])
        background.fill([0, 0, 0])

##        self.orderedSprites = pygame.sprite.OrderedUpdates()
        self.orderedSprites = pygame.sprite.LayeredUpdates()

        for y in range(self.WorldY):
            for x in range(self.WorldX):
                posx = (self.WidthX / 2) + (x * (p2)) - (y * (p2)) - (p2)
                posy = (x * (p4)) + (y * (p4)) - (self.array[x][y][0] * ph)
                # Layers from top of the screen to the bottom
                l = x + y
                self.orderedSprites.add(TileSprite(self.ArrayToString(self.array[x][y][1]),
                                                   posx, posy, self.dxoff, self.dyoff, x, y), layer=l)

        highlightSprite = None
        self.refresh_screen = 0
        while 1:
            self.clock.tick(0)
            self.dirty = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    # When the mouse is moved, check to see if...
                    b = event.buttons
                    # Is the right mouse button held? If so, do scrolling & refresh whole screen
                    if (event.buttons == (0,0,1)):
                        self.MoveScreen("mouse")
                    else:
                        pygame.mouse.get_rel()  #Reset mouse position for scrolling


            rectlist = self.orderedSprites.draw(self.screen)
##            for r in rectlist:
##                self.dirty.append(r)

            self.last_pos = pygame.mouse.get_pos()
            # Draw mouseSprite at cursor position
            mouseSprite = pygame.sprite.GroupSingle(MouseSprite(pygame.mouse.get_pos()))
            mouseSprite.draw(self.screen)
            self.dirty.append(mouseSprite.sprite.rect)
            # Find sprites that the mouseSprite intersects with
            collision_list1 = pygame.sprite.spritecollide(mouseSprite.sprite, self.orderedSprites, False)#, pygame.sprite.collide_mask)
            collision_list = pygame.sprite.spritecollide(mouseSprite.sprite, collision_list1, False, pygame.sprite.collide_mask)

            # Find position of cursor relative to the confines of the selected tile
            # Use first item in the list
            if collision_list:
                # Strip out any items in the collision list which should be excluded, e.g. the highlight itself
                collision_list2 = []
                for t in range(len(collision_list)):
                    if not collision_list[t].col_exclude:
                        collision_list2.append(collision_list[t])
                collision_list = collision_list2
                coltile = collision_list[-1]
                x = coltile.xWorld
                y = coltile.yWorld
                # Find where this tile would've been drawn on the screen, and subtract the mouse's position
                mousex, mousey = pygame.mouse.get_pos()
                posx = (self.WidthX / 2) + (x * (p2)) - (y * (p2)) - (p2)
                posy = (x * (p4)) + (y * (p4)) - (self.array[x][y][0] * ph)
                offx = mousex - (posx + self.dxoff)
                offy = mousey - (posy + self.dyoff)
                # Then compare these offsets to the table of values for this particular kind of tile
                # to find which overlay selection sprite should be drawn
                # Height in 16th incremenets, width in 8th increments
                offx8 = offx / p8
                offy16 = offy / p16
                
                # Then lookup the mask number based on this, this should be drawn on the screen
                tilesubposition = type0[offy16][offx8]
                self.tilesubposition = tilesubposition
                # Add old dirty area to dirtylist
                if not highlightSprite:
                    highlightSprite = HighlightSprite()
                    self.orderedSprites.add(highlightSprite, layer=(x+y))
                highlightSprite.changepos(tilesubposition, str(coltile.type),
                                          posx, posy, self.dxoff, self.dyoff, x, y)
                self.orderedSprites.change_layer(highlightSprite, (x+y))
            else:
                # No collision, cursor outside game area, set highlight to nothing
                if highlightSprite:
                    highlightSprite.changepos(0, "0000",
                                              0, 0, self.dxoff, self.dyoff, 0, 0)
                
            if collision_list:
                ii = collision_list[-1]
                layer = self.orderedSprites.get_layer_of_sprite(ii)
                pygame.display.set_caption("FPS: %.1f, Tile: (%s,%s) of type: %s | layer: %s" %
                                           (self.clock.get_fps(), ii.xWorld, ii.yWorld, ii.type, layer))
            else:
                pygame.display.set_caption("FPS: %.1f" %
                                           (self.clock.get_fps()))

            # If land height has been altered, or the screen has been moved
            # we need to refresh the entire screen
            if self.refresh_screen == 1:
                pygame.display.update()
                self.refresh_screen = 0
                self.orderedSprites.clear(self.screen, background)
            else:
                pygame.display.update()



    def ArrayToString(self, array):
        """Convert a heightfield array to a string"""
        return "%s%s%s%s" % (array[0], array[1], array[2], array[3])

    def PaintLand2(self):
        """Paint the land as a series of sprites"""
        self.refresh_screen = 1

        self.orderedSprites.update(self.dxoff, self.dyoff)

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

        self.PaintLand2()

    def ScreenToIso(self, wxy=(0,0)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        TileRatio = 2.0
        wx, wy = wxy

        dx = wx - (self.WidthX/2) - self.dxoff
        dy = wy - (p/2) - self.dyoff

        x = int((dy + (dx / TileRatio)) / (p/2))
        y = int((dy - (dx / TileRatio)) / (p/2))
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
        
        self.PaintLand2()
        #self.HighlightTile()


if __name__ == "__main__":
    world = World.World()
    MainWindow = DisplayMain()
    MainWindow.MainLoop()








    
