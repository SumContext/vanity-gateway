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

CFG_groq_gpt20b = """
{
    "projectConfig": {
        "gateway_url": "https://localhost:8443/chat/completions",
        "nickname": "groq-gpt-20b",
        "parameters": {
            "max_tokens": 400,
            "temperature": 0.5,
            "include_reasoning": true
        }
    }
}
"""
CFG_lmstudio20b = """
{
    "projectConfig": {
        "gateway_url": "https://localhost:8443/chat/completions",
        "nickname": "lmstudio20b",
        "parameters": {
            "max_tokens": 400,
            "temperature": 0.5,
            "include_reasoning": true
        }
    }
}
"""

def reslv_test():
    some_str = "\nAND ALSO STRINGS!!!"
    test_file = cwfd + "/coconuts/TestA.md"
    content = vg_io.reslv.re_solve(test_file)
    print(content)

def main():
    reslv_test()

    some_cfg_file = os.path.join(cwfd, "vg_cfg/rq_test_cfg.json")
    some_key_path = os.path.join(cwfd, "vg_cfg/test.key")
    
    # set a cfg with load_from_file or inline_set
    # cfg = vg_io.cfg.load_from_file(some_cfg_file, some_key_path)
    # cfg = vg_io.cfg.inline_set(CFG_groq_gpt20b, some_key_path)
    cfg = vg_io.cfg.inline_set(CFG_lmstudio20b, some_key_path)

    # runs test_prompt builder
    cert = os.path.join(cwfd, "vg_cfg/server.crt")
    content, err = vg_io.rqs.parse_response(cfg, test_prompt, verify=cert)

    print(content)


def test_prompt(cfg, *builder_args):
    # max_size = cfg.projectConfig.maxSupportedFileSize
    # # file_path = builder_args[0]
    # try:
    #     # if os.path.getsize(file_path) > max_size:
    #     #     return "(skipped: file too large)", True
    # except Exception as e:
    #     return f"File size check failed: {str(e)}", True
    # # code_content, err = Load_Plaintxt(file_path)
    # if err:
    #     return code_content, True
    # extra_context = builder_args[0] if builder_args else "large project"
    # prompt = "Provide a markdown code escaped 111 chars or less summary of this file."
    payload = {
        "model": cfg.projectConfig.nickname,
        "include_reasoning": True,
        "messages": [
            {"role": "user",
            "content": "Who is the 1st President of the United States?"}
        ]
    }
    return payload, False

if __name__ == "__main__":
    main()

