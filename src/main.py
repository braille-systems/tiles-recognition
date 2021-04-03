import os
import argparse
from typing import NewType, List, Optional
from contextlib import contextmanager
from itertools import count

import cv2 as cv
import numpy as np
import imutils
from imutils import perspective

import utils
from dots import BrailleDots, dots_to_chars
from defs import Image, Contour, Point, BoundingBox


@contextmanager
def cd(path):
    if LOG:
        with utils.cd(path):
            yield
    else:
        yield


def save(filename: str, image: Image) -> None:
    if LOG:
        cv.imwrite(f'{filename}-{IMAGE_NAME}.png', image)


def are_dups(polygon1: Contour, polygon2: Contour) -> bool:
    c1 = utils.centroid(polygon1)
    c2 = utils.centroid(polygon2)
    return utils.distance(c1, c2) <= 30


def filter_dup_polygons(polygons: List[Contour]) -> List[Contour]:
    clusters = []
    copy = list(polygons)
    while copy:
        p1 = copy[0]
        del copy[0]
        cluster = [p1]
        for i, p2 in zip(count(len(copy) - 1, step=-1), copy[::-1]):
            if are_dups(p1, p2):
                cluster.append(p2)
                del copy[i]
        clusters.append(cluster)

    def key(polygon):
        return cv.contourArea(polygon), -utils.n_vertices(polygon)

    return [min(cluster, key=key) for cluster in clusters]


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
        blockSize=11,
        C=2,
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

    copy = image.copy()

    polygons = [
        cv.approxPolyDP(
            contour,
            epsilon=0.01 * cv.arcLength(contour, closed=True),
            closed=True
        )
        for contour in contours
        if 1000 <= cv.contourArea(contour)
    ]
    polygons = [
        polygon for polygon in polygons
        if 5 <= utils.n_vertices(polygon) <= 9 and cv.isContourConvex(polygon)
    ]
    for polygon in polygons:
        cv.circle(
            copy,
            utils.centroid(polygon),
            radius=0,
            color=(0, 0, 255),
            thickness=2,
        )
    polygons = filter_dup_polygons(polygons)
    print(f'\tpolygons found: {len(polygons)}')

    cv.drawContours(
        copy, polygons,
        contourIdx=-1,  # Draw all
        color=(0, 0, 255)  # BGR
    )

    save(f'contours', copy)

    return polygons


def get_warped_tile(image: Image, contour: Contour) -> Optional[Image]:
    contour = sorted(
        [(contour[i][0][0], contour[i][0][1])
         for i in range(len(contour))],
        key=sum
    )
    if LOGLOG:
        print(f'\tcontour = {contour}')

    bottom_right = contour[-1]
    top_left_top = min(contour[:2], key=lambda p: p[1])
    top_left_bottom = max(contour[:2], key=lambda p: p[1])
    top_left = (top_left_bottom[0], top_left_top[1])

    max_dim = max(image.shape)
    top_right = sorted(contour, key=lambda p: p[0] + max_dim - p[1])[-1]
    bottom_left = sorted(contour, key=lambda p: max_dim - p[0] + p[1])[-1]

    if LOGLOG:
        print(f'\t\ttop_left_top = {top_left_top}')
        print(f'\t\ttop_left_bottom = {top_left_bottom}')
        print(f'\t\tbottom_right = {bottom_right}')
        print(f'\t\ttop_right = {top_right}')
        print(f'\t\tbottom_left = {bottom_left}')

    warped = perspective.four_point_transform(
        image, np.array([top_left, top_right, bottom_right, bottom_left])
    )

    # Origin tile has 24mm width and 30mm height
    height = utils.distance(bottom_right, top_right)
    width = utils.distance(bottom_right, bottom_left)
    if width != 0 and 0.8 <= height / width <= 40 / 24:
        save(f'warped-{top_left}', warped)
        return warped
    return None


def add_dot(dots: BrailleDots, tile: Image, bb: BoundingBox) -> BrailleDots:
    x, y, w, h = bb
    tile_height, tile_width, _ = tile.shape

    d = 10
    # Dots sides (left and right)
    s1 = 1 / 3
    s2 = 2 / 3
    # Dots levels
    l1 = 1 / 4
    l2 = 2 / 4
    l3 = 3 / 4

    rects = [
        (int(s * tile_width - d), int(l * tile_height - d), 2 * d, 2 * d)
        for s, l in [
            (s1, l1), (s1, l2), (s1, l3),
            (s2, l1), (s2, l2), (s2, l3),
        ]
    ]
    for i, rect in enumerate(rects, start=1):
        if utils.dot_in_bb((x + w // 2, y + h // 2), rect):
            return dots.copy(**{f'd{i}': True})
    return dots


def detect_dots(tile: Image, i_tile: int) -> BrailleDots:
    with cd('sources'):
        resized = imutils.resize(tile, width=70)
        save(f'source-{i_tile}', resized)

    gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)

    with cd('binary'):
        binary = cv.adaptiveThreshold(
            gray,
            maxValue=255,
            adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv.THRESH_BINARY,
            blockSize=11,
            C=2,
        )
        save(f'binary-{i_tile}', binary)

    with cd('closing'):
        closing = cv.morphologyEx(
            binary, op=cv.MORPH_CLOSE,
            kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
        )
        save(f'closing-{i_tile}', closing)

    with cd('bbs'):
        contours, _ = cv.findContours(
            closing, mode=cv.RETR_LIST, method=cv.CHAIN_APPROX_SIMPLE
        )

        copy = closing.copy()
        dots = BrailleDots()
        for contour in contours:
            bb = cv.boundingRect(contour)
            x, y, w, h = bb
            if w <= 12 or h <= 12 or 37 <= w or 37 <= h:
                continue
            dots = add_dot(dots, resized, bb)
            cv.rectangle(copy, (x, y), (x + w - 2, y + h - 2), color=(100, 100, 100))
        save(f'bbs-{i_tile}', copy)

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
            color=(0, 255, 0)  # BGR
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
            dots = detect_dots(tile, i)
            c = dots_to_chars.get(dots)

            x, y, w, h = bb
            scale = 0.35
            color = (255, 255, 100)
            cv.putText(
                result, f'{i}: {str(c)}',
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

    return result


def run(images_path: str) -> None:
    out_path = 'out'

    for root, _, filenames in os.walk(images_path):
        for filename in filenames:
            print(f'In progress: {filename}')

            image = cv.imread(os.path.join(root, filename))
            if image is None:
                continue

            no_ext = utils.remove_file_extension(filename)

            global IMAGE_NAME
            IMAGE_NAME = no_ext

            image = imutils.resize(image, width=1000)
            with utils.cd(out_path):
                save('source', image)
                result = process(image)
                name = f'result-{IMAGE_NAME}' if LOG else no_ext
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
        '-vv', '--vverbose', action='store_true',
        help='makes algorithm work more verbose then verbose',
    )
    parser.add_argument(
        'path', type=str,
        help='images path to run algorithm on',
        default='images'
    )
    args = parser.parse_args()
    if args.verbose or args.vverbose:
        global LOG
        LOG = True
    if args.vverbose:
        global LOGLOG
        LOGLOG = True

    run(args.path)


if __name__ == '__main__':
    LOG = False
    LOGLOG = False
    IMAGE_NAME = None
    main()
