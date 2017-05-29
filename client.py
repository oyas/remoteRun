#!/usr/bin/env python3
# coding: utf-8

#
# remoteRun-server.socket と通信を行う。
#
# $ client.py -q 'query JSON'
#

import sys
import socket
import json
import argparse

import config


class Client:
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def send(self, data):
        s = self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket_path)
        message = json.dumps( data )
        s.send( message.encode() )
        rec = s.recv(32768).decode()
        s.close()
        return rec

def query(data, noloads = False):
    client = Client(config.SOCKET_PATH)
    received = client.send(data)
    if noloads: return received
    else:       return json.loads(received)

def main():
    parser = argparse.ArgumentParser(description='client.py')
    parser.add_argument('--query', '-q', default='{}', help='JSON query')
    args = parser.parse_args()

    data = {}
    try:
        data = json.loads(args.query)
    except json.JSONDecodeError:
        print("JSON Decode Error!")
        exit(1)

    received = query(data, True)
    print(received)

if __name__ == '__main__':
    main()
