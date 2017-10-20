import socket
import threading
import argparse
import os

CRLF = "\r\n"

def run_server(host, port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(5)
        print('File server is listening at', port)
        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_client, args=(conn, addr, host, port)).start()
    finally:
        listener.close()

def handle_get(parsedData):
    current_dir = os.getcwd()
    file_dir = current_dir + "\\files\\"
    get_command = parsedData[1]
    if get_command == '\\' or get_command == '/':
        return str(os.listdir(file_dir))
    else:
        filename = get_command[1:]
        #TODO: add error handling for if file doesn't exist
        file = open(file_dir + filename, 'r')
        response_body = ""
        for line in file:
            response_body = response_body + line
        return response_body

def handle_client(conn, addr, host, port):
    print('New client from', addr)
    try:
        data = conn.recv(1024)
        if not data:
            return
        data = data.decode('utf-8')
        print(data)
        parsedData = data.split()
        print(parsedData)
        response_body = ""
        if parsedData[0] == "GET":
            response_body = handle_get(parsedData)
        print(response_body)
        response = "HTTP/1.1 200 OK%sConnection: keep-alive%sServer: %s%s"%(CRLF, CRLF, host, CRLF)
        if response_body:
            response = response + CRLF + response_body + CRLF
        conn.sendall(response.encode('utf-8'))
    finally:
        conn.close()


# Usage python httpfileserver.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="file server port", type=int, default=8007)
args = parser.parse_args()
run_server('localhost', args.port)
