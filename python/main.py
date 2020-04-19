from typing import List

import cv2
import imutils
import numpy as np
from scipy.spatial import distance as dist


def find_dots(letter_pic):
    gray = cv2.cvtColor(letter_pic, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, h = cv2.findContours(thresh, 1, 2)
    big_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        if 10 < area < 1000:  # actually ~100
            big_contours.append(cnt)
    coordinates = []
    for cnt in big_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(thresh, (x, y), (x + w, y + h), (0, 0, 255), 1)
        coordinates.append((x + w / 2, y + h / 2))

    height, width, _ = letter_pic.shape
    coordinates = [(c[0] / width, c[1] / height) for c in coordinates]
    dots = []
    for coord in coordinates:
        dots.append(classify_dots(coord))
    dots.sort()

    return brl_to_rus(dots), thresh


def classify_dots(coord):
    col = 0 if coord[0] < 0.5 else 1
    if coord[1] < 11 / 30:
        row = 0
    elif coord[1] < 19 / 30:
        row = 1
    else:
        row = 2
    return row + 3 * col + 1  # dot number from 1 to 6


def brl_to_rus(brl: List[int]) -> str:
    if brl == [1]:
        return "а"
    elif brl == [1, 2]:
        return "б"
    elif brl == [2, 4, 5, 6]:
        return "в"
    elif brl == [1, 2, 4, 5]:
        return "г"
    elif brl == [1, 4, 5]:
        return "д"
    elif brl == [1, 5]:
        return "е"
    elif brl == [1, 6]:
        return "ё"
    elif brl == [2, 4, 5]:
        return "ж"
    elif brl == [1, 3, 5, 6]:
        return "з"
    elif brl == [2, 4]:
        return "и"
    elif brl == [1, 2, 3, 4, 6]:
        return "й"
    elif brl == [1, 3]:
        return "к"
    elif brl == [1, 2, 3]:
        return "л"
    elif brl == [1, 3, 4]:
        return "м"
    elif brl == [1, 3, 4, 5]:
        return "н"
    elif brl == [1, 3, 5]:
        return "о"
    elif brl == [1, 2, 3, 4]:
        return "п"
    elif brl == [1, 2, 3, 5]:
        return "р"
    elif brl == [2, 3, 4]:
        return "с"
    elif brl == [2, 3, 4, 5]:
        return "т"
    elif brl == [1, 3, 6]:
        return "у"
    elif brl == [1, 2, 4]:
        return "ф"
    elif brl == [1, 2, 5]:
        return "х"
    elif brl == [1, 4]:
        return "ц"
    elif brl == [1, 2, 3, 4, 5]:
        return "ч"
    elif brl == [1, 5, 6]:
        return "ш"
    elif brl == [1, 3, 4, 6]:
        return "щ"
    elif brl == [1, 2, 3, 5, 6]:
        return "ъ"
    elif brl == [2, 3, 4, 6]:
        return "ы"
    elif brl == [2, 3, 4, 5, 6]:
        return "ь"
    elif brl == [2, 4, 6]:
        return "э"
    elif brl == [1, 2, 5, 6]:
        return "ю"
    elif brl == [1, 2, 4, 6]:
        return "я"
    return ""


#


def find_pentagons(img):
    # Find pentagons on image

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 1)
    ret, thresh = cv2.threshold(blurred, 127, 255, 1)

    contours, h = cv2.findContours(thresh, 1, 2)

    big_contours = []
    displayed_pic = img.copy()

    for cnt in contours:
        # peri = cv2.arcLength(cnt, True)
        # approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        area = cv2.contourArea(cnt)
        if len(approx) == 5 and area > 100:
            big_contours.append(approx)
    print("Found {} contours.".format(len(big_contours)))
    return big_contours, displayed_pic


def get_odd(x):
    # Get odd number

    x = int(x)
    return x - 1 if x % 2 == 0 else x


def order_points(pts):
    # Order points: top-left, top-right, bottom-right, and bottom-left order

    x_sorted = pts[np.argsort(pts[:, 0]), :]
    left_most = x_sorted[:2, :]
    right_most = x_sorted[2:, :]
    left_most = left_most[np.argsort(left_most[:, 1]), :]
    (tl, bl) = left_most
    D = dist.cdist(tl[np.newaxis], right_most, "euclidean")[0]
    (br, tr) = right_most[np.argsort(D)[::-1], :]
    return np.array([tl, tr, br, bl], dtype="float32")


def get_warped_image(img, pts):
    # Get warped image by 4 points

    pts1 = order_points(pts)
    w1 = int(((pts1[0][0] - pts1[1][0]) ** 2 + (pts1[0][1] - pts1[1][1]) ** 2) ** 0.5)
    w2 = int(((pts1[2][0] - pts1[3][0]) ** 2 + (pts1[2][1] - pts1[3][1]) ** 2) ** 0.5)
    h1 = int(((pts1[0][0] - pts1[3][0]) ** 2 + (pts1[0][1] - pts1[3][1]) ** 2) ** 0.5)
    h2 = int(((pts1[1][0] - pts1[2][0]) ** 2 + (pts1[1][1] - pts1[2][1]) ** 2) ** 0.5)
    w = min(w1, w2)
    h = min(h1, h2)
    pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, matrix, (w, h))
    return warped


def get_min_indexes(contour):
    # Get indexes of two points with the smallest distance

    a = list(map(lambda x: np.array(x[0]), contour))
    a = np.array(a)
    idx = (0, 0)
    min_dist = 0
    for i in range(len(a) - 1):
        for j in range(i + 1, len(a)):
            ai = np.array([a[i]], dtype=np.int32)
            aj = np.array([a[j]], dtype=np.int32)
            distance = dist.cdist(ai, aj, "euclidean")
            if min_dist == 0 or min_dist > distance:
                min_dist = distance
                idx = (i, j)
    i, j = idx
    return i, j


def get_warped_tile(tile_image, contour):
    # Get image of warped tile
    # Rotated, actually

    a = list(map(lambda x: np.array(x[0]), contour))
    a = np.array(a)

    # Find the smallest pair
    i, j = get_min_indexes(contour)

    pnt1 = tuple(a[i])
    pnt2 = tuple(a[j])
    # Sort points for y coordinate
    if pnt1[1] > pnt2[1]:
        pnt1, pnt2 = pnt2, pnt1

    # Get the first point from a not including ith and jth elements
    pnt = a[0]
    for k in range(len(a)):
        if k not in (i, j):
            pnt = a[k]
            break

    # Check if the pnt above the line on pnt1 and pnt2
    # Lets get the pseudo scalar multiplication by the determinant
    a1, a2 = pnt[0] - pnt1[0], pnt[1] - pnt1[1]
    b1, b2 = pnt2[0] - pnt1[0], pnt2[1] - pnt1[1]
    # 1 means pnt above the line, 0 - below
    pnt_above = 1 if a1 * b2 - a2 * b1 < 0 else 0

    # Find out if the line increases
    increases = 1 if pnt1[0] > pnt2[0] else 0

    # Lets get an angle to rotate the image
    # print("increases: {}, pnt_above: {}".format(increases, pnt_above))
    angle = 0
    if increases:
        if pnt_above:
            angle = 180
    else:
        if pnt_above:
            angle = -90
        else:
            angle = 90

    # Get tile rect
    rect = cv2.minAreaRect(a)
    box = cv2.boxPoints(rect)

    # Rotate so that the top is parallel to the horizon
    tile_rect = get_warped_image(tile_image.copy(), box)

    # Rotate the tile rect at the angle
    rotated_tile_image = imutils.rotate_bound(tile_rect, angle)

    return rotated_tile_image


def get_warped_tiles(pentagon_contours, img_with_pentagons):
    # Get images of warped tiles

    tiles = []
    for contour in pentagon_contours:
        out = get_warped_tile(img_with_pentagons.copy(), contour)
        tiles.append(out)
    return tiles


def main():
    whole_img = cv2.imread('images/1b.JPG')
    # whole_img = imutils.rotate_bound(whole_img.copy(), 20)  # you can test rotation here
    whole_img = imutils.resize(whole_img, width=1500)
    pentagon_contours, img_with_pentagons = find_pentagons(whole_img)
    # Sort pentagons by x coordinate:
    sorted_contours = sorted(pentagon_contours,
                             key=lambda ctr: cv2.boundingRect(ctr)[0] + cv2.boundingRect(ctr)[1])
    tiles = get_warped_tiles(sorted_contours, img_with_pentagons)

    cropped_letters = tiles[:]
    classified = []
    for i in range(len(cropped_letters)):
        letter_pic = imutils.resize(cropped_letters[i], width=30)
        let, thresh = find_dots(letter_pic)
        cv2.imshow("Tile thresh #{}".format(i), thresh)
        classified.append((let, thresh))
        print("Letter #{} is {}".format(i, let))

    cv2.imshow("Whole image", whole_img)
    for i in range(len(tiles)):
        cv2.imshow("Tile #{}".format(i), tiles[i])
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
