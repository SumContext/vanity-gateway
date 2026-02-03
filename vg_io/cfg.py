
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

# oai.py

import json, types
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import time
import random

def load_from_file(target_file, secret_key_path):
    with open(target_file, "r", encoding="utf-8") as f:
        cfg = json.load(f, object_hook=lambda d: types.SimpleNamespace(**d))
    with open(secret_key_path, "r") as f:
        cfg.secret_k = f.read().strip()        
    return cfg

def inline_set(raw_json, secret_key_path):
    # import types, json
    # Convert dict -> SimpleNamespace recursively
    def to_ns(obj):
        if isinstance(obj, dict):
            return types.SimpleNamespace(**{k: to_ns(v) for k, v in obj.items()})
        if isinstance(obj, list):
            return [to_ns(x) for x in obj]
        return obj
    # Parse the JSON string passed in
    raw_cfg = json.loads(raw_json)
    cfg = to_ns(raw_cfg)
    with open(secret_key_path, "r") as f:
        cfg.secret_k = f.read().strip()
    return cfg
