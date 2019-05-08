import sys
import zmq
import utilities
import os


class Client:
    port_server = "9999"
    context = None
    socket = None
    dictionary_files = {}
    chunk_file = 2000
    path_file = "files_client/"

    def __init__(self):
        self.context = zmq.Context()
        print("Connecting to server...")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % self.port_server)

    def send_message(self, message):
        self.socket.send_multipart(['send_message'.encode(), message.encode()])
        response = self.socket.recv().decode()
        print(response)

    def send_file(self, file_name):
        if os.path.exists(file_name):
            try:
                file = open(file_name, 'rb')
                hash_file = utilities.md5_for_file(file_name)
                print("hash_file to send: "+hash_file+"("+file_name+")")
                # print("chunk file: "+str(self.chunk_file))
                part = 0
                while True:
                    data = file.read(self.chunk_file)
                    # print(data)
                    if not data:
                        print("no more data")
                        print("data: " + str(part*self.chunk_file))
                        part = -1
                        self.socket.send_multipart(['send_file'.encode(), str(hash_file).encode(), str(part).encode(), ''.encode()])
                        print("server response: " + self.socket.recv_multipart()[0].decode())
                        break
                    print("sending the part: "+str(part))
                    self.socket.send_multipart(['send_file'.encode(), str(hash_file).encode(), str(part).encode(), data])
                    server_response = self.socket.recv_multipart()
                    print("server response: " + server_response[0].decode())
                    part += 1
                    if server_response[0].decode() != 'OK':
                        print("ERROR - " + server_response[1].decode())
                        break
                print("finish to send the file")
            except IOError as error:
                print(error)
        else:
            print('The file "' + file_name + '" no exist. Try again')

    def get_file(self, hash_file_name, name_file_to_save):
        part = 0
        if os.path.exists(self.path_file + name_file_to_save):
            os.remove(self.path_file + name_file_to_save)
        while True:
            self.socket.send_multipart(['get_file'.encode(), hash_file_name.encode(), str(part).encode()])
            response = self.socket.recv_multipart()
            method = response[0].decode()
            if (not response[0]) or method == 'ERROR':
                print('ERROR to get the file '+hash_file_name+': '+response[1].decode())
                break
            elif method == 'send_file':
                hash_file = response[1].decode()
                part = int(response[2].decode())
                data = response[3]
                if hash_file == hash_file_name:
                    if part == 0:
                        try:
                            print("create file '" + name_file_to_save + "'")
                            file = open(self.path_file + name_file_to_save, "ab")
                            file.write(data)
                            self.dictionary_files[hash_file] = {"file": file, "puntero_parte": 0, "parts": []}
                        except IOError as error:
                            print("ERROR - The file '" + name_file_to_save + "' its already exist (" + str(error) + ")")
                            break
                    elif part == -1:
                        if self.dictionary_files[hash_file]["file"]:
                            self.add_file_part(hash_file)
                            self.dictionary_files[hash_file]["file"].close()
                            self.dictionary_files.pop(hash_file)
                            print("the file '" + hash_file + "' its complete")
                        else:
                            print("ERROR - The file to close '" + hash_file + "' no exist")
                        break
                    else:
                        if self.dictionary_files[hash_file]["file"]:
                            print(name_file_to_save + " - receiving the part " + str(part))
                            if self.dictionary_files[hash_file]["puntero_parte"]+1 == part:
                                # print("add the data directly in the file")
                                self.dictionary_files[hash_file]["file"].write(data)
                                self.dictionary_files[hash_file]["puntero_parte"] += 1
                            else:
                                # print("add the data in the dictionary")
                                self.dictionary_files[hash_file]["parts"].append({"part": part, "data": data})
                            self.add_file_part(hash_file)
                        else:
                            print("ERROR - The file '" + hash_file + "' to write the part " + str(part) + " no exist")
                            break
                else:
                    print("The file received '"+hash_file+"' is different to the wanted '"+hash_file_name+"'")
                    break
            else:
                print("The method '"+method+"' no is valid")
                break
            part += 1
        self.add_file_part(hash_file_name)

    def add_file_part(self, hash_file):
        # print("add_file_part")
        if self.dictionary_files.get(hash_file):
            count = 0
            while count < len(self.dictionary_files[hash_file]["parts"]):
                part = self.dictionary_files[hash_file]["parts"][count]
                if part["part"] == self.dictionary_files[hash_file]["puntero_parte"]:
                    self.dictionary_files[hash_file]["file"].write(part["data"])
                    self.dictionary_files[hash_file]["puntero_parte"] += 1
                    self.dictionary_files[hash_file]["parts"].pop(count)
                    count = 0
                else:
                    count += 1


if __name__ == '__main__':
    client = Client()
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
