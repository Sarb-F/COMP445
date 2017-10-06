import socket
import argparse
import sys
import httplib
import json
import pycurl
import StringIO

#! /usr/bin/env python
# NOTE FOR GAB: This is what you can turn into the httpc curl-like thing. You'll need to change the name of some arguments and add a bunch, but some stuff is already there to get you started. Also, obviously, rename this file to httpc.py
# NOTE FOR GAB: don't forget to edit the readme file in this folder to have httpc instead of what it has

##if args.post:
##    response = httplib.post_request(args.url, args.port, "")
##elif args.get:
##    response = httplib.get_request(args.url, args.port, {}, "")
    

##print(response)

def run(args):
	url = args.url
	port = args.port
	post = args.post
	get = args.get
	verbose = args.v
	file = args.f
	header = args.h
	inline = args.d
	data = inline
	args = ""
	form = ""
	json = ""
	argsTrue = False
	formTrue = False
	jsonTrue = False
	isAForm = True
	finalArgs = {}
	finalForm = {}
	finalJson = {}
	temp = "{}"
	response = StringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, 'https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere')
	c.setopt(c.WRITEFUNCTION, response.write)
	c.setopt(c.HTTPHEADER, ['Content-Type: application/json','Accept-Charset: UTF-8'])
	c.setopt(c.POSTFIELDS, '@request.json')
	c.perform()
	c.close()
	print (response.getvalue())
	response.close()
def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--url", help="server host", type=str, default="http://www.google.ca", required=True)
        parser.add_argument("--port", help="server port", type=int, default=80, required=True)
        parser.add_argument("--post", help="Use post", action="store_true")
        parser.add_argument("--get", help="Use get", action="store_true")
        parser.add_argument("-v", help="starts it in verbose mode", action="store_true")
        parser.add_argument("--f", help="filename", type=str, default="")
        parser.add_argument("--d", help="inline data", type=str, default="")
        parser.add_argument("--h", help="Input a header", type=str, default='')
        parser.set_defaults(func=run)
        args = parser.parse_args()
        args.func(args)

if __name__=="__main__":
	main()
