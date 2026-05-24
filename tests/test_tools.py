"""
Tests for langchain-mycelia-signal v2.0.0.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.tools import BaseTool


class TestConfig:
    def test_supported_pairs_includes_core(self):
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS
        core = {"BTCUSD", "ETHUSD", "SOLUSD", "EURUSD", "XAUUSD",
                "US_CPI", "WTI", "USDTUSD", "USDCUSD", "BTCUSD_VWAP"}
        assert core.issubset(set(SUPPORTED_PAIRS.keys()))

    def test_supported_pairs_count(self):
        from langchain_mycelia_signal.config import SUPPORTED_PAIRS
        assert len(SUPPORTED_PAIRS) >= 56

    def test_indices_complete(self):
        from langchain_mycelia_signal.config import INDICES
        expected = {"MSVI_BTC", "MSVI_ETH", "MSXI_BTC", "MSXI_ETH", "MSSI", "MSTI"}
        assert set(INDICES.keys()) == expected

    def test_derivatives_complete(self):
        from langchain_mycelia_signal.config import DERIVATIVES
        assert "FUNDING_BTC" in DERIVATIVES
        assert "OI_ETH" in DERIVATIVES
        assert "BASIS_SOL" in DERIVATIVES

    def test_gas_chains_complete(self):
        from langchain_mycelia_signal.config import GAS_CHAINS
        expected = {"ETHEREUM", "BASE", "ARBITRUM", "POLYGON", "OPTIMISM", "SOLANA", "INDEX"}
        assert set(GAS_CHAINS.keys()) == expected

    def test_get_endpoint_valid_pair(self):
        from langchain_mycelia_signal.config import get_endpoint
        url = get_endpoint("BTCUSD")
        assert url == "https://api.myceliasignal.com/oracle/price/btc/usd/preview"

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
        assert url == "https://api.myceliasignal.com/oracle/price/btc/usd/vwap/preview"

    def test_get_endpoint_paid_mode(self):
        from langchain_mycelia_signal.config import get_endpoint
        with patch.dict(os.environ, {"MYCELIA_WALLET_PRIVATE_KEY": "0xtest"}):
            url = get_endpoint("BTCUSD")
            assert "/preview" not in url
            assert url == "https://api.myceliasignal.com/oracle/price/btc/usd"

    def test_get_generic_endpoint(self):
        from langchain_mycelia_signal.config import get_generic_endpoint, INDICES
        url = get_generic_endpoint(INDICES, "MSVI_BTC")
        assert url == "https://api.myceliasignal.com/oracle/volatility/btc/usd/preview"

    def test_is_paid_mode_false_when_no_key(self):
        from langchain_mycelia_signal.config import is_paid_mode
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MYCELIA_WALLET_PRIVATE_KEY", None)
            assert is_paid_mode() is False

    def test_is_paid_mode_true_when_key_set(self):
        from langchain_mycelia_signal.config import is_paid_mode
        with patch.dict(os.environ, {"MYCELIA_WALLET_PRIVATE_KEY": "0xdeadbeef"}):
            assert is_paid_mode() is True

    def test_pricing_tiers(self):
        from langchain_mycelia_signal.config import get_price_usd
        assert get_price_usd("BTCUSD") == "$0.01"
        assert get_price_usd("BTCUSD_VWAP") == "$0.02"
        assert get_price_usd("US_CPI") == "$0.10"
        assert get_price_usd("WTI") == "$0.10"
        assert get_price_usd("MSVI_BTC") == "$0.05"
        assert get_price_usd("FUNDING_BTC") == "$0.05"
        assert get_price_usd("OI_BTC") == "$0.01"
        assert get_price_usd("BASIS_BTC") == "$0.02"
        assert get_price_usd("COT_BTC") == "$1.00"


class TestClient:
    def test_fetch_price_free_mode_200(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pair": "BTC/USD",
            "price": "76700.00",
            "currency": "USD",
            "timestamp": "2026-05-24T08:00:00Z",
            "sources": ["binance", "coinbase", "kraken"],
            "method": "median",
        }
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            result = fetch_price("BTCUSD")
        assert "76700.00" in result

    def test_fetch_price_402_free_mode(self):
        from langchain_mycelia_signal.client import fetch_price
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {}
        mock_response.headers = {}
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

    def test_fetch_json_200(self):
        from langchain_mycelia_signal.client import fetch_json
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": 34.5, "regime": "ELEVATED"}
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            result = fetch_json("https://api.myceliasignal.com/oracle/stress/market/preview")
        assert result["value"] == 34.5
        assert result["regime"] == "ELEVATED"

    def test_fetch_json_402_free_mode(self):
        from langchain_mycelia_signal.client import fetch_json
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {}
        mock_response.headers = {}
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MYCELIA_WALLET_PRIVATE_KEY", None)
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.get.return_value = mock_response
                result = fetch_json("https://api.myceliasignal.com/oracle/stress/market")
        assert result["error"] == "payment_required"


class TestTools:
    def test_price_tool_is_callable(self):
        from langchain_mycelia_signal.tools import get_mycelia_price
        assert isinstance(get_mycelia_price, BaseTool)

    def test_index_tool_is_callable(self):
        from langchain_mycelia_signal.tools import get_mycelia_index
        assert isinstance(get_mycelia_index, BaseTool)

    def test_funding_tool_is_callable(self):
        from langchain_mycelia_signal.tools import get_mycelia_funding
        assert isinstance(get_mycelia_funding, BaseTool)

    def test_weather_tool_is_callable(self):
        from langchain_mycelia_signal.tools import get_mycelia_weather
        assert isinstance(get_mycelia_weather, BaseTool)

    def test_gas_tool_is_callable(self):
        from langchain_mycelia_signal.tools import get_mycelia_gas
        assert isinstance(get_mycelia_gas, BaseTool)

    def test_dlc_enum_tool_is_callable(self):
        from langchain_mycelia_signal.tools import dlc_register_enum
        assert isinstance(dlc_register_enum, BaseTool)

    def test_dlc_numeric_tool_is_callable(self):
        from langchain_mycelia_signal.tools import dlc_register_numeric
        assert isinstance(dlc_register_numeric, BaseTool)

    def test_all_tools_have_descriptions(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        for tool in MyceliaSignalTools().as_list():
            assert len(tool.description) > 0, f"{tool.name} has no description"


class TestMyceliaSignalTools:
    def test_as_list_returns_15_tools(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        tools = MyceliaSignalTools().as_list()
        assert isinstance(tools, list)
        assert len(tools) == 15

    def test_price_tools_returns_1(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        assert len(MyceliaSignalTools().price_tools()) == 1

    def test_index_tools_returns_1(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        assert len(MyceliaSignalTools().index_tools()) == 1

    def test_derivatives_tools_returns_3(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        assert len(MyceliaSignalTools().derivatives_tools()) == 3

    def test_data_tools_returns_4(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        assert len(MyceliaSignalTools().data_tools()) == 4

    def test_dlc_tools_returns_6(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        assert len(MyceliaSignalTools().dlc_tools()) == 6

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
        assert len(MyceliaSignalTools().supported_pairs) >= 56

    def test_repr(self):
        from langchain_mycelia_signal import MyceliaSignalTools
        r = repr(MyceliaSignalTools())
        assert "tools=15" in r
        assert "indices=6" in r
