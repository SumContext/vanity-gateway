#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.
#
# Permission is  hereby  granted,  free  of  charge,  to  any  person
# obtaining a copy of  this  software  and  associated  documentation
# files  (the  "Software"),  to  deal   in   the   Software   without
# restriction, including without limitation the rights to use,  copy,
# modify, merge, publish, distribute, sublicense, and/or sell  copies
# of the Software, and to permit persons  to  whom  the  Software  is
# furnished to do so.
#
# The above copyright notice and  this  permission  notice  shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT  WARRANTY  OF  ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES  OF
# MERCHANTABILITY,   FITNESS   FOR   A   PARTICULAR    PURPOSE    AND
# NONINFRINGEMENT.  IN  NO  EVENT  SHALL  THE  AUTHORS  OR  COPYRIGHT
# OWNER(S) BE LIABLE FOR  ANY  CLAIM,  DAMAGES  OR  OTHER  LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING  FROM,
# OUT OF OR IN CONNECTION WITH THE  SOFTWARE  OR  THE  USE  OR  OTHER
# DEALINGS IN THE SOFTWARE.
######################################################################

# ex_client.py
from datetime import datetime, timezone
import pathspec
import vg_io
import subprocess, threading, re, os, sys, inspect, shutil, argparse, random, math, json, fnmatch, requests, json, types, smart_open
rows, columns = os.popen('stty size', 'r').read().split() #http://goo.gl/cD4CFf
#"pydoc -p 1234" will start a HTTP server on port 1234, allowing you to browse
#the documentation at "http://localhost:1234/" in your preferred Web browser.
cwf = os.path.abspath(inspect.getfile(inspect.currentframe())) # Current Working File
cwfd = os.path.dirname(cwf) # Current Working File Path

# def reslv_test():
#     some_str = "\nAND ALSO STRINGS!!!"
#     test_file = cwfd + "/coconuts/TestA.md"
#     content = vg_io.reslv.re_solve(test_file)
#     print(content)

def sws_test():
    some_str = "\nAND ALSO STRINGS!!!"
    vg_io.reslv.sws_re_solve_json(cwfd + "/sws/sws.json")

def sws_test_w_vars():
    some_str = "\nAND ALSO STRINGS!!!"
    # ctx = locals()
    # vg_io.reslv.sws_re_solve_json(cwfd + "/sws/sws.json", context=ctx)
    vg_io.reslv.sws_re_solve_json(cwfd + "/sws/sws.json", context=locals())

def main( ):
    # tst_coconuts()
    # tst_json()
    # sws_test() # safer
    sws_test_w_vars()
    # reslv_test()

if __name__ == "__main__":
    main()
