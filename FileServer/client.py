import zmq
import sys
from utilities import md5_for_file


class Client:
    port_server = "9999"
    chunk_file = 20
    context = None
    socket = None

    def __init__(self):
        self.context = zmq.Context()
        print("Connecting to server...")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % self.port_server)
        if len(sys.argv) > 2:
            self.socket.connect("tcp://localhost:%s" % self.port_server)

    def send_message(self, message):
        self.socket.send(message.encode())
        response = self.socket.recv().decode()
        print(response)

    def send_file(self, file_name):
        hash_file = md5_for_file(file_name)
        print("hash_file to send: "+hash_file)
        file = open(file_name, 'r')
        part = 0
        while True:
            data = file.read(self.chunk_file)
            if not data:
                part = -1
                self.socket.send_multipart([str(hash_file).encode(), str(part).encode(), ''.encode()])
                print("server response: " + self.socket.recv_string())
                break
            print("sending the part: "+str(part))
            self.socket.send_multipart([str(hash_file).encode(), str(part).encode(), data.encode()])
            server_response = self.socket.recv_string()
            print("server response: " + server_response)
            part += 1
            if server_response != 'ok':
                break
        print("finish to send the file")


if __name__ == '__main__':
    client = Client()
    while True:
        print("press any key to send server file:")
        input()
        client.send_file('server.py')
        print("press any key to send client file:")
        input()
        client.send_file('client.py')
        print("press any key to send utilities file:")
        input()
        client.send_file('utilities.py')
