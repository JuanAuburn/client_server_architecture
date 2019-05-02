import zmq
import utilities
import os


class Server:
    port = "9999"
    context = None
    socket = None
    count_files = 0
    dictionary_files = {}

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)

    def listen(self):
        while True:
            try:
                message = self.socket.recv_multipart()
                method = message[0]
                if method:
                    method = method.decode()
                    # print("method: "+method)
                    if method == 'send_file':
                        method, hash_file, part, data = message
                        hash_file = hash_file.decode()
                        part = int(part.decode())
                        self.get_file(hash_file, part, data)
                    elif method == 'get_file':
                        method, hash_file_name, part = message
                        hash_file_name = hash_file_name.decode()
                        part = int(part.decode())
                        self.send_file(hash_file_name, part)
                    elif method == 'send_message':
                        method, message_content = message
                        message_content = message_content.decode()
                        self.read_message(message_content)
            except zmq.ZMQError as error:
                print("Error to get request '" + str(error) + "'")
                try:
                    self.socket.send_multipart(['ERROR'.encode(), ("Error to get request '" + str(error) + "'").encode()])
                except zmq.ZMQError as error:
                    print("ERROR '" + str(error) + "'")
                break

    def read_message(self, message):
        print("Received message: ", message)
        self.socket.send_multipart(['OK'.encode(), ''.encode()])

    def get_file(self, hash_file, part, data):
        if part == 0:
            if os.path.exists('files/' + hash_file):
                print("ERROR - The file '" + hash_file + "' its already exist")
                self.socket.send_multipart(['ERROR'.encode(), 'the file already exist'.encode()])
            else:
                try:
                    print("create file '" + hash_file + "'")
                    file = open('files/' + hash_file, "ab")
                    file.write(data)
                    self.dictionary_files[hash_file] = file
                    self.socket.send_multipart(['OK'.encode(), ''.encode()])
                except IOError as error:
                    print("ERROR - The file '" + hash_file + "' its already exist (" + str(error) + ")")
                    self.socket.send_multipart(['OK'.encode(), 'the file already exist'.encode()])
        elif part == -1:
            if self.dictionary_files.get(hash_file):
                self.dictionary_files[hash_file].close()
                self.dictionary_files.pop(hash_file)
                print("the file '" + hash_file + "' its complete")
                self.socket.send_multipart(['OK'.encode(), ''.encode()])
            else:
                print("ERROR - The file to close '" + hash_file + "' no exist")
                self.socket.send_multipart(['ERROR'.encode(), 'the file to finish no exist or already finish'.encode()])
        else:
            if self.dictionary_files.get(hash_file):
                file = self.dictionary_files[hash_file]
                print(hash_file + " - receiving the part " + str(part))
                file.write(data)
                self.socket.send_multipart(['OK'.encode(), ''.encode()])
            else:
                print("ERROR - The file '" + hash_file + "' to write the part " + str(part) + " no exist")
                self.socket.send_multipart(['ERROR'.encode(), 'the file to write no exist or already created'.encode()])

    def send_file(self, hash_file, part):
        print("hash_file to send: "+hash_file)
        if os.path.exists('files/' + hash_file):
            try:
                file = open('files/' + hash_file, 'rb')
                file.read(utilities.chunk_file*part)
                data = file.read(utilities.chunk_file)
                if not data:
                    part = -1
                    self.socket.send_multipart(['send_file'.encode(), str(hash_file).encode(), str(part).encode(), ''.encode()])
                    # print("client response: " + self.socket.recv_multipart()[0].decode())
                else:
                    print("sending the part: "+str(part))
                    self.socket.send_multipart(['send_file'.encode(), str(hash_file).encode(), str(part).encode(), data])
                    # print("client response: " + self.socket.recv_multipart()[0].decode())
                file.close()
                print("finish to send the file")
            except IOError as error:
                self.socket.send_multipart(['ERROR'.encode(), ('Can´t find the file with the hash: '+hash_file).encode()])
                print(error)
        else:
            print("The file '" + hash_file + "' no exist")
            self.socket.send_multipart(['ERROR'.encode(), ('Can´t find the file with the hash: ' + hash_file).encode()])


if __name__ == '__main__':
    server = Server()
    print("Server running")
    server.listen()
