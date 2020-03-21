# coding=utf-8

import RPi.GPIO as GPIO
import VL53L0X
import time

CALIBRATION_FILENAME = "distSensorsCalibration.txt"

sensor_front_r_pin, sensor_front_l_pin = 13, 11
sensor_left_f_pin, sensor_left_b_pin = 5, 27
sensor_back_r_pin, sensor_back_l_pin = 17, 9
sensor_right_f_pin, sensor_right_b_pin = 12, 18
sensor_front_r, sensor_front_l = VL53L0X.VL53L0X(address=0x2A), VL53L0X.VL53L0X(address=0x2B)
sensor_left_f, sensor_left_b = VL53L0X.VL53L0X(address=0x2C), VL53L0X.VL53L0X(address=0x2D)
sensor_back_r, sensor_back_l = VL53L0X.VL53L0X(address=0x2E), VL53L0X.VL53L0X(address=0x2F)
sensor_right_f, sensor_right_b = VL53L0X.VL53L0X(address=0x4A), VL53L0X.VL53L0X(address=0x4F)


def init_sensors():
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


def shut_down():
    sensors_pins_and_sensors = [[sensor_right_f_pin, sensor_right_f], [sensor_right_b_pin, sensor_right_b],
                                [sensor_left_f_pin, sensor_left_f], [sensor_left_b_pin, sensor_left_b],
                                [sensor_front_r_pin, sensor_front_r], [sensor_front_l_pin, sensor_front_l],
                                [sensor_back_r_pin, sensor_back_r], [sensor_back_l_pin, sensor_back_l]]
    for sensor_id, sensor_sensor in sensors_pins_and_sensors:
        sensor_sensor.stop_ranging()
        time.sleep(0.5)
        GPIO.output(sensor_id, GPIO.HIGH)


def print_info():
    print "0 - калибровка по передней стороне Валеры"
    print "1 - калибровка по левой стороне Валеры"
    print "2 - калибровка по задней стороне Валеры"
    print "3 - калибровка по правой стороне Валеры"
    print "5 - показать содержимое"
    print "6 - завершить (нужно использовать, иначе Валере бывает плохо)"
    print ""


init_sensors()

print_info()

dataFile = None

while True:
    try:
        fileRead = open(CALIBRATION_FILENAME, 'r')
        fileContent = fileRead.read().split("\n")
        fileRead.close()
        calibration_code = int(input())
        if calibration_code == 0:
            dataFile = open(CALIBRATION_FILENAME, 'w')
            val = str(sensor_front_l.get_distance() - sensor_front_r.get_distance())
            print "\ncalibration: " + val + "\n"
            dataFile.write("f_r " + val + "\n")
            for fileString in fileContent[1:]:
                dataFile.write(fileString + "\n")
            dataFile.close()
        elif calibration_code == 1:
            dataFile = open(CALIBRATION_FILENAME, 'w')
            for fileString in fileContent[:1]:
                dataFile.write(fileString + "\n")
            val = str(sensor_left_b.get_distance() - sensor_left_f.get_distance())
            print "\ncalibration: " + val + "\n"
            dataFile.write("l_f " + val + "\n")
            for fileString in fileContent[2:]:
                dataFile.write(fileString + "\n")
            dataFile.close()
        elif calibration_code == 2:
            dataFile = open(CALIBRATION_FILENAME, 'w')
            for fileString in fileContent[:2]:
                dataFile.write(fileString + "\n")
            val = str(sensor_back_r.get_distance() - sensor_back_l.get_distance())
            print "\ncalibration: " + val + "\n"
            dataFile.write("b_l " + val + "\n")
            for fileString in fileContent[3:]:
                dataFile.write(fileString + "\n")
            dataFile.close()
        elif calibration_code == 3:
            dataFile = open(CALIBRATION_FILENAME, 'w')
            for fileString in fileContent[:3]:
                dataFile.write(fileString + "\n")
            val = str(sensor_right_f.get_distance() - sensor_right_b.get_distance())
            print "\ncalibration: " + val + "\n"
            dataFile.write("r_b " + val + "\n")
            dataFile.close()
        elif calibration_code == 5:
            for fileString in fileContent:
                print fileString
        elif calibration_code == 6:
            print "Пока"
            shut_down()
            exit()
        else:
            raise ValueError
    except SyntaxError:
        print "\n!!! Что-то не так с вводом. Попробуй ещё раз\n"
    except ValueError:
        print "\n!!! Что-то не так с вводом. Попробуй ещё раз\n"
    finally:
        print_info()
