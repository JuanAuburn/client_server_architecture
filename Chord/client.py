import sys
import zmq
import utilities
import os


class Client:
    chunk_file = None
    server_ip = ""
    dictionary_files = {}
    path_file = "files_client/"

    def __init__(self, server_ip="127.0.0.1:11000"):
        self.chunk_file = utilities.chunk_file
        self.server_ip = server_ip
        if not os.path.exists(self.path_file):
            os.mkdir(self.path_file)

    def send_file(self, file_name):
        hash_list_to_send = []
        data_map = {}
        if os.path.exists(file_name):
            try:
                file = open(file_name, 'rb')
                hash_file = utilities.md5_for_file(file_name)
                print("hash_file to send: "+hash_file+"("+file_name+")")
                # print("chunk file: "+str(utilities.chunk_file))
                part = 0
                while True:
                    data = file.read(self.chunk_file)
                    # print(data)
                    if not data:
                        print("no more data")
                        break
                    hash_subpart = utilities.md5_for_data(data)
                    hash_subpart = hash_subpart + ".part"+str(part)
                    hash_list_to_send.append(hash_subpart)
                    data_map[hash_subpart] = data
                    part += 1
                print("sending the sub parts")
                address_to_server = self.server_ip
                while True:
                    context_to_server = zmq.Context()
                    socket_to_server = context_to_server.socket(zmq.REQ)
                    socket_to_server.connect("tcp://"+address_to_server)
                    print("connect to: " + address_to_server + " and ask is your hash " + hash_file)
                    socket_to_server.send_multipart(['is_your_hash'.encode(), hash_file.encode()])
                    message = socket_to_server.recv_multipart()
                    if message[0].decode() == 'yes':
                        print("Server response: YES")
                        self.dictionary_files[hash_file] = {"address": address_to_server, "parts": hash_list_to_send}
                        for count in range(len(hash_list_to_send)):
                            print("Sending the part: " + hash_list_to_send[count])
                            socket_to_server.send_multipart(['send_file'.encode(), hash_list_to_send[count].encode(), data_map[hash_list_to_send[count]]])
                            message = socket_to_server.recv_multipart()
                        break
                    else:
                        print("Server response: NO")
                        address_to_server = message[1].decode()
                print("finish to send the file")
            except IOError as error:
                print(error)
        else:
            print('The file "' + file_name + '" no exist. Try again')

    def get_file(self, hash_file_name, name_file_to_save):
        print("get_file()")
        if os.path.exists(self.path_file + name_file_to_save):
            os.remove(self.path_file + name_file_to_save)
        if self.dictionary_files[hash_file_name]:
            print("create file '" + name_file_to_save + "'")
            file = open(self.path_file + name_file_to_save, "ab")
            all_data = {}
            address_to_server = self.dictionary_files[hash_file_name]["address"]
            list_of_hashes = self.dictionary_files[hash_file_name]["parts"]
            context_to_server = zmq.Context()
            socket_to_server = context_to_server.socket(zmq.REQ)
            print("connect to: " + address_to_server)
            socket_to_server.connect("tcp://"+address_to_server)
            for hash_file in list_of_hashes:
                # print("socket_to_server, " + address + ", " + hash_file)
                socket_to_server.send_multipart(['get_file'.encode(), hash_file.encode()])
                response = socket_to_server.recv_multipart()
                status = response[0].decode()
                if status == 'OK':
                    data = response[1]
                    part = hash_file.split('.part')[1]
                    all_data[part] = data
                else:
                    message = response[1].decode()
                    print("ERROR - " + message)
            # print("Construyendo file")
            for count in range(len(all_data.keys())):
                # print(count)
                file.write(all_data[str(count)])
            file.close()
        else:
            print("ERROR - cant find the hash in the dictionary")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        client = Client(sys.argv[1])
        while True:
            print("write the file name to send: ")
            file_name1 = input()
            if file_name1 != '':
                client.send_file(file_name1)
                hash_file1 = ''
                if os.path.exists(file_name1):
                    hash_file1 = utilities.md5_for_file(file_name1)
                print("press any key for continue to get the same file: ")
                input()
                client.get_file(hash_file1, file_name1)
            else:
                print("The file name to send can not be empty. Try again")
            # print("press any key to get the file: 9694b7c165af81f4d9d372f54117c0f1")
            # input()
            # client.get_file_by_hash('9694b7c165af81f4d9d372f54117c0f1')
            # print("press any key to send server file:")
            # input()
            # client.send_file('server.py')
            # print("press any key to send client file:")
            # input()
            # client.send_file('client.py')
            # print("press any key to send utilities file:")
            # input()
            # client.send_file('utilities.py')
    else:
        print("no send arguments")
