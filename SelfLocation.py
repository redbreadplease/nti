map = [[' ', '-', ' ', '-', ' ', '-', ' ', '-', ' ', '-', ' ', '-', ' ', ' ', ' ', '-', ' '],
       ['|', '0', ' ', '0', ' ', '0', ' ', '0', ' ', '0', ' ', '0', '|', ' ', '|', '0', '|'],
       [' ', ' ', ' ', '-', ' ', ' ', ' ', '-', ' ', '-', ' ', ' ', ' ', '-', ' ', ' ', ' '],
       ['|', '0', '|', ' ', '|', '0', '|', '0', '|', ' ', '|', '0', ' ', '0', ' ', '0', '|'],
       [' ', ' ', ' ', '-', ' ', ' ', ' ', ' ', ' ', '-', ' ', ' ', ' ', '-', ' ', '-', ' '],
       ['|', '0', ' ', '0', ' ', '0', '|', '0', ' ', '0', ' ', '0', '|', ' ', '|', '0', '|'],
       [' ', '-', ' ', '-', ' ', ' ', ' ', ' ', ' ', '-', ' ', ' ', ' ', '-', ' ', ' ', ' '],
       ['|', '0', '|', ' ', '|', '0', '|', '0', '|', ' ', '|', '0', ' ', '0', ' ', '0', '|'],
       [' ', ' ', ' ', '-', ' ', ' ', ' ', '-', ' ', '-', ' ', ' ', ' ', '-', ' ', ' ', ' '],
       ['|', '0', ' ', '0', ' ', '0', ' ', '0', ' ', '0', ' ', '0', '|', ' ', '|', '0', '|'],
       [' ', ' ', ' ', '-', ' ', ' ', ' ', '-', ' ', ' ', ' ', ' ', ' ', '-', ' ', '-', ' '],
       ['|', '0', '|', ' ', '|', '0', '|', ' ', '|', '0', ' ', '0', ' ', '0', ' ', '0', '|'],
       [' ', '-', ' ', '-', ' ', ' ', ' ', '-', ' ', '-', ' ', ' ', ' ', '-', ' ', ' ', ' '],
       ['|', '0', ' ', '0', ' ', '0', ' ', '0', '|', ' ', '|', '0', '|', ' ', '|', '0', '|'],
       [' ', ' ', ' ', '-', ' ', ' ', ' ', ' ', ' ', '-', ' ', '-', ' ', '-', ' ', ' ', ' '],
       ['|', '0', '|', ' ', '|', '0', ' ', '0', ' ', '0', ' ', '0', ' ', '0', ' ', '0', '|'],
       [' ', '-', ' ', ' ', ' ', '-', ' ', '-', ' ', '-', ' ', '-', ' ', '-', ' ', '-', ' ']]


def resignment(movement_directions):
    for i in range(len(movement_directions)):
        if movement_directions[i] == 0:
            movement_directions[i] = 3
        elif movement_directions[i] == 1:
            movement_directions[i] = 0
        elif movement_directions[i] == 2:
            movement_directions[i] = 1
        elif movement_directions[i] == 3:
            movement_directions[i] = 2


def trying(movement_directions, i, j):
    temp_i = i
    temp_j = j
    for num in range(len(movement_directions)):
        flag = False
        if movement_directions[num] == 0:
            if temp_i != 1:
                if map[temp_i - 1][temp_j] != '-':
                    temp_i -= 2
                    flag = True
                else:
                    break
            else:
                break
        elif movement_directions[num] == 1:
            if temp_j != 1:
                if map[temp_i][temp_j - 1] != '|':
                    temp_j -= 2
                    flag = True
                else:
                    break
            else:
                break
        elif movement_directions[num] == 2:
            if temp_i != 15:

                if map[temp_i + 1][temp_j] != '-':
                    temp_i += 2
                    flag = True
                else:
                    break
            else:
                break
        elif movement_directions[num] == 3:
            if temp_j != 15:
                if map[temp_i][temp_j + 1] != '|':
                    temp_j += 2
                    flag = True
                else:
                    break
            else:
                break
        if num >= len(movement_directions) - 1:
            print(int((i - 1) / 2), int((j - 1) / 2), '\n', movement_directions[num])


def self_locate(movement_directions, i, j):
    trying(movement_directions, i * 2 + 1, j * 2 + 1)
    resignment(movement_directions)

    trying(movement_directions, i * 2 + 1, j * 2 + 1)
    resignment(movement_directions)

    trying(movement_directions, i * 2 + 1, j * 2 + 1)
    resignment(movement_directions)

    trying(movement_directions, i * 2 + 1, j * 2 + 1)
    resignment(movement_directions)

    if i == 0 and j == 0:
        for i in range(8):
            for j in range(8):
                if i != 0 or j != 0:
                    if map[i * 2 + 1][j * 2 + 1] != ' ':
                        self_locate(movement_directions, i, j)
