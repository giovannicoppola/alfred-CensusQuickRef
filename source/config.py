#!/usr/bin/env python3
# Config file for census browser
#New York – Clear ☀️   🌡️+34°F (feels +31°F, 79%) 🌬️↓2mph 🌓&m Sun Jan 29 09:14:20 2023
#W4Q1 – 29 ➡️ 335 – 263 ❇️ 101


import os
import sys
import zipfile

WF_DATA = os.getenv('alfred_workflow_data')
INDEX_DB = WF_DATA + '/index.db'



UStotPop = 329484123



if not os.path.exists(WF_DATA):
    os.makedirs(WF_DATA)


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def logF(log_message, file_name):
    with open(file_name, "a") as f:
        f.write(log_message + "\n")





def checkDatabase():
    
    DB_ZIPPED = 'index.db.zip'
    
    if os.path.exists(DB_ZIPPED):  # there is a zipped database: distribution version
        log ("found distribution database, extracting")
        with zipfile.ZipFile(DB_ZIPPED, "r") as zip_ref:
            zip_ref.extractall(WF_DATA)
        os.remove (DB_ZIPPED)
    elif os.path.exists('index.db'):  # there is a new version, possibly rebuilt via script: replace the version in DATA
        os.rename('index.db', INDEX_DB)




checkDatabase()


