#!/usr/bin/env python3
# Config file for census browser
#New York – Clear ☀️   🌡️+34°F (feels +31°F, 79%) 🌬️↓2mph 🌓&m Sun Jan 29 09:14:20 2023
#W4Q1 – 29 ➡️ 335 – 263 ❇️ 101


import os
import sys

INDEX_DB = '../bigFiles/index.db'
DATA_FILE = '../bigFiles/pcen_v2020_y20.sas7bdat'



def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def logF(log_message, file_name):
    with open(file_name, "a") as f:
        f.write(log_message + "\n")
