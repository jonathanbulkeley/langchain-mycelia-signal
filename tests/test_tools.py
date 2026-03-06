"""
Tests for langchain-mycelia-signal.

Run with: pytest tests/
"""

import os
from unittest.mock import MagicMock, patch

import pytest


# -- Config tests --------------------------------------------------------------

class TestConfig:

    def test_supported_pairs_complete(self):
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS
        expected = {
            "BTCUSD", "BTCUSD_VWAP", "ETHUSD", "EURUSD", "XAUUSD",
            "SOLUSD", "BTCEUR", "BTCEUR_VWAP", "ETHEUR", "SOLEUR", "XAUEUR"
        }
        assert set(SUPPORTED_PAIRS.keys()) == expected

    def test_get_endpoint_valid_pair(self):
        from langchain_mycelia_signal.config import get_endpoint
        url = get_endpoint("BTCUSD")
        assert url == "https://api.myceliasignal.com/oracle/btcusd"

    def test_get_endpoint_case_insensitive(self):
        from langchain_mycelia_signal.config import get_endpoint
        assert get_endpoint("btcusd") == get_endpoint("BTCUSD")

    def test_get_endpoint_invalid_pair(self):
        from langchain_mycelia_signal.config import get_endpoint
        with pytest.raises(ValueError, match="Unsupported pair"):
            get_endpoint("DOGEUSD")

    def test_get_endpoint_vwap(self):
        from langchain_mycelia_signal.config import get_endpoint
        url = get_endpoint("BTCUSD_VWAP")
        assert url == "https://api.myceliasignal.com/oracle/btcusd/vwap"

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
        from langchain_mycelia_signal.config import PAIR_DESCRIPTIONS, SUPPORTED_PAIRS
        assert set(PAIR_DESCRIPTIONS.keys()) == set(SUPPORTED_PAIRS.keys())


# -- Client tests --------------------------------------------------------------

class TestClient:

    def _mock_200_response(self, pair="BTCUSD"):
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {
            "pair":      pair,
            "price":     "84231.50",
            "currency":  "USD",
            "timestamp": "2026-03-05T12:00:00Z",
            "sources":   "Coinbase,Kraken,Bitstamp,Gemini,Bitfinex,Binance,BinanceUS,OKX,Gate.io",
            "method":    "median",
            "signature": "MEUCIQD...",
            "pubkey":    "02abc...",
            "canonical": "v1|BTCUSD|84231.50|USD|2|2026-03-05T12:00:00Z|abc123|Coinbase,...|median",
        }
        return mock

    def _mock_402_response(self):
        mock = MagicMock()
        mock.status_code = 402
        mock.json.return_value = {
            "x402_payment_required": {
                "maxAmountRequired": "1000",
                "payTo": "0xrecipient",
                "asset": "0xusdc",
                "extra": {"chainId": "8453"},
            }
        }
        return mock

    def test_fetch_price_free_mode_200(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = self._mock_200_response()

        with patch("langchain_mycelia_signal.client.is_paid_mode", return_value=False), \
             patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = fetch_price("BTCUSD")

        assert "84231.50" in result
        assert "BTCUSD" in result
        assert "USD" in result

    def test_fetch_price_free_mode_402_returns_upgrade_message(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = self._mock_402_response()

        with patch("langchain_mycelia_signal.client.is_paid_mode", return_value=False), \
             patch("langchain_mycelia_signal.client.get_wallet_key", return_value=None), \
             patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = fetch_price("BTCUSD")

        assert "MYCELIA_WALLET_PRIVATE_KEY" in result
        assert "x402" in result

    def test_fetch_price_invalid_pair(self):
        from langchain_mycelia_signal.client import fetch_price
        with pytest.raises(ValueError, match="Unsupported pair"):
            fetch_price("INVALID")

    def test_fetch_price_timeout(self):
        import httpx
        from langchain_mycelia_signal.client import fetch_price

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = httpx.TimeoutException("timed out")
            mock_client_class.return_value = mock_client

            result = fetch_price("BTCUSD")

        assert "timed out" in result.lower() or "timeout" in result.lower()

    def test_result_includes_signed_false_when_no_signature(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pair": "BTCUSD", "price": "84000", "currency": "USD",
            "timestamp": "2026-03-05T12:00:00Z", "sources": "Coinbase,Kraken",
            "method": "median",
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = fetch_price("BTCUSD")

        assert "Signed:    False" in result

    def test_result_includes_signed_true_when_signature_present(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = self._mock_200_response()

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = fetch_price("BTCUSD")

        assert "Signed:    True" in result


# -- Tool tests ----------------------------------------------------------------

class TestTools:

    def test_tool_is_callable(self):
        from langchain_core.tools import BaseTool
        from langchain_mycelia_signal.tools import get_mycelia_price
        assert isinstance(get_mycelia_price, BaseTool)

    def test_tool_has_name(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        assert get_mycelia_price.name == "get_mycelia_price"

    def test_tool_has_description(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        desc = get_mycelia_price.description
        assert "BTCUSD" in desc
        assert "pair" in desc.lower()

    def test_tool_description_lists_all_pairs(self):
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS
        from langchain_mycelia_signal.tools import get_mycelia_price
        desc = get_mycelia_price.description
        for pair in SUPPORTED_PAIRS:
            assert pair in desc, f"Pair {pair} missing from tool description"


# -- MyceliaSignalTools class tests --------------------------------------------

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
            t = MyceliaSignalTools()
            assert t.mode == "free"

    def test_mode_paid_when_key_set(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        with patch.dict(os.environ, {"MYCELIA_WALLET_PRIVATE_KEY": "0xdeadbeef"}):
            t = MyceliaSignalTools()
            assert t.mode == "paid"

    def test_supported_pairs_count(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        t = MyceliaSignalTools()
        assert len(t.supported_pairs) == 11

    def test_repr_contains_mode_and_counts(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        t = MyceliaSignalTools()
        r = repr(t)
        assert "mode=" in r
        assert "pairs=11" in r
        assert "tools=1" in r