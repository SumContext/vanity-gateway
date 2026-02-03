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

current list
vg_io.rqs   for requests

in progress
vg_io.oai   for langchain_openai

future list
vg_io.goog  for langchain_google_genai
langchain_anthropic langchain_aws langchain_chroma langchain_classic 
langchain_community langchain_core langchain_deepseek 
langchain_experimental langchain_fireworks 
langchain_groq langchain_huggingface langchain_mistralai 
langchain_mongodb langchain_ollama  
langchain_perplexity langchain_tests langchain_text_splitters 
langchain_xai

we will also act as a requests library mirror

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
import logging  # Added for debug logs

logging.basicConfig(level=logging.INFO)

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
    # Validate incoming authorization token
    auth = request.headers.get("Authorization")
    if not auth or auth != f"Bearer {TEST_KEY}":
        raise fastapi.HTTPException(status_code=401, detail="Invalid or missing authorization token")

    # 1. Get routing info from URL
    nickname = request.query_params.get("nickname")
    if not nickname:
        raise fastapi.HTTPException(status_code=400, detail="Missing nickname in URL")

    # 2. Load Gateway Registry (vg_cfg.json)
    gate_cfg = load_cfg_from_path(os.path.join(cwfd, "vg_cfg/vg_cfg.json"))
    provider = getattr(gate_cfg.providers, nickname, None)
    if not provider:
        raise fastapi.HTTPException(status_code=404, detail=f"Provider {nickname} not found")

    # 3. Handle specific API types (Step 1: Requests)
    if provider.api == "requests":
        # Load the provider-specific key
        with open(os.path.join(cwfd, provider.key_path), "r") as f:
            provider_key = f.read().strip()

        # 4. Prepare the forward-facing payload
        payload = await request.json()
        
        # SURGICAL FIX: Map nickname to the provider's actual model string
        # This replaces the local nickname with what Groq/OpenAI expects
        payload["model"] = provider.model

        # Merge URL parameters into the JSON payload with type handling
        for key, value in request.query_params.items():
            if key == "nickname":
                continue
            
            # Surgical fix for types: handle digits, floats, and booleans
            if value.isdigit():
                payload[key] = int(value)
            elif value.replace('.', '', 1).isdigit() and '.' in value: # Handle floats
                payload[key] = float(value)
            elif value.lower() == "true":
                payload[key] = True
            elif value.lower() == "false":
                payload[key] = False
            else:
                payload[key] = value
        # LOGGING: See exactly what we are sending upstream
        print(f"Forwarding to: {provider.url}")
        print(f"Final Payload: {json.dumps(payload, indent=2)}")

        # 5. Forward to the actual provider
        headers = {"Authorization": f"Bearer {provider_key}", "Content-Type": "application/json"}
        resp = requests.post(provider.url, headers=headers, json=payload, timeout=30)
        return fastapi.responses.JSONResponse(content=resp.json(), status_code=resp.status_code)
    
    elif provider.api == "langchain_openai":
        # Load the provider-specific key
        with open(os.path.join(cwfd, provider.key_path), "r") as f:
            provider_key = f.read().strip()

        # Prepare payload and merge URL params (same logic as requests branch)
        payload = await request.json()
        payload["model"] = provider.model

        for key, value in request.query_params.items():
            if key == "nickname":
                continue
            if value.isdigit():
                payload[key] = int(value)
            elif value.replace('.', '', 1).isdigit() and '.' in value:
                payload[key] = float(value)
            elif value.lower() == "true":
                payload[key] = True
            elif value.lower() == "false":
                payload[key] = False
            else:
                payload[key] = value

        logging.info("Forwarding to langchain_openai provider URL %s", provider.url)
        headers = {"Authorization": f"Bearer {provider_key}", "Content-Type": "application/json"}
        resp = requests.post(provider.url, headers=headers, json=payload, timeout=30)
        return fastapi.responses.JSONResponse(content=resp.json(), status_code=resp.status_code)
    
    elif provider.api == "langchain_aws":
        # AWS Bedrock - credentials from environment or AWS config
        payload = await request.json()
        payload["model"] = provider.model

        for key, value in request.query_params.items():
            if key == "nickname":
                continue
            if value.isdigit():
                payload[key] = int(value)
            elif value.replace('.', '', 1).isdigit() and '.' in value:
                payload[key] = float(value)
            elif value.lower() == "true":
                payload[key] = True
            elif value.lower() == "false":
                payload[key] = False
            else:
                payload[key] = value

        logging.info("Forwarding to AWS Bedrock model %s", provider.model)
        
        from langchain_aws import ChatBedrock
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        
        lc_messages = []
        role_map = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}
        for msg in payload.get("messages", []):
            role = msg.get("role")
            content = msg.get("content")
            if role in role_map and content:
                lc_messages.append(role_map[role](content=content))
        
        llm = ChatBedrock(
            model_id=provider.model,
            region_name=getattr(provider, "region", "us-east-1"),
            model_kwargs={
                "temperature": payload.get("temperature", 0.7),
                "max_tokens": payload.get("max_tokens", None),
            }
        )
        
        response = llm.invoke(lc_messages)
        
        usage = {}
        if hasattr(response, 'response_metadata') and 'usage' in response.response_metadata:
            usage = response.response_metadata['usage']
        
        response_json = {
            "id": f"chatcmpl-{''.join([chr(random.randint(97, 122)) for _ in range(29)])}",
            "object": "chat.completion",
            "created": int(datetime.now(timezone.utc).timestamp()),
            "model": provider.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response.content},
                "finish_reason": "stop"
            }],
            "usage": usage
        }
        
        return fastapi.responses.JSONResponse(content=response_json, status_code=200)

#https://openrouter.ai/api/v1

def main():
    """Main entry point for the application"""
    uvicorn.run(
        "vanity-gateway:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="vg_cfg/server.key",
        ssl_certfile="vg_cfg/server.crt",
    )

if __name__ == "__main__":
    main()