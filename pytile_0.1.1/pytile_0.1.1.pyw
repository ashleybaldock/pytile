#!/usr/bin/python
# pyTile - 0.1.1
#
# Written by Timothy Baldock
#
# http://entropy.me.uk/pytile
#

import os, sys
import pygame
import random, math
from copy import copy

import World

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

class HighlightSprite(pygame.sprite.Sprite):
    """Sprites for displaying ground selection highlight"""
    image = None
    rect = None
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        if HighlightSprite.image is None:
            groundImage = pygame.image.load("ground.png")
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
            for i in HighlightSprite.tile_images:
                HighlightSprite.tile_images[i].convert()
                HighlightSprite.tile_images[i].set_colorkey((231,255,255), pygame.RLEACCEL)
        self.image = pygame.Surface((p,p))
        self.image.set_colorkey((0,0,0))
        self.exclude = True
    def changepos(self, type, tiletype, xpos, ypos, xoff, yoff, xWorld, yWorld):
        """Set highlight to appear on a different tile"""
        self.image.fill((0,0,0))
        if type == 0:
            # Empty Image
            pass
        # Corner bits, made up of two images
        elif type == 1:
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (0,0), (0,0,p4,p))
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (0,0), (0,0,p4,p))
        elif type == 2:
            self.image.blit(HighlightSprite.tile_images["%s%sXX" % (tiletype[0], tiletype[1])], (p4,0), (p4,0,p2,p))
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (p4,0), (p4,0,p2,p))
        elif type == 3:
            self.image.blit(HighlightSprite.tile_images["X%s%sX" % (tiletype[1], tiletype[2])], (p4x3,0), (p4x3,0,p4,p))
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (p4x3,0), (p4x3,0,p4,p))
        elif type == 4:
            self.image.blit(HighlightSprite.tile_images["XX%s%s" % (tiletype[2], tiletype[3])], (p4,0), (p4,0,p2,p))
            self.image.blit(HighlightSprite.tile_images["%sXX%s" % (tiletype[0], tiletype[3])], (p4,0), (p4,0,p2,p))
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
        if type == 0:
            self.rect = (self.xpos - xoff, self.ypos - yoff, 1, 1)
        else:
            self.rect = (self.xpos - xoff, self.ypos - yoff, p, p)
        self.type = type
        self.xWorld = xWorld
        self.yWorld = yWorld
        self.layer = xWorld + yWorld
    def update(self, xoff, yoff):
        """Update position of sprite with new offsets"""
        self.rect = (self.xpos - xoff, self.ypos - yoff, p, p)

class TileSprite(pygame.sprite.Sprite):
    """Ground tiles"""
    image = None
    def __init__(self, type, xpos, ypos, xoff, yoff, xWorld, yWorld, exclude=False):
        pygame.sprite.Sprite.__init__(self)
        if TileSprite.image is None:
            groundImage = pygame.image.load("ground.png")
            TileSprite.image = groundImage.convert()
            # Tile images will be composited using rendering later, for now just read them in
            TileSprite.tile_images = {}
            # Left and Right cliff images
            TileSprite.tile_images["CL11"] = TileSprite.image.subsurface((p*0,p*2,p,p))
            TileSprite.tile_images["CL10"] = TileSprite.image.subsurface((p*1,p*2,p,p))
            TileSprite.tile_images["CL01"] = TileSprite.image.subsurface((p*2,p*2,p,p))
            TileSprite.tile_images["CR11"] = TileSprite.image.subsurface((p*3,p*2,p,p))
            TileSprite.tile_images["CR10"] = TileSprite.image.subsurface((p*4,p*2,p,p))
            TileSprite.tile_images["CR01"] = TileSprite.image.subsurface((p*5,p*2,p,p))
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
        self.exclude = exclude
        self.image = TileSprite.tile_images[type]
        self.xpos = xpos
        self.ypos = ypos
        self.rect = (self.xpos - xoff, self.ypos - yoff, p, p)
        self.type = type
        self.xWorld = xWorld
        self.yWorld = yWorld
    def update(self, xoff, yoff):
        """Update position of sprite with new offsets"""
        self.rect = (self.xpos - xoff, self.ypos - yoff, p, p)

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

class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""
    def __init__(self, width, height):
        # Initialize PyGame
        pygame.init()
        
        # Set the window Size
        self.screen_width = width
        self.screen_height = height
        
        # Create the Screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))#, pygame.RESIZABLE)

        # X and Y dimensions of the world, taken from the generated array
        self.array = world.MakeArray()
        self.WorldX = len(self.array)
        self.WorldY = len(self.array[0])

        # Width and Height of the world, in pixels
        self.WorldWidth = (self.WorldX + self.WorldY) * p2
        self.WorldWidth2 = self.WorldWidth / 2
        self.WorldHeight = ((self.WorldX + self.WorldY) * p4) + p2

        # Initial screen offset
        # Screen offset is from 0,0 in World pixel coordinate space
        self.dxoff = 0
        self.dyoff = 0

        #tell pygame to keep sending up keystrokes when they are held down
        pygame.key.set_repeat(500, 30)

        # Setup fonts
        self.font = pygame.font.Font(None, 12)

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        # Initiate the clock
        self.clock = pygame.time.Clock()

##        background = pygame.Surface([self.screen_width, self.screen_height])
##        background.fill([0, 0, 0])

        self.orderedSprites = pygame.sprite.LayeredUpdates()

        self.paint_world()

        highlightSprite = None
        self.mouseSprite = None
        self.last_pos = None
        coltile = None
        self.last_mouse_position = pygame.mouse.get_pos()
        lmb_current_drag = False
        rmb_current_drag = False
        while True:
            self.clock.tick(0)
            self.dirty = []
            # If there's a quit event, don't bother parsing the event queue
            if pygame.event.peek(pygame.QUIT):
                pygame.display.quit()
                sys.exit()
            lmb_drags = []
            rmb_drags = []
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()

                # Modifier keys will also need to be dealt with in sequence, as these affect the actions
                # required by mouse motions (probably best to have a tool be "active", and for this to be
                # stored along with the move durations in the list of LMB events
                #
                # RMB click and drag moves the screen, scrollwheel in/out zooms in inspection mode,
                # alters tool settings in tool modes (unless RMB down, in which case scrollwheel always
                # zooms in/out)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # LMB down - start a new LMB drag
                        lmb_current_drag = [event.pos, event.pos, False]
                    if event.button == 3:
                        # RMB down - start a new RMB drag and stop current LMB drag (if present)
                        rmb_current_drag = [event.pos, event.pos]
                        if lmb_current_drag:
                            lmb_drags.append(lmb_current_drag)
                            lmb_current_drag = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # LMB up - end current LMB drag (if present, could've been ended in other ways)
                        if lmb_current_drag:
                            lmb_drags.append(lmb_current_drag)
                            lmb_current_drag = False
                    if event.button == 3:
                        # RMB up - end current RMB drag
                        rmb_drags.append(rmb_current_drag)
                        rmb_current_drag = False
                if event.type == pygame.MOUSEMOTION:
                    self.last_mouse_position = event.pos
                    if event.buttons[2] == 1:
                        # RMB pressed, change rmb_drag endpoint
                        rmb_current_drag[1] = event.pos
                    elif event.buttons[0] == 1:
                        # LMB pressed, change lmb_drag endpoint
                        if lmb_current_drag:
                            lmb_current_drag[1] = event.pos
                        else:
                            lmb_current_drag = [event.pos, event.pos, False]

            # Must then end any currently active drags, but leave the mouse button states open for the next
            # frame (e.g. take a snapshot of the current drag progress, but don't delete it
            if lmb_current_drag:
                lmb_drags.append(lmb_current_drag)
            if rmb_current_drag:
                rmb_drags.append(rmb_current_drag)

##            if rmb_drags or lmb_drags:
##                print "LMB drags: %s, RMB drags: %s" % (lmb_drags, rmb_drags)

            if rmb_drags:
                # Do screen movement
                total_drag = [rmb_drags[0][0], rmb_drags[-1][1]]
                if total_drag[0][0] != total_drag[1][0] or total_drag[0][1] != total_drag[1][1]:
                    self.move_screen(total_drag)
                # As this part of the current drag has been processed, set the start point of the next
                # bit to the end point of this bit
                # Remove this to enable constant drag scrolling (though using it this way would require
                # some kind of modifier based on the framerate, to ensure that it scrolls at a consistent
                # speed on all speeds of platform)
                if rmb_current_drag:
                    rmb_current_drag[0] = rmb_current_drag[1]

            if lmb_drags:
                # Do selection, interaction etc.
                # First locate collision position of the start and end point of the drag (if these differ)
                for drag in lmb_drags:
                    if not drag[2]:
                        tileposition = self.CollideLocate(drag[0], self.orderedSprites)
                        if tileposition:
                            subtileposition = self.SubTilePosition(drag[0], tileposition)
                        else:
                            subtileposition = None
                        drag[2] = (tileposition, subtileposition)
                    else:
                        tileposition, subtileposition = drag[2]
                    # Drag or click must be on a sprite
                    # If that sprite is a ground tile, and a ground tile altering tool is selected
                    # then perform ground alteration
                    if tileposition:
                        # Set start position
                        start = drag[0]
                        # If end position different to start, set end position
                        if drag[0] != drag[1]:
                            end = drag[1]
                        else:
                            end = None
                        if end:
                            # Addback keeps the cursor on the 0 level of the terrain and ensures that the user
                            # must bring the mouse back up to the 0 level before the raising function will
                            # work again
                            addback = 0
                            # Raise height by y difference / ph
                            diff = (end[1] - start[1]) / ph
                            diffrem = (end[1] - start[1]) % ph
                            if diff != 0:
                                invdiff = - diff
                                totalchange, realchange = self.modify_tile(tileposition, subtileposition, invdiff)
                                x = tileposition.xWorld
                                y = tileposition.yWorld
                                # Also raise the height of the stored copy of the tile in the drag object
                                drag[2][0].ypos += realchange * ph
                                if invdiff < 0:
                                    # Moving down
                                    if totalchange > invdiff:
                                        # Have moved tile down by less than the total change
                                        # Thus an additional offset must be made to force the cursor to be
                                        # brought back up to the level of the terrain
                                        addback = (invdiff - totalchange) * ph
##                                print "invdiff: %s, realchange: %s, totalchange: %s, addback: %s" % (invdiff, realchange, totalchange, addback)
                                # This could be optimised to not recreate the entire sprite array
                                # and only correct the tiles which have been modified
                                self.paint_world()
                            if drag == lmb_current_drag:
                                # If this is a drag operation which is split across multiple frames then
                                # the start location for the next frame needs to be modified to reflect the bits
                                # which were processed this frame
                                lmb_current_drag[0] = (lmb_current_drag[1][0],
                                                       lmb_current_drag[1][1] - diffrem + addback)

            # Lastly draw highlight at current position of mouse
            # If there is an active drag operation ongoing, then the highlight needs to be affected by this

            if lmb_current_drag and lmb_current_drag[2]:
                self.last_pos = self.last_mouse_position
                coltile = lmb_current_drag[2][0]
                subtileposition = lmb_current_drag[2][1]
            elif self.last_pos != self.last_mouse_position:
                self.last_pos = self.last_mouse_position
                coltile = self.CollideLocate(self.last_mouse_position, self.orderedSprites)
                if coltile:
                    subtileposition = self.SubTilePosition(self.last_mouse_position, coltile)
            # Find position of cursor relative to the confines of the selected tile
            # Use first item in the list
            if coltile:
                if not highlightSprite:
                    highlightSprite = HighlightSprite()
                if not self.orderedSprites.has(highlightSprite):
                    self.orderedSprites.add(highlightSprite, layer=(coltile.xWorld + coltile.yWorld))
                if highlightSprite.rect:
                    self.dirty.append(highlightSprite.rect)
                # This whole coltile thing really ought to change, since it bears little resemblance to the
                # tile which highlightSprite represents - maybe better to set attributes of the highlight
                # directly?
                highlightSprite.changepos(subtileposition, str(self.array_to_string(self.array[coltile.xWorld][coltile.yWorld][1])),
                                          coltile.xpos, coltile.ypos, self.dxoff, self.dyoff,
                                          coltile.xWorld, coltile.yWorld)
                self.dirty.append(highlightSprite.rect)
                self.orderedSprites.change_layer(highlightSprite, (coltile.xWorld + coltile.yWorld))
            else:
                # No collision, cursor outside game area, set highlight to nothing
                if highlightSprite:
                    if highlightSprite.rect:
                        self.dirty.append(highlightSprite.rect)
                    highlightSprite.changepos(0, "0000",
                                              0, 0, self.dxoff, self.dyoff, 0, 0)
                    self.dirty.append(highlightSprite.rect)

            # Write some useful info on the top bar
            if coltile:
                ii = coltile
                layer = self.orderedSprites.get_layer_of_sprite(ii)
                pygame.display.set_caption("FPS: %i | Tile: (%s,%s) of type: %s, layer: %s | dxoff: %s dyoff: %s" %
                                           (self.clock.get_fps(), ii.xWorld, ii.yWorld, ii.type, layer, self.dxoff, self.dyoff))
            else:
                pygame.display.set_caption("FPS: %i | dxoff: %s dyoff: %s" %
                                           (self.clock.get_fps(), self.dxoff, self.dyoff))


            rectlist = self.orderedSprites.draw(self.screen)

            # If land height has been altered, or the screen has been moved
            # we need to refresh the entire screen
            if self.refresh_screen == 1:
                pygame.display.update()
                self.screen.fill((0,0,0))
                self.refresh_screen = 0
            else:
                pygame.display.update(self.dirty)


# Only mark dirty when the cursor position has significantly changed (i.e. new graphic)

# Could also use a mode which maintains the slope of the tile, and simply increases its height
# shift+LMBdrag - preserve slope and move up/down (whole tile only)
# ctrl+LMBdrag  - vertex, modify this vertex and its neighbours
#               - edge, modify this edge, its facing neighbour and the vertices at either end
#               - tile, modify this tile, its surrounding neighbour edges and vertices
#

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

    def modify_tile(self, tile, subtile, amount):
        """Raise (or lower) a tile based on the subtile"""
        tgrid = tGrid(self.array[tile.xWorld][tile.yWorld][1])
        t = self.array[tile.xWorld][tile.yWorld][0]
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

        self.array[tile.xWorld][tile.yWorld][1] = tgrid
        # Tile must not be reduced to below 0
        if t < 0:
            t = 0
        ct = self.array[tile.xWorld][tile.yWorld][0]
        self.array[tile.xWorld][tile.yWorld][0] = t
        # Return the total amount of height change, and the real amount
        return (total, ct - t)

    def SubTilePosition(self, mousepos, tile):
        """Find the sub-tile position of the cursor"""
        x = tile.xWorld
        y = tile.yWorld
        # Find where this tile would've been drawn on the screen, and subtract the mouse's position
        mousex, mousey = mousepos
        posx = self.WorldWidth2 - (x * (p2)) + (y * (p2)) - p2
        posy = (x * (p4)) + (y * (p4)) - (self.array[x][y][0] * ph)
        offx = mousex - (posx - self.dxoff)
        offy = mousey - (posy - self.dyoff)
        # Then compare these offsets to the table of values for this particular kind of tile
        # to find which overlay selection sprite should be drawn
        # Height in 16th incremenets, width in 8th increments
        offx8 = offx / p8
        offy16 = offy / p16
        # Then lookup the mask number based on this, this should be drawn on the screen
        try:
            tilesubposition = type[tile.type][offy16][offx8]
            return tilesubposition
        except IndexError:
            print "offy16: %s, offx8: %s, coltile: %s" % (offy16, offx8, tile.type)
            return None

    def CollideLocate(self, mousepos, collideagainst):
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

    def array_to_string(self, array):
        """Convert a heightfield array to a string"""
        return "%s%s%s%s" % (array[0], array[1], array[2], array[3])

    def paint_world(self):
        """Paint the world as a series of sprites
        Includes ground and other objects"""
        self.refresh_screen = 1
        self.orderedSprites.empty()     # This doesn't necessarily delete the sprites though
        # Top-left of view relative to world given by self.dxoff, self.dyoff
        # Find the base-level tile at this position
        topleftTileY, topleftTileX = self.screen_to_iso((self.dxoff, self.dyoff))
        for x1 in range(self.screen_width / p + 1):
            for y1 in range(self.screen_height / p4):
                x = int(topleftTileX - x1 + math.ceil(y1 / 2.0))
                y = int(topleftTileY + x1 + math.floor(y1 / 2.0))
                # Tile must be within the bounds of the map
                if (x >= 0 and y >= 0) and (x < self.WorldX and y < self.WorldY):
                    posx = self.WorldWidth2 - (x * p2) + (y * p2) - p2
                    posybase = (x * p4) + (y * p4)
                    l = x + y
                    # Add vertical surfaces for this tile (if any)
                    # A1/A2 are top and right vertices of tile in front/left of the one we're testing
                    if x == self.WorldX - 1:
                        A1 = 0
                        A2 = 0
                    else:
                        A1 = self.array[x+1][y][1][3] + self.array[x+1][y][0]
                        A2 = self.array[x+1][y][1][2] + self.array[x+1][y][0]
                    # B1/B2 are left and bottom vertices of tile we're testing
                    B1 = self.array[x][y][1][0] + self.array[x][y][0]
                    B2 = self.array[x][y][1][1] + self.array[x][y][0]
                    while B1 > A1 or B2 > A2:
                        if B1 > B2:
                            B1 -= 1
                            posy = posybase - B1 * ph
                            self.orderedSprites.add(TileSprite("CL10",
                                                    posx, posy, self.dxoff, self.dyoff, x, y, exclude=True), layer=l)
                        elif B1 == B2:
                            B1 -= 1
                            B2 -= 1
                            posy = posybase - B1 * ph
                            self.orderedSprites.add(TileSprite("CL11",
                                                    posx, posy, self.dxoff, self.dyoff, x, y, exclude=True), layer=l)
                        else:
                            B2 -= 1
                            posy = posybase - B1 * ph
                            self.orderedSprites.add(TileSprite("CL01",
                                                    posx, posy, self.dxoff, self.dyoff, x, y, exclude=True), layer=l)
                    # A1/A2 are top and right vertices of tile in front/right of the one we're testing
                    if y == self.WorldY - 1:
                        A1 = 0
                        A2 = 0
                    else:
                        A1 = self.array[x][y+1][1][3] + self.array[x][y+1][0]
                        A2 = self.array[x][y+1][1][0] + self.array[x][y+1][0]
                    # B1/B2 are left and bottom vertices of tile we're testing
                    B1 = self.array[x][y][1][2] + self.array[x][y][0]
                    B2 = self.array[x][y][1][1] + self.array[x][y][0]
                    while B1 > A1 or B2 > A2:
                        if B1 > B2:
                            B1 -= 1
                            posy = posybase - B1 * ph
                            self.orderedSprites.add(TileSprite("CR10",
                                                    posx, posy, self.dxoff, self.dyoff, x, y, exclude=True), layer=l)
                        elif B1 == B2:
                            B1 -= 1
                            B2 -= 1
                            posy = posybase - B1 * ph
                            self.orderedSprites.add(TileSprite("CR11",
                                                    posx, posy, self.dxoff, self.dyoff, x, y, exclude=True), layer=l)
                        else:
                            B2 -= 1
                            posy = posybase - B1 * ph
                            self.orderedSprites.add(TileSprite("CR01",
                                                    posx, posy, self.dxoff, self.dyoff, x, y, exclude=True), layer=l)
                    # And add the tile itself
                    posy = posybase - (self.array[x][y][0] * ph)
                    self.orderedSprites.add(TileSprite(self.array_to_string(self.array[x][y][1]),
                                                       posx, posy, self.dxoff, self.dyoff, x, y), layer=l)



    def screen_to_iso(self, (wx,wy)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        TileRatio = 2.0
        # Convert coordinates to be relative to the position of tile (0,0)
        dx = wx - self.WorldWidth2
        dy = wy - (p2)
        # Do some maths
        x = int((dy + (dx / TileRatio)) / (p2))
        y = int((dy - (dx / TileRatio)) / (p2))
##        if x < 0 or y < 0:
##            return (0,0)
##        if x >= (self.WorldX) or y >= (self.WorldY):
##            return (0,0)
        return (x,y)

    def move_screen(self, drag):
        """Move the screen on mouse input"""
        start_x, start_y = drag[0]
        end_x, end_y = drag[1]
        rel_x = start_x - end_x
        rel_y = start_y - end_y
        self.dxoff += rel_x
        self.dyoff += rel_y

        self.paint_world()





# Hitboxes for subtile selection
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

type_lookup = [[0,0,0,0],[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1],[1,1,1,1]]

type = {}

# Flat tile
type["0000"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,8,8,9,9,7,7,0],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Left vertex
type["1000"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,8,4,4,0,0,0],
                [1,1,8,4,4,7,0,0],
                [1,1,8,9,9,7,7,0],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,9,3,3],
                [0,0,5,9,9,6,6,0],
                [0,0,0,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Bottom vertex
type["0100"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,8,8,9,9,7,7,0],
                [1,1,9,9,9,9,3,3],
                [1,1,5,2,2,6,3,3],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Right vertex
type["0010"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,7,0,0],
                [0,0,8,4,4,7,3,3],
                [0,8,8,9,9,7,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,6,6,0],
                [0,5,5,9,9,6,0,0],
                [0,0,5,2,2,0,0,0],
                [0,0,0,2,2,0,0,0],]
# Top vertex
type["0001"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,0,8,4,4,7,0,0],
                [0,1,8,9,9,7,3,0],
                [1,1,8,9,9,7,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Bottom-Left edge
type["1100"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,8,4,4,0,0,0],
                [1,1,8,4,4,7,0,0],
                [1,1,8,9,9,7,7,0],
                [1,1,5,9,9,9,3,3],
                [0,5,5,2,2,6,3,3],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Bottom-Right edge
type["0110"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,7,0,0],
                [0,0,8,4,4,7,3,3],
                [0,8,8,9,9,7,3,3],
                [1,1,9,9,9,6,3,3],
                [1,1,5,2,2,6,6,0],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Top-Right edge
type["0011"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,0,8,4,4,7,0,0],
                [0,0,8,9,9,7,3,3],
                [0,8,8,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,6,6,0],
                [0,5,5,9,9,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Top-Left edge
type["1001"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,0,8,4,4,7,0,0],
                [1,1,8,9,9,7,0,0],
                [1,1,9,9,9,7,7,0],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,9,3,3],
                [0,5,5,9,9,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Right vertex down
type["1101"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,8,8,9,9,7,7,0],
                [1,1,9,9,9,7,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,5,9,9,6,3,3],
                [0,5,5,2,2,6,3,3],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,0,0,0,0,0],]
# Top vertex down
type["1110"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,8,8,4,4,7,7,0],
                [1,8,8,4,4,7,7,3],
                [1,1,8,4,4,7,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,5,9,9,6,3,3],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,0,0,0,0,0],]
# Left vertex down
type["0111"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,8,8,9,9,7,7,0],
                [1,1,8,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,5,9,9,6,3,3],
                [1,1,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,0,0,0,0,0],]
# Bottom vertex down
type["1011"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,8,8,9,9,7,7,0],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,6,6,0],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Left vertex two-up
type["2101"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,8,4,4,0,0,0],
                [1,1,8,4,4,7,7,0],
                [1,1,8,4,4,7,7,3],
                [1,1,8,4,4,7,3,3],
                [1,1,5,9,9,9,3,3],
                [0,5,5,9,9,6,3,3],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,0,0,0,0,0],]
# Bottom vertex two-up
type["1210"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,8,8,4,4,7,7,0],
                [1,8,8,4,4,7,7,3],
                [1,1,8,4,4,7,3,3],
                [1,1,5,9,9,6,3,3],
                [1,1,5,2,2,6,3,3],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,0,0,0,0,0],]
# Right vertex two-up
type["0121"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,7,0,0],
                [0,8,8,4,4,7,3,3],
                [1,8,8,4,4,7,3,3],
                [1,1,8,4,4,7,3,3],
                [1,1,9,9,9,6,3,3],
                [1,1,5,9,9,6,6,0],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,0,0,0,0,0],]
# Top vertex two-up
type["1012"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,0,8,4,4,7,0,0],
                [0,8,8,9,9,7,7,0],
                [1,1,8,9,9,7,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,6,6,0],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]
# Left & Right vertices up
type["1010"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,8,4,4,7,0,0],
                [1,1,8,4,4,7,3,3],
                [1,1,8,9,9,7,3,3],
                [1,1,9,9,9,9,3,3],
                [0,5,5,9,9,6,6,0],
                [0,0,5,9,9,6,0,0],
                [0,0,0,2,2,0,0,0],
                [0,0,0,2,2,0,0,0],]
# Bottom & Top vertices up
type["0101"] = [[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,4,4,0,0,0],
                [0,0,8,4,4,7,0,0],
                [0,0,8,4,4,7,0,0],
                [0,1,8,9,9,7,3,0],
                [1,1,8,9,9,7,3,3],
                [1,1,9,9,9,9,3,3],
                [1,1,5,2,2,6,3,3],
                [0,5,5,2,2,6,6,0],
                [0,0,5,2,2,6,0,0],
                [0,0,0,2,2,0,0,0],]

if __name__ == "__main__":
	os.environ["SDL_VIDEO_CENTERED"] = "1"
	world = World.World()
	MainWindow = DisplayMain(800, 500)
	MainWindow.MainLoop()








    
