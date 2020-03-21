import commands

robot_hostname = commands.getoutput("cat /etc/hostname")

server_robot_ip = "192.168.1.103"
server_robot_hostname = "raspberrypi1"
only_client_robot_hostname = "raspberrypi2"
ready_word = "ready"
min_sensors_round_diff = 15
min_sensors_progressive_diff = 15
p_coef = 1.3

right_straight_from_wall_dist = 80
right_sideways_from_wall_dist = 130

align_wall_deviation = 10
round_align_deviation = 10

kp_progressive_align = 8
kp_round_align = 8

ki_progressive_align = 0.01
ki_round_align = 0.01

optical_flow_deviation = 50

optical_flow_straight_cell_size = 8000 if robot_hostname == server_robot_hostname else 8900
optical_flow_sideways_cell_size = 8900

min_progressive_move_val = 200
max_progressive_move_val = 400
min_sideways_move_val = 500
max_sideways_move_val = 550
min_round_move_val = 200
max_round_move_val = 400

FRONT_DIRECTION = 0
LEFT_DIRECTION = 1
BACK_DIRECTION = 2
RIGHT_DIRECTION = 3


wheel_coefficient_front_r_minus = 0
wheel_coefficient_front_l_minus = 0
wheel_coefficient_back_r_minus = 80
wheel_coefficient_back_l_minus = 0
