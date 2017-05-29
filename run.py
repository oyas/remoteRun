#!/usr/bin/env python3
# coding: utf-8

#
# タスクを実際に実行する
#

import os
import stat
import subprocess
import argparse
import json
from datetime import datetime
import shutil

import config


def ssh(hostname, cmd):
    #ssh_cmd = ['ssh', hostname,"'{}'".format(' '.join(cmd)) ]
    #ssh_cmd = ['ssh', hostname, ' '.join(cmd) ]
    ssh_cmd = ['ssh', hostname] + cmd
    #res = subprocess.run(ssh_cmd, stdout=subprocess.PIPE)
    res = subprocess.run(ssh_cmd)#, shell=True)
    print(res)
    if( res.returncode != 0 ):
        print("SSH error happened.")
        exit(1)
    return res

def pull_data(hostname, srcdir, tmpPath = config.TMP_PATH):
    src = '{}:{}'.format(hostname, os.path.join(tmpPath, srcdir))
    dst = config.TMP_PATH_SERVER
    scp_cmd = ['rsync', '-a', '--exclude', "'.*'", src, dst ]
    print("pull_data")
    #print(scp_cmd)
    res = subprocess.run(scp_cmd)#, shell=True)
    print(res)
    if( res.returncode != 0 ):
        print("Error")
        exit(1)
    return os.path.join(dst, srcdir)

def push_data(hostname, srcdir, tmpPath = config.TMP_PATH):
    #print("tmpPath: {} {}".format(tmpPath, srcdir))
    dstPath = tmpPath
    #print("dstPath: {}".format(dstPath))
    src = os.path.join(config.TMP_PATH_SERVER, srcdir)
    dst = '{}:{}'.format(hostname, dstPath)
    scp_cmd = ['rsync', '-a', '--exclude', "'.*'", src, dst ]
    print("push_data")
    #print(scp_cmd)
    res = subprocess.run(scp_cmd)#, shell=True)
    print(res)
    if( res.returncode != 0 ):
        print("Error")
        exit(1)
    return os.path.join(dstPath, srcdir)

def main():
    # 引数解析
    parser = argparse.ArgumentParser(description='run.py')
    parser.add_argument('name', help='Source Directory')
    parser.add_argument('host', help='Host name of computer for running Task.')
    args = parser.parse_args()

    print('--- Args ---')
    print('name : {}'.format(args.name))
    print('host : {}'.format(args.host))
    print('')

    # ディレクトリの準備
    if( os.path.isdir(config.TMP_PATH_SERVER) == False ):
        os.makedirs(config.TMP_PATH_SERVER, exist_ok=True)

    # 実行用データを持ってくる
    tmpPath = pull_data(config.HOSTNAME_FRONT, args.name)
    print('pull_data ok. tmpPath: {}'.format(tmpPath))

    # JSONデータを読み込む
    f = open(os.path.join(tmpPath, config.ORDERFILE_NAME), 'r')
    order = json.load(f)
    f.close()
    # taskを実行するホスト
    host = args.host
    # 実行ファイル
    #args.run = 'run.sh'
    args.run = order['run']

    # make run.sh
    runsh_path = os.path.join(tmpPath, 'run.sh')
    f = open(runsh_path,'w')
    f.write('#!/bin/bash\n')
    f.write('\n')
    f.write('source /etc/profile\n')
    f.write('source ~/.bash_profile\n')
    f.write('cd `dirname $0`\n')
    f.write('cd src\n')
    f.write('{} 2>&1 | tee ../log\n'.format(args.run))
    f.close()
    os.chmod(runsh_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    # TMP_PATH_TASKSディレクトリを用意する
    ssh(host, ['mkdir', '-p', config.TMP_PATH_TASKS])

    # taskを送信する
    dstPath = push_data(host, args.name, config.TMP_PATH_TASKS)
    #print('push_data ok. dstPath: {}'.format(dstPath))

    # 実行
    cmd = [ os.path.join(dstPath, 'run.sh') ]
    ssh(host, cmd)

    # 実行結果データを回収する
    tmpPath = pull_data(host, args.name, config.TMP_PATH_TASKS)
    push_data(config.HOSTNAME_FRONT, args.name)

    # クリーンアップ
    subprocess.run(['rm', '-r', tmpPath])
    ssh(host, ['rm', '-r', dstPath])

    # 完了メッセージ
    print('Finished.')


if __name__ == '__main__':
    main()
