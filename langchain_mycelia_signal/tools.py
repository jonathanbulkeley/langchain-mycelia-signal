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
    Each response includes the price, timestamp, number of sources, aggregation
    method, and (in paid mode) a cryptographic signature for on-chain verification.

    Supported pairs:
        BTCUSD      — Bitcoin / US Dollar spot (median, 9 sources)
        BTCUSD_VWAP — Bitcoin / US Dollar 5-min VWAP
        ETHUSD      — Ethereum / US Dollar spot (median, 5 sources)
        EURUSD      — Euro / US Dollar spot (median, 8 sources incl. central banks)
        XAUUSD      — Gold / US Dollar spot (median, 8 sources)
        SOLUSD      — Solana / US Dollar spot (median, 9 sources)
        BTCEUR      — Bitcoin / Euro spot (cross-rate + direct feeds)
        BTCEUR_VWAP — Bitcoin / Euro 5-min VWAP
        ETHEUR      — Ethereum / Euro spot (hybrid)
        SOLEUR      — Solana / Euro spot (hybrid)
        XAUEUR      — Gold / Euro spot (cross-rate)

    Args:
        pair: The trading pair to query. Use uppercase with no slash,
              e.g. 'BTCUSD', 'ETHUSD', 'XAUUSD'. VWAP variants use
              underscore suffix: 'BTCUSD_VWAP', 'BTCEUR_VWAP'.

    Returns:
        Formatted string with price, timestamp, source count, method,
        and signature fields (signed attestation in paid mode).

    Examples:
        get_mycelia_price("BTCUSD")
        get_mycelia_price("ETHUSD")
        get_mycelia_price("XAUUSD")
        get_mycelia_price("EURUSD")
        get_mycelia_price("BTCUSD_VWAP")
    """
    return fetch_price(pair)
