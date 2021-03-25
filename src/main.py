import os
import argparse
from typing import NewType, List, Optional, Tuple
from contextlib import contextmanager

import cv2 as cv
import imutils
from imutils import perspective
import numpy as np

import utils
from dots import BrailleDots, dots_to_chars
from defs import Point, BoundingBox


Image = NewType('Image', np.ndarray)
Contour = NewType('Contours', np.ndarray)


@contextmanager
def cd(path):
    if LOG:
        with utils.cd(path):
            yield
    else:
        yield


def save(filename: str, image: Image) -> None:
    if LOG:
        cv.imwrite(filename + '.png', image)


def detect_polygons(image: Image) -> List[Contour]:
    """Return contours of all tile-like polygons"""

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    blurred = cv.GaussianBlur(
        gray, ksize=(9, 9), sigmaX=1, borderType=cv.BORDER_REFLECT
    )
    save('blurred', blurred)

    binary = cv.adaptiveThreshold(
        blurred,
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

    contours_image = image.copy()
    cv.drawContours(
        contours_image, polygons,
        contourIdx=-1,  # Draw all
        color=(0, 0, 255)  # BGR
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
    height = utils.distance(bottom_right, top_right)
    width = utils.distance(bottom_right, bottom_left)
    if width != 0 and abs(height / width - tile_height / tile_width) < 0.6:
        save(f'warped-{top_left}', warped)
        return warped
    return None


def add_dot(dots: BrailleDots, bb: BoundingBox) -> BrailleDots:
    size = 18

    # Dots sides (left and right)
    s1 = 8
    s2 = 24

    # Dots levels
    l1 = 8
    l2 = 25
    l3 = 43

    rects = [
        ('d1', (s1, l1, size, size)),
        ('d2', (s1, l2, size, size)),
        ('d3', (s1, l3, size, size)),
        ('d4', (s2, l1, size, size)),
        ('d5', (s2, l2, size, size)),
        ('d6', (s2, l3, size, size)),
    ]
    for dot, rect in rects:
        if utils.bb_in_bb(bb, rect):
            return dots.copy(**{dot: True})
    return dots


def detect_dots(tile: Image) -> BrailleDots:
    resized = imutils.resize(tile, width=50)
    gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)

    binary = cv.adaptiveThreshold(
        gray,
        maxValue=255,
        adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=13,
        C=20,
    )
    save('binary', binary)

    # Alternative approach is not to close and set area threshold
    closing = cv.morphologyEx(
        binary, op=cv.MORPH_CLOSE,
        kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    )
    save('closing', closing)

    contours, _ = cv.findContours(
        closing, mode=cv.RETR_LIST, method=cv.CHAIN_APPROX_SIMPLE
    )

    dots = BrailleDots()
    copy = closing.copy()
    for contour in contours:
        bb = cv.boundingRect(contour)
        dots = add_dot(dots, bb)
        x, y, w, h = bb
        cv.rectangle(copy, (x, y), (x + w, y + h), color=(100, 100, 100))
    save('bbs', copy)

    return dots


def process(image: Image) -> Image:
    result = image.copy()

    with cd('detection'):
        polygons = sorted(
            detect_polygons(image),
            key=lambda contour: cv.boundingRect(contour)[0]
        )
        cv.drawContours(
            result, polygons,
            contourIdx=-1,  # Draw all
            color=(0, 0, 255)  # BGR
        )

    with cd('warping'):
        tiles = []
        tile_bbs = []
        for polygon in polygons:
            tile = get_warped_tile(image, polygon)
            bb = cv.boundingRect(polygon)
            if tile is not None:
                tiles.append(tile)
                tile_bbs.append(bb)

            x, y, _, h = bb
            cv.putText(
                result, 'X',
                org=(x + 4, y + 10),
                fontFace=cv.FONT_HERSHEY_COMPLEX,
                fontScale=0.4,
                color=(255, 100, 0),
                thickness=1
            )

    with cd('dotification'):
        for i, (tile, bb) in enumerate(zip(tiles, tile_bbs)):
            with cd(f'tile-{i}'):
                dots = detect_dots(tile)
                c = dots_to_chars.get(dots)
                save(f'{str(c)}-{dots}.png', tile)

            if c is not None:
                x, y, w, h = bb
                scale = 0.35
                color = (255, 255, 100)
                cv.putText(
                    result, f'{i}: {c}',
                    org=(x, y + h + 15),
                    fontFace=cv.FONT_HERSHEY_COMPLEX,
                    fontScale=scale,
                    color=color,
                    thickness=0
                )
                cv.putText(
                    result, str(dots),
                    org=(x, y + h + 30),
                    fontFace=cv.FONT_HERSHEY_COMPLEX,
                    fontScale=scale,
                    color=color,
                    thickness=0
                )
                cv.rectangle(
                    result, (x, y), (x + w, y + h),
                    color=(0, 255, 0), thickness=1
                )

    return result


def run(images_path: str):
    out_path = 'out'

    for root, _, filenames in os.walk(images_path):
        for filename in filenames:
            print(f'In progress: {filename}')

            image = cv.imread(os.path.join(root, filename))
            if image is None:
                continue

            no_ext = utils.remove_file_extension(filename)
            with utils.cd(out_path):
                with cd(f'image-{no_ext}'):
                    save('source', image)
                    result = process(image)
                    name = 'result' if LOG else no_ext
                    cv.imwrite(name + '.png', result)

    print('Done!')


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""This utility takes png or jpg photos,
        detects Braille Tiles and classifies them as cyrillic letters.
        """
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='makes algorithm work verbose',
    )
    parser.add_argument(
        'path', type=str,
        help='images path to run algorithm on',
        default='images'
    )
    args = parser.parse_args()
    if args.verbose:
        global LOG
        LOG = True
    run(args.path)


if __name__ == '__main__':
    LOG = False
    main()
