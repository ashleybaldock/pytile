from PIL import Image, ImageDraw, ImageFont
# compare a to b, b to c, c to d and d to a

max_edge_difference = 2

output = []

for a in range(5):
    for b in range(5):
        for c in range(5):
            for d in range(5):
                if 0 in [a,b,c,d]:
                    # Must be one vertex at 0
                    if not (abs(a-b) > 2 or abs(b-c) > 2 or abs(c-d) > 2 or abs(d-a) > 2):
                        # All sides must have at most 2 units of up/down movement
                        output.append([a,b,c,d])

g0 = []
g1 = []
g2 = []
g3 = []
g4 = []

print "with 0, not 1, 2, 3 or 4"
for o in output:
    if 0 in o and not 1 in o and not 2 in o and not 3 in o and not 4 in o:
        g0.append(o)
        print o
print "with 1, not 2, 3 or 4"
for o in output:
    if 1 in o and not 2 in o and not 3 in o and not 4 in o:
        g1.append(o)
        print o
print "with 2, not 3 or 4"
for o in output:
    if 2 in o and not 3 in o and not 4 in o:
        g2.append(o)
        print o
print "with 3"
for o in output:
    if 3 in o:
        g3.append(o)
        print o
print "with 4"
for o in output:
    if 4 in o:
        g4.append(o)
        print o
print len(output)

def draw_polygon(x, y):
    draw.polygon([(-1+x*64, 49+y*64), (31+x*64, 33+y*64), (31+x*64, 49+y*64)], fill=(0,190,0))
    draw.polygon([(32+x*64, 33+y*64), (64+x*64, 49+y*64), (32+x*64, 48+y*64)], fill=(0,190,0))
    draw.polygon([(64+x*64, 48+y*64), (32+x*64, 64+y*64), (32+x*64, 48+y*64)], fill=(0,190,0))
    draw.polygon([(31+x*64, 64+y*64), (-1+x*64, 48+y*64), (31+x*64, 48+y*64)], fill=(0,190,0))

def draw_heights(x, y, h):
    draw.line([(0+x*64, 48+y*64), (0+x*64, 48+y*64-h[0]*8)], fill=(255,0,0))
    draw.line([(32+x*64, 33+y*64), (32+x*64, 33+y*64-h[1]*8)], fill=(255,0,0))
    draw.line([(63+x*64, 48+y*64), (63+x*64, 48+y*64-h[2]*8)], fill=(255,0,0))
    draw.line([(31+x*64, 63+y*64), (31+x*64, 63+y*64-h[3]*8)], fill=(255,0,0))

    draw.line([(0+x*64, 48+y*64-h[0]*8), (31+x*64, 33+y*64-h[1]*8)], fill=(0,0,255))
    draw.line([(32+x*64, 33+y*64-h[1]*8), (63+x*64, 48+y*64-h[2]*8)], fill=(0,0,200))
    draw.line([(63+x*64, 48+y*64-h[2]*8), (32+x*64, 63+y*64-h[3]*8)], fill=(0,0,160))
    draw.line([(31+x*64, 63+y*64-h[3]*8), (0+x*64, 48+y*64-h[0]*8)], fill=(0,0,120))

out = Image.new("RGB", (640, 640), (231,255,255))

draw = ImageDraw.Draw(out)

oi = 0

for y in range(10):
    for x in range(10):
        draw_polygon(x, y)
        try:
            draw_heights(x, y, output[oi])
        except IndexError:
            pass
        oi += 1


##draw.text((2,52), "0", fill=(0,0,0))
##draw.text((32,25), "0", fill=(0,0,0))
##draw.text((60,52), "0", fill=(0,0,0))
##draw.text((38,58), "0", fill=(0,0,0))

del draw

out.save("testout.png", "PNG")









