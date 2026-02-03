#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.

"""Unit tests for vanity-gateway.py"""

import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from fastapi.testclient import TestClient
import types

# Import the app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import with underscore since the filename has a hyphen
import importlib.util
spec = importlib.util.spec_from_file_location("vanity_gateway", os.path.join(os.path.dirname(os.path.dirname(__file__)), "vanity-gateway.py"))
vanity_gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vanity_gateway)

app = vanity_gateway.app
load_cfg_from_path = vanity_gateway.load_cfg_from_path

client = TestClient(app)

# Test fixtures
TEST_KEY = "d4adfc04387b63baf75b46544beb0476cfcbcedbb88f21e339d7d29d095d8db6"
MOCK_PROVIDER_KEY = "provider-key-67890"

MOCK_VG_CFG = {
    "providers": {
        "groq-fast": {
            "api": "requests",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key_path": "vg_cfg/Groq.key",
            "model": "openai/gpt-oss-20b"
        },
        "openai-gpt4": {
            "api": "langchain_openai",
            "url": "https://api.openai.com/v1",
            "key_path": "vg_cfg/openai.key",
            "model": "gpt-4o"
        }
    }
}

MOCK_CHAT_PAYLOAD = {
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "groq-fast"
}

MOCK_PROVIDER_RESPONSE = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "openai/gpt-oss-20b",
    "choices": [{
        "index": 0,
        "message": {"role": "assistant", "content": "Hello! How can I help?"},
        "finish_reason": "stop"
    }],
    "usage": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12}
}


class TestLoadCfgFromPath:
    """Test configuration loading"""
    
    def test_load_cfg_converts_to_namespace(self):
        mock_data = '{"providers": {"test": {"api": "requests"}}}'
        with patch("builtins.open", mock_open(read_data=mock_data)):
            cfg = load_cfg_from_path("dummy.json")
            assert hasattr(cfg, "providers")
            assert hasattr(cfg.providers, "test")
            assert cfg.providers.test.api == "requests"


class TestChatCompletionsAuth:
    """Test authentication and authorization"""
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_missing_auth_header(self):
        response = client.post("/chat/completions?nickname=groq-fast", json=MOCK_CHAT_PAYLOAD)
        assert response.status_code == 401
        assert "Invalid or missing authorization token" in response.json()["detail"]
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_invalid_auth_token(self):
        response = client.post(
            "/chat/completions?nickname=groq-fast",
            json=MOCK_CHAT_PAYLOAD,
            headers={"Authorization": "Bearer wrong-token"}
        )
        assert response.status_code == 401
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_valid_auth_token(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
            mock_post.return_value.status_code = 200
            
            response = client.post(
                "/chat/completions?nickname=groq-fast",
                json=MOCK_CHAT_PAYLOAD,
                headers={"Authorization": f"Bearer {TEST_KEY}"}
            )
            assert response.status_code == 200


class TestChatCompletionsRouting:
    """Test provider routing logic"""
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_missing_nickname(self):
        response = client.post(
            "/chat/completions",
            json=MOCK_CHAT_PAYLOAD,
            headers={"Authorization": f"Bearer {TEST_KEY}"}
        )
        assert response.status_code == 400
        assert "Missing nickname" in response.json()["detail"]
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_unknown_provider(self):
        response = client.post(
            "/chat/completions?nickname=unknown-provider",
            json=MOCK_CHAT_PAYLOAD,
            headers={"Authorization": f"Bearer {TEST_KEY}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRequestsProvider:
    """Test requests-based provider forwarding"""
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_forwards_to_provider(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
            mock_post.return_value.status_code = 200
            
            response = client.post(
                "/chat/completions?nickname=groq-fast",
                json=MOCK_CHAT_PAYLOAD,
                headers={"Authorization": f"Bearer {TEST_KEY}"}
            )
            
            assert response.status_code == 200
            assert mock_post.called
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_replaces_model_with_provider_model(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
            mock_post.return_value.status_code = 200
            
            response = client.post(
                "/chat/completions?nickname=groq-fast",
                json=MOCK_CHAT_PAYLOAD,
                headers={"Authorization": f"Bearer {TEST_KEY}"}
            )
            
            assert response.status_code == 200
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_merges_url_params_as_integers(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
            mock_post.return_value.status_code = 200
            
            response = client.post(
                "/chat/completions?nickname=groq-fast&max_tokens=100",
                json=MOCK_CHAT_PAYLOAD,
                headers={"Authorization": f"Bearer {TEST_KEY}"}
            )
            
            assert response.status_code == 200
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_merges_url_params_as_floats(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
            mock_post.return_value.status_code = 200
            
            response = client.post(
                "/chat/completions?nickname=groq-fast&temperature=0.5",
                json=MOCK_CHAT_PAYLOAD,
                headers={"Authorization": f"Bearer {TEST_KEY}"}
            )
            
            assert response.status_code == 200
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_merges_url_params_as_booleans(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
            mock_post.return_value.status_code = 200
            
            response = client.post(
                "/chat/completions?nickname=groq-fast&stream=false",
                json=MOCK_CHAT_PAYLOAD,
                headers={"Authorization": f"Bearer {TEST_KEY}"}
            )
            
            assert response.status_code == 200
        
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("requests.post") as mock_post:
                mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
                mock_post.return_value.status_code = 200
                
                response = client.post(
                    "/chat/completions?nickname=groq-fast",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                assert response.status_code == 200
                assert mock_post.called
                call_args = mock_post.call_args
                assert call_args[0][0] == "https://api.groq.com/openai/v1/chat/completions"
                assert call_args[1]["headers"]["Authorization"] == f"Bearer {MOCK_PROVIDER_KEY}"
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    @patch("tests.test_vanity_gateway.vanity_gateway.load_cfg_from_path")
    def test_replaces_model_with_provider_model(self, mock_load_cfg):
        mock_load_cfg.return_value = types.SimpleNamespace(**MOCK_VG_CFG)
        
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("requests.post") as mock_post:
                mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
                mock_post.return_value.status_code = 200
                
                client.post(
                    "/chat/completions?nickname=groq-fast",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                sent_payload = mock_post.call_args[1]["json"]
                assert sent_payload["model"] == "openai/gpt-oss-20b"
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    @patch("tests.test_vanity_gateway.vanity_gateway.load_cfg_from_path")
    def test_merges_url_params_as_integers(self, mock_load_cfg):
        mock_load_cfg.return_value = types.SimpleNamespace(**MOCK_VG_CFG)
        
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("requests.post") as mock_post:
                mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
                mock_post.return_value.status_code = 200
                
                client.post(
                    "/chat/completions?nickname=groq-fast&max_tokens=100",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                sent_payload = mock_post.call_args[1]["json"]
                assert sent_payload["max_tokens"] == 100
                assert isinstance(sent_payload["max_tokens"], int)
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    @patch("tests.test_vanity_gateway.vanity_gateway.load_cfg_from_path")
    def test_merges_url_params_as_floats(self, mock_load_cfg):
        mock_load_cfg.return_value = types.SimpleNamespace(**MOCK_VG_CFG)
        
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("requests.post") as mock_post:
                mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
                mock_post.return_value.status_code = 200
                
                client.post(
                    "/chat/completions?nickname=groq-fast&temperature=0.5",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                sent_payload = mock_post.call_args[1]["json"]
                assert sent_payload["temperature"] == 0.5
                assert isinstance(sent_payload["temperature"], float)
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    @patch("tests.test_vanity_gateway.vanity_gateway.load_cfg_from_path")
    def test_merges_url_params_as_booleans(self, mock_load_cfg):
        mock_load_cfg.return_value = types.SimpleNamespace(**MOCK_VG_CFG)
        
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("requests.post") as mock_post:
                mock_post.return_value.json.return_value = MOCK_PROVIDER_RESPONSE
                mock_post.return_value.status_code = 200
                
                client.post(
                    "/chat/completions?nickname=groq-fast&stream=false",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                sent_payload = mock_post.call_args[1]["json"]
                assert sent_payload["stream"] is False
                assert isinstance(sent_payload["stream"], bool)


class TestLangchainOpenAIProvider:
    """Test langchain_openai provider forwarding"""
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    def test_forwards_to_langchain_provider(self):
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("vg_io.oai.ChatOpenAI") as mock_chat:
                mock_response = Mock()
                mock_response.content = "Test response"
                mock_response.response_metadata = {}
                mock_chat.return_value.invoke.return_value = mock_response
                
                response = client.post(
                    "/chat/completions?nickname=openai-gpt4",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                assert response.status_code == 200
    
    @patch("builtins.open", mock_open(read_data=TEST_KEY))
    @patch("tests.test_vanity_gateway.vanity_gateway.load_cfg_from_path")
    def test_replaces_model_for_langchain(self, mock_load_cfg):
        mock_load_cfg.return_value = types.SimpleNamespace(**MOCK_VG_CFG)
        
        with patch("builtins.open", mock_open(read_data=MOCK_PROVIDER_KEY)):
            with patch("vg_io.oai.ChatOpenAI") as mock_chat:
                mock_response = Mock()
                mock_response.content = "Test"
                mock_response.response_metadata = {}
                mock_chat.return_value.invoke.return_value = mock_response
                
                response = client.post(
                    "/chat/completions?nickname=openai-gpt4",
                    json=MOCK_CHAT_PAYLOAD,
                    headers={"Authorization": f"Bearer {TEST_KEY}"}
                )
                
                assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
