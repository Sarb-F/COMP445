import socket
import argparse
import sys
import re
from urllib.parse import urlparse

CRLF = "\r\n"

# Method to make a TCP connection to a specified hostname and port
# Connection is set on the global conn variable
def connect(host, port):
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(100.00)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn.connect((host, port))

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
    temp = response.split()
    
    for c in range(len(temp)):
        if temp[c] == "HTTP/1.1":
            code = temp[c + 1]
            status = temp[c + 2]
    
    for c in range(len(temp)):
        if temp[c] != "chunked":
            header += temp[c]
            header += " "
        if temp[c] == "chunked":
            header += temp[c]
            header += " "
            value = c + 1
            break

    for c in range(len(temp)):
        if c < value:
            continue
        else:
            body += temp[c]
            body += " "

    display = {"status": status, "code": code, "body": body, "header": header, "response": response}
    return display

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
    try:
        # Connect to the host
        connect(host, port)
        # Construct the message
        message = "GET %s HTTP/1.1%s" % (path, CRLF)
        for header in headers:
            message = "%s%s: %s%s"%(message, header, headers[header], CRLF)
        message = message + CRLF + body + CRLF
        # Send message
        conn.send(message.encode('utf-8'))
        buf = conn.recv(10000)
        buf = buf.decode('utf-8')
    finally:
        close_connection()
    return parse_response(buf)

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
    try:
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
        conn.send(byte_message)
        buf = conn.recv(10000)
        buf = buf.decode('utf-8')
    finally:
        close_connection()
    return parse_response(buf)
