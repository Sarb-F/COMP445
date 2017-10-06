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
    conn.settimeout(10.00)
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
    #print(temp)
    
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
        buf = conn.recv(1000)
        buf = buf.decode('utf-8')
    finally:
        close_connection()
    return parse_response(buf)

# NOTE FOR GAB: From what I read on POST requests, the body is mainly used for the queries, but idk if it works differently for files (which can also be sent using POST), so maybe you will have to change the "queries" parameter to just a simple "body" string parameter and move the parsing queries part of this method into the httpc script
# NOTE FOR GAB: There is also a lot of duplication between this method and the get method, but honestly idc that much. Feel free to clean it up if you feel like it, but eh
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
        # If there are queries, then add those to the message
        message = message + body + CRLF
        # Send message
        conn.send(message.encode('utf-8'))
        buf = conn.recv(1000)
        buf = buf.decode('utf-8')
    finally:
        close_connection()
    return parse_response(buf)
