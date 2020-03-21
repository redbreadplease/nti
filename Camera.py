from math import sqrt
from time import sleep

from PIL import Image, ImageFilter
from picamera import PiCamera

import RPi.GPIO as GPIO
import time
from math import sqrt


def get_artag_matrix(filename):
    thumbnail_width, thumbnail_height = 400, 400
    img_blur_b_w_contour = Image.open(filename).filter(ImageFilter.GaussianBlur(radius=3)).convert('L').point(
        lambda point_greyness: 0 if point_greyness < 128 else 255, '1')
    img_blur_b_w_contour.thumbnail((thumbnail_width, thumbnail_height))
    thumbnail_width, thumbnail_height = img_blur_b_w_contour.size
    img_blur_b_w_contour = img_blur_b_w_contour.load()
    colored_matrix_view = [[(lambda x: 1 if x == 0 else 0)(img_blur_b_w_contour[column, row]) for column in
                            range(thumbnail_width)] for row in range(thumbnail_height)]
    wave_value = 2
    for row in range(len(colored_matrix_view)):
        for column in range(len(colored_matrix_view[row])):
            if colored_matrix_view[row][column] == 1:
                stack = [[row, column]]
                while len(stack) > 0:
                    last_r, last_c = stack[-1]
                    colored_matrix_view[last_r][last_c] = wave_value
                    if last_r > 0 and colored_matrix_view[last_r - 1][last_c] != wave_value and \
                            colored_matrix_view[last_r - 1][last_c] != 0:
                        stack.append([last_r - 1, last_c])
                    elif last_c > 0 and colored_matrix_view[last_r][last_c - 1] != wave_value and \
                            colored_matrix_view[last_r][last_c - 1] != 0:
                        stack.append([last_r, last_c - 1])
                    elif last_r < len(colored_matrix_view) - 1 and colored_matrix_view[last_r + 1][last_c] \
                            != wave_value and colored_matrix_view[last_r + 1][last_c] != 0:
                        stack.append([last_r + 1, last_c])
                    elif last_c < len(colored_matrix_view[0]) - 1 and colored_matrix_view[last_r][last_c + 1] \
                            != wave_value and colored_matrix_view[last_r][last_c + 1] != 0:
                        stack.append([last_r, last_c + 1])
                    else:
                        stack.pop()
                wave_value += 1
    # each contains: left_top, left_bottom, right_bottom, right_top
    corners = [[] for _ in range(wave_value - 2)]
    corners_pseudo_dists = [[] for _ in range(wave_value - 2)]

    def get_pseudo_length(pixel1, pixel2):
        return (pixel1[0] - pixel2[0]) ** 2 + (pixel1[1] - pixel2[1]) ** 2

    for checking_wave in range(2, wave_value):
        for row in range(len(colored_matrix_view)):
            for column in range(len(colored_matrix_view[row])):
                if colored_matrix_view[row][column] == checking_wave:
                    if not corners[checking_wave - 3]:
                        corners[checking_wave - 3] = [[row, column] for _ in range(4)]
                        corners_pseudo_dists[checking_wave - 3] = [get_pseudo_length([row, column], [0, 0]),
                                                                   get_pseudo_length([row, column],
                                                                                     [len(colored_matrix_view), 0]),
                                                                   get_pseudo_length([row, column],
                                                                                     [len(colored_matrix_view),
                                                                                      len(colored_matrix_view[row])]),
                                                                   get_pseudo_length([row, column],
                                                                                     [0,
                                                                                      len(colored_matrix_view[row])])]
                    else:
                        if corners_pseudo_dists[checking_wave - 3][0] < get_pseudo_length([0, 0], [row, column]):
                            corners[checking_wave - 3][0] = [row, column]
                            corners_pseudo_dists[checking_wave - 3][0] = get_pseudo_length(
                                [0, 0], corners[checking_wave - 3][0])

                        if corners_pseudo_dists[checking_wave - 3][1] < get_pseudo_length(
                                [len(colored_matrix_view), 0], [row, column]):
                            corners[checking_wave - 3][1] = [row, column]
                            corners_pseudo_dists[checking_wave - 3][1] = get_pseudo_length(
                                [len(colored_matrix_view), 0], corners[checking_wave - 3][1])

                        if corners_pseudo_dists[checking_wave - 3][2] < get_pseudo_length(
                                [len(colored_matrix_view), len(colored_matrix_view[0])], [row, column]):
                            corners[checking_wave - 3][2] = [row, column]
                            corners_pseudo_dists[checking_wave - 3][2] = get_pseudo_length(
                                [len(colored_matrix_view), len(colored_matrix_view[0])], corners[checking_wave - 3][2])

                        if corners_pseudo_dists[checking_wave - 3][3] < get_pseudo_length(
                                [0, len(colored_matrix_view[0])], [row, column]):
                            corners[checking_wave - 3][3] = [row, column]
                            corners_pseudo_dists[checking_wave - 3][3] = get_pseudo_length(
                                [0, len(colored_matrix_view[0])], corners[checking_wave - 3][3])

    del corners_pseudo_dists

    print corners

    min_dist = 15

    def get_distance(point1, point2):
        return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    true_corners = []

    print corners

    for left_top, left_bottom, right_bottom, right_top in corners:
        if not (get_distance(left_top, left_bottom) < min_dist and get_distance(left_top, right_bottom) < min_dist
                and get_distance(left_top, right_top) < min_dist and get_distance(left_bottom, right_bottom) < min_dist
                and get_distance(left_bottom, right_top) < min_dist
                and get_distance(right_bottom, right_top) < min_dist):
            true_corners.append([left_top, left_bottom, right_bottom, right_top])

    corners = true_corners[:]

    del true_corners

    left_top, left_bottom, right_bottom, right_top = corners[0]

    def get_coordinates_in_relation(point1, point2, quotient1, quotient2):
        return [int(round((point1[0] * quotient1 + point2[0] * quotient2) / (quotient1 + quotient2))),
                int(round((point1[1] * quotient1 + point2[1] * quotient2) / (quotient1 + quotient2)))]

    checking1 = get_coordinates_in_relation(left_top, right_bottom, 3, 13)
    checking2 = get_coordinates_in_relation(right_bottom, left_top, 3, 13)
    checking3 = get_coordinates_in_relation(right_top, left_bottom, 3, 13)
    checking4 = get_coordinates_in_relation(left_bottom, right_top, 3, 13)

    temp1 = get_coordinates_in_relation(checking2, checking3, 4, 1)
    temp2 = get_coordinates_in_relation(checking2, checking3, 3, 2)
    temp3 = get_coordinates_in_relation(checking2, checking3, 2, 3)
    temp4 = get_coordinates_in_relation(checking2, checking3, 1, 4)
    temp5 = get_coordinates_in_relation(checking4, checking1, 4, 1)
    temp6 = get_coordinates_in_relation(checking4, checking1, 3, 2)
    temp7 = get_coordinates_in_relation(checking4, checking1, 2, 3)
    temp8 = get_coordinates_in_relation(checking4, checking1, 1, 4)

    un_bits_positions = [
        get_coordinates_in_relation(checking2, checking4, 4, 1),
        get_coordinates_in_relation(checking2, checking4, 3, 2),
        get_coordinates_in_relation(checking2, checking4, 2, 3),
        get_coordinates_in_relation(checking2, checking4, 1, 4),

        temp1,
        get_coordinates_in_relation(temp1, temp5, 4, 1),
        get_coordinates_in_relation(temp1, temp5, 3, 2),
        get_coordinates_in_relation(temp1, temp5, 2, 3),
        get_coordinates_in_relation(temp1, temp5, 1, 4),
        temp5,

        temp2,
        get_coordinates_in_relation(temp2, temp6, 4, 1),
        get_coordinates_in_relation(temp2, temp6, 3, 2),
        get_coordinates_in_relation(temp2, temp6, 2, 3),
        get_coordinates_in_relation(temp2, temp6, 1, 4),
        temp6,

        temp3,
        get_coordinates_in_relation(temp3, temp7, 4, 1),
        get_coordinates_in_relation(temp3, temp7, 3, 2),
        get_coordinates_in_relation(temp3, temp7, 2, 3),
        get_coordinates_in_relation(temp3, temp7, 1, 4),
        temp7,

        temp4,
        get_coordinates_in_relation(temp4, temp8, 4, 1),
        get_coordinates_in_relation(temp4, temp8, 3, 2),
        get_coordinates_in_relation(temp4, temp8, 2, 3),
        get_coordinates_in_relation(temp4, temp8, 1, 4),
        temp8,

        get_coordinates_in_relation(checking3, checking1, 4, 1),
        get_coordinates_in_relation(checking3, checking1, 3, 2),
        get_coordinates_in_relation(checking3, checking1, 2, 3),
        get_coordinates_in_relation(checking3, checking1, 1, 4)
    ]

    un_bits = []

    def is_there_white_color(img_matrix, row, column):
        pixels_amount = 0
        pixels_amount += img_matrix[row][column] == 0
        try:
            pixels_amount += 0 == img_matrix[row + 1][column]
        except IndexError:
            print "Out of"
        try:
            pixels_amount += 0 == img_matrix[row][column + 1]
        except IndexError:
            print "Out of"
        try:
            pixels_amount += 0 == img_matrix[row + 1][column]
        except IndexError:
            print "Out of"
        try:
            pixels_amount += 0 == img_matrix[row - 1][column]
        except IndexError:
            print "Out of"
        try:
            pixels_amount += 0 == img_matrix[row][column - 1]
        except IndexError:
            print "Out of"
        return pixels_amount > 2

    for i in range(len(un_bits_positions)):
        un_bits.append(1 * is_there_white_color(colored_matrix_view, un_bits_positions[i][0], un_bits_positions[i][1]))

    row = [[0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, un_bits[0], un_bits[1], un_bits[2], un_bits[3], 0, 0],
           [0, un_bits[4], un_bits[5], un_bits[6], un_bits[7], un_bits[8], un_bits[9], 0],
           [0, un_bits[10], un_bits[11], un_bits[12], un_bits[13], un_bits[14], un_bits[15], 0],
           [0, un_bits[16], un_bits[17], un_bits[18], un_bits[19], un_bits[20], un_bits[21], 0],
           [0, un_bits[22], un_bits[23], un_bits[24], un_bits[25], un_bits[26], un_bits[27], 0],
           [0, 0, un_bits[28], un_bits[29], un_bits[30], un_bits[31], 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0]]

    if is_there_white_color(colored_matrix_view, checking1[0], checking1[1]):
        return [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, un_bits[0], un_bits[1], un_bits[2], un_bits[3], 0, 0],
            [0, un_bits[4], un_bits[5], un_bits[6], un_bits[7], un_bits[8], un_bits[9], 0],
            [0, un_bits[10], un_bits[11], un_bits[12], un_bits[13], un_bits[14], un_bits[15], 0],
            [0, un_bits[16], un_bits[17], un_bits[18], un_bits[19], un_bits[20], un_bits[21], 0],
            [0, un_bits[22], un_bits[23], un_bits[24], un_bits[25], un_bits[26], un_bits[27], 0],
            [0, 0, un_bits[28], un_bits[29], un_bits[30], un_bits[31], 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    elif is_there_white_color(colored_matrix_view, checking2[0], checking2[1]):
        return [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, un_bits[31], un_bits[30], un_bits[29], un_bits[28], 0, 0],
            [0, un_bits[27], un_bits[26], un_bits[25], un_bits[24], un_bits[23], un_bits[22], 0],
            [0, un_bits[21], un_bits[20], un_bits[19], un_bits[18], un_bits[17], un_bits[16], 0],
            [0, un_bits[15], un_bits[14], un_bits[13], un_bits[12], un_bits[11], un_bits[10], 0],
            [0, un_bits[9], un_bits[8], un_bits[7], un_bits[6], un_bits[5], un_bits[4], 0],
            [0, 0, un_bits[3], un_bits[2], un_bits[1], un_bits[0], 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    elif is_there_white_color(colored_matrix_view, checking3[0], checking3[1]):
        return [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, un_bits[9], un_bits[15], un_bits[21], un_bits[27], 0, 0],
            [0, un_bits[3], un_bits[8], un_bits[14], un_bits[20], un_bits[26], un_bits[31], 0],
            [0, un_bits[2], un_bits[7], un_bits[13], un_bits[19], un_bits[25], un_bits[30], 0],
            [0, un_bits[1], un_bits[6], un_bits[12], un_bits[18], un_bits[24], un_bits[29], 0],
            [0, un_bits[0], un_bits[5], un_bits[11], un_bits[17], un_bits[23], un_bits[28], 0],
            [0, 0, un_bits[4], un_bits[10], un_bits[16], un_bits[22], 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    else:
        return [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, un_bits[22], un_bits[16], un_bits[10], un_bits[4], 0, 0],
            [0, un_bits[28], un_bits[23], un_bits[17], un_bits[11], un_bits[5], un_bits[0], 0],
            [0, un_bits[29], un_bits[24], un_bits[18], un_bits[12], un_bits[6], un_bits[1], 0],
            [0, un_bits[30], un_bits[25], un_bits[19], un_bits[13], un_bits[7], un_bits[2], 0],
            [0, un_bits[31], un_bits[26], un_bits[20], un_bits[14], un_bits[8], un_bits[3], 0],
            [0, 0, un_bits[27], un_bits[21], un_bits[15], un_bits[9], 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]


photo_name = 'cam_image.jpg'


def make_photo():
    camera = PiCamera()
    camera.start_preview()
    for i in range(1):
        print "Sleeping"
        sleep(2)
        print "Making photo"
        camera.capture('/home/pi/Temp/VL53L0X_rasp_python/python/' + photo_name)
    camera.stop_preview()
    sleep(0.5)


def get_ar_tag_decoding():
    make_photo()
    matrix = get_artag_matrix(photo_name)
    for row in matrix:
        print " ".join(map(str, row))
    return heming(matrix)


p = None


def init_cam_servo():
    global p
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)
    # GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    p = GPIO.PWM(26, 50)
    p.start(0)


def shut_down_servo():
    p.stop()
    GPIO.cleanup()


TURN_FRONT = 7
TURN_RIGHT = 2
TURN_LEFT = 11


def turn_left():
    global p
    p.ChangeDutyCycle(TURN_LEFT)
    time.sleep(0.5)


def turn_front():
    global p
    p.ChangeDutyCycle(TURN_FRONT)
    time.sleep(0.5)


def turn_right():
    global p
    p.ChangeDutyCycle(TURN_RIGHT)
    time.sleep(0.5)


artag = None


def set_artag(new_artag):
    global artag
    artag = new_artag[:]


def get_commands_from_ar_tag():
    binStr = artag_to_bin_str()
    print(binStr)
    analysedBinStr = analyse_bin_str(binStr)
    print(analysedBinStr)
    # print(get_commands_from_bin_str(binStr))
    return get_commands_from_bin_str(analysedBinStr)


def artag_to_bin_str():
    binnumber = ""
    for i in range(4):
        binnumber += str(artag[1][2 + i])
    for i in range(4):
        for j in range(6):
            binnumber += str(artag[2 + i][1 + j])
    for i in range(4):
        binnumber += str(artag[6][2 + i])
    return binnumber


def analyse_bin_str(string):
    numbersOfCheckBits = [0, 1, 3, 7, 15, 31]
    sum = -1
    for j in numbersOfCheckBits:
        # counter = -(int(string[j]))
        counter = 0
        # print(str(j) + "; " + str(counter) + "; ", end="")
        for i in range(j, len(string), (j + 1) * 2):
            #           print(min(j+1, len(string)-1))
            for k in range(0, j + 1):
                if i + k >= len(string):
                    break
                if (i + k) != j:
                    if string[i + k] == "1":
                        # print(str(i + k) + " ", end="")
                        counter -= -1
        if int(string[j]) != counter % 2:
            print("Fuck %d check bit is wrong" % j)
            sum += j + 1
        else:
            print("Okay %d check bit is good" % j)
    if sum == -1:
        print("Bin str is all ok")
        return string
    else:
        print("Boolshit %d bit is wrong" % sum)
        return string[0:sum] + str((int(string[sum]) + 1) % 2) + string[sum + 1:]


def get_commands_from_bin_str(string):
    commands = ""
    bits = list(range(len(string)))
    print(bits)
    del bits[31]
    del bits[15]
    del bits[7]
    del bits[3]
    del bits[1]
    del bits[0]
    print(bits)
    for i in range(0, len(bits), 2):
        print("i = " + str(i) + "; " + str(int(string[bits[i]])) + "; " + str(string[bits[i + 1]]))
        commands += str(int(string[bits[i]]) * 2 + int(string[bits[i + 1]])) + " "
    return commands

# make_photo()
# matrix = get_artag_matrix(photo_name)
# for _row in range(len(matrix)):
#    print " ".join(map(str, matrix[_row]))
# set_artag(matrix)
# print(get_commands_from_ar_tag())
