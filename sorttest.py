# A test of various color sorting algorithms. See output sorttest.png.

from colorpalette import *

WIDTH = 1024
SEGMENT_HEIGHT = 32


def fill_area(img, arr, y):
    for i in range(len(arr)):
        fill_rect(img, Rect(i, y, 1, SEGMENT_HEIGHT), arr[i])

def write_segments(segments, path):
    n = len(segments)

    img = Image.new("RGB", (WIDTH, SEGMENT_HEIGHT * n), 0)

    for i in range(n):
        fill_area(img, segments[i], i * SEGMENT_HEIGHT)

    img.save(path)

def sort_1(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return h + 0.04 * s + 0.2 * v

def sort_2(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return h

def sort_3(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return (h*100)**2 + (30*v)**2

def sort_4(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return (h*100)**2 + (30*v)**2 - (10*s)**2

def sort_5(rgb):
    r,g,b = rgb
    return r*r + g*g + b*b

def sort_6(rgb):
    return (80*sort_5(rgb))**2 + sort_4(rgb)

def sort_7(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return int(10*h)

def sort_8(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return int(10*h) + v

def sort_9(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return int(10*h) + s

def sort_10(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return int(10*v) + h

def sort_11(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return int(10*s) + h

sort_funcs = [sort_1, sort_2, sort_3, sort_4, sort_5, sort_6, sort_7, sort_8, sort_9, sort_10, sort_11]

rand = []
for i in range(WIDTH):
    rand.append(RGB(random.random(), random.random(), random.random()))

segments = [rand]
for sort_func in sort_funcs:
    segments.append(sorted(rand, key=sort_func))

write_segments(segments, "sorttest.png")