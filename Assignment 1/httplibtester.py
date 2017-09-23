import socket
import argparse
import sys
import httplib

# NOTE FOR GAB: This is what you can turn into the httpc curl-like thing. You'll need to change the name of some arguments and add a bunch, but some stuff is already there to get you started. Also, obviously, rename this file to httpc.py
# NOTE FOR GAB: don't forget to edit the readme file in this folder to have httpc instead of what it has
parser = argparse.ArgumentParser()
parser.add_argument("--url", help="server host", default="http://www.google.ca")
parser.add_argument("--port", help="server port", type=int, default=80)
parser.add_argument("--post", help="Use post", action="store_true")
args = parser.parse_args()
if args.post:
    response = httplib.post_request(args.url, args.port, {})
else:
    response = httplib.get_request(args.url, args.port, {})
print(response)