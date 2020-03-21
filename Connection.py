import select
import socket as sckt
import sys

from Config import server_robot_ip


def get_message():
    print "Starting client..."
    host = server_robot_ip
    port = 15000  # Server port

    s = sckt.socket(sckt.AF_INET, sckt.SOCK_STREAM)
    s.settimeout(2)

    try:
        s.connect((host, port))
    except:
        print 'Unable to connect'
        sys.exit()

    while True:
        print "trying to get message"
        socket_list = [sys.stdin, s]
        print "g1"
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
        print "g2"
        for sock in read_sockets:
            print "g3"
            if sock == s:
                print "g4"
                data = sock.recv(4096)
                if not data:
                    print "exit"
                    sys.exit()
                else:
                    print "g5"
                    s.close()
                    return data


def send_client_message(to_send):
    print "Starting client..."
    host = server_robot_ip
    port = 15000

    s = sckt.socket(sckt.AF_INET, sckt.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
    except:
        print 'Unable to connect'
        s.close()
        sys.exit()

    s.send(to_send)
    s.close()


def run_server():
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
    PORT = 15000

    server_socket = sckt.socket(sckt.AF_INET, sckt.SOCK_STREAM)

    server_socket.setsockopt(sckt.SOL_SOCKET, sckt.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print "Chat server started on port " + str(PORT)

    try:
        while True:
            read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

            for sock in read_sockets:
                # New connection
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)

                # Some incoming message from a client
                else:
                    try:
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            for socket in CONNECTION_LIST:
                                if socket != server_socket and socket != sock:
                                    try:
                                        socket.send(data)
                                    except:
                                        socket.close()
                                        CONNECTION_LIST.remove(socket)
                    except:
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue
    finally:
        server_socket.close()
