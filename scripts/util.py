#!/usr/bin/python
# coding: utf-8

import os

def find_files(dir):
    return [os.path.join(dir, s) for s in os.listdir(dir)]

def print_popen2_info(cout, cin, cerr):
    if cout != None:
        for s in cout:
            print s[:-1]

    if cerr != None:
        for s in cerr:
            print s[:-1]
