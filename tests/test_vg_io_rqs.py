#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.

"""Unit tests for vg_io.rqs module"""

import pytest
import json
import types
from unittest.mock import Mock, patch, MagicMock
import requests

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vg_io import rqs


class TestGetResponse:
    """Test get_response function"""
    
    def test_successful_request(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {"messages": [{"role": "user", "content": "test"}]}, False
        
        mock_response = {
            "choices": [{"message": {"role": "assistant", "content": "response"}}]
        }
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status = Mock()
            
            result, err = rqs.get_response(mock_cfg, mock_builder)
            
            assert not err
            assert result == mock_response
            assert mock_post.called
            assert mock_post.call_args[0][0] == "https://test.api/v1"
    
    def test_payload_builder_error(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def failing_builder(cfg):
            return "Builder error", True
        
        result, err = rqs.get_response(mock_cfg, failing_builder)
        
        assert err
        assert result == "Builder error"
    
    def test_request_exception(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {"messages": []}, False
        
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Connection error")
            
            result, err = rqs.get_response(mock_cfg, mock_builder)
            
            assert err
            assert "Connection error" in result
    
    def test_includes_auth_header(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="secret-123"
        )
        
        def mock_builder(cfg):
            return {"messages": []}, False
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = {}
            mock_post.return_value.raise_for_status = Mock()
            
            rqs.get_response(mock_cfg, mock_builder)
            
            headers = mock_post.call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer secret-123"
    
    def test_url_params_passed(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {"messages": []}, False
        
        params = {"nickname": "groq-fast", "temperature": "0.7"}
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = {}
            mock_post.return_value.raise_for_status = Mock()
            
            rqs.get_response(mock_cfg, mock_builder, params=params)
            
            assert mock_post.call_args[1]["params"] == params


class TestParseResponse:
    """Test parse_response function"""
    
    def test_successful_parse(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {"messages": []}, False
        
        mock_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Hello, world!"
                }
            }]
        }
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()
            
            content, err = rqs.parse_response(mock_cfg, mock_builder)
            
            assert not err
            assert content == "Hello, world!"
    
    def test_strips_code_blocks(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {"messages": []}, False
        
        mock_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "```python\nprint('hello')\n```"
                }
            }]
        }
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()
            
            content, err = rqs.parse_response(mock_cfg, mock_builder)
            
            assert not err
            assert content == "print('hello')"
    
    def test_handles_get_response_error(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def failing_builder(cfg):
            return "Builder failed", True
        
        content, err = rqs.parse_response(mock_cfg, failing_builder)
        
        assert err
        assert content == "Builder failed"
    
    def test_handles_malformed_response(self):
        mock_cfg = types.SimpleNamespace(
            projectConfig=types.SimpleNamespace(gateway_url="https://test.api/v1"),
            secret_k="test-key"
        )
        
        def mock_builder(cfg):
            return {"messages": []}, False
        
        mock_response = {"invalid": "structure"}
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()
            
            content, err = rqs.parse_response(mock_cfg, mock_builder)
            
            assert err
            assert "Error parsing JSON response" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
