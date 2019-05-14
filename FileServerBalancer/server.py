import sys
import zmq
import utilities
import os


class Server:
    port = None
    context = None
    socket = None
    path_file = "files_server/"

    def __init__(self, port):
        self.port = port
        self.path_file = "files_server_"+port+"/"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)
        if not os.path.exists(self.path_file):
            os.mkdir(self.path_file)

    def listen(self):
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
    if len(sys.argv) > 1:
        server = Server(sys.argv[1])
        print("Server running")
        server.listen()
    else:
        print("no send arguments")
