import os
from typing import NewType, List, Optional, Tuple
from collections import defaultdict
from contextlib import contextmanager

import cv2 as cv
import imutils
from imutils import perspective
import numpy as np

import utils
from dots import BrailleDots, dots_to_chars


Image = NewType('Image', np.ndarray)
Contour = NewType('Contours', np.ndarray)
BoundingBox = NewType('BoundingBox', Tuple[int, int, int, int])


@contextmanager
def cd(path):
    if log:
        with utils.cd(path):
            yield
    else:
        yield


def save(filename: str, image: Image) -> None:
    if log:
        cv.imwrite(filename + '.png', image)


def detect_polygons(image: Image) -> List[Contour]:
    binary = cv.adaptiveThreshold(
        image,
        maxValue=255,
        adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=3,
        C=1,
    )
    save('binary', binary)

    opening = cv.morphologyEx(
        binary, op=cv.MORPH_OPEN,
        kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (2, 2))
    )
    save('opening', opening)

    contours, _ = cv.findContours(
        opening, mode=cv.RETR_LIST, method=cv.CHAIN_APPROX_SIMPLE
    )

    polygons = [cv.approxPolyDP(contour, epsilon=3, closed=True)
                for contour in contours
                if 1000 <= cv.contourArea(contour) <= 50000]
    polygons = [polygon for polygon in polygons if 5 <= len(polygon) <= 9]
    print(f'\tpolygons found: {len(polygons)}')

    contours_image = cv.drawContours(
        image, polygons,
        contourIdx=-1,  # Draw all
        color=255
    )
    save(f'contours', contours_image)

    return polygons


def get_warped_tile(image: Image, contour: Contour) -> Optional[Image]:
    contour = sorted(
        [(contour[i][0][0], contour[i][0][1])
         for i in range(len(contour))],
        key=sum
    )
    print(f'\tcontour = {contour}')

    bottom_right = contour[-1]
    top_left_top = min(contour[:2], key=lambda p: p[1])
    top_left_bottom = max(contour[:2], key=lambda p: p[1])
    top_left = (top_left_bottom[0], top_left_top[1])

    max_dim = max(image.shape)
    top_right = sorted(contour, key=lambda p: p[0] + max_dim - p[1])[-1]
    bottom_left = sorted(contour, key=lambda p: max_dim - p[0] + p[1])[-1]

    print(f'\t\ttop_left_top = {top_left_top}')
    print(f'\t\ttop_left_bottom = {top_left_bottom}')
    print(f'\t\tbottom_right = {bottom_right}')
    print(f'\t\ttop_right = {top_right}')
    print(f'\t\tbottom_left = {bottom_left}')

    warped = perspective.four_point_transform(
        image, np.array([top_left, top_right, bottom_right, bottom_left])
    )

    tile_width = 24  # millimeters
    tile_height = 30  # millimeters
    height = bottom_right[1] - top_right[1]
    width = bottom_right[0] - bottom_left[0]
    if abs(height / width - tile_height / tile_width) < 0.2:  # TODO подобрать коэф
        save(f'warped-{top_left}', warped)
        return warped
    return None


def bb_in_bb(checked: BoundingBox, reference: BoundingBox) -> bool:
    x, y, w, h = checked
    xx = x + w
    yy = y + h

    rx, ry, rw, rh = reference
    rxx = rx + rw
    ryy = ry + rh

    xs_in = rx <= x <= rxx and rx <= xx <= rxx
    ys_in = ry <= y <= ryy and ry <= yy <= ryy
    return xs_in and ys_in


def add_dot(dots: BrailleDots, bb: BoundingBox) -> BrailleDots:
    size = 18

    # Dots sides (left and right)
    s1 = 8
    s2 = 27

    # Dots levels
    l1 = 8
    l2 = 25
    l3 = 43

    rects = [
        ('d1', (s1, l1, s1 + size, l1 + size)),
        ('d2', (s1, l2, s1 + size, l2 + size)),
        ('d3', (s1, l3, s1 + size, l3 + size)),
        ('d4', (s2, l1, s2 + size, l1 + size)),
        ('d5', (s2, l2, s2 + size, l2 + size)),
        ('d6', (s2, l3, s2 + size, l3 + size)),
    ]
    for dot, rect in rects:
        if bb_in_bb(bb, rect):
            return dots.copy(**{dot: True})
    return dots


def detect_dots(tile: Image) -> BrailleDots:
    resized = imutils.resize(tile, width=50)
    save('resized', resized)

    binary = cv.adaptiveThreshold(
        resized,
        maxValue=255,
        adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=13,
        C=20,
    )
    save('binary', binary)

    closing = cv.morphologyEx(
        binary, op=cv.MORPH_CLOSE,
        kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    )
    save('closing', closing)

    contours, _ = cv.findContours(
        closing, mode=cv.RETR_LIST, method=cv.CHAIN_APPROX_SIMPLE
    )

    dots = BrailleDots()
    for contour in contours:
        dots = add_dot(dots, cv.boundingRect(contour))

    return dots


def run(image: Image) -> None:
    save('source', image)

    with cd('preprocessing'):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        save('gray', gray)

        blurred = cv.GaussianBlur(
            gray, ksize=(9, 9), sigmaX=1, borderType=cv.BORDER_REFLECT
        )
        save('blurred', blurred)

    with cd('detection'):
        polygons = detect_polygons(blurred)

    with cd('warping'):
        tiles = [get_warped_tile(gray, polygon) for polygon in polygons]
        tiles = [tile for tile in tiles if tile is not None]

    with cd('classification'):
        d = defaultdict(list)
        for i, tile in enumerate(tiles):
            with cd(str(i)):
                dots = detect_dots(tile)
                d[dots].append(tile)

    with cd('result'):
        for dots, tiles in d.items():
            c = dots_to_chars.get(dots)
            if c is None:
                continue
            for i, tile in enumerate(tiles):
                cv.imwrite(f'{str(c)}-{dots}-{str(i)}.png', tile)


def main():
    images_path = 'images'
    out_path = 'out'

    for root, _, filenames in os.walk(images_path):
        for filename in filenames:
            print(f'In progress: {filename}')

            image = cv.imread(os.path.join(root, filename))
            if image is None:
                continue

            path = os.path.join(out_path, filename)
            with utils.cd(utils.remove_file_extension(path)):
                run(image)

    print('Done!')


if __name__ == '__main__':
    log = True
    main()
else:
    raise RuntimeError('I am main!')
