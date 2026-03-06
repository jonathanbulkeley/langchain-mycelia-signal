"""
Tests for langchain-mycelia-signal package.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.tools import BaseTool


# ─────────────────────────────────────────────
# Config Tests
# ─────────────────────────────────────────────

class TestConfig:
    def test_supported_pairs_complete(self):
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS
        expected = {"BTCUSD", "BTCUSD_VWAP", "ETHUSD", "EURUSD", "XAUUSD",
                    "SOLUSD", "BTCEUR", "BTCEUR_VWAP", "ETHEUR", "SOLEUR", "XAUEUR"}
        assert set(SUPPORTED_PAIRS.keys()) == expected

    def test_get_endpoint_valid_pair(self):
        from langchain_mycelia_signal.config import get_endpoint
        url = get_endpoint("BTCUSD")
        assert url == "https://api.myceliasignal.com/oracle/btcusd/preview"

    def test_get_endpoint_case_insensitive(self):
        from langchain_mycelia_signal.config import get_endpoint
        assert get_endpoint("btcusd") == get_endpoint("BTCUSD")

    def test_get_endpoint_invalid_pair(self):
        from langchain_mycelia_signal.config import get_endpoint
        with pytest.raises(ValueError, match="Unsupported pair"):
            get_endpoint("INVALID")

    def test_get_endpoint_vwap(self):
        from langchain_mycelia_signal.config import get_endpoint
        url = get_endpoint("BTCUSD_VWAP")
        assert url == "https://api.myceliasignal.com/oracle/btcusd/vwap/preview"

    def test_is_paid_mode_false_when_no_key(self):
        from langchain_mycelia_signal.config import is_paid_mode
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MYCELIA_WALLET_PRIVATE_KEY", None)
            assert is_paid_mode() is False

    def test_is_paid_mode_true_when_key_set(self):
        from langchain_mycelia_signal.config import is_paid_mode
        with patch.dict(os.environ, {"MYCELIA_WALLET_PRIVATE_KEY": "0xdeadbeef"}):
            assert is_paid_mode() is True

    def test_pair_descriptions_match_supported_pairs(self):
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS, PAIR_DESCRIPTIONS
        assert set(SUPPORTED_PAIRS.keys()) == set(PAIR_DESCRIPTIONS.keys())


# ─────────────────────────────────────────────
# Client Tests
# ─────────────────────────────────────────────

class TestClient:
    def test_fetch_price_free_mode_200(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pair": "BTCUSD",
            "price": "70000.00",
            "currency": "USD",
            "timestamp": "2026-03-06T00:00:00Z",
            "sources": ["coinbase", "kraken"],
            "method": "median",
            "preview": True,
            "signed": False,
        }
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            result = fetch_price("BTCUSD")
        assert "70000.00" in result
        assert "BTCUSD" in result

    def test_fetch_price_free_mode_402_returns_upgrade_message(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {"error": "payment required"}
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MYCELIA_WALLET_PRIVATE_KEY", None)
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.get.return_value = mock_response
                result = fetch_price("BTCUSD")
        assert "MYCELIA_WALLET_PRIVATE_KEY" in result

    def test_fetch_price_invalid_pair(self):
        from langchain_mycelia_signal.client import fetch_price
        with pytest.raises(ValueError, match="Unsupported pair"):
            fetch_price("INVALID")

    def test_fetch_price_timeout(self):
        import httpx
        from langchain_mycelia_signal.client import fetch_price
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("timeout")
            result = fetch_price("BTCUSD")
        assert "timed out" in result

    def test_result_includes_signed_false_when_no_signature(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pair": "BTCUSD",
            "price": "70000.00",
            "currency": "USD",
            "timestamp": "2026-03-06T00:00:00Z",
            "sources": ["coinbase"],
            "method": "median",
            "preview": True,
            "signed": False,
        }
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            result = fetch_price("BTCUSD")
        assert "Signed:    False" in result

    def test_result_includes_signed_true_when_signature_present(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pair": "BTCUSD",
            "price": "70000.00",
            "currency": "USD",
            "timestamp": "2026-03-06T00:00:00Z",
            "sources": ["coinbase"],
            "method": "median",
            "signature": "abc123",
            "pubkey": "0xdeadbeef",
            "canonical": "v1|BTCUSD|70000.00|USD|2|...",
        }
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            result = fetch_price("BTCUSD")
        assert "Signed:    True" in result


# ─────────────────────────────────────────────
# Tool Tests
# ─────────────────────────────────────────────

class TestTools:
    def test_tool_is_callable(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        assert isinstance(get_mycelia_price, BaseTool)

    def test_tool_has_name(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        assert get_mycelia_price.name == "get_mycelia_price"

    def test_tool_has_description(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        assert len(get_mycelia_price.description) > 0

    def test_tool_description_lists_all_pairs(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS
        for pair in SUPPORTED_PAIRS:
            assert pair in get_mycelia_price.description


# ─────────────────────────────────────────────
# MyceliaSignalTools Tests
# ─────────────────────────────────────────────

class TestMyceliaSignalTools:
    def test_as_list_returns_list(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        tools = MyceliaSignalTools().as_list()
        assert isinstance(tools, list)
        assert len(tools) == 1

    def test_mode_free_when_no_key(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MYCELIA_WALLET_PRIVATE_KEY", None)
            assert MyceliaSignalTools().mode == "free"

    def test_mode_paid_when_key_set(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        with patch.dict(os.environ, {"MYCELIA_WALLET_PRIVATE_KEY": "0xdeadbeef"}):
            assert MyceliaSignalTools().mode == "paid"

    def test_supported_pairs_count(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        assert len(MyceliaSignalTools().supported_pairs) == 11

    def test_repr_contains_mode_and_counts(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        r = repr(MyceliaSignalTools())
        assert "free" in r or "paid" in r