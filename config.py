#!/usr/bin/env python3
# coding: utf-8

#
# config.py 各種設定
#

import os

#
# Front Server
#

# オーダーを受け付けるホストの名前(Master serverから見た名前)
HOSTNAME_FRONT = 'localhost'

# Front側の実行データの一時保存ディレクトリ
TMP_PATH = os.path.join("/", "tmp", "remoteRun")

# remoteRunインストールディレクトリ(Front Server内)
INSTALLDIR_FRONT = '~/git/remoteRun/'

# Unix Domain Socket の保存先
SOCKET_PATH = os.path.join(TMP_PATH, 'server.socket')



#
# Master Server 中継サーバーの設定
#

# 一時データ保存場所
TMP_PATH_SERVER = os.path.join("/", "tmp", "remoteRun_server")



#
# Task runner server タスク実行サーバー
#

# タスク実行用サーバーのホスト名(中継サーバーから見た名前)
HOSTNAME_TASK_SERVERS = [
    'localhost',
];

# 一時データ保存場所・ワークスペース
TMP_PATH_TASKS = os.path.join("/", "tmp", "remoteRun_tasks")



#
# 変更しない
#

# タスクの情報を保存しておくファイル名
ORDERFILE_NAME = 'orderfile.json'


