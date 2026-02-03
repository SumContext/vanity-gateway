#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.

# aws.py

import json, types, os
from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import time
import random
import configparser

def get_response(cfg, payload_builder, *builder_args, verify=True, params=None):
    """
    Use langchain_aws - Send Message to AWS Bedrock
    """
    try:
        payload, err = payload_builder(cfg, *builder_args)
        if err: return payload, True

        if params:
            payload.update(params)

        lc_messages = []
        role_map = {
            "system": SystemMessage,
            "user": HumanMessage,
            "assistant": AIMessage,
        }
        for msg in payload.get("messages", []):
            role = msg.get("role")
            content = msg.get("content")
            if role in role_map and content:
                lc_messages.append(role_map[role](content=content))
            else:
                raise ValueError(f"Invalid message: {msg}")

        # Load AWS credentials from key_path if provided
        aws_access_key_id = None
        aws_secret_access_key = None
        if hasattr(cfg, 'key_path') and cfg.key_path:
            config = configparser.ConfigParser()
            config.read(cfg.key_path)
            if 'default' in config:
                aws_access_key_id = config['default'].get('aws_access_key_id')
                aws_secret_access_key = config['default'].get('aws_secret_access_key')

        llm = ChatBedrock(
            model_id=payload["model"],
            region_name=getattr(cfg, 'aws_region', 'us-east-1'),
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
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
            "id": f"chatcmpl-{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=29))}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": payload["model"],
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": usage
        }

        return response_json, False
    except Exception as e:
        return f"Error: {str(e)}", True

def parse_response(cfg, payload_builder, *builder_args, verify=True, params=None):
    """
    Use langchain_aws - Receive Response from AWS Bedrock
    """
    data, err = get_response(cfg, payload_builder, *builder_args, verify=verify, params=params)
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
