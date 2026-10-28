#!/bin/bash
set -e                                  # 중간에 하나라도 실패하면 멈춘다
cd ~/mybot
git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart mybot
systemctl status mybot --no-pager       # 잘 켜졌는지 한 번 보여 준다
