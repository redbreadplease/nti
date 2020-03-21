import serial

ser = serial.Serial("/dev/ttyS0", 9600, timeout=5)


def signal_to_move(a1, a2, b1, b2, c1, c2, d1, d2):
    ser.write(str(int(a1)) + "q" + str(int(a2)) + "w" + str(int(b1)) + "e" + str(int(b2)) + "r" +
              str(int(c1)) + "t" + str(int(c2)) + "y" + str(int(d1)) + "u" + str(int(d2)) + "i")


while True:
    print("press 0 to stop move")
    print("press 1 to move straight")
    print("press 2 to move back")
    print("press 3 to move left")
    print("press 4 to move right")
    print("press 5 to move counterclockwise")
    print("press 6 to move clockwise")
    print("press F to pay respect")

    code = input()

    direction = -1
    if code == "F":
        print("respect payed")
    else:
        direction = int(code)

    val = 600

    if direction == 1:
        signal_to_move(0, val, 0, val, 0, val, 0, val)

    elif direction == 2:
        signal_to_move(val, 0, val, 0, val, 0, val, 0)

    elif direction == 3:
        signal_to_move(0, 0, val, val, 0, 0, val, val)

    elif direction == 4:
        signal_to_move(val, val, 0, 0, val, val, 0, 0)

    elif direction == 5:
        signal_to_move(val, val, 0, val, 0, 0, val, 0)

    elif direction == 6:
        signal_to_move(0, 0, val, 0, val, val, 0, val)

    elif direction == 0:
        signal_to_move(0, 0, 0, 0, 0, 0, 0, 0)
