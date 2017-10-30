import argparse
import random
import math
import os.path
import colorsys
from collections import namedtuple

from PIL import Image


RGB = namedtuple("RGB", ['r', 'g', 'b'])
Rect = namedtuple("Rect", ['x', 'y', 'w', 'h'])


def eps_equal(rgb1, rgb2, eps = 0.01):
    return abs(rgb2.r - rgb1.r) <= eps and abs(rgb2.g - rgb1.g) <= eps and abs(rgb2.b - rgb1.b) <= eps


def unnormalize_rgb(rgb):
    return RGB(int(rgb.r * 255), int(rgb.g * 255), int(rgb.b * 255))


def sort_func(rgb):
    h,s,v = colorsys.rgb_to_hsv(*rgb)
    return h #int(10*v) + h


def sort_colors(palette):
    palette.sort(key=sort_func)
    return palette


def fill_rect(image, rect, rgb_value):
    color = unnormalize_rgb(rgb_value)
    for row in range(rect.h):
        for col in range(rect.w):
            image.putpixel((col + rect.x, row + rect.y), color)


def dist(rgb1, rgb2):
    """Computes the Eucledian distance between two RGB points."""
    return (rgb1.r - rgb2.r) ** 2 + (rgb1.g - rgb2.g) ** 2 + (rgb1.b - rgb2.b) ** 2


def calc_average_rgb(pixels):
    n = len(pixels)

    if (n == 0):
        return RGB(-1, -1, -1)

    sum_r = 0
    sum_g = 0
    sum_b = 0
    for rgb in pixels:
        sum_r += rgb.r
        sum_g += rgb.g
        sum_b += rgb.b

    return RGB(sum_r / n, sum_g / n, sum_b / n)


def initialize_centers(pixels, num_colors):
    centers = []
    centers.append(random.choice(pixels))
    # pick centers from the farthest points from the closest center (https://en.wikipedia.org/wiki/K-means%2B%2B)
    for _ in range(1, num_colors):
        farthest_dist = 0
        farthest_rgb = None
        for rgb in pixels:
            nearest_dist = 1e9
            nearest_center = None
            for center in centers:
                cur_dist = dist(rgb, center)
                if cur_dist < nearest_dist:
                    nearest_dist = cur_dist
                    nearest_center = center

            if nearest_dist > farthest_dist:
                farthest_rgb = rgb
                farthest_dist = nearest_dist
        centers.append(farthest_rgb)
    return centers

def k_means_clustering(pixels, num_colors, log=False):
    if log:
        log_img = Image.new("RGB", (512, 1), 0)
        log_img.save("log_img.png")

    # Note: the choice of initial cluster centers largerly
    # determines the final palette.

    centers = initialize_centers(pixels, num_colors)
    # simply random sampling yields inconsistent results
    # centers = random.sample(pixels, num_colors)
    
    done = False
    while not done:
        clusters = [[] for _ in range(len(centers))]

        # assign pixel to cluster (nearest center point)
        for rgb in pixels:
            closest_center = 0
            closest_dist = int(1e9)
            for idx, center_point in enumerate(centers):
                cur_dist = dist(rgb, center_point)
                if cur_dist < closest_dist:
                    closest_center = idx
                    closest_dist = cur_dist
                
            clusters[closest_center].append(rgb)
        
        # calculate new centers
        done = True
        for idx, cluster in enumerate(clusters):
            new_center = calc_average_rgb(cluster)
            # if cluster isn't empty
            if (new_center.r != -1):
                # check for convergence
                if eps_equal(centers[idx], new_center):
                    done = done and True
                else:
                    done = False

                centers[idx] = new_center
        
        if log:
            write_palette_to_source(centers, "log_img.png", "log_img.png")

    return centers


def get_palette(image_path, num_colors = 5):
    image = Image.open(image_path)
    image.thumbnail((128, 128))  # convert the image to a thumbnail to speed up the quantization process
    # transforms rgb pixel values to be in range [0, 1]
    pixels = list(map(lambda x: RGB._make((x[0] / 255, x[1] / 255, x[2] / 255)), image.getdata()))
    return k_means_clustering(pixels, num_colors)


def write_palette(palette, output_path):
    image = Image.new("RGB", (256, 128), 0xffffff)  # new image with white background
    n = len(palette)
    col_width = math.ceil(image.width / n)
    for idx, rgb in enumerate(palette):
        x = idx * col_width
        rect = Rect(x, 0, min(col_width, image.width - x), image.height)
        fill_rect(image, rect, rgb)
    image.save(output_path)


def write_palette_to_source(palette, source_path, output_path):
    src_img = Image.open(source_path)

    palette_width = min(int(src_img.width * 0.2), 64)

    # copy the source image and add space for the palette at the bottom
    out_img = src_img.transform((src_img.width, src_img.height + palette_width), Image.EXTENT, data=(0, 0, src_img.width, src_img.height + palette_width))
    
    n = len(palette)
    col_width = math.ceil(src_img.width / n)
    for idx, rgb in enumerate(palette):
        x = idx * col_width
        rect = Rect(x, src_img.height, min(col_width, src_img.width - x), palette_width)
        fill_rect(out_img, rect, rgb)

    out_img.save(output_path)


def write_color_wheel(path, width, height):
    # Simple HSV wheel test.
    img = Image.new("RGB", (width, height), 0)
    for i in range(width):
        rgb = colorsys.hsv_to_rgb(i / width, 1, 1)
        rgb = RGB(*rgb)
        fill_rect(img, Rect(i, 0, 1, height), rgb)
    img.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("-o", "--outputpath", type=str)
    parser.add_argument("-c", "--colors", type=int, default=5)
    args = parser.parse_args()
    
    output_path = args.outputpath
    if not args.outputpath:
        split_name = os.path.splitext(os.path.basename(args.path))
        output_path = split_name[0] + "_palette" + split_name[1]

    palette = get_palette(args.path, args.colors)
    # write_palette(palette, output_path)
    write_palette_to_source(sort_colors(palette), args.path, output_path)