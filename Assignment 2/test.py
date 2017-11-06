import socket
import threading
import argparse
import time

def testing(filename):
    if('&' in filename or '$' in filename):
        print("Found it!")

testing("Hello$.txt")
