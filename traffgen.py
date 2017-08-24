import socket
import time
import random
import string
from optparse import OptionParser

DEFAULT_PORT = 2127  # Arbitrary non-privileged port
FLAG_OK = "OK"
DEFAULT_BUFFER_SIZE = 1024


class Sender(object):

    def __init__(self, receiver_ip, data_size, send_count):
        self.receiver_ip = receiver_ip
        self.data_size = data_size
        self.sending_count = send_count
        self.success_count = 0
        self.sleep = 0

    @staticmethod
    def create_data(size):
        text = ""
        for num in range(0, size):
            char = random.choice(string.ascii_uppercase + string.digits)
            text += char
        data = bytearray(text, "utf8")
        return data

    def start(self):
        data = Sender.create_data(self.data_size)
        while self.success_count < self.sending_count:
            success = Sender.send_data(self.receiver_ip, data)
            if success:
                self.success_count += 1
                time.sleep(self.sleep)
            else:
                time.sleep(1)
        return True

    @staticmethod
    def send_data(address, data):
        print("Sending to: " + address)
        destination = (address, DEFAULT_PORT)
        out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            out_sock.connect(destination)
            out_sock.sendall(data)
            out_sock.close()
        except socket.error:
            print("Socket error..")
            return False
        return True


class Receiver(object):

    def __init__(self):
        self.receive_count = 0
        self.backlog = 128

    def start(self):
        host = ''  # Symbolic name meaning all available interfaces
        source = (host, DEFAULT_PORT)
        out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        out_sock.bind(source)
        out_sock.listen(self.backlog)
        while True:
            Receiver.__accept(out_sock)

    @staticmethod
    def __accept(outgoing_socket):
        in_sock, incoming_ip = outgoing_socket.accept()
        print('Incoming connection from: ', incoming_ip)
        data = ""
        count = 0
        while True:
            try:
                chunk = in_sock.recv(DEFAULT_BUFFER_SIZE)
                if not chunk:
                    in_sock.close()
                    print("Finished receiving! Total size: " + str(len(data)))
                    print("------------------------------")
                    print("Waiting...")
                    break
                count += 1
                print("Retrieving chunk #" + str(count) + " : " + chunk)
                data += chunk
            except socket.error:
                print("Error Occurred.")
                break

        in_sock.close()


def get_options():
    parser = OptionParser()
    parser.add_option("--server")
    parser.add_option("--server_ip")
    parser.add_option("--data_size")
    parser.add_option("--send_count")
    parser.add_option("--sleep")
    (options, args) = parser.parse_args()
    return options


def is_server(options):
    server_option = options.server
    result = False
    if server_option == "true":
        result = True
        print("Running as Server..")
    else:
        print("Running as Client..")
    return result


def main():
    options = get_options()
    if is_server(options):
        server = Receiver()
        server.start()
    else:
        server_ip = options.server_ip
        data_size = options.data_size
        send_count = options.send_count
        sleep = options.sleep
        if server_ip and data_size and send_count:
            sender = Sender(server_ip, int(data_size), int(send_count))
            if sleep:
                sender.sleep = int(sleep)
            sender.start()
        else:
            print("Incorrect options!")

main()
