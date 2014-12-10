import os, sys
import pygame
import random, math
from copy import copy

x = 240
y = 40
z = 60
xd = 100
yd = 100
zd = 100

xoff = 400
yoff = 200

rot = 0

def find_vertices(x,y,z, xd,yd,zd, rot=0, tilt=0):
    """"""
    # Return a list of tuples of (x,y,z) coordinates for the 3D bounding box of the object specified
    # by its position in x,y,z and dimensions in x,y,z (as well as rotation and tilt later)
    vertices = []
    xux = xd * math.cos(math.radians(rot))
    xuy = xd * math.sin(math.radians(rot))
    yux = yd * math.sin(math.radians(rot))
    yuy = yd * math.cos(math.radians(rot))
    for c in [z-zd, z+zd]:
        vertices.append((x+xux+yux, y+xuy-yuy, c))
        vertices.append((x+xux-yux, y+xuy+yuy, c))
        vertices.append((x-xux-yux, y-xuy+yuy, c))
        vertices.append((x-xux+yux, y-xuy-yuy, c))
    return vertices

def min_xyz(vertices, xyz):
    """"""
    vals = []
    # Collect all the vertices of the correct type together
    for k in vertices:
        vals.append(k[xyz])
    # Find the lowest value
    min_val = min(vals)
    min_vertices = []
    while vals.count(min_val):
        i = vals.index(min_val)
        vals[i] = None
        min_vertices.append(vertices[i])
    return min_vertices

def max_xyz(vertices, xyz):
    """Get the max vertices in the specified dimension from a list, x=0,y=1,z=2"""
    vals = []
    # Collect all the vertices of the correct type together
    for k in vertices:
        vals.append(k[xyz])
    # Find the highest value (may be more than one instance)
    max_val = max(vals)
    max_vertices = []
    while vals.count(max_val):
        i = vals.index(max_val)
        vals[i] = None
        max_vertices.append(vertices[i])
    return max_vertices

def find_edges(x,y,z, xd,yd,zd, rot=0, tilt=0):
    """"""
    # Return a set of start and end coordinates for line segments to draw to represent a cube
    # in 3D space, each of these coordinates can then be passed to a function to convert from
    # 3D space to the isometric projection
    edges = []
    # Draw from corner, to 3 other corners, do this 4 times for all 12 edges
    xux = xd * math.cos(math.radians(rot))
    xuy = xd * math.sin(math.radians(rot))
    yux = yd * math.sin(math.radians(rot))
    yuy = yd * math.cos(math.radians(rot))
    a1 = (x+xux+yux, y+xuy-yuy, z+zd)
    b1 = (x+xux-yux, y+xuy+yuy, z+zd)
    c1 = (x-xux-yux, y-xuy+yuy, z+zd)
    d1 = (x-xux+yux, y-xuy-yuy, z+zd)
    a2 = (x+xux+yux, y+xuy-yuy, z-zd)
    b2 = (x+xux-yux, y+xuy+yuy, z-zd)
    c2 = (x-xux-yux, y-xuy+yuy, z-zd)
    d2 = (x-xux+yux, y-xuy-yuy, z-zd)
    # x-xd, y-yd, z-zd
    edges.append((a2, b2))
    edges.append((a2, d2))
    edges.append((a2, a1))
    # x+xd, y+yd, z-zd
    edges.append((d1, a1))
    edges.append((d1, d2))
    edges.append((d1, c1))
    # x+xd, y-yd, z+zd
    edges.append((b1, a1))
    edges.append((b1, b2))
    edges.append((b1, c1))
    # x-xd, y+yd, z+zd
    edges.append((c2, c1))
    edges.append((c2, d2))
    edges.append((c2, b2))
    return edges

##theta = math.radians(90-35.264)     # True iso
theta = math.radians(90-30)         # 2:1 iso
alpha = math.radians(-45)
sinTheta = math.sin(theta)
cosTheta = math.cos(theta)
sinAlpha = math.sin(alpha)
cosAlpha = math.cos(alpha)
##leeway = 5

##zp = zpos
##xp = xpos*cosAlpha + xpos * sinAlpha
##yp = ypos*cosAlpha - ypos * sinAlpha
##x = xp
##y = zp*cosTheta - yp*sinTheta


def world_to_screen(x,y=None,z=None):
    """Convert world coordinates to screen coordinates"""
    if y == None and z == None:
        x,y,z = x
    zp = z
    xp = x*cosAlpha + y*sinAlpha
    yp = y*cosAlpha - x*sinAlpha
    x = xp + xoff
    y = yp*cosTheta - zp*sinTheta + yoff
    return (x,y)


##print find_vertices(x,y,z, xd,yd,zd)
##print find_edges(x,y,z, xd,yd,zd)


os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()

screen = pygame.display.set_mode((800,500))
pygame.key.set_repeat(500, 30)
font = pygame.font.Font(None, 12)
bigfont = pygame.font.Font(None, 16)

clock = pygame.time.Clock()
toggle_coords = True
toggle_origin = True
toggle_backfaces = True
while True:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            pygame.display.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            # Position
            if e.key == pygame.K_d:
                x += 10
            if e.key == pygame.K_q:
                x -= 10
            if e.key == pygame.K_a:
                y += 10
            if e.key == pygame.K_e:
                y -= 10
            if e.key == pygame.K_w:
                z += 10
            if e.key == pygame.K_s:
                z -= 10
            # Size
            if e.key == pygame.K_l:
                xd += 10
            if e.key == pygame.K_u:
                xd -= 10
            if e.key == pygame.K_j:
                yd += 10
            if e.key == pygame.K_o:
                yd -= 10
            if e.key == pygame.K_i:
                zd += 10
            if e.key == pygame.K_k:
                zd -= 10
            # Screen offset
            if e.key == pygame.K_DOWN:
                yoff += 10
            if e.key == pygame.K_UP:
                yoff -= 10
            if e.key == pygame.K_LEFT:
                xoff -= 10
            if e.key == pygame.K_RIGHT:
                xoff += 10
            # Rotation
            if e.key == pygame.K_z:
                rot -= 1
                if rot < 0:
                    rot += 360
            if e.key == pygame.K_x:
                rot += 1
                if rot >= 360:
                    rot -= 360
            # Toggle coordinate display
            if e.key == pygame.K_t:
                if toggle_coords:
                    toggle_coords = False
                else:
                    toggle_coords = True
            # Toggle origin display
            if e.key == pygame.K_y:
                if toggle_origin:
                    toggle_origin = False
                else:
                    toggle_origin = True
            # Toggle backface display
            if e.key == pygame.K_r:
                if toggle_backfaces:
                    toggle_backfaces = False
                else:
                    toggle_backfaces = True
    # Draw axes
    if toggle_origin:
        pygame.draw.line(screen, (255,0,0), world_to_screen(0,0,0), world_to_screen(50,0,0), 3)
        coords = font.render("X", False, (255,255,255))
        cx, cy = world_to_screen(50,0,0)
        cx += 5
        cy -= 4
        screen.blit(coords, (cx,cy))
        pygame.draw.line(screen, (0,255,0), world_to_screen(0,0,0), world_to_screen(0,50,0), 3)
        coords = font.render("Y", False, (255,255,255))
        cx, cy = world_to_screen(0,50,0)
        cx += 5
        cy -= 4
        screen.blit(coords, (cx,cy))
        pygame.draw.line(screen, (0,0,255), world_to_screen(0,0,0), world_to_screen(0,0,50), 3)
        coords = font.render("Z", False, (255,255,255))
        cx, cy = world_to_screen(0,0,50)
        cx += 5
        cy -= 4
        screen.blit(coords, (cx,cy))


    lines = find_edges(x,y,z, xd,yd,zd, rot)
    i = 0
    oldcaption = None
    for k in lines:
        i += 1
        col = (255,255,0)
        if i > 3:
            col = (255,0,0)
        if i > 6:
            col = (0,255,0)
        if i > 9:
            col = (0,0,255)
        if toggle_backfaces or i > 3:
            pygame.draw.line(screen, col, world_to_screen(k[0]), world_to_screen(k[1]))

    points = find_vertices(x,y,z, xd,yd,zd, rot)


    for p in points:
        pygame.draw.circle(screen, (255,255,255), world_to_screen(p), 3)
        if toggle_coords:
            coords = font.render("(%.1f, %.1f, %.1f)" % (p[0],p[1],p[2]), False, (255,255,255))
            cx, cy = world_to_screen(p)
            cx += 5
            cy -= 4
            screen.blit(coords, (cx,cy))

    pygame.display.update()
    screen.fill((0,0,0))

    caption = bigfont.render("FPS: %i | x,y,z: (%s,%s,%s) xd,yd,zd: (%s,%s,%s) xoff,yoff: (%s,%s) rot: %s" % (clock.get_fps(), x,y,z, xd,yd,zd, xoff,yoff, rot), True, (255,255,255))
    screen.blit(caption, (0,3))





    