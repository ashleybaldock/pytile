"""
bezier.py - Calculates a bezier curve from control points. 
 
Depends on the 2d vector class found here: http://www.pygame.org/wiki/2DVectorClass
 
2007 Victor Blomqvist
Released to the Public Domain
"""
import pygame
from pygame.locals import *
 
from vec2d import *
 
gray = (100,100,100)
lightgray = (200,200,200)
red = (255,0,0)
darkred = (192,0,0)
green = (0,255,0)
darkgreen = (0,128,0)
blue = (0,0,255)
darkblue = (0,0,192)
brown = (72,64,0)
silver = (224,216,216)
X,Y,Z = 0,1,2
black = (0,0,0)
white = (255,255,255)
 
def calculate_bezier(p, steps = 30):
    """
    Calculate a bezier curve from 4 control points and return a 
    list of the resulting points.
    
    The function uses the forward differencing algorithm described here: 
    http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
    """
    
    t = 1.0 / steps
    temp = t*t
    
    f = p[0]
    fd = 3 * (p[1] - p[0]) * t
    fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
    fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t
    
    fddd = fddd_per_2 + fddd_per_2
    fdd = fdd_per_2 + fdd_per_2
    fddd_per_6 = fddd_per_2 * (1.0 / 3)
    
    points = []
    tangents = []
    for x in range(steps):
        points.append(f)
        tangents.append(fd)
        f = f + fd + fdd_per_2 + fddd_per_6
        fd = fd + fdd + fddd_per_2
        fdd = fdd + fddd
        fdd_per_2 = fdd_per_2 + fddd_per_2
    points.append(f)
    tangents.append(fd)
    return (points, tangents)

def get_at_width(point, tangent, width):
    newpoint = point + tangent.perpendicular_normal() * width
    return newpoint

def get_point_at_width(a, b, width):
    a_to_b = b - a
    c = a + a_to_b.perpendicular_normal() * width
    d = b + a_to_b.perpendicular_normal() * width
    return d

def get_points_at_width((a1, b1, b2, a2), width):
    a1_to_b1 = b1 - a1
    a2_to_b2 = b2 - a2
    ab1_pn = a1_to_b1.perpendicular_normal()
    ab2_pn = a2_to_b2.perpendicular_normal()
    c1 = a1 + ab1_pn * width
    c2 = a2 + ab2_pn * -width
    d1 = b1 + ab1_pn * width + a1_to_b1.normalized() * width
    d2 = b2 + ab2_pn * -width + a2_to_b2.normalized() * -width
    return [c1, d1, d2, c2]

def draw_curve(points, colour, screen):
    b_points = calculate_bezier(points)
    pygame.draw.lines(screen, colour, False, b_points)

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 500))
 
    ### Control points that are later used to calculate the curve
    control_points = [vec2d(100,50), vec2d(150,450), vec2d(500,100), vec2d(450, 450)]
 
    ### The currently selected point
    selected = None
    
    clock = pygame.time.Clock()
    pts = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for p in control_points:
                    if abs(p.x - event.pos[X]) < 10 and abs(p.y - event.pos[Y]) < 10 :
                        selected = p
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                x,y = pygame.mouse.get_pos()
                control_points.append(vec2d(x,y))
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                selected = None
        
        ### Draw stuff
        screen.fill(darkgreen)
                
        if selected is not None:
            selected.x, selected.y = pygame.mouse.get_pos()
            pygame.draw.circle(screen, green, selected, 10)
        
        ### Draw control points
        for p in control_points:
            pygame.draw.circle(screen, blue, p, 4)
        ### Draw control "lines"
        pygame.draw.lines(screen, lightgray, False, [control_points[0],control_points[1]])
        pygame.draw.lines(screen, lightgray, False, [control_points[2],control_points[3]])
        # Use control points to generate series of curves to draw
        # Need to transform the vectors of the control points
        # Add 0+1 and 2+3
        width = 15

        # And now the better method (more accurate)
        cps, tangents = calculate_bezier(control_points, 30)
        pygame.draw.lines(screen, red, False, cps)


        # Find total distance of all line segments being dealt with
        # Divide this by the sleeper density
        # Then draw sleepers at positions along the center line, at right angles to its current
        # tangent gradient, at regular spacings
        # Have to lookup the
        sleeper_spacing = 15
        sleeper_width = 5
        sleeper_length = 25
        sleeper_points = []
        overflow = 0
        for p in range(1, len(cps)):
            # Find gradient of a->b
            b = cps[p]
            a = cps[p-1]
            a_to_b = b - a
            ab_n = a_to_b.normalized()
            # Vector to add to start vector, to get offset start location
            if overflow > 0:
                start_vector = (overflow) * ab_n
            else:
                start_vector = overflow * ab_n
            # Number of sleepers to draw in this section
            n_sleepers = (a_to_b + start_vector).get_length() / (ab_n * sleeper_spacing).get_length()
            # Loop through n_sleepers
            for n in range(n_sleepers):
                sleeper_points.append([get_at_width(a - start_vector + n*ab_n*sleeper_spacing - ab_n*0.5*sleeper_width, a_to_b, -sleeper_length),
                                       get_at_width(a - start_vector + n*ab_n*sleeper_spacing - ab_n*0.5*sleeper_width, a_to_b, sleeper_length),
                                       get_at_width(a - start_vector + n*ab_n*sleeper_spacing + ab_n*0.5*sleeper_width, a_to_b, sleeper_length),
                                       get_at_width(a - start_vector + n*ab_n*sleeper_spacing + ab_n*0.5*sleeper_width, a_to_b, -sleeper_length)])
            # Finally calculate overflow for the next loop
            overflow = (a_to_b + start_vector).get_length() % (ab_n * sleeper_spacing).get_length()

        # Finally draw all the sleeper points
        for p in sleeper_points:
            pygame.draw.polygon(screen, brown, p, 0)

        points2 = []
        for p in range(0, len(cps)):
            points2.append(get_at_width(cps[p], tangents[p], width))
        pygame.draw.lines(screen, silver, False, points2, 3)
        points3 = []
        for p in range(0, len(cps)):
            points3.append(get_at_width(cps[p], tangents[p], -width))
        pygame.draw.lines(screen, silver, False, points3, 3)

        # Draw bezier box hints
##        for p in range(0, len(points2), 1):
##            pygame.draw.line(screen, black, points2[p], points3[p])
##        for p in points2:
##            pygame.draw.circle(screen, black, p, 2)
##        for p in points3:
##            pygame.draw.circle(screen, black, p, 2)
        ### Flip screen
        pygame.display.flip()
        clock.tick(100)
        #print clock.get_fps()
##        running = False
    
if __name__ == '__main__':
    main()