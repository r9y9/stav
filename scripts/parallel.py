#!/usr/bin/python
# coding: utf-8

from util import *
import os
import popen2


def parallel(src, tgt, dst_dir, diff):
    if not os.path.exists("./align"):
        raise RuntimeError, "Binary of feature alignment is not found. Please run `go build /path/to/align.go` before running this script."

    root, ext = os.path.splitext(src)
    dst_path = os.path.join(dst_dir, os.path.basename(root) + "_parallel.json")
    cmd = "./align -src=" + src + " -target=" + tgt + " -o=" + dst_path

    # Differencial spectral compensation
    if diff == True:
        cmd += " -diff"

    print cmd
    cout, cin, cerr = popen2.popen3(cmd)
    print_popen2_info(cout, cin, cerr)
    return dst_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Feature extraction for VC.")
    parser.add_argument("--src_dir", dest="src_dir", type=str, required=True)
    parser.add_argument("--tgt_dir", dest="tgt_dir", type=str, required=True)
    parser.add_argument("--dst_dir", dest="dst_dir", type=str, required=True)
    parser.set_defaults(diff=False)
    parser.add_argument("--diff", dest="diff", action="store_true")
    args = parser.parse_args()

    src_files = find_files(args.src_dir)
    tgt_files = find_files(args.tgt_dir)
    src_files.sort()
    tgt_files.sort()

    if not os.path.exists(args.dst_dir):
        os.makedirs(args.dst_dir)

    for i in range(len(src_files)):
        src, tgt = src_files[i], tgt_files[i]
        if os.path.basename(src) != os.path.basename(tgt):
            raise RuntimeError, "Filename must be equal."

        parallel(src, tgt, args.dst_dir, args.diff)

    print "Finished"
