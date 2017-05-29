#!/usr/bin/env python3
# coding: utf-8

#
# RemoteRunのインターフェース
# このスクリプト経由で各種操作を行う。
#
# Help:
#   $ remoteRun.py -h
#

import os
import subprocess
import argparse
import json
from datetime import datetime
import shutil

import client
import config


def run(args):
    # 絶対パスに変換
    args.srcdir = os.path.abspath(args.srcdir)

    # 実行時間から、タスク名を決める
    if len(args.name) == 0:
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.name = date
        cnt = 0
        while os.path.exists(os.path.join(config.TMP_PATH, args.name)):
            args.name = '{}_{}'.format(date, cnt)
            cnt += 1
    elif os.path.exists(os.path.join(config.TMP_PATH, args.name)):
        print('[Error] すでに存在するタスク名です {}'.format(args.name))
        exit(1)

    print('--- Args ---')
    print('srcdir : {}'.format(args.srcdir))
    print('run    : {}'.format(args.run))
    print('name   : {}'.format(args.name))
    print('')

    # 存在確認
    if( os.path.isdir(args.srcdir) == False):
        print('[Error] ディレクトリが存在しません: {}'.format(args.srcdir))
        exit(1)
    if( os.path.isfile(args.run) == False):
        print('[Error] ファイルが存在しません: {}'.format(args.run))
        exit(1)

    # 実行待ちのため、一時的なディレクトリにコピー
    tmpPath = os.path.join(config.TMP_PATH, args.name)
    tmpSrcPath = os.path.join(tmpPath, 'src')
    shutil.copytree(args.srcdir, tmpSrcPath, ignore=shutil.ignore_patterns('.*'))  # ディレクトリごとコピー

    # orderfile.jsonの作成
    orderfilePath = os.path.join(tmpPath, config.ORDERFILE_NAME)
    f = open(orderfilePath, "w")
    json.dump(args.__dict__, f)
    f.close()

    # Taskの登録
    data = {
        'request': 'query',
        'data': args.__dict__,
    }
    client.query(data)

    # 完了メッセージ
    print('Success. Order received.')


def status(args):
    data = {'request': 'status'}
    received = client.query(data)
    wt = received.get('WaitingTasks')
    if wt != None: print('WaitingTasks[{}]'.format(wt))
    for key, status in sorted( received.items() ):
        if( key != 'WaitingTasks' ):
            print('{}: {}'.format(key, status))


def pull(args):
    task_path = os.path.join(config.TMP_PATH, args.name, 'src')
    if not os.path.exists(task_path):
        print('[Error] 存在しないタスクです {}'.format(args.name))
        exit(1)

    dst_path = args.dst or args.name
    if os.path.exists(os.path.join(dst_path)):
        print('[Error] ディレクトリがすでに存在します {}'.format(args.dst))
        exit(1)

    # pull data
    shutil.move(task_path, dst_path)

    # pullが終わったことを伝える
    data = {
        'request': 'pulled',
        'name': args.name,
    }
    client.query(data)


def main():
    # 引数解析
    parser = argparse.ArgumentParser(description='remoteRun.py')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    # subcommand run
    parser_run = subparsers.add_parser('run', help='request task')
    parser_run.add_argument('--srcdir', '-s', default='./',
                        help='Source Directory')
    parser_run.add_argument('--run', '-r', default='./run.sh',
                        help='Program path to Run')
    parser_run.add_argument('--name', default='',
                        help='Unique name of task')
    # subcommand status
    parser_status = subparsers.add_parser('status', help='see status')
    # subcommand status
    parser_pull = subparsers.add_parser('pull', help='pull result data of finished task')
    parser_pull.add_argument('name', help='Task name')
    parser_pull.add_argument('--dst', default='', help='Directory name for save')
    # parse
    args = parser.parse_args()

    # switch subcommand
    if args.command == 'run':
        run(args)
    elif args.command == 'status':
        status(args)
    elif args.command == 'pull':
        pull(args)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()
