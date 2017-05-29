#!/usr/bin/env python3
# coding: utf-8

#
# Front Server に定期的に通信を行い、タスクを受け取る処理を行う
#

import os
import sys
import time
import subprocess
import argparse
import json
from datetime import datetime
import threading

import config

COMMAND_CLIENT = os.path.join( config.INSTALLDIR_FRONT, 'client.py')
COMMAND_RUN = os.path.abspath( os.path.join(os.path.dirname(__file__), 'run.py') )

# host state
Free = 0
Busy = 1
# list of hosts to run task
hosts = {}

def ssh(hostname, cmd):
    ssh_cmd = ['ssh', hostname] + cmd
    res = subprocess.run(ssh_cmd, stdout=subprocess.PIPE)
    #print(res)
    if( res.returncode != 0 ):
        print("SSH error happened.")
        exit(1)
    return res


# remoteRun/client.py へリクエストを送る
def query(data):
    print('[{}] send query.'.format(datetime.now()))
    host = config.HOSTNAME_FRONT
    query = "'{}'".format( json.dumps(data) )
    res = ssh(host, [COMMAND_CLIENT, '--query', query])
    resData = res.stdout.decode('utf-8')
    return json.loads( resData )


# Task一覧
Tasks = {}

# Task runner thread
class TaskThread(threading.Thread):
    def __init__(self, name, host):
        threading.Thread.__init__(self)
        self.name = name
        self.host = host

    def run(self):
        print('Task start: {} [{}]'.format(self.name, self.host))
        hosts[self.host] = Busy
        try:
            cmd = [COMMAND_RUN, self.name, self.host]
            devnull = open('/dev/null', 'w')
            self.proc = subprocess.Popen(cmd, stdout=devnull, stderr=devnull)
            #self.proc = subprocess.Popen(cmd)
            #print( self.proc )
            while self.proc.returncode == None:
                time.sleep(1)  # sleep 1 seconds
                self.proc.poll()
            print( "Task finished: {} [{}]".format(self.name, self.host) )
        except:
            print("[Error] Task runner error. {}".format(self.name))
            Tasks.pop( self.name )
        finally:
            hosts[self.host] = Free


def getStatus():
    ret = {}
    dellist = []
    for name, thread in Tasks.items():
        #print("getStatus: {} => {}".format(name, thread))
        data = ""
        if thread.proc.returncode == None:
            data = 'Running [in {}]'.format(thread.host)
        else:
            data = 'Finished [{}]'.format( thread.proc.returncode )
            dellist.append(name)
        ret[name] = data

    # 終了したタスクを削除
    for name in dellist:
        Tasks.pop(name)

    return ret

def freehost():
    for host, stat in hosts.items():
        if stat == Free:
            return host
    return None

def runNextTask(status, host):
    res = query({'request': 'nextTask', 'status': status})
    if res['name'] != None:
        name = res['name']
        print('nextTask: {} [{}]'.format( name, host ))
        thread = TaskThread(name, host)
        thread.setDaemon(True)
        thread.start()
        Tasks[name] = thread   # 登録

def send_status(status):
    query({'request': 'ping', 'status': status})

def main():
    # set all task server status for Free
    for host in config.HOSTNAME_TASK_SERVERS:
        hosts[host] = Free

    try:
        while True:
            status = getStatus()
            host = freehost()
            #print("free host is {}".format(host))
            if host != None:
                runNextTask(status, host)
            else:
                send_status(status)

            time.sleep(10)  # sleep 10 seconds

    except:
        print('Error happened. Finish.')

if __name__ == '__main__':
    main()
