#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.

"""Unit tests for vg_io.oai module"""

import pytest
import json
import types
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vg_io import oai


class TestGetResponse:
    """Test get_response function for langchain_openai"""
    
    def test_successful_request(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [{"role": "user", "content": "test"}],
                "model": "gpt-4o",
                "temperature": 0.7
            }, False
        
        with patch("vg_io.oai.ChatOpenAI") as mock_chat:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.response_metadata = {"token_usage": {"total_tokens": 10}}
            mock_instance.invoke.return_value = mock_response
            mock_chat.return_value = mock_instance
            
            result, err = oai.get_response(mock_cfg, mock_builder)
            
            assert not err
            assert result["choices"][0]["message"]["content"] == "Test response"
            assert "usage" in result
    
    def test_payload_builder_error(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def failing_builder(cfg):
            return "Builder error", True
        
        result, err = oai.get_response(mock_cfg, failing_builder)
        
        assert err
        assert result == "Builder error"
    
    def test_converts_messages_to_langchain_format(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [
                    {"role": "system", "content": "You are helpful"},
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ],
                "model": "gpt-4o"
            }, False
        
        with patch("vg_io.oai.ChatOpenAI") as mock_chat:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Response"
            mock_response.response_metadata = {}
            mock_instance.invoke.return_value = mock_response
            mock_chat.return_value = mock_instance
            
            oai.get_response(mock_cfg, mock_builder)
            
            invoke_args = mock_instance.invoke.call_args[0][0]
            assert len(invoke_args) == 3
    
    def test_merges_params_into_payload(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [{"role": "user", "content": "test"}],
                "model": "gpt-4o"
            }, False
        
        params = {"temperature": 0.9, "max_tokens": 500}
        
        with patch("vg_io.oai.ChatOpenAI") as mock_chat:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Response"
            mock_response.response_metadata = {}
            mock_instance.invoke.return_value = mock_response
            mock_chat.return_value = mock_instance
            
            oai.get_response(mock_cfg, mock_builder, params=params)
            
            chat_init_kwargs = mock_chat.call_args[1]
            assert chat_init_kwargs["temperature"] == 0.9
            assert chat_init_kwargs["max_tokens"] == 500
    
    def test_handles_invalid_message_role(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [{"role": "invalid", "content": "test"}],
                "model": "gpt-4o"
            }, False
        
        with patch("vg_io.oai.ChatOpenAI"):
            result, err = oai.get_response(mock_cfg, mock_builder)
            
            assert err
            assert "Invalid message" in result
    
    def test_creates_openai_compatible_response(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [{"role": "user", "content": "test"}],
                "model": "gpt-4o"
            }, False
        
        with patch("vg_io.oai.ChatOpenAI") as mock_chat:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test content"
            mock_response.response_metadata = {"token_usage": {"total_tokens": 15}}
            mock_instance.invoke.return_value = mock_response
            mock_chat.return_value = mock_instance
            
            result, err = oai.get_response(mock_cfg, mock_builder)
            
            assert not err
            assert "id" in result
            assert result["object"] == "chat.completion"
            assert "created" in result
            assert result["model"] == "gpt-4o"
            assert result["choices"][0]["message"]["role"] == "assistant"
            assert result["choices"][0]["finish_reason"] == "stop"


class TestParseResponse:
    """Test parse_response function"""
    
    def test_successful_parse(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [{"role": "user", "content": "test"}],
                "model": "gpt-4o"
            }, False
        
        with patch("vg_io.oai.ChatOpenAI") as mock_chat:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Hello, world!"
            mock_response.response_metadata = {}
            mock_instance.invoke.return_value = mock_response
            mock_chat.return_value = mock_instance
            
            content, err = oai.parse_response(mock_cfg, mock_builder)
            
            assert not err
            assert content == "Hello, world!"
    
    def test_strips_code_blocks(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {
                "messages": [{"role": "user", "content": "test"}],
                "model": "gpt-4o"
            }, False
        
        with patch("vg_io.oai.ChatOpenAI") as mock_chat:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "```python\nprint('hello')\n```"
            mock_response.response_metadata = {}
            mock_instance.invoke.return_value = mock_response
            mock_chat.return_value = mock_instance
            
            content, err = oai.parse_response(mock_cfg, mock_builder)
            
            assert not err
            assert content == "print('hello')"
    
    def test_handles_get_response_error(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def failing_builder(cfg):
            return "Builder failed", True
        
        content, err = oai.parse_response(mock_cfg, failing_builder)
        
        assert err
        assert content == "Builder failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
