import sys
import zmq
import utilities
import os
import threading
import json
from ast import literal_eval


class Balancer:
    bind_port = "9001"
    valid_server_list_to_send = [
        {"address": "tcp://localhost:9002", "capacity": 100000},
        {"address": "tcp://localhost:9003", "capacity": 1000000},
        {"address": "tcp://localhost:9004", "capacity": 10000000}
    ]
    server_list = []
    context_to_client = None
    socket_to_client = None
    dictionary_files = {}
    path_file = "files_client/"
    now_position_server = 0

    def __init__(self):
        # create socket to bind clients
        self.context_to_client = zmq.Context()
        self.socket_to_client = self.context_to_client.socket(zmq.REP)
        self.socket_to_client.bind("tcp://*:%s" % self.bind_port)

    def listen(self):
        while True:
            try:
                message = self.socket_to_client.recv_multipart()
                method = message[0]
                if method:
                    method = method.decode()
                    # print("method: "+method)
                    if method == 'servers_to_send_files':
                        method, hash_file, files_list = message
                        hash_file = hash_file.decode()
                        files_list = literal_eval(files_list.decode())
                        # print(files_list)
                        if self.dictionary_files.get(hash_file):
                            print('ERROR - The hash_file already exist')
                            # self.socket_to_client.send_multipart(['ERROR'.encode(), 'The hash_file already exist'.encode()])
                            self.socket_to_client.send_multipart(['OK'.encode(), json.dumps(self.dictionary_files[hash_file]).encode()])
                        else:
                            response = self.assignment_servers(files_list)
                            self.dictionary_files[hash_file] = response
                            print("finish to assignment address")
                            # print(response)
                            self.socket_to_client.send_multipart(['OK'.encode(), json.dumps(response).encode()])
                    elif method == 'get_servers_of_file':
                        method, hash_file = message
                        hash_file = hash_file.decode()
                        if self.dictionary_files.get(hash_file):
                            self.socket_to_client.send_multipart(['OK'.encode(), json.dumps(self.dictionary_files.get(hash_file)).encode()])
                        else:
                            self.socket_to_client.send_multipart(['ERROR'.encode(), 'The hash_file no exist'.encode()])
                    else:
                        self.socket_to_client.send_multipart(['ERROR'.encode(), ('The method ' + method + ' no exist').encode()])
            except zmq.ZMQError as error:
                print("Error to get request '" + str(error) + "'")
                try:
                    self.socket_to_client.send_multipart(['ERROR'.encode(), ("Error to get request '" + str(error) + "'").encode()])
                except zmq.ZMQError as error:
                    print("ERROR '" + str(error) + "'")
                break

    def assignment_servers(self, files_list):
        address_dict = {}
        # print("len file_list: " + str(len(files_list)))
        for count in range(len(files_list)):
            hash_file = files_list[count]
            if hash_file:
                while True:
                    self.now_position_server += 1
                    if len(self.valid_server_list_to_send) == 0:
                        self.now_position_server = None
                        break
                    else:
                        if self.now_position_server >= len(self.valid_server_list_to_send):
                            self.now_position_server = 0
                        if self.valid_server_list_to_send[self.now_position_server]['capacity'] >= utilities.chunk_file:
                            break
                # print(self.now_position_server)
                if self.now_position_server is None:
                    print("The balancer no have more valid servers to send files")
                    break
                if address_dict.get(self.valid_server_list_to_send[self.now_position_server]['address']):
                    address_dict[self.valid_server_list_to_send[self.now_position_server]['address']].append(hash_file)
                else:
                    address_dict[self.valid_server_list_to_send[self.now_position_server]['address']] = [hash_file]
                self.valid_server_list_to_send[self.now_position_server]['capacity'] -= utilities.chunk_file
        return address_dict


if __name__ == '__main__':
    server = Balancer()
    print("Balancer running")
    server.listen()
