import socket
import argparse
import sys
import httplib
import json

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
	argsTrue = False
	formTrue = False
	isAForm = True
	finalArgs = {}
	finalForm = {}
	temp = "{}"
	
	for c in url:
                if c is "?":
                        lhs, rhs = url.split("?", 1)
                if c is "&":
                        args = rhs.split("&")
                        argsTrue = True
	if(argsTrue is True):
                for c in args:
                        lhs, rhs = c.split("=", 1)
                        finalArgs[lhs] = rhs
        
	if(header is not 'h' and header is not ""):
            header = header.replace("'", '"')
            j = json.loads(header)
	else:
            j = {}

	dict = {'"args"': finalArgs, '"headers"': header, '"url"': url}
	for c in inline:
                if c is "&":
                        isAForm = False
	
	if(isAForm is True):
                for c in inline:
                        if c is "&":
                                form = inline.split("&")
                                formTrue = True
                if(formTrue is True):
                        temp = ""
                        for c in form:
                                lhs, rhs = c.split("=", 1)
                                finalForm[lhs] = rhs	
        
	if(temp is not "{}"):
                inline = "Null"
                data = '""'
                
	if(file is not ""):
                with open(file) as data_file:    
                    jsonOutput = json.load(data_file)
                
	dictPost = {'"args"': finalArgs, '"data"': data, '"files"': jsonOutput, '"form"': finalForm, '"headers"': header, "'json'": inline, '"url"': url}

	if(verbose is True):
            if post:
                response = httplib.post_request(url, port, j, "")
                print(response['status'])
                print(response['code'])
                print(response['body'])
                print(response['header'])
                print(response['response'])
                print(dictPost)
            if get:
                if(inline is '' and file is ''):
                    response = httplib.get_request(url, port, j, "")
                    print(response['status'])
                    print(response['code'])
                    print(response['body'])
                    print(response['header'])
                    print(response['response'])
                    print(dict)
                else:
                    print("Cannot perform a --f and a --d command for --get")

	if(verbose is False):
            if post:
                httplib.post_request(url, port, j, "")
                print(dictPost)
            if get:
                if(inline is '' and file is ''):
                    httplib.get_request(url, port, j, "")
                    print(dict)                    
                else:
                    print("Cannot perform a --f and a --d command for --get")
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
