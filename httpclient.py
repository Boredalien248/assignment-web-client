#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# importing necessary modules 
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # splits the whole response wherever there is a space and makes an array and provides the data in index 1 
        code = data.split(" ")
        return int(code[1])

    def get_headers(self,data):
        # splits the whole response wherever "\r\n\r\n" is present and makes an array and provides the data in index 0 as the header always comes before the first "\r\n\r\n"
        header = data.split("\r\n\r\n")[0]
        header += "\r\n\r\n"
        return header

    def get_body(self, data):
        # splits the whole response wherever "\r\n\r\n" is present and makes an array and provides the data in index 1 as the body always comes after the first "\r\n\r\n"
        body = data.split("\r\n\r\n")
        if body is None:
            return ''
        else:
            return body[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        # buffer = bytearray()
        # done = False
        # while not done:
        #     part = sock.recv(1024)
        #     if (part):
        #         buffer.extend(part)
        #     else:
        #         done = not part
        # return buffer.decode('utf-8')
        
        # goes through the the data received and gets every data from the response even if it crosses 1024 bytes 
        the_response = ''
        done = False 
        while not done:
            message = sock.recv(1024)
            if len(message) <= 0:
                done = True
            the_response += message.decode("utf-8")
        
        return the_response

    def GET(self, url, args=None):
        code = 500
        body = ""

        # the formatting used 
        FORMAT = 'utf-8'

        # finding out the port, hostname and the scheme used in the request
        port = urllib.parse.urlparse(url).port
        host = urllib.parse.urlparse(url).hostname
        scheme = urllib.parse.urlparse(url).scheme
        path = urllib.parse.urlparse(url).path
        query = urllib.parse.urlparse(url).query

        # returning 400 error if port and host not mentioned 
        if port is None and host is None:
            return HTTPResponse(400, body)
        
        # setting default port if none mentioned or provided 
        if port is None and scheme == 'https':
            port = 443
        if port is None and scheme == 'http':
            port = 80

        # print(path)
        
        # connect to the server 
        self.connect(host, port)

        # if the path is empty then use \
        if path is None: 
            path = '/'

        # if there is a query add it with the path 
        if query is not None:
            path += f'?{query}'

        # fomatting the request
        request = f'GET {path} HTTP/1.1\r\nHost:{host}\r\nConnection: close\r\n\r\n'

        # send the request 
        self.sendall(request)

        # receive all the data and store it in socket.
        # response = self.socket.recv(4096)
        response = self.recvall(self.socket)
        response = response.encode(FORMAT)
        response = response.decode(FORMAT)

        # display the response 
        # print(response)

        # get the code and body into respective variables
        code = self.get_code(response)
        print(code)
        print('\n')

        body = self.get_body(response)
        print(body)
        print('\n')

        # close the connection
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # the formatting used 
        FORMAT = 'utf-8'

        # finding out the port, hostname and the scheme used in the request
        port = urllib.parse.urlparse(url).port
        host = urllib.parse.urlparse(url).hostname
        scheme = urllib.parse.urlparse(url).scheme
        path = urllib.parse.urlparse(url).path
        query = urllib.parse.urlparse(url).query

        # returning 400 error if port and host not mentioned 
        if port is None and host is None:
            return HTTPResponse(400, body)
        
        # setting default port if none mentioned or provided 
        if port is None and scheme == 'https':
            port = 443
        if port is None and scheme == 'http':
            port = 80

        # connect to the server 
        self.connect(host, port)

        # if the path is empty then use \
        if path is None: 
            path = '/'

        # if there is a query add it with the path 
        if query is not None:
            path += f'?{query}'

        if args is not None:
            args = urllib.parse.urlencode(args)
        else:
            args = ''
            args = urllib.parse.urlencode(args)
        
        length_args = len(args)
        
        request = f'POST {path} HTTP/1.1\r\nHost:{host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length_args}\r\nConnection: close\r\n\r\n{args}\r\n\r\n'

        # send the request 
        self.sendall(request)

        # receive all the data and store it in socket.
        response = self.recvall(self.socket)
        response = response.encode(FORMAT)
        response = response.decode(FORMAT)

        # display the response 
        print(response)

        # get the code and body into respective variables
        code = self.get_code(response)
        body = self.get_body(response)

        # close the connection
        self.close()


        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
