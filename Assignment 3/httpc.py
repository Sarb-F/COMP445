import socket
import argparse
import sys
import httplib
import json

# Method to run the curl app, takes in the arguments given by the user. 
# Then helps parse through the information and determines whether or not the user can perform that curl option.
# Sends the information to the HTTP library and retrieves curl information and parses it for the user to view. 
def run(args):
        #retrieves all of the arguments given by the user. 
	url = args.url
	port = args.port
	post = args.post
	get = args.get
	verbose = args.v
	file = args.f
	header = args.h
	inline = args.d
	data = inline
	output = args.o
	args = ""
	form = ""
	argsTrue = False
	formTrue = False
	isAForm = True
	finalArgs = {}
	finalForm = {}
	temp = "{}"
	jsonOutput = {}

	#Parses url
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
            
        # output to be displayed for get requests. 
	dict = {'"args"': finalArgs, '"headers"': header, '"url"': url}

	# deals with the parsing of the form for a post, otherwise will be placed in data and json parts of the curl output
	for c in inline:
                if c is "&":
                        isAForm = True
                        print("ok")
	
	if(isAForm is True):
                for c in inline:
                        if c is "&":
                                form = inline.split("&")
                                formTrue = True
                                print("hello")
                if(formTrue is True):
                        temp = ""
                        for c in form:
                                lhs, rhs = c.split("=", 1)
                                finalForm[lhs] = rhs
                        formTrue = False
        
	if(temp is not "{}"):
                inline = "Null"
                data = '""'

        # takes json information from a file to be sent through post. If the information is in the shape of a form it will process that instead 
	if(file is not ""):
                '''data_file = open(file, 'rb')
                jsonOutput = data_file.read(100000)'''
                jsonOutput = b''
                with open(file, 'rb') as data_file:
                    while True:
                        newData = data_file.read(1024)
                        if not newData:
                            break
                        jsonOutput += newData
                '''        jsonOutput = json.load(data_file)
                        temp = jsonOutput
                        
                for c in temp:
                        if c is "&":
                                isAForm = True
                
                if(isAForm is True):
                        for c in temp:
                                if c is "&":
                                        form = temp.split("&")
                                        formTrue = True
                        if(formTrue is True):
                                jsonOutput = {}
                                for c in form:
                                        lhs, rhs = c.split("=", 1)
                                        jsonOutput[lhs] = rhs'''
                
	dictPost = {'"args"': finalArgs, '"data"': data, '"files"': jsonOutput, '"form"': finalForm, '"headers"': header, "'json'": inline, '"url"': url}

        # used if the user wants a verbose output
	if(verbose is True):
            if post:
                if((file is "" and inline is "") or (file is "" and inline is not "") or (file is not "" and inline is "")): # checks that the user did not input both --f and --d at the same time
                        if(file is not ""): # if user inputted a file
                                if(output is not ""): # Implemented -0 functionality
                                        response = httplib.post_request(url, port, j, jsonOutput) # send to post and receive a response
                                        orig_stdout = sys.stdout
                                        f = open(output, 'w')
                                        sys.stdout = f

                                        print(response['body'])

                                        sys.stdout = orig_stdout
                                        f.close()

                                        print(response['status']) # print the status of the message
                                        print(response['code']) # print the status code of the message
                                        print(response['body']) # print the body of the message
                                        print(response['header']) # print the header of the message
                                        print(response['response']) # print the response of the message
                                        print(dictPost) # print entire post response
                                else:
                                        response = httplib.post_request(url, port, j, jsonOutput) # send to post and receive a response
                                        print(response['status']) # print the status of the message
                                        print(response['code']) # print the status code of the message
                                        print(response['body']) # print the body of the message
                                        print(response['header']) # print the header of the message
                                        print(response['response']) # print the response of the message
                                        print(dictPost) # print entire post response                                
                                
                        else: # if user inputed data
                                if(output is not ""): # Implemented -0 functionality
                                        response = httplib.post_request(url, port, j, inline) # send to post and receive a response
                                        orig_stdout = sys.stdout
                                        f = open(output, 'w')
                                        sys.stdout = f

                                        print(response['body'])

                                        sys.stdout = orig_stdout
                                        f.close()

                                        print(response['status']) # print the status of the message
                                        print(response['code']) # print the status code of the message
                                        print(response['body']) # print the body of the message
                                        print(response['header']) # print the header of the message
                                        print(response['response']) # print the response of the message
                                        print(dictPost) # print entire post response
                                else:                                        
                                        body = inline.encode()
                                        response = httplib.post_request(url, port, j, body) # send to post and receive a response
                                        print(response['status']) # print the status of the message
                                        print(response['code']) # print the status code of the message
                                        print(response['body']) # print the body of the message
                                        print(response['header']) # print the header of the message
                                        print(response['response']) # print the response of the message
                                        print(dictPost) # print entire post response
                else:
                        print("Cannot perform a --f and a --d command together for --post")
            if get:
                if(inline is '' and file is ''):
                    if(output is not ""):
                            response = httplib.get_request(url, port, j, "") # send to get and receive response
                            orig_stdout = sys.stdout
                            f = open(output, 'w')
                            sys.stdout = f

                            print(response['body'])

                            sys.stdout = orig_stdout
                            f.close()

                            print(response['status']) # print the status of the message
                            print(response['code']) # print the status code of the message
                            print(response['body']) # print the body of the message
                            print(response['header']) # print the header of the message
                            print(response['response']) # print the response of the message
                            print(dict) # print entire post response
                    else:
                            response = httplib.get_request(url, port, j, "") # send to get and receive response
                            print("response coming")
                            print(response['status'])
                            print(response['code'])
                            print(response['body'])
                            print(response['header'])
                            print(response['response'])
                            print(dict) # print entire get response
                else:
                    print("Cannot perform a --f and a --d command for --get")

        # used if the user does not want a verbose output
	else:
            if post:
                if((file is "" and inline is "") or (file is "" and inline is not "") or (file is not "" and inline is "")):
                        if(file is not ""):
                                if(output is not ""):
                                        response = httplib.post_request(url, port, j, jsonOutput)
                                        print(dictPost)
                                        orig_stdout = sys.stdout
                                        f = open(output, 'w')
                                        sys.stdout = f

                                        print(response['body'])

                                        sys.stdout = orig_stdout
                                        f.close()
                                else:
                                        httplib.post_request(url, port, j, jsonOutput)
                                        print(dictPost)
                        else:
                                if(output is not ""):
                                        response = httplib.post_request(url, port, j, inline)
                                        print(dictPost)
                                        orig_stdout = sys.stdout
                                        f = open(output, 'w')
                                        sys.stdout = f

                                        print(response['body'])

                                        sys.stdout = orig_stdout
                                        f.close()
                                else:
                                        httplib.post_request(url, port, j, inline)
                                        print(dictPost)
                else:
                        print("Cannot perform a --f and a --d command together for --post")
            if get:
                if(inline is '' and file is ''):
                        if(output is not ""):
                                response = httplib.get_request(url, port, j, "") # send to get and receive response
                                orig_stdout = sys.stdout
                                f = open(output, 'w')
                                sys.stdout = f

                                print(response['body'])

                                sys.stdout = orig_stdout
                                f.close()
                                print(dict)
                        else:
                                httplib.get_request(url, port, j, "")
                                print(dict)                                        
                else:
                    print("Cannot perform a --f and a --d command for --get")
                    
# main area that handles the receiving of curl commands from the user and sets defaults where necessary
def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--url", help="server host", type=str, default="http://www.google.ca", required=True)
        parser.add_argument("--port", help="server port", type=int, default=80)
        parser.add_argument("--post", help="Use post", action="store_true")
        parser.add_argument("--get", help="Use get", action="store_true")
        parser.add_argument("-v", help="starts it in verbose mode", action="store_true")
        parser.add_argument("--f", help="filename", type=str, default="")
        parser.add_argument("--d", help="inline data", type=str, default="")
        parser.add_argument("--h", help="Input a header", type=str, default='')
        parser.add_argument("--o", help="output to a designated file", type=str, default="")
        parser.set_defaults(func=run)
        args = parser.parse_args()
        args.func(args)
        #python httpc.py --post --url "http://localhost/thing2.pdf" --port 8007 -v --f "Comp445-F17_LA3.pdf"
        #python httpc.py --get --url "http://localhost/" --port 8007 -v

# function that runs the entire program
if __name__=="__main__":
	main()
