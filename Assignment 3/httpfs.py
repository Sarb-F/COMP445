import socket
import threading
import argparse
import os
import os.path
import json
import mimetypes
from packet import Packet
from packet_constructor import Packet_Constructor

CRLF = "\r\n"
debug = False
file_dir = os.getcwd() + "\\files\\"
p_constructor = Packet_Constructor()

def run_server(host, port, dir):
    global file_dir
    file_dir = dir
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        #listener.listen(5)
        print('File server is listening at', port)
        while True:
            data, sender = conn.recvfrom(1024)
            handle_packet(conn, data, sender)
            #threading.Thread(target=handle_client, args=(conn, addr, host, port)).start()
    finally:
        conn.close()

def get_file_dir():
    global file_dir
    return file_dir

def get_filename(parsedData):
    if parsedData[1] == '\\' or parsedData[1] == '/':
        return
    return parsedData[1][1:]

def get_file_mimetype(filename):
    if(os.path.isfile(get_file_dir() + filename) == False):
        raise IOError("File " + filename + " does not exist.")   
    file_dir = get_file_dir()
    mimetypes.init()
    return mimetypes.guess_type(file_dir + filename)

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
    if(debug):
        print("The following headers were found")
        print(headers)
    return headers

def handle_get(parsedData):
    file_dir = get_file_dir()
    filename = get_filename(parsedData)
        
    if not filename:
        return str(os.listdir(file_dir)).encode('utf-8')
    else:
        if(os.path.isfile(file_dir + filename) == False):
            raise IOError("File " + filename + " does not exist for GET.")
        response_body = b''
        with open(file_dir + filename, 'rb') as file:
            while True:
                newData = file.read(1024)
                if not newData:
                    break
                response_body += newData
        return response_body

def handle_post(parsedData, header_data, body_data):
    file_dir = get_file_dir()
    post_command = parsedData[1]
    if(post_command == '/' or post_command == '\\'):
        raise SystemError("Command did not contain a file.")
    
    filename = post_command[1:]
    if(('~' in filename) or ('#' in filename) or ('%' in filename) or ('&' in filename) or ('*' in filename) or ('{' in filename) or ('}' in filename) or (':' in filename) or ('<' in filename) or ('>' in filename) or ('?' in filename) or ('+' in filename) or ('|' in filename) or ('"' in filename)):
        raise IOError("File " + filename + " is an invalid filename.")
    
    overwrite = True
    headers = get_headers(header_data)
    if headers and 'overwrite' in headers:
        overwrite = (headers['overwrite'] == 'true')
    if not overwrite:
        file_list = os.listdir(file_dir)
        if filename in file_list:
            if(os.path.isfile(filename) == True and overwrite == False):
                raise SystemError("File " + filename + " already exists for POST and overwrite was false.")
            return
    
    file = open(file_dir + filename, 'wb')

    if(body_data == CRLF.encode()):
        raise SystemError("Message body was empty.")
    file.write(body_data)

def checkIfGoodDirectoryGet(filename):
    if(filename and ('/' in filename or '\\' in filename)):
        raise Exception("You cannot go there for GET! Stop trying to hack our system.")

def checkIfGoodDirectoryPost(filename):
    cwd = get_file_dir()
    if('/' in filename or '\\' in filename):
        raise Exception("You cannot Post the file there! Stop trying to hack our system.")

def handle_packet(conn, data, sender):
    global p_constructor
    p = Packet.from_bytes(data)
    payload = p_constructor.add_packet(p, conn, sender)
    '''p = Packet.from_bytes(data)
    if p.seq_num is 0:
        current_payload = p.payload
    else:
        current_payload += p.payload'''
    
    '''if(debug):
        print('New client from', addr)
    data = b''
    conn.settimeout(0.50)
    #Read in data from the socket until there is a timeout. Then we know there is no more to read
    while True:
        try:
            newData = conn.recv(1024)
            if(debug):
                print(newData)
            if not newData:
                break
            data +=  newData
            break;
        except:
            break'''
    '''print(sender)
    print(p.seq_num)
    print(data)
    print(p.peer_ip_addr)
    print(p.peer_port)'''
    if(payload):
        print("Received last packet")
        response = handle_data(payload, sender)
        print("Sending packets")
        print(response)
        Packet_Constructor.send_as_packets(response, conn, sender, p.peer_ip_addr, p.peer_port)
        '''new_p = Packet(packet_type=0,
                       seq_num=p.seq_num,
                       peer_ip_addr=p.peer_ip_addr,
                       peer_port=p.peer_port,
                       is_last_packet=True,
                       payload=response)
        print("Sending packet")
        print(response)
        conn.sendto(new_p.to_bytes(), sender)'''
        print("Sent!")
    else:
        print("is not the last packet")

def handle_data(data, addr):
    host = "localhost"
    #Because the body of the message is often binary, we cannot decode it. So look for /r/n/r/n which marks the start of the body and parse header and body separately
    crlf_count = 0
    header_data = b''
    body_data = b''
    for bit in data:
        bit = bit.to_bytes(1, byteorder='big')
        if crlf_count < 4:
            header_data += bit
            if (crlf_count == 0 or crlf_count == 2) and bit == b'\r':
                crlf_count += 1
            elif (crlf_count == 1 or crlf_count == 3) and bit == b'\n':
                crlf_count += 1
            else:
                crlf_count = 0
        else:
            body_data += bit
    header_data = header_data.decode('utf-8')
    parsedData = header_data.split()
    response_body = ""
    try:
        response = "HTTP/1.1 200 OK%sConnection: keep-alive%sServer: %s%s"%(CRLF, CRLF, host, CRLF)
        if parsedData[0] == "GET":
            filename = get_filename(parsedData)
            checkIfGoodDirectoryGet(filename)
            if(debug):
                    print("GET request")
            if filename:
                if(debug):
                    print("GET request for file " + filename)
                type = get_file_mimetype(filename)
                filetype = type[0]
                if(filetype is None):
                    filetype = ""
                response = response + "Content-Disposition: attachment;filename=\"" + filename + "\"" + CRLF + "Content-Type: " + filetype + CRLF
            response_body = handle_get(parsedData)
        elif parsedData[0] == "POST":
            filename = get_filename(parsedData)
            checkIfGoodDirectoryPost(filename)
            if(debug):
                print("POST request for file " + filename)
            response_body = handle_post(parsedData, header_data, body_data)
        bytes = response.encode('utf-8')
        if response_body:
            bytes = bytes + CRLF.encode('utf-8')
            bytes = bytes + response_body
            bytes = bytes + CRLF.encode('utf-8')
        return bytes
        #conn.sendall(bytes)
    except IOError as IO:
        if(debug):
            print("404 Error triggered")
        response = "HTTP/1.1 404 ERROR: File could not be found%sConnection: keep-alive%sServer: %s%s"%(CRLF, CRLF, host, CRLF)
        response = response + str(IO)
        bytes = response.encode('utf-8')
        return bytes
        #conn.sendall(bytes)
    except SystemError as SE:
        if(debug):
            print("400 Error triggered")
        response = "HTTP/1.1 400 ERROR: Bad Request%sConnection: keep-alive%sServer: %s%s"%(CRLF, CRLF, host, CRLF)
        response = response +str(SE)
        bytes = response.encode('utf-8')
        return bytes
        #conn.sendall(bytes)
    except Exception as e:
        if(debug):
            print("403 Error triggered")
        response = "HTTP/1.1 403 ERROR: Security Error%sConnection: keep-alive%sServer: %s%s"%(CRLF, CRLF, host, CRLF)
        response = response + str(e)
        bytes = response.encode('utf-8')
        return bytes
        #conn.sendall(bytes)

# Usage python httpfileserver.py [--port port-number]
current_dir = os.getcwd() + "\\files\\"
parser = argparse.ArgumentParser()
parser.add_argument("-p", help="file server port", type=int, default=8007)
parser.add_argument("-v", help="verbose", action="store_true")
parser.add_argument("-d", help="file directory", type=str, default=current_dir)
args = parser.parse_args()
if(os.path.isdir(args.d)):
    if(args.v):
        debug = True
        print("Running with verbose in directory " + args.d)
    run_server('localhost', args.p, args.d)
else:
    print("Directory " + args.d + " provided is not an existing directory")