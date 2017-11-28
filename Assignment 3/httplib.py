import socket
import argparse
import ipaddress
import sys
import re
from urllib.parse import urlparse
from packet import Packet
from packet_constructor import Packet_Constructor
from packet_sender import Packet_Sender

CRLF = "\r\n"
router_host="localhost"
router_port=3000
seq_num = 0
router = (router_host, router_port)
conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
p_constructor = Packet_Constructor()
received_payload = False
payload = None

# Method to make a TCP connection to a specified hostname and port
# Connection is set on the global conn variable
def connect(host, port, peer_ip):
    global conn
    global p_constructor
    global router
    global seq_num
    print(peer_ip)
    print(port)
    data = b''

    p = Packet(packet_type=Packet_Constructor.syn_type,
                       seq_num=seq_num,
                       peer_ip_addr=peer_ip,
                       peer_port=port,
                       is_last_packet=False,
                       payload=data)
    
    conn.sendto(p.to_bytes(), router) 

    response, sender = conn.recvfrom(1024)
    p = Packet.from_bytes(response)

    if(p.packet_type == Packet_Constructor.syn_ack_type):
        p.packet_type = Packet_Constructor.ack_type
        conn.sendto(p.to_bytes(), sender)
    else:
        print(p.packet_type)
        connect(host, port, peer_ip)

    #TODO: TCP handshake here

# Method to close the open TCP connection
def close_connection():
	global conn
	conn.close()

# Method that takes in the response returned and parses it and returns a dictionary to allow a user to
# view which section of the response they prefer or to view the entirety of the response
def parse_response(response):
    status = ""
    code = ""
    body = ""
    header = ""
    value = 0
    crlf_count = 0

    header_data = b''
    body_data = b''
    for bit in response:
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

    for c in range(len(header_data)):
        if header_data[c] == "HTTP/1.1":
            code = header_data[c + 1]
            status = header_data[c + 2]
    
    for c in range(len(header_data)):
        if header_data[c] != "chunked":
            header += temp[c]
            header += " "
        if header_data[c] == "chunked":
            header += header_data[c]
            header += " "
            value = c + 1
            break
    for c in range(len(header_data)):
        if c < value:
            continue
        else:
            body += header_data[c]
            body += " "
        
    display = {"status": status, "code": code, "body": body, "header": header, "response": response}
    print("I am over here")
    return display

def communicate_with_server(data, host, port):
    global conn
    global router
    global received_payload
    global payload

    try:
        received_payload = False
        payload = None
        peer_ip = ipaddress.ip_address(socket.gethostbyname(host))
        connect(host, port, peer_ip)
        Packet_Sender.send_as_packets(data, conn, router, peer_ip, port)
        while(not received_payload):
            data, sender = conn.recvfrom(1024)
            #TODO: these packets should be received on different threads, like how httpfs receives packets
            threading.Thread(target=handle_packet_client, args=(conn, data, sender)).start()
    finally:
        close_connection()
        return payload

def handle_packet_client(conn, data, sender):
    global p_constructor
    global received_payload
    global payload

    p = Packet.from_bytes(data)
    print(p.seq_num)
    payload = p_constructor.add_packet(p, conn, sender)
    if(payload):
        print(payload)
        received_payload = True
    else:
        print("payload was not received.")
    
# Method to perform a get request to a specified url with the given headers and body
# @param url: the url to perform the get request on
# @param port: the port to perform the get request on
# @param headers: a dict of http headers where keys are the header names and values are the header values
# @param body: a string containing the http body
# @return: the response from the server
def get_request(url, port, headers, body):
    global conn
    # Parse the url
    url = urlparse(url)
    path = url.path
    if path == "":
        path = "/"
    host = url.netloc
    headers["Host"] = host
    # Connect to the host
    
    # Construct the message
    message = "GET %s HTTP/1.1%s" % (path, CRLF)
    for header in headers:
        message = "%s%s: %s%s"%(message, header, headers[header], CRLF)
    message = message + CRLF + body + CRLF
    # Send message
    response = communicate_with_server(message.encode('utf-8'), host, port)
    
    return parse_response(response)

# Method to perform a post request to a specified url with the given headers and query
# @param url: the url to perform the get request on
# @param port: the port to perform the get request on
# @param headers: a dict of http headers where keys are the header names and values are the header values
# @param queries: a dict containing the queries for this request where keys are the query names and values are the query values
# @return: the response from the server
def post_request(url, port, headers, body):
    global conn
    url = urlparse(url)
    path = url.path
    if path == "":
        path = "/"
    host = url.netloc
    headers["Host"] = host
    # Connect to the host
    connect(host, port)
    # Construct the message
    message = "POST %s HTTP/1.1%s" % (path, CRLF)
    for header in headers:
        message = "%s%s: %s%s"%(message, header, headers[header], CRLF)
    message = message + CRLF
    byte_message = message.encode('utf-8')
    # If there are queries, then add those to the message
    byte_message = byte_message + body + CRLF.encode('utf-8')
    # Send message
    response = communicate_with_server(byte_message, host, port)
        
    return parse_response(response)
