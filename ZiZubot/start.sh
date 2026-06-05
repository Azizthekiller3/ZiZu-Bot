#!/bin/bash
set -e
cd /home/runner/workspace/ZiZubot
export PATH="/home/runner/workspace/.pythonlibs/bin:$PATH"
pip install -q -r requirements.txt
python bot.py
