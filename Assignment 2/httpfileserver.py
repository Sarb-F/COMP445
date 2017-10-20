import socket
import threading
import argparse
import os
import json
import mimetypes

CRLF = "\r\n"

#TODO: add in debug printing messages
#TODO: add in the command line arguments the assignment describes

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

def get_file_dir():
    current_dir = os.getcwd()
    file_dir = current_dir + "\\files\\"
    return file_dir

def get_message_body(data):
    parsedData = data.split(CRLF)
    #TODO: add error handling for if there is actually no body
    #print(parsedData)
    #second last split should be the body
    return parsedData[len(parsedData)-2]

def get_filename(parsedData):
    if parsedData[1] == '\\' or parsedData[1] == '/':
        return
    return parsedData[1][1:]

def get_file_mimetype(filename):
    #TODO: add error handling if file doesn't exist
    file_dir = get_file_dir()
    mimetypes.init()
    return mimetypes.guess_type(file_dir + filename)
    '''
    mime = magic.Magic(mime=True)
    return mime.from_file(file_dir + filename)'''

def get_headers(data):
    headers = {}
    parsedData = data.split(CRLF)
    for i in range(1, len(parsedData)):
        header = parsedData[i]
        #If we reached the empty line between header and body, stop reading header elements
        if header == '':
            break
        headerComponents = header.split(": ")
        headers[headerComponents[0]] = headerComponents[1]
    print(headers)
    return headers

def handle_get(parsedData):
    file_dir = get_file_dir()
    filename = get_filename(parsedData)
    if not filename:
        return str(os.listdir(file_dir)).encode('utf-8')
    else:
        #TODO: add error handling for if file doesn't exist
        '''file = open(file_dir + filename, 'r')
        response_body = ""
        for line in file:
            response_body = response_body + line'''
        file = open(file_dir + filename, 'rb')
        response_body = file.read(10000)
        return response_body

def handle_post(parsedData, data):
    file_dir = get_file_dir()
    post_command = parsedData[1]
    #TODO: add error handling for if command does not contain a filename (as in, it is just /)
    #TODO: add error handling for if the filename is an invalid filename
    filename = post_command[1:]
    
    overwrite = True
    headers = get_headers(data)
    if headers and 'overwrite' in headers:
        overwrite = (headers['overwrite'] == 'true')
    if not overwrite:
        file_list = os.listdir(file_dir)
        if filename in file_list:
            #TODO: error message here for if overwrite is false and there is already a file with the requested name
            return
    
    file = open(file_dir + filename, 'w')
    message_body = get_message_body(data)
    #print(message_body)
    #TODO: add error handling if message body is null or not a valid json
    body_json = json.loads(message_body)
    file_contents = body_json['contents']
    file.write(file_contents)

def handle_client(conn, addr, host, port):
    print('New client from', addr)
    try:
        data = conn.recv(10024)
        if not data:
            return
        data = data.decode('utf-8')
        print("data\n\n")
        print(data)
        parsedData = data.split()
        #print(parsedData)
        response_body = ""
        #TODO: edit the response message if there is an error. Should have a 4xx type response code and a fitting message
        response = "HTTP/1.1 200 OK%sConnection: keep-alive%sServer: %s%s"%(CRLF, CRLF, host, CRLF)
        if parsedData[0] == "GET":
            filename = get_filename(parsedData)
            if filename:
                type = get_file_mimetype(filename)
                print(type)
                response = response + "Content-Disposition: attachment;filename=\"" + filename + "\"" + CRLF + "Content-Type: " + type[0] + CRLF
            response_body = handle_get(parsedData)
        elif parsedData[0] == "POST":
            response_body = handle_post(parsedData, data)
        #print(response_body)
        #if response_body:
        #    response = response + CRLF + response_body + CRLF
        bytes = response.encode('utf-8')
        if response_body:
            bytes = bytes + CRLF.encode('utf-8')
            bytes = bytes + response_body
            bytes = bytes + CRLF.encode('utf-8')
        conn.sendall(bytes)
    finally:
        conn.close()


# Usage python httpfileserver.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="file server port", type=int, default=8007)
args = parser.parse_args()
run_server('localhost', args.port)
