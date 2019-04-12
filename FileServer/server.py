import zmq


class Server:
    port = "9999"
    chunk_file = 20
    context = None
    socket = None
    count_files = 0
    dictionary_files = {}

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)

    def read_messages(self):
        while True:
            try:
                message = self.socket.recv().decode()
                print("Received message: ", message)
                self.socket.send_string("receive")
            except zmq.ZMQError as error:
                print("Error to read message '" + str(error) + "'")

    def read_files(self):
        while True:
            try:
                hash_file, part, data = self.socket.recv_multipart()
                hash_file = hash_file.decode()
                # print("hash_file: "+hash_file)
                # print("part: "+part.decode())
                part = int(part.decode())
                data = data.decode()
                # print(data)
                if part == 0:
                    if not self.dictionary_files.get(hash_file):
                        try:
                            file = open('files/' + hash_file, "x")
                            print("create file '" + hash_file + "'")
                            file.write(data)
                            self.dictionary_files[hash_file] = file
                            self.socket.send_string("ok")
                        except IOError as error:
                            print("ERROR - The file '" + hash_file + "' its already exist (" + str(error) + ")")
                            self.socket.send_string("the file already exist")
                    else:
                        print("ERROR - The file '" + hash_file + "' its already exist")
                        self.socket.send_string("the file already exist")
                elif part == -1:
                    if self.dictionary_files.get(hash_file):
                        self.dictionary_files[hash_file].close()
                        self.dictionary_files.pop(hash_file)
                        print("the file '" + hash_file + "' its complete")
                        self.socket.send_string("ok")
                    else:
                        print("ERROR - The file to close '" + hash_file + "' no exist")
                        self.socket.send_string("the file to finish no exist or already finish")
                else:
                    if self.dictionary_files.get(hash_file):
                        file = self.dictionary_files[hash_file]
                        print(hash_file + " - receiving the part " + str(part))
                        file.write(data)
                        self.socket.send_string("ok")
                    else:
                        print("ERROR - The file '" + hash_file + "' to write the part " + str(part) + " no exist")
                        self.socket.send_string("the file to write no exist or already created")
            except zmq.ZMQError as error:
                print("Error to read file '" + str(error) + "'")
                try:
                    self.socket.send_string("ERROR")
                except zmq.ZMQError as error:
                    print("ERROR '" + str(error) + "'")
                break


if __name__ == '__main__':
    server = Server()
    server.read_files()
