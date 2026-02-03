#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock, patch
from vg_io import aws

@pytest.fixture
def mock_cfg():
    cfg = Mock()
    cfg.aws_region = "us-west-2"
    cfg.key_path = None  # No key file in tests
    return cfg

@pytest.fixture
def mock_payload_builder():
    def builder(cfg):
        return {
            "model": "anthropic.claude-sonnet-4-5-20250929-v1:0",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 1000
        }, False
    return builder

def test_get_response_success(mock_cfg, mock_payload_builder):
    with patch('vg_io.aws.ChatBedrock') as mock_bedrock:
        mock_response = Mock()
        mock_response.content = "Hello! How can I help?"
        mock_response.response_metadata = {'usage': {'input_tokens': 10, 'output_tokens': 20}}
        mock_bedrock.return_value.invoke.return_value = mock_response
        
        result, err = aws.get_response(mock_cfg, mock_payload_builder)
        
        assert not err
        assert result['object'] == 'chat.completion'
        assert result['choices'][0]['message']['content'] == "Hello! How can I help?"
        assert result['usage'] == {'input_tokens': 10, 'output_tokens': 20}

def test_get_response_with_params(mock_cfg, mock_payload_builder):
    with patch('vg_io.aws.ChatBedrock') as mock_bedrock:
        mock_response = Mock()
        mock_response.content = "Response"
        mock_response.response_metadata = {}
        mock_bedrock.return_value.invoke.return_value = mock_response
        
        params = {"temperature": 0.9}
        result, err = aws.get_response(mock_cfg, mock_payload_builder, params=params)
        
        assert not err

def test_get_response_default_region():
    cfg = Mock(spec=[])
    
    def builder(cfg):
        return {"model": "test", "messages": [{"role": "user", "content": "Hi"}]}, False
    
    with patch('vg_io.aws.ChatBedrock') as mock_bedrock:
        mock_response = Mock()
        mock_response.content = "Hi"
        mock_response.response_metadata = {}
        mock_bedrock.return_value.invoke.return_value = mock_response
        
        result, err = aws.get_response(cfg, builder)
        
        assert not err
        mock_bedrock.assert_called_once()
        assert mock_bedrock.call_args[1]['region_name'] == 'us-east-1'

def test_get_response_builder_error(mock_cfg):
    def error_builder(cfg):
        return "Builder error", True
    
    result, err = aws.get_response(mock_cfg, error_builder)
    
    assert err
    assert result == "Builder error"

def test_get_response_invalid_message(mock_cfg):
    def builder(cfg):
        return {"model": "test", "messages": [{"role": "invalid", "content": "Hi"}]}, False
    
    result, err = aws.get_response(mock_cfg, builder)
    
    assert err
    assert "Invalid message" in result

def test_parse_response_success(mock_cfg, mock_payload_builder):
    with patch('vg_io.aws.ChatBedrock') as mock_bedrock:
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_response.response_metadata = {}
        mock_bedrock.return_value.invoke.return_value = mock_response
        
        result, err = aws.parse_response(mock_cfg, mock_payload_builder)
        
        assert not err
        assert result == "Test response"

def test_parse_response_strips_code_blocks(mock_cfg, mock_payload_builder):
    with patch('vg_io.aws.ChatBedrock') as mock_bedrock:
        mock_response = Mock()
        mock_response.content = "```python\nprint('hello')\n```"
        mock_response.response_metadata = {}
        mock_bedrock.return_value.invoke.return_value = mock_response
        
        result, err = aws.parse_response(mock_cfg, mock_payload_builder)
        
        assert not err
        assert result == "print('hello')"
