"""
LangChain tools for Mycelia Signal oracle data.

Usage:
    from langchain_mycelia_signal import MyceliaSignalTools

    tools = MyceliaSignalTools().as_list()
    # Pass tools to your LangChain agent
"""

from langchain_core.tools import tool

from .client import fetch_price
from .config import PAIR_DESCRIPTIONS, SUPPORTED_PAIRS


@tool
def get_mycelia_price(pair: str) -> str:
    """
    Get a real-time price attestation from Mycelia Signal oracle.

    Returns cryptographically signed price data for the requested trading pair.
    Each response includes the price, timestamp, sources, aggregation method,
    and (in paid mode) a cryptographic signature for on-chain verification.

    CRYPTO SPOT (10 sats / $0.01):
        BTCUSD, BTCEUR, BTCJPY
        ETHUSD, ETHEUR, ETHJPY
        SOLUSD, SOLEUR, SOLJPY
        XRPUSD, ADAUSD, DOGEUSD

    CRYPTO VWAP — 5-minute (20 sats / $0.02):
        BTCUSD_VWAP, BTCEUR_VWAP

    PRECIOUS METALS (10 sats / $0.01):
        XAUUSD, XAUEUR, XAUJPY

    FX PAIRS (10 sats / $0.01):
        EURUSD, EURJPY, EURGBP, EURCHF, EURCNY, EURCAD
        GBPUSD, GBPJPY, GBPCHF, GBPCNY, GBPCAD
        USDJPY, USDCHF, USDCNY, USDCAD
        CHFJPY, CHFCAD, CNYJPY, CNYCAD, CADJPY

    US ECONOMIC INDICATORS (1000 sats / $0.10):
        US_CPI, US_CPI_CORE, US_UNRATE, US_NFP
        US_FEDFUNDS, US_GDP, US_PCE, US_YIELD_CURVE

    EU ECONOMIC INDICATORS (1000 sats / $0.10):
        EU_HICP, EU_HICP_CORE, EU_HICP_SERVICES
        EU_UNRATE, EU_GDP, EU_EMPLOYMENT

    COMMODITIES (1000 sats / $0.10):
        WTI, BRENT, NATGAS, COPPER, DXY

    Args:
        pair: The trading pair or indicator to query. Use uppercase with no slash,
              e.g. 'BTCUSD', 'EURUSD', 'XAUUSD', 'US_CPI', 'WTI'.
              VWAP variants use underscore suffix: 'BTCUSD_VWAP'.

    Returns:
        Formatted string with price, timestamp, source count, method,
        and signature fields (signed attestation in paid mode).

    Examples:
        get_mycelia_price("BTCUSD")
        get_mycelia_price("EURUSD")
        get_mycelia_price("XAUUSD")
        get_mycelia_price("US_CPI")
        get_mycelia_price("WTI")
        get_mycelia_price("BTCUSD_VWAP")
    """
    return fetch_price(pair)
