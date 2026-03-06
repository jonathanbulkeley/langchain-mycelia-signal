"""
Configuration for langchain-mycelia-signal.

Free mode:   No env var needed. Hits free endpoints. No signature returned.
Paid mode:   Set MYCELIA_WALLET_PRIVATE_KEY to a funded Base wallet private key.
             Tool pays $0.001 per query via x402 (USDC on Base) automatically.
             Returns fully cryptographically signed attestation.
"""

import os

# Base URL for the Mycelia Signal API
API_BASE_URL = "https://api.myceliasignal.com"

# All supported pairs and their endpoint paths
SUPPORTED_PAIRS = {
    "BTCUSD":      "/oracle/btcusd",
    "BTCUSD_VWAP": "/oracle/btcusd/vwap",
    "ETHUSD":      "/oracle/ethusd",
    "EURUSD":      "/oracle/eurusd",
    "XAUUSD":      "/oracle/xauusd",
    "SOLUSD":      "/oracle/solusd",
    "BTCEUR":      "/oracle/btceur",
    "BTCEUR_VWAP": "/oracle/btceur/vwap",
    "ETHEUR":      "/oracle/etheur",
    "SOLEUR":      "/oracle/soleur",
    "XAUEUR":      "/oracle/xaueur",
}

# Human-readable descriptions for each pair (used in tool docstring)
PAIR_DESCRIPTIONS = {
    "BTCUSD":      "Bitcoin / US Dollar spot price (median of 9 sources)",
    "BTCUSD_VWAP": "Bitcoin / US Dollar 5-minute volume-weighted average price",
    "ETHUSD":      "Ethereum / US Dollar spot price (median of 5 sources)",
    "EURUSD":      "Euro / US Dollar spot price (median of 8 sources including central banks)",
    "XAUUSD":      "Gold (XAU) / US Dollar spot price (median of 8 sources)",
    "SOLUSD":      "Solana / US Dollar spot price (median of 9 sources)",
    "BTCEUR":      "Bitcoin / Euro spot price (cross-rate + direct exchange feeds)",
    "BTCEUR_VWAP": "Bitcoin / Euro 5-minute volume-weighted average price",
    "ETHEUR":      "Ethereum / Euro spot price (hybrid: direct EUR feeds + cross-rate)",
    "SOLEUR":      "Solana / Euro spot price (hybrid: direct EUR feeds + cross-rate)",
    "XAUEUR":      "Gold (XAU) / Euro spot price (cross-rate: XAUUSD / EURUSD)",
}


def get_wallet_key() -> str | None:
    """Return the wallet private key from environment, or None if not set."""
    return os.environ.get("MYCELIA_WALLET_PRIVATE_KEY")


def is_paid_mode() -> bool:
    """Return True if a wallet key is configured (paid mode), False otherwise."""
    return get_wallet_key() is not None


def get_endpoint(pair: str) -> str:
    """Return the full API URL for a given pair."""
    pair = pair.upper().replace("/", "").replace("-", "_")
    if pair not in SUPPORTED_PAIRS:
        raise ValueError(
            f"Unsupported pair: '{pair}'. "
            f"Supported pairs: {', '.join(SUPPORTED_PAIRS.keys())}"
        )
    return API_BASE_URL + SUPPORTED_PAIRS[pair]
