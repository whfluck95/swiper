#!/bin/bash

# 软重启 (平滑重启)

# master 19308
# |- worker 22771  <- 1000
# |- worker 22772  <- 9367
# |- worker 22773  <- 7353
# |- worker 22774  <- 5614

# 1. 主进程收到重启信号 kill -HUP 19308
# 2. 主进程开启新的子进程
# 3. 子进程开始处理用户新的请求

# |- worker 7625   <- 100
# |- worker 7626   <- 562
# |- worker 7627   <- 98
# |- worker 7628   <- 302


echo 'server restart...'

BASE_DIR='/opt/swiper/'
PID=`cat $BASE_DIR/logs/gunicorn.pid`
kill -HUP $PID

echo 'done'
