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

# vanity-gateway.py

"""

Vanity Gateway Proxy Server Manages credentials for all partners in one application

This updated chat_completions endpoint will:
- validate the incoming test token (as before),
- forward the incoming payload to the configured provider,
- return the provider's response back to the caller.

not implemented yet:
- load provider configuration

"""

###################################
from datetime import datetime, timezone
from string import Template
import vg_io
import fastapi
import uvicorn

import pkgutil, importlib
import langchain
import pathspec
import subprocess, threading, re, os, sys, inspect, shutil, argparse, random, math, json, fnmatch, requests, types, smart_open

# rows, columns = os.popen('stty size', 'r').read().split() #http://goo.gl/cD4CFf
# "pydoc -p 1234" will start a HTTP server on port 1234, allowing you to browse
# the documentation at "http://localhost:1234/" in your preferred Web browser.
cwf = os.path.abspath(inspect.getfile(inspect.currentframe())) # Current Working File
cwfd = os.path.dirname(cwf) # Current Working File Path

###################################

app = fastapi.FastAPI()

# Load the test key (used to authenticate callers to this vanity gateway)
BASE = os.path.dirname(os.path.abspath(__file__))
TEST_KEY_PATH = os.path.join(BASE, "vg_cfg/test.key")

with open(TEST_KEY_PATH, "r") as f:
    TEST_KEY = f.read().strip()

# Reuse helper from req_test: load config into a SimpleNamespace
def load_cfg_from_path(cfg_path):
    """
    Load JSON config and convert to SimpleNamespace for attribute access.
    Mirrors req_test.load_cfg behavior.
    """
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f, object_hook=lambda d: types.SimpleNamespace(**d))

@app.post("/chat/completions")
async def chat_completions(request: fastapi.Request):
    """
    Validate incoming token, forward the payload to the configured provider,
    and return the provider response back to the caller.
    """

    # Validate Authorization header
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise fastapi.HTTPException(status_code=401, detail="Missing Bearer token")

    token = auth.split(" ", 1)[1]
    if token != TEST_KEY:
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")

    # Read incoming payload (we expect the client to POST the provider payload)
    try:
        payload = await request.json()
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    # Determine config paths (reuse commented lines from req_test)
    vg_cfg_path = os.path.join(cwfd, "vg_cfg/vg_cfg.json")
    secretkey_path = os.path.join(cwfd, "vg_cfg/secret.key")

    # Load provider config and secret
    try:
        cfg = load_cfg_from_path(vg_cfg_path)
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=500, detail=f"Provider config not found at {vg_cfg_path}")
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=f"Failed to load provider config: {e}")

    try:
        with open(secretkey_path, "r") as f:
            cfg.secret_k = f.read().strip()
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=500, detail=f"Secret key not found at {secretkey_path}")
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=f"Failed to read secret key: {e}")

    # Validate minimal config fields
    try:
        api_url = cfg.projectConfig.API_URL
        # If this says localhost:8443, you have a configuration loop.
        print(f"Forwarding to: {api_url}") 
        model_name = cfg.projectConfig.JuniorLLM if hasattr(cfg.projectConfig, "JuniorLLM") else None
    except Exception:
        raise fastapi.HTTPException(status_code=500, detail="Invalid provider config structure (missing projectConfig.API_URL)")

    if not api_url:
        raise fastapi.HTTPException(status_code=500, detail="Provider API_URL not configured")

    # Forward the payload to the provider
    try:
        headers = {
            "Authorization": f"Bearer {cfg.secret_k}",
            "Content-Type": "application/json"
        }
        # Use the same verify behavior as rqs.get_response (if server cert exists)
        verify_cert = os.path.join(cwfd, "vg_cfg/server.crt")
        verify_flag = True 
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30, verify=verify_flag)
        resp.raise_for_status()
        # Return the provider response body directly
        return fastapi.responses.JSONResponse(content=resp.json(), status_code=200)

    except requests.exceptions.RequestException as e:
        # Mirror rqs.get_response style error handling
        detail = f"Network/API Error: {str(e)}"
        raise fastapi.HTTPException(status_code=502, detail=detail)
    except ValueError:
        # JSON decode error
        raise fastapi.HTTPException(status_code=502, detail="Provider returned non-JSON response")
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=f"Unexpected Error: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "vanity-gateway:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="vg_cfg/server.key",
        ssl_certfile="vg_cfg/server.crt",
    )

