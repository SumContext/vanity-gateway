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
###################################

# rqs.py
# from datetime import datetime, timezone
# import pathspec
# import vg_io
# import subprocess, threading, re, os, sys, inspect, shutil, argparse, random, math, json, fnmatch, requests, json, types, smart_open
# rows, columns = os.popen('stty size', 'r').read().split() #http://goo.gl/cD4CFf
# #"pydoc -p 1234" will start a HTTP server on port 1234, allowing you to browse
# #the documentation at "http://localhost:1234/" in your preferred Web browser.
# cwf = os.path.abspath(inspect.getfile(inspect.currentframe())) # Current Working File
# cwfd = os.path.dirname(cwf) # Current Working File Path
# #    vg_cfg = os.path.join(home_cfg_dir, "vg_cfg/rq_test_cfg.json")

import json, requests, types, os

def get_response(cfg, payload_builder, *builder_args, verify=True, params=None):
    """
    Use requests lib - Send Message to Server
    Orchestrates config loading, and API calls.
    Now requires cfg as first argument.
    'params' argument to support URL encoding.
    """
    try:
        # Use gateway_url from config instead of a hardcoded API_URL
        target_url = cfg.projectConfig.gateway_url
        
        payload, err = payload_builder(cfg, *builder_args)
        if err: return payload, True

        headers = {
            "Authorization": f"Bearer {cfg.secret_k}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            target_url,
            headers=headers,
            json=payload,
            params=params, # URL encodes nickname and parameters
            timeout=30,
            verify=verify
        )
        response.raise_for_status()
        return response.json(), False
    except Exception as e:
        return f"Error: {str(e)}", True

def parse_response(cfg, payload_builder, *builder_args, verify=True, params=None):
    data, err = get_response(cfg, payload_builder, *builder_args, verify=verify, params=params)
    """
    Use requests lib - Receive Response from server
    Now requires cfg as first argument.
    """
    # data, err = get_response(cfg, payload_builder, *builder_args, verify=verify)
    if err:
        return data, True

    try:
        message = data['choices'][0]['message']
        content = message.get('content', '').strip()

        if content.startswith("```"):
            lines = content.splitlines()
            if len(lines) >= 2:
                content = "\n".join(lines[1:-1]).strip()
            else:
                content = content.replace("```", "").strip()

        return content, False

    except (KeyError, IndexError, TypeError) as e:
        return f"Error parsing JSON response: {str(e)}", True
