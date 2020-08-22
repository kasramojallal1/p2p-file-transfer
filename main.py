import socket
import threading
import time
import glob
import os

cluster, address, port, discovery_time = '', '127.0.0.1', 0, 0
my_clusters = []
connected_clusters = []

free_riders = []


# This function is for reading the data provided in files for the nodes
def read_cluster_list_file():
    my_file = open(cluster + '.txt', "r")
    result = my_file.read().split(',')

    if result[0] != '':
        for i in range(len(result)):
            s1 = result[i]
            new_port = int(s1[s1.index('p') + 1:])
            my_clusters.append(new_port)

    my_file.close()


# TO start the udp server
def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((address, port))
    print('server running ...')

    server_handler(sock)


# to handle both the discovery messaged and the get messages sent to the server
def server_handler(c):
    while True:
        data, which_address = c.recvfrom(1024)
        msg = str(data, 'utf-8')

        if msg[0:4] == 'dis=':
            msg = msg.replace('dis=', '')
            msg = msg[:-1]
            handle_discovery_input_msg(msg)

        if msg[0:4] == 'get=':
            msg = msg.replace('get=', '')
            port_for_get = str(which_address)[14:19]
            os.chdir(cluster)
            for file in glob.glob(msg):
                print(file + ' was found')
                free_tcp = get_free_tcp_port()
                fThread = threading.Thread(target=create_tcp_server, args=(free_tcp, file))
                fThread.daemon = True
                fThread.start()
                handle_get_msg(c, port_for_get, free_tcp)
            os.chdir("../")


# To start the TCP server in order to send the selected file for other nodes
def create_tcp_server(on_port, file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', on_port))
    sock.listen(3)
    print("tcp server running on port: " + str(on_port))

    while True:
        c, a = sock.accept()

        file_bytes = get_file_on_string(file)
        c.send(bytes(file_bytes, 'utf-8'))


# this function provides the data that wants to be sent to the other nodes by our client
def get_file_on_string(file):
    os.chdir(cluster)
    my_file = open(str(file), "r")
    result = my_file.read()
    os.chdir("../")
    return result


# handles the the get messages and if they are free riders it will respond by delay
def handle_get_msg(c, port_for_get, msg):
    if port_for_get in free_riders:
        time.sleep(5)
        c.sendto(bytes(str(msg), 'utf-8'), ('127.0.0.1', int(port_for_get)))
    else:
        c.sendto(bytes(str(msg), 'utf-8'), ('127.0.0.1', int(port_for_get)))


# handles the discovery messaged and adds the new clusters to the cluster list
def handle_discovery_input_msg(msg):
    result01 = []

    result = msg.split(',')

    for i in range(len(result)):
        result01.append(int(result[i]))

    for j in range(len(result01)):
        if result01[j] not in my_clusters:
            my_clusters.append(result01[j])


# this function creates a UDP client to send the discovery messages
def start_client(to_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        connected_clusters.append(to_port)

        msg = make_output(to_port)

        iThread = threading.Thread(target=client_send_msg, args=(sock, msg, to_port))
        iThread.daemon = True
        iThread.start()
    except:
        print('port ' + str(to_port) + ' is not available yet')


# this function creates a UDP client to send the get messages
def start_client_for_get(to_port, my_request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        msg = 'get=' + str(my_request)

        iThread = threading.Thread(target=client_send_msg_for_get,
                                   args=(sock, msg, to_port))
        iThread.daemon = True
        iThread.start()

        wThread = threading.Thread(target=client_udp_for_result,
                                   args=(sock,))
        wThread.daemon = True
        wThread.start()
    except:
        print('port ' + str(to_port) + ' is not available yet')


# handles the part of the client that sends the discovery messages continuously
def client_send_msg(sock, msg, to_port):
    while True:
        time.sleep(discovery_time)
        sock.sendto(bytes(msg, 'utf-8'), ('127.0.0.1', to_port))


# handles the part of the client that sends the get message
def client_send_msg_for_get(sock, msg, to_port):
    sock.sendto(bytes(msg, 'utf-8'), ('127.0.0.1', to_port))


# handles the part of the UDP client that receives the TCP port of the other node
def client_udp_for_result(sock):
    while True:
        try:
            data, server = sock.recvfrom(1024)
            msg = str(data, 'utf-8')
            print('--------------')
            print('my TCP port is: ' + msg)
            print(server)

            create_tcp_client(int(msg))
        except:
            # print('server not available')
            continue


# creates a TCP client to connect to the TCP server of the other node to get the file
def create_tcp_client(to_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((address, to_port))

    iThread = threading.Thread(target=get_tcp_data_files, args=(sock,))
    iThread.daemon = True
    iThread.start()


# handles the part of the TCP client that receives the data of the file from other node
def get_tcp_data_files(sock):
    while True:
        data = sock.recv(1024)
        msg = str(data, 'utf-8')
        os.chdir(cluster)
        f = open("received_file.txt", "w")
        f.write(msg)
        f.close()
        os.chdir("../")


# makes the output that wants to be send to the other nodes for discovery messages
def make_output(to_port):
    result01 = []
    result_string = ''

    for i in range(len(my_clusters)):
        if my_clusters[i] != to_port:
            result01.append(my_clusters[i])

    result01.append(port)

    result_string += 'dis='

    for i in range(len(result01)):
        result_string += str(result01[i])
        result_string += ','

    return result_string


# checks which clusters are new, so it can send them discovery message
def subtraction():
    new_array = []

    for i in range(len(my_clusters)):
        if my_clusters[i] not in connected_clusters:
            new_array.append(my_clusters[i])

    return new_array


# create a client to send the discovery messages when we discover a new node
def handle_new_cluster():
    while True:
        time.sleep(2)
        sub_array = subtraction()

        for i in range(len(sub_array)):
            qThread = threading.Thread(target=start_client,
                                       args=(sub_array[i],))
            qThread.daemon = True
            qThread.start()


# creates a new TCP server on a free port of the system
def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, res_port = tcp.getsockname()
    tcp.close()
    return res_port


# the interface that checks what our request is
def start_interface():
    while True:
        time.sleep(1)
        request0 = input('what is your request: ')
        if request0 == 'get':
            request0 = input('what file: ')
            for i in range(len(my_clusters)):
                zThread = threading.Thread(target=start_client_for_get,
                                           args=(my_clusters[i], request0))
                zThread.daemon = True
                zThread.start()
        elif request0 == 'list':
            for i in range(len(my_clusters)):
                if my_clusters[i] == 5000:
                    print('N1:127.0.0.1 port: 5000')
                if my_clusters[i] == 2000:
                    print('N2:127.0.0.1 port: 2000')
                if my_clusters[i] == 3000:
                    print('N3:127.0.0.1 port: 3000')


# main part of the code
if __name__ == "__main__":
    cluster = input('enter your cluster: ')
    read_cluster_list_file()
    port = int(input('enter port: '))
    discovery_time = int(input('enter discovery time: '))

    threading.Thread(target=start_udp_server).start()

    for i in range(len(my_clusters)):
        pThread = threading.Thread(target=start_client,
                                   args=(my_clusters[i],))
        pThread.daemon = True
        pThread.start()

    threading.Thread(target=handle_new_cluster).start()

    threading.Thread(target=start_interface).start()
