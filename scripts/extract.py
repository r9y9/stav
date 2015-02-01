#!/usr/bin/python
# coding: utf-8

import os
import popen2
from util import *


def extract_mcep(path, dst_dir, order):
    if not os.path.exists("./extract_mcep"):
        raise RuntimeError, "Binary of feature extarction is not found. Please run `go build /path/to/extract_mcep.go` before running this script."

    root, ext = os.path.splitext(path)
    dst_path = os.path.join(dst_dir, os.path.basename(root) + ".json")

    cmd = "./extract_mcep -src=" + path + \
        " -o=" + dst_path + " -order=" + str(order)
    print cmd
    cout, cin, cerr = popen2.popen3(cmd)
    print_popen2_info(cout, cin, cerr)
    return dst_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Feature extraction for VC.")
    parser.add_argument("--src_dir", dest="src_dir", type=str, required=True)
    parser.add_argument("--dst_dir", dest="dst_dir", type=str, required=True)
    parser.add_argument("--limit", dest="limit", type=int, default=100)
    parser.add_argument("--order", dest="order", type=int, default=40)

    args = parser.parse_args()

    if not os.path.exists(args.dst_dir):
        os.makedirs(args.dst_dir)

    files = find_files(args.src_dir)
    files.sort()

    count = 0
    for f in files:
        count += 1
        # do it
        extract_mcep(f, args.dst_dir, args.order)
        if count > args.limit:
            break

    print "Finished."
