import os
import commands
import Connection
from MovementAndSensors import *
from Camera import *


def aligns_sequence(direction):
    do_round_align_by_(direction)
    do_progressive_align_by_(direction)
    do_round_align_by_(direction)
    stop_move()


def do_some_align():
    if is_wall_front() and is_wall_left():
        aligns_sequence(FRONT_DIRECTION)
        aligns_sequence(LEFT_DIRECTION)
    elif is_wall_left() and is_wall_back():
        aligns_sequence(LEFT_DIRECTION)
        aligns_sequence(BACK_DIRECTION)
    elif is_wall_back() and is_wall_right():
        aligns_sequence(BACK_DIRECTION)
        aligns_sequence(RIGHT_DIRECTION)
    elif is_wall_right() and is_wall_front():
        aligns_sequence(RIGHT_DIRECTION)
        aligns_sequence(FRONT_DIRECTION)

    elif is_wall_front():
        aligns_sequence(FRONT_DIRECTION)
    elif is_wall_left():
        aligns_sequence(LEFT_DIRECTION)
    elif is_wall_back():
        aligns_sequence(BACK_DIRECTION)
    elif is_wall_right():
        aligns_sequence(RIGHT_DIRECTION)


def run_server():
    os.system("python -c \"from Connection import run_server;run_server()\" &")
    time.sleep(0.5)


def send_message(message):
    Connection.send_client_message(message)


def get_message():
    return Connection.get_message()


maze_size = 39
maze_map = [[" " for _ in range(maze_size)] for _ in range(maze_size)]

robot_row, robot_column = (maze_size - 1) // 2, (maze_size - 1) // 2

direction_to_move_to = []


def fill_walls_around_cell(_row, _column):
    maze_map[_row + 1][_column] = "-"
    maze_map[_row - 1][_column] = "-"
    maze_map[_row][_column + 1] = "|"
    maze_map[_row][_column - 1] = "|"


def update_map():
    maze_map[robot_row][robot_column] = "*"

    if is_wall_front() and is_wall_front():
        print "fill front"
        fill_walls_around_cell(robot_row - 2, robot_column)
    elif maze_map[robot_row - 2][robot_column] == " " and not maze_map[robot_row - 1][robot_column] == "-":
        maze_map[robot_row - 2][robot_column] = "?"

    if is_wall_left() and is_wall_left():
        print "fill left"
        fill_walls_around_cell(robot_row, robot_column - 2)
    elif maze_map[robot_row][robot_column - 2] == " " and not maze_map[robot_row][robot_column - 1] == "|":
        maze_map[robot_row][robot_column - 2] = "?"

    if is_wall_back() and is_wall_back():
        print "fill back"
        fill_walls_around_cell(robot_row + 2, robot_column)
    elif maze_map[robot_row + 2][robot_column] == " " and not maze_map[robot_row + 1][robot_column] == "-":
        maze_map[robot_row + 2][robot_column] = "?"

    if is_wall_right() and is_wall_right():
        print "fill right"
        fill_walls_around_cell(robot_row, robot_column + 2)
    elif maze_map[robot_row][robot_column + 2] == " " and not maze_map[robot_row][robot_column + 1] == "|":
        maze_map[robot_row][robot_column + 2] = "?"


def update_robot_position_by_movement(just_move_code):
    global robot_row, robot_column
    if just_move_code == 0:
        robot_row -= 2
    elif just_move_code == 1:
        robot_column -= 2
    elif just_move_code == 2:
        robot_row += 2
    elif just_move_code == 3:
        robot_column += 2


def is_map_built():
    for _row in range(len(maze_map)):
        for _column in range(len(maze_map[_row])):
            if maze_map[_row][_column] == "?":
                return False
    return True


def update_path():
    matrix_view = [[0 for _ in range(maze_size)] for _ in range(maze_size)]
    for _row in range(maze_size):
        for _column in range(maze_size):
            if maze_map[_row][_column] == "-" or maze_map[_row][_column] == "|":
                matrix_view[_row][_column] = -1
            elif maze_map[_row][_column] == "?":
                matrix_view[_row][_column] = -2
    wave_value = 1
    matrix_view[robot_row][robot_column] = wave_value + 1
    end_row, end_column = None, None
    while True:
        print "c1"
        if end_row and end_column:
            break
        wave_value += 1
        for _row in range(maze_size):
            if end_row and end_column:
                break
            for _column in range(maze_size):
                if matrix_view[_row][_column] == wave_value:
                    if _row > 1 and matrix_view[_row - 1][_column] != -1 and matrix_view[_row - 2][_column] == -2:
                        matrix_view[_row - 2][_column] = wave_value + 1
                        end_row, end_column = _row - 2, _column
                        break
                    if _column > 1 and matrix_view[_row][_column - 1] != -1 and matrix_view[_row][_column - 2] == -2:
                        matrix_view[_row][_column - 2] = wave_value + 1
                        end_row, end_column = _row, _column - 2
                        break
                    if _row < maze_size - 2 and matrix_view[_row + 1][_column] != -1 \
                            and matrix_view[_row + 2][_column] == -2:
                        matrix_view[_row + 2][_column] = wave_value + 1
                        end_row, end_column = _row + 2, _column
                        break
                    if _column < maze_size + 2 and matrix_view[_row][_column + 1] != -1 \
                            and matrix_view[_row][_column + 2] == -2:
                        matrix_view[_row][_column + 2] = wave_value + 1
                        end_row, end_column = _row, _column + 2
                        break

                    if _row > 1 and matrix_view[_row - 1][_column] != -1 and matrix_view[_row - 2][_column] == 0:
                        matrix_view[_row - 2][_column] = wave_value + 1
                    if _column > 1 and matrix_view[_row][_column - 1] != -1 and matrix_view[_row][_column - 2] == 0:
                        matrix_view[_row][_column - 2] = wave_value + 1
                    if _row < maze_size - 2 and matrix_view[_row + 1][_column] != -1 \
                            and matrix_view[_row + 2][_column] == 0:
                        matrix_view[_row + 2][_column] = wave_value + 1
                    if _column < maze_size + 2 and matrix_view[_row][_column + 1] != -1 \
                            and matrix_view[_row][_column + 2] == 0:
                        matrix_view[_row][_column + 2] = wave_value + 1
    cells_wave_stack = [[end_row, end_column]]

    print "c2"
    print ""
    for _row in range(maze_size):
        s = ""
        for _column in range(maze_size):
            s += str(maze_map[_row][_column]) + " "
        print s

    while cells_wave_stack[-1] != [robot_row, robot_column]:
        last_cell_row, last_cell_column = cells_wave_stack[-1]
        last_wave_value = matrix_view[last_cell_row][last_cell_column]

        if last_cell_row > 1 and matrix_view[last_cell_row - 1][last_cell_column] != -1 and \
                matrix_view[last_cell_row - 2][last_cell_column] == last_wave_value - 1:
            cells_wave_stack.append([last_cell_row - 2, last_cell_column])
        elif last_cell_column > 1 and matrix_view[last_cell_row][last_cell_column - 1] != -1 and \
                matrix_view[last_cell_row][last_cell_column - 2] == last_wave_value - 1:
            cells_wave_stack.append([last_cell_row, last_cell_column - 2])
        elif last_cell_row < maze_size - 2 and matrix_view[last_cell_row + 1][last_cell_column] != -1 and \
                matrix_view[last_cell_row + 2][last_cell_column] == last_wave_value - 1:
            cells_wave_stack.append([last_cell_row + 2, last_cell_column])
        elif last_cell_column < maze_size - 2 and matrix_view[last_cell_row][last_cell_column + 1] != -1 and \
                matrix_view[last_cell_row][last_cell_column + 2] == last_wave_value - 1:
            cells_wave_stack.append([last_cell_row, last_cell_column + 2])

    print "c3"
    directions_wave_stack = []
    for i in range(len(cells_wave_stack) - 1):
        now_row, now_col = cells_wave_stack[i]
        prev_row, prev_col = cells_wave_stack[i + 1]
        if now_row - prev_row == 2:
            directions_wave_stack.append(2)
        elif now_row - prev_row == -2:
            directions_wave_stack.append(0)
        elif now_col - prev_col == 2:
            directions_wave_stack.append(3)
        elif now_col - prev_col == -2:
            directions_wave_stack.append(1)
        else:
            directions_wave_stack.append(-1)

    print "c4"
    global direction_to_move_to
    direction_to_move_to = directions_wave_stack[:]


def write_console(message):
    with open('log.txt', 'w') as _file:
        _file.write(message)
        _file.close()


most_top, most_down, most_right, most_left = None, None, None, None


def is_map_enough_for_localisation():
    global most_top, most_down, most_right, most_left
    most_top, most_down, most_right, most_left = None, None, None, None
    for _row in range(maze_size):
        for _column in range(maze_size):
            if (maze_map[_row][_column] == "*" or maze_map[_row][_column] == "?") and (
                    most_top is None or _row < most_top):
                most_top = _row
            if (maze_map[_row][_column] == "*" or maze_map[_row][_column] == "?") and (
                    most_left is None or _column < most_left):
                most_left = _column
            if (maze_map[_row][_column] == "*" or maze_map[_row][_column] == "?") and (
                    most_down is None or _row > most_down):
                most_down = _row
            if (maze_map[_row][_column] == "*" or maze_map[_row][_column] == "?") and (
                    most_right is None or _column > most_right):
                most_right = _column

    return most_right - most_left >= 14 and most_down - most_top >= 14


if robot_hostname == only_client_robot_hostname:
    print "Eeee"
    write_console("Eeee")
elif robot_hostname == server_robot_hostname:
    print "Oooo"
    write_console("Oooo")


if robot_hostname == server_robot_hostname:
    print "it\'s server. Waiting for confirmation"
    write_console("it\'s server. Waiting for confirmation")
    msg_found = get_message()
    print "found message: " + str(msg_found)
    write_console("found message: " + str(msg_found))
    if msg_found == ready_word:
        print "sent ready word"
        write_console("send ready word")
        while True:
            print get_message()
            time.sleep(0.7)
    else:
        print "Something wrong with connection"
        write_console("Something wrong with connection")

elif robot_hostname == only_client_robot_hostname:
    print "it\'s only client. Waiting for confirmation"
    write_console("it\'s only client. Waiting for confirmation")
    send_message(ready_word)
    print "sending message"
    write_console("sending message")
    msg_found = get_message()
    print "found message: " + str(msg_found)
    write_console("found message: " + str(msg_found))
    if msg_found == ready_word:
        print "it\'s ready word"
        write_console("it\'s ready word")
        while True:
            print send_message("Tu")
            time.sleep(0.35)
    else:
        print "Something wrong with connection"
        write_console("Something wrong with connection")


try:
    init_sensors()
    update_map()
    while not is_map_built():
        if is_map_enough_for_localisation():
            stop_move()
            shut_down()
            write_console(str((robot_row - most_top) // 2) + " " + str((robot_column - most_left) // 2))
            exit()
        print "-" * maze_size
        for row in range(len(maze_map)):
            print " ".join(map(str, maze_map[row]))

        print_all_sensors()

        if not direction_to_move_to:
            update_path()
        else:
            print str(is_wall_front()) + " " + str(is_wall_left()) + " " + str(is_wall_back()) + " " + str(
                is_wall_right())
            do_some_align()
            direction_now = direction_to_move_to.pop()
            print "dir: " + str(direction_now)
            drive_cell_by_(direction_now)
            print "row: " + str(robot_row) + "  column: " + str(robot_column)
            do_some_align()
            update_robot_position_by_movement(direction_now)
            print "update: "
            print "row: " + str(robot_row) + "  column: " + str(robot_column)
            update_map()
except KeyboardInterrupt:
    stop_move()
    shut_down()
