import sys
import zmq
import utilities
import os


class Server:
    id = None
    my_ip = None
    context = None
    socket = None
    successor = None
    predecessor = None
    finger_table = []
    path_file = "files_server/"
    my_range_to_save = []

    def __init__(self, ip, address_to_ring):
        port = ip.split(":")[1]
        self.id = utilities.md5_for_string(ip)
        self.my_ip = ip
        self.path_file = "files_server_"+port+"/"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://"+ip)
        if not os.path.exists(self.path_file):
            os.mkdir(self.path_file)
        self.init(address_to_ring)

    def init(self, address_to_ring):
        if address_to_ring:
            address = address_to_ring
            while True:
                context_to_server = zmq.Context()
                socket_to_server = context_to_server.socket(zmq.REQ)
                socket_to_server.connect("tcp://"+address)
                print("connect to: " + address)
                socket_to_server.send_multipart(['is_your_hash'.encode(), self.id.encode()])
                message = socket_to_server.recv_multipart()
                if message[0].decode() == 'yes':
                    self.predecessor = [address, message[1].decode()]
                    self.successor = [message[2].decode(), message[3].decode()]
                    socket_to_server.send_multipart(['enter_the_game'.encode(), self.id.encode(), self.my_ip.encode()])
                    message = socket_to_server.recv_multipart()
                    if message[0].decode() == 'ok':
                        self.update_range(self.successor[1])
                        print("THE SERVER ENTRY IN THE RING")
                    else:
                        print("ERROR - CANT ENTRY IN THE RING")
                    break
                else:
                    address = message[1].decode()
        else:
            self.my_range_to_save = [[self.id, utilities.max_value], [utilities.min_value, self.id]]
            print("self.my_range_to_save = " + str(self.my_range_to_save))

    def update_range(self, hash):
        if utilities.hexa1_smaller_than_hexa2(hash, self.id):
            self.my_range_to_save = [[self.id, utilities.max_value], [utilities.min_value, hash]]
            print("self.my_range_to_save = " + str(self.my_range_to_save))
        else:
            self.my_range_to_save = [[self.id, hash]]
            print("self.my_range_to_save = " + str(self.my_range_to_save))

    def listen(self):
        print("SERVER IS RUNNING")
        while True:
            try:
                message = self.socket.recv_multipart()
                method = message[0]
                if method:
                    method = method.decode()
                    # print("method: "+method)
                    if method == 'send_file':
                        method, hash_file, data = message
                        hash_file = hash_file.decode()
                        self.get_file(hash_file, data)
                    elif method == 'get_file':
                        method, hash_file_name = message
                        hash_file_name = hash_file_name.decode()
                        self.send_file(hash_file_name)
                    elif method == 'is_your_hash':
                        hash = message[1].decode()
                        if self.is_my_hash(hash):
                            if self.successor:
                                self.socket.send_multipart(['yes'.encode(), self.id.encode(), self.successor[0].encode(), self.successor[1].encode()])
                            else:
                                self.socket.send_multipart(['yes'.encode(), self.id.encode(), self.my_ip.encode(), self.id.encode()])
                        else:
                            self.socket.send_multipart(['no'.encode(), self.successor[0].encode()])
                    elif method == 'enter_the_game':
                        hash = message[1].decode()
                        ip_address = message[2].decode()
                        self.socket.send_multipart(['ok'.encode()])
                        print("THE NEW SERVER " + ip_address + " ENTRY IN THE RING")
                        self.successor = [ip_address, hash]
                        if len(self.my_range_to_save) == 1:
                            self.send_files_to_range(hash, self.my_range_to_save[0][1], ip_address)
                        else:
                            if utilities.hexa1_greater_than_hexa2(hash, self.id):
                                self.send_files_to_range(hash, self.my_range_to_save[1][1], ip_address)
                            else:
                                self.send_files_to_range(hash, self.my_range_to_save[0][1], ip_address)
                                self.send_files_to_range(self.my_range_to_save[1][0], self.my_range_to_save[1][1], ip_address)
                        self.update_range(hash)
                    else:
                        print("ERROR - the method (" + method + ") not exist")
                        self.socket.send_multipart(['ERROR'.encode(), ('the method (' + method + ') not exist').encode()])
            except zmq.ZMQError as error:
                print("Error to get request '" + str(error) + "'")
                try:
                    self.socket.send_multipart(['ERROR'.encode(), ("Error to get request '" + str(error) + "'").encode()])
                except zmq.ZMQError as error:
                    print("ERROR '" + str(error) + "'")
                break

    def is_my_hash(self, hash):
        if self.id == hash:
            return True
        elif len(self.my_range_to_save) == 1:
            if utilities.hexa1_greater_than_hexa2(hash, self.id):
                if utilities.hexa1_smaller_than_hexa2(hash, self.my_range_to_save[0][1]):
                    return True
                else:
                    return False
            else:
                return False
        else:
            if hash == utilities.min_value:
                return True
            elif hash == utilities.max_value:
                return True
            elif utilities.hexa1_greater_than_hexa2(hash, self.my_range_to_save[0][0]):
                if utilities.hexa1_smaller_than_hexa2(hash, self.my_range_to_save[0][1]):
                    return True
                else:
                    if utilities.hexa1_greater_than_hexa2(hash, self.my_range_to_save[1][0]):
                        if utilities.hexa1_smaller_than_hexa2(hash, self.my_range_to_save[1][1]):
                            return True
                        else:
                            return False
                    else:
                        return False
            else:
                if utilities.hexa1_greater_than_hexa2(hash, self.my_range_to_save[1][0]):
                    if utilities.hexa1_smaller_than_hexa2(hash, self.my_range_to_save[1][1]):
                        return True
                    else:
                        return False
                else:
                    return False

    def send_files_to_range(self, hash1, hash2, address):
        # print("send_files_to_range, "+hash1+" , "+hash2)
        context_to_server = zmq.Context()
        socket_to_server = context_to_server.socket(zmq.REQ)
        socket_to_server.connect("tcp://"+address)
        print("connect to: " + address)
        list_elements = os.listdir(self.path_file)
        # print(list_elements)
        for x in range(len(list_elements)):
            hash_file = list_elements[x].split(".part")[0]
            print(hash_file)
            if hash_file == hash1:
                print("hash_file == hash1")
                file = open(self.path_file + list_elements[x], 'rb')
                data = file.read()
                file.close()
                print("send file: "+list_elements[x])
                socket_to_server.send_multipart(['send_file'.encode(), list_elements[x].encode(), data])
                socket_to_server.recv_multipart()
                os.remove(self.path_file + list_elements[x])
            elif utilities.hexa1_greater_than_hexa2(hash_file, hash1):
                if utilities.hexa1_smaller_than_hexa2(hash_file, hash2):
                    print("hash_file entry in the range")
                    print("open("+self.path_file+list_elements[x]+", 'rb')")
                    file = open(self.path_file + list_elements[x], 'rb')
                    data = file.read()
                    file.close()
                    print("send file: " + list_elements[x])
                    socket_to_server.send_multipart(['send_file'.encode(), list_elements[x].encode(), data])
                    socket_to_server.recv_multipart()
                    os.remove(self.path_file + list_elements[x])

    def get_file(self, hash_file, data):  # el servidor obtiene un archivo
        if os.path.exists(self.path_file + hash_file):
            print("ERROR - The file '" + hash_file + "' its already exist")
            self.socket.send_multipart(['ERROR'.encode(), 'the file already exist'.encode()])
        else:
            try:
                print("create file '" + hash_file + "'")
                file = open(self.path_file + hash_file, "ab")
                file.write(data)
                file.close()
                self.socket.send_multipart(['OK'.encode(), ''.encode()])
            except IOError as error:
                print("ERROR - The file '" + hash_file + "' its already exist (" + str(error) + ")")
                self.socket.send_multipart(['OK'.encode(), 'the file already exist'.encode()])

    def send_file(self, hash_file):  # enviarle un archivo al cliente
        print("hash_file to send: "+hash_file)
        if os.path.exists(self.path_file + hash_file):
            try:
                file = open(self.path_file + hash_file, 'rb')
                data = file.read()
                self.socket.send_multipart(['OK'.encode(), data])
                file.close()
                print("finish to send the file")
            except IOError as error:
                self.socket.send_multipart(['ERROR'.encode(), ('Can´t find the file with the hash: '+hash_file).encode()])
                print(error)
        else:
            print("The file '" + hash_file + "' no exist")
            self.socket.send_multipart(['ERROR'.encode(), ('Can´t find the file with the hash: ' + hash_file).encode()])


if __name__ == '__main__':
    if len(sys.argv) > 2:
        server = Server(sys.argv[1], sys.argv[2])
        print("Server running")
        server.listen()
    elif len(sys.argv) > 1:
        server = Server(sys.argv[1], None)
        print("Server running")
        server.listen()
    else:
        print("no send arguments")
