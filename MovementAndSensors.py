import serial

import time

import RPi.GPIO as GPIO
import VL53L0X

from Config import *


def shut_down():
    global sensors_pins_and_sensors
    for sensor_id, sensor_tof in sensors_pins_and_sensors:
        sensor_tof.stop_ranging()
        time.sleep(0.5)
        GPIO.output(sensor_id, GPIO.HIGH)


def print_all_sensors():
    print("fr: ", sensor_front_r.get_distance(),
          "rf: ", sensor_right_f.get_distance(),
          "rb: ", sensor_right_b.get_distance(),
          "br: ", sensor_back_r.get_distance(),
          "bl: ", sensor_back_l.get_distance(),
          "lb: ", sensor_left_b.get_distance(),
          "lf: ", sensor_left_f.get_distance(),
          "fl: ", sensor_front_l.get_distance())


sensor_front_r_pin, sensor_front_l_pin = 13, 11
sensor_left_f_pin, sensor_left_b_pin = 5, 27
sensor_back_r_pin, sensor_back_l_pin = 17, 9
sensor_right_f_pin, sensor_right_b_pin = 12, 18

sensor_front_r, sensor_front_l = None, None
sensor_left_f, sensor_left_b = None, None
sensor_back_r, sensor_back_l = None, None
sensor_right_f, sensor_right_b = None, None

sensors_pins_and_sensors = [[sensor_right_f_pin, sensor_right_f], [sensor_right_b_pin, sensor_right_b],
                            [sensor_left_f_pin, sensor_left_f], [sensor_left_b_pin, sensor_left_b],
                            [sensor_front_r_pin, sensor_front_r], [sensor_front_l_pin, sensor_front_l],
                            [sensor_back_r_pin, sensor_back_r], [sensor_back_l_pin, sensor_back_l]]


def init_sensors():
    global sensors_pins_and_sensors, sensor_front_r, sensor_front_l, sensor_left_f, sensor_left_b, sensor_back_r, \
        sensor_back_l, sensor_right_f, sensor_right_b

    sensor_front_r, sensor_front_l = VL53L0X.VL53L0X(address=0x2A), VL53L0X.VL53L0X(address=0x2B)
    sensor_left_f, sensor_left_b = VL53L0X.VL53L0X(address=0x2C), VL53L0X.VL53L0X(address=0x2D)
    sensor_back_r, sensor_back_l = VL53L0X.VL53L0X(address=0x2E), VL53L0X.VL53L0X(address=0x2F)
    sensor_right_f, sensor_right_b = VL53L0X.VL53L0X(address=0x4A), VL53L0X.VL53L0X(address=0x4F)

    sensors_pins_and_sensors = [[sensor_right_f_pin, sensor_right_f], [sensor_right_b_pin, sensor_right_b],
                                [sensor_left_f_pin, sensor_left_f], [sensor_left_b_pin, sensor_left_b],
                                [sensor_front_r_pin, sensor_front_r], [sensor_front_l_pin, sensor_front_l],
                                [sensor_back_r_pin, sensor_back_r], [sensor_back_l_pin, sensor_back_l]]

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for sensor_pin, _ in sensors_pins_and_sensors:
        GPIO.setup(sensor_pin, GPIO.OUT)
        GPIO.output(sensor_pin, GPIO.LOW)
    time.sleep(0.5)
    for sensor_pin, sensor_sensor in sensors_pins_and_sensors:
        GPIO.output(sensor_pin, GPIO.HIGH)
        time.sleep(0.5)
        sensor_sensor.start_ranging(4)
    time.sleep(0.5)
    timing = sensor_front_r.get_timing()
    if timing < 20000:
        timing = 20000
    print("timing %d ms" % (timing / 1000))


def is_wall(d1, d2):
    return (d1 + d2) / 2. < 240 and d1 < 240 and d2 < 240 and abs(d1 - d2) < 100


def is_wall_by_one_sensor(d):
    return d < 300


def is_wall_front():
    return is_wall(sensor_front_l.get_distance(), sensor_front_r.get_distance())


def is_wall_left():
    return is_wall(sensor_left_b.get_distance(), sensor_left_f.get_distance())


def is_wall_back():
    return is_wall(sensor_back_l.get_distance(), sensor_back_r.get_distance())


def is_wall_right():
    return is_wall(sensor_right_b.get_distance(), sensor_right_f.get_distance())


def is_wall_for_stop(d1, d2):
    return (d1 + d2) / 2. < 120 and d1 < 140 and d2 < 140


def is_wall_front_for_stop():
    return is_wall_for_stop(sensor_front_l.get_distance(), sensor_front_r.get_distance())


def is_wall_left_for_stop():
    return is_wall_for_stop(sensor_left_b.get_distance(), sensor_left_f.get_distance())


def is_wall_back_for_stop():
    return is_wall_for_stop(sensor_back_l.get_distance(), sensor_back_r.get_distance())


def is_wall_right_for_stop():
    return is_wall_for_stop(sensor_right_b.get_distance(), sensor_right_f.get_distance())


ser = serial.Serial("/dev/ttyS0", 9600, timeout=5)


def move_clockwise(val):
    val = min(max_round_move_val, max(min_round_move_val, val))
    signal_to_move(0, 0, val, 0, val, val, 0, val)


def move_counterclockwise(val):
    val = min(max_round_move_val, max(min_round_move_val, val))
    signal_to_move(val, val, 0, val, 0, 0, val, 0)


def move_back(val):
    val = min(max_progressive_move_val, max(min_progressive_move_val, val))
    signal_to_move(val + (50 if robot_hostname == server_robot_hostname else 0), 0,
                   val + (0 if robot_hostname == server_robot_hostname else 0), 0, val, 0, val, 0)


def move_right(val):
    val = min(max_sideways_move_val, max(min_sideways_move_val, val))
    signal_to_move(val, val, 0, 0, val, val, 0, 0)


def move_straight(val):
    val = min(max_progressive_move_val, max(min_progressive_move_val, val))
    signal_to_move(0, val, 0, val + (50 if robot_hostname == server_robot_hostname else 0), 0,
                   val + (50 if robot_hostname == server_robot_hostname else 0), 0, val)


def move_left(val):
    val = min(max_sideways_move_val, max(min_sideways_move_val, val))
    signal_to_move(0, 0, val, val, 0, 0, val, val)


def stop_move():
    signal_to_move(0, 0, 0, 0, 0, 0, 0, 0)


def signal_to_move(a1, a2, b1, b2, c1, c2, d1, d2):
    ser.write(str(int(a1)) + "q" + str(int(a2)) + "w" + str(int(b1)) + "e" + str(int(b2)) + "r" +
              str(int(c1)) + "t" + str(int(c2)) + "y" + str(int(d1)) + "u" + str(int(d2)) + "i")


def do_round_align(get_first_dist, get_second_dist):
    sum_err, good = 0, 0
    while good < 8:
        d1, d2 = get_first_dist(), get_second_dist()
        err = (d1 - d2) * kp_round_align + sum_err * ki_round_align
        sum_err += err
        if err > 0:
            move_counterclockwise(err)
        else:
            move_clockwise(err)
        if abs(d1 - d2) < round_align_deviation:
            good += 1
            sum_err = 0
        else:
            good = 0


def do_round_align_by_(code):
    if code == 0:
        print "do_round_align_by_0"
        do_round_align(sensor_front_r.get_distance, sensor_front_l.get_distance)
    elif code == 1:
        print "do_round_align_by_1"
        do_round_align(sensor_left_f.get_distance, sensor_left_b.get_distance)
    elif code == 2:
        print "do_round_align_by_2"
        do_round_align(sensor_back_l.get_distance, sensor_back_r.get_distance)
    elif code == 3:
        print "do_round_align_by_3"
        do_round_align(sensor_right_b.get_distance, sensor_right_f.get_distance)
    stop_move()


def do_progressive_align(get_first_dist, get_second_dist, kp, ki, right_dist_to_wall, move_to_wall, move_from_wall):
    good, sum_err = 0, 0
    while good < 8:
        d1, d2 = get_first_dist(), get_second_dist()
        err = ((get_first_dist() + get_second_dist()) // 2 - right_dist_to_wall) * kp + sum_err * ki
        sum_err = sum_err + err
        if err > 0:
            move_to_wall(err)
        else:
            move_from_wall(err)

        if abs(d1 + d2) / 2 - right_dist_to_wall < align_wall_deviation:
            good += 1
            sum_err = 0
        else:
            good = 0


def do_progressive_align_by_(code):
    if code == 0:
        print "do_progressive_align_by_0"
        do_progressive_align(sensor_front_r.get_distance, sensor_front_l.get_distance, kp_progressive_align,
                             ki_progressive_align, right_straight_from_wall_dist, move_straight, move_back)
    elif code == 1:
        print "do_progressive_align_by_1"
        do_progressive_align(sensor_left_f.get_distance, sensor_left_b.get_distance, kp_round_align,
                             ki_round_align, right_sideways_from_wall_dist, move_left, move_right)
    elif code == 2:
        print "do_progressive_align_by_2"
        do_progressive_align(sensor_back_r.get_distance, sensor_back_l.get_distance, kp_progressive_align,
                             ki_progressive_align, right_straight_from_wall_dist, move_back, move_straight)
    elif code == 3:
        print "do_progressive_align_by_3"
        do_progressive_align(sensor_right_f.get_distance, sensor_right_b.get_distance, kp_round_align,
                             ki_round_align, right_sideways_from_wall_dist, move_right, move_left)


def do_align(get_first_dist, get_second_dist, move_to_wall, move_from_wall, moving_sideways, right_from_wall_dist):
    while True:
        d1, d2 = get_first_dist(), get_second_dist()
        print("d1: " + str(d1) + "  d2: " + str(d2))
        circle_err = max(min_round_move_val, min(max_round_move_val, abs(d1 - d2) * p_coef))
        if d1 - d2 > min_sensors_round_diff:
            move_counterclockwise(circle_err)
        elif d2 - d1 > min_sensors_round_diff:
            move_clockwise(circle_err)
        else:
            mid_dist = (d1 + d2) / 2.
            progressive_err = max(
                min_progressive_move_val * (not moving_sideways) + min_sideways_move_val * moving_sideways,
                min(max_progressive_move_val * (not moving_sideways) + max_sideways_move_val * moving_sideways,
                    abs(mid_dist - right_from_wall_dist) * p_coef))
            if mid_dist - right_from_wall_dist > align_wall_deviation:
                move_to_wall(progressive_err)
            elif right_from_wall_dist - mid_dist > align_wall_deviation:
                move_from_wall(progressive_err)
            else:
                stop_move()
                return


def do_front_align():
    do_align(sensor_front_r.get_distance, sensor_front_l.get_distance, move_straight, move_back, False,
             right_straight_from_wall_dist)


def do_left_align():
    do_align(sensor_left_f.get_distance, sensor_left_b.get_distance, move_left, move_right, True,
             right_sideways_from_wall_dist)


def do_back_align():
    do_align(sensor_back_l.get_distance, sensor_back_r.get_distance, move_back, move_straight, False,
             right_straight_from_wall_dist)


def do_right_align():
    do_align(sensor_right_b.get_distance, sensor_right_f.get_distance, move_right, move_left, True,
             right_sideways_from_wall_dist)


def drive_one_cell(right_optical_flow_distance, direction):
    _ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1
    )
    while True:
        a = _ser.read()
        if a == "y":
            break
    old_x, old_y = "", ""
    while True:
        a = _ser.read()
        if a != "x":
            old_x += a
        else:
            break
    while True:
        a = _ser.read()
        if a != "y":
            old_y += a
        else:
            break
    err = right_optical_flow_distance
    while True:
        print("err: " + str(err))
        x, y = "", ""
        while True:
            a = _ser.read()
            if a != "x":
                x = x + a
            else:
                break
        while True:
            a = _ser.read()
            if a != "y":
                y = y + a
            else:
                break
        if direction == 0:
            if is_wall_front_for_stop() or abs(
                    right_optical_flow_distance - int(x) + int(old_x)) < optical_flow_deviation:
                stop_move()
                break
            print "drive one cell straight"
            err = max(min_progressive_move_val,
                      min(max_progressive_move_val, abs(right_optical_flow_distance - int(x) + int(old_x))))
            move_straight(err)

        elif direction == 2:
            if is_wall_back_for_stop() or abs(
                    right_optical_flow_distance - int(x) + int(old_x)) < optical_flow_deviation:
                stop_move()
                break
            print "drive one cell back"
            print "err: " + str(right_optical_flow_distance - int(x) + int(old_x))
            err = max(min_progressive_move_val,
                      min(max_progressive_move_val, abs(right_optical_flow_distance - int(x) + int(old_x))))
            move_back(err)

        elif direction == 1:
            if is_wall_left_for_stop() or abs(-optical_flow_sideways_cell_size - int(y) + int(
                    old_y)) < optical_flow_deviation:
                stop_move()
                break
            err = min(max_sideways_move_val,
                      max(min_sideways_move_val, abs(-optical_flow_sideways_cell_size - int(y) + int(old_y))))
            print(err)
            d1 = sensor_front_l.get_distance()
            d2 = sensor_front_r.get_distance()
            v = 350
            print(d1)
            print(d2)
            print("---")
            prov = 0
            if (d1 < 200) and (d2 < 200) and (abs(d1 - d2) < 150):
                prov = 1
                err2 = (d1 - d2) * 10
                print("err2 " + str(err2))
                if (abs(err2 / 10) < 10):
                    err2 = 0
                    err3 = ((d1 + d2) / 2 - right_straight_from_wall_dist)
                    print("err3 " + str(err3))
                    if abs(err3) > 15:
                        if err3 < 0:
                            ser.write("0q0w400e0r0t0y400u0i")  # up
                        else:
                            ser.write("0q0w0e400r0t0y0u400i")  # down
                    else:
                        if err2 > 40:
                            err2 = 40
                        if err2 < -40:
                            err2 = -40
                        print("errrrrrrrrr")
                        ser.write("0q0w" + str(abs(v) + err2) + "e" + str(abs(v) - err2) + "r0t0y" + str(
                            abs(v) - err2) + "u" + str(abs(v) + err2) + "i")

                else:
                    if err2 > 40:
                        err2 = 40
                    if err2 < -40:
                        err2 = -40
                    print("errrrrrrrrr")
                    ser.write("0q0w" + str(abs(v) + err2) + "e" + str(abs(v) - err2) + "r0t0y" + str(
                        abs(v) - err2) + "u" + str(abs(v) + err2) + "i")
            d1 = sensor_back_r.get_distance()
            d2 = sensor_back_l.get_distance()
            v = 350
            print(d1)
            print(d2)
            print("---")
            if (prov == 0) and (d1 < 200) and (d2 < 200) and (abs(d1 - d2) < 150):
                err2 = (d1 - d2) * 10
                print("err2 " + str(err2))
                if (abs(err2 / 10) < 10):
                    err2 = 0
                    err3 = ((d1 + d2) / 2 - right_straight_from_wall_dist)
                    print("err3 " + str(err3))
                    if abs(err3) > 15:
                        if err3 < 0:
                            ser.write("0q0w0e400r0t0y0u400i")  # down

                        else:
                            ser.write("0q0w400e0r0t0y400u0i")  # up
                    else:
                        if err2 > 40:
                            err2 = 40
                        if err2 < -40:
                            err2 = -40
                        print("errrrrrrrrr")
                        ser.write("0q0w" + str(abs(v) + err2) + "e" + str(abs(v) - err2) + "r0t0y" + str(
                            abs(v) - err2) + "u" + str(abs(v) + err2) + "i")
                else:
                    if err2 > 40:
                        err2 = 40
                    if err2 < -40:
                        err2 = -40
                    print("errrrrrrrrr")
                    ser.write("0q0w" + str(abs(v) + err2) + "e" + str(abs(v) - err2) + "r0t0y" + str(
                        abs(v) - err2) + "u" + str(abs(v) + err2) + "i")
            else:
                move_left(err)
        elif direction == 3:
            if is_wall_right_for_stop() or optical_flow_sideways_cell_size - int(y) + int(
                    old_y) < optical_flow_deviation:
                stop_move()
                break
            err = min(max_sideways_move_val,
                      max(min_sideways_move_val, abs(optical_flow_sideways_cell_size - int(y) + int(old_y))))
            if err > 350:
                err = 350
            d1 = sensor_front_l.get_distance()
            d2 = sensor_front_r.get_distance()
            v = err
            prov = 0
            if (d1 < 200) and (d2 < 200) and (abs(d1 - d2) < 150):
                prov = 1
                err2 = (d1 - d2) * 10
                print("err2 " + str(err2))
                if (abs(err2 / 10) < 10):
                    err2 = 0
                    err3 = ((d1 + d2) / 2 - right_straight_from_wall_dist)
                    print("err3 " + str(err3))
                    if abs(err3) > 15:
                        if err3 < 0:
                            ser.write("400q0w0e0r400t0y0u0i")  # down
                        else:
                            ser.write("0q400w0e0r0t400y0u0i")  # up
                    else:
                        if err2 > 40:
                            err2 = 40
                        ser.write(str(abs(v) - err2) + "q" + str(abs(v) - err2) + "w0e0r" + str(
                            abs(v) + err2) + "t" + str(abs(v) + err2) + "y0u0i")

                else:
                    if err2 > 40:
                        err2 = 40
                    ser.write(
                        str(abs(v) - err2) + "q" + str(abs(v) - err2) + "w0e0r" + str(abs(v) + err2) + "t" + str(
                            abs(v) + err2) + "y0u0i")
            d1 = sensor_back_r.get_distance()
            d2 = sensor_back_l.get_distance()
            v = err
            if (prov == 0) and (d1 < 200) and (d2 < 200) and (abs(d1 - d2) < 150):
                err2 = (d1 - d2) * 10
                print("err2 " + str(err2))
                if (abs(err2 / 10) < 10):
                    err2 = 0

                    err3 = ((d1 + d2) / 2 - right_straight_from_wall_dist)
                    print("err3 " + str(err3))
                    if abs(err3) > 15:
                        if err3 > 0:
                            ser.write("400q0w0e0r400t0y0u0i")  # down
                        else:
                            ser.write("0q400w0e0r0t400y0u0i")  # up
                    else:
                        if err2 > 40:
                            err2 = 40
                        ser.write(str(abs(v) - err2) + "q" + str(abs(v) - err2) + "w0e0r" + str(
                            abs(v) + err2) + "t" + str(abs(v) + err2) + "y0u0i")

                else:
                    if err2 > 40:
                        err2 = 40
                    ser.write(
                        str(abs(v) - err2) + "q" + str(abs(v) - err2) + "w0e0r" + str(abs(v) + err2) + "t" + str(
                            abs(v) + err2) + "y0u0i")
            else:
                move_right(err)
    stop_move()


def drive_cell_straight():
    drive_one_cell(optical_flow_straight_cell_size, FRONT_DIRECTION)


def drive_cell_right():
    drive_one_cell(optical_flow_sideways_cell_size, RIGHT_DIRECTION)


def drive_cell_back():
    drive_one_cell(-optical_flow_straight_cell_size, BACK_DIRECTION)


def drive_cell_left():
    drive_one_cell(-optical_flow_sideways_cell_size, LEFT_DIRECTION)


def drive_cell_by_(direction):
    if direction == 0:
        drive_cell_straight()
    elif direction == 1:
        drive_cell_left()
    elif direction == 2:
        drive_cell_back()
    elif direction == 3:
        drive_cell_right()
