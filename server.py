#!/usr/bin/env python3
# coding: utf-8

#
# タスクの情報を管理する
# server.socket を生成する。操作には`client.py`を使う。
#

import os
import sys
import socket
import json
from queue import Queue
from datetime import datetime
import argparse

import config


class Server:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.status = {}
        self.queue = Queue()

    def start(self):
        print('start server.')
        s = self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        dirpath = os.path.dirname(self.socket_path)
        if( os.path.isdir(dirpath) == False ):
            os.makedirs(dirpath, exist_ok=True)
        s.bind(self.socket_path)
        s.listen(1)
        try:
            while True:
                connection, address = s.accept()
                print('[{}] connect.'.format(datetime.now()))
                self.accepted(connection, address)
                print('[{}] disconnect.'.format(datetime.now()))
        finally:
            os.remove(self.socket_path)

    # 受信処理
    def accepted(self, connection, address):
        data_str = connection.recv(32768).decode().strip()  # limit is 32KB
        print("receive from client : {}".format( data_str ))
        data = json.loads(data_str)
        senddata = json.dumps( self.request(data) )
        connection.send( senddata.encode() )
        print("send to client      : {}".format(senddata))

    def request(self, data):
        req = data.get('request')
        d = data.get('data')

        # status update
        status = data.get('status')
        if isinstance(status, dict):
            self.status.update( status )

        # request
        if   req == 'query'         : return self.query(d)
        elif req == 'nextTask'      : return self.nextTask()
        elif req == 'ping'          : return {'ping':True}
        elif req == 'status'        : return self.status
        elif req == 'pulled'        : return self.pulled(data)
        else: return {}

    def query(self, data):
        name = data.get('name')
        print('query: {}'.format(name))
        if name != None:
            self.queue.put( name )
            self.status[name] = 'Waiting to run'
        self.status['WaitingTasks'] = self.queue.qsize()
        return {'received':True}

    def nextTask(self):
        if self.queue.empty():
            return {'name': None}
        name = self.queue.get(timeout=1)
        self.status['WaitingTasks'] = self.queue.qsize()
        self.status[name] = 'sending'
        return {'name': name}

    def pulled(self, data):
        name = data.get('name')
        self.status.pop(name)
        return {'received':True}


def main():
    parser = argparse.ArgumentParser(description='server.py: front end server')
    parser.add_argument('-f', '--force', action="store_true",
            help='remove socket file if already exists.')
    args = parser.parse_args()

    if os.path.exists(config.SOCKET_PATH):
        if args.force:
            os.remove(config.SOCKET_PATH)
        else:
            print('{} is already exists.'.format(config.SOCKET_PATH))
            return

    server = Server(config.SOCKET_PATH)
    server.start()

if __name__ == '__main__':
    main()
