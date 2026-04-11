"""
Configuration for langchain-mycelia-signal.
Free mode:   No env var needed. Hits preview endpoints. Returns unsigned price data.
Paid mode:   Set MYCELIA_WALLET_PRIVATE_KEY to a funded Base wallet private key.
             Tool pays automatically via x402 (USDC on Base).
             Price pairs: $0.01 per query. Econ/commodities: $0.10 per query.
             Returns fully cryptographically signed attestation.
"""
import os

# Base URL for the Mycelia Signal API
API_BASE_URL = "https://api.myceliasignal.com"

# All supported pairs and their endpoint paths — new namespace (Mar 15 2026)
SUPPORTED_PAIRS = {
    # ── Crypto spot ───────────────────────────────────────────────────────────
    "BTCUSD":           "/oracle/price/btc/usd",
    "BTCEUR":           "/oracle/price/btc/eur",
    "BTCJPY":           "/oracle/price/btc/jpy",
    "ETHUSD":           "/oracle/price/eth/usd",
    "ETHEUR":           "/oracle/price/eth/eur",
    "ETHJPY":           "/oracle/price/eth/jpy",
    "SOLUSD":           "/oracle/price/sol/usd",
    "SOLEUR":           "/oracle/price/sol/eur",
    "SOLJPY":           "/oracle/price/sol/jpy",
    "XRPUSD":           "/oracle/price/xrp/usd",
    "ADAUSD":           "/oracle/price/ada/usd",
    "DOGEUSD":          "/oracle/price/doge/usd",
    # ── Stablecoin pegs ───────────────────────────────────────────────────────────
    "USDTUSD":          "/oracle/price/usdt/usd",
    "USDCUSD":          "/oracle/price/usdc/usd",
    "USDTEUR":          "/oracle/price/usdt/eur",
    "USDTJPY":          "/oracle/price/usdt/jpy",
    # ── Crypto VWAP ───────────────────────────────────────────────────────────────
    "BTCUSD_VWAP":      "/oracle/price/btc/usd/vwap",
    "BTCEUR_VWAP":      "/oracle/price/btc/eur/vwap",
    "ETHUSD_VWAP":      "/oracle/price/eth/usd/vwap",
    # ── Precious metals ───────────────────────────────────────────────────────
    "XAUUSD":           "/oracle/price/xau/usd",
    "XAUEUR":           "/oracle/price/xau/eur",
    "XAUJPY":           "/oracle/price/xau/jpy",
    # ── FX pairs ──────────────────────────────────────────────────────────────
    "EURUSD":           "/oracle/price/eur/usd",
    "EURJPY":           "/oracle/price/eur/jpy",
    "EURGBP":           "/oracle/price/eur/gbp",
    "EURCHF":           "/oracle/price/eur/chf",
    "EURCNY":           "/oracle/price/eur/cny",
    "EURCAD":           "/oracle/price/eur/cad",
    "GBPUSD":           "/oracle/price/gbp/usd",
    "GBPJPY":           "/oracle/price/gbp/jpy",
    "GBPCHF":           "/oracle/price/gbp/chf",
    "GBPCNY":           "/oracle/price/gbp/cny",
    "GBPCAD":           "/oracle/price/gbp/cad",
    "USDJPY":           "/oracle/price/usd/jpy",
    "USDCHF":           "/oracle/price/usd/chf",
    "USDCNY":           "/oracle/price/usd/cny",
    "USDCAD":           "/oracle/price/usd/cad",
    "CHFJPY":           "/oracle/price/chf/jpy",
    "CHFCAD":           "/oracle/price/chf/cad",
    "CNYJPY":           "/oracle/price/cny/jpy",
    "CNYCAD":           "/oracle/price/cny/cad",
    "CADJPY":           "/oracle/price/cad/jpy",
    # ── US Economic indicators ────────────────────────────────────────────────
    "US_CPI":           "/oracle/econ/us/cpi",
    "US_CPI_CORE":      "/oracle/econ/us/cpi_core",
    "US_UNRATE":        "/oracle/econ/us/unrate",
    "US_NFP":           "/oracle/econ/us/nfp",
    "US_FEDFUNDS":      "/oracle/econ/us/fedfunds",
    "US_GDP":           "/oracle/econ/us/gdp",
    "US_PCE":           "/oracle/econ/us/pce",
    "US_YIELD_CURVE":   "/oracle/econ/us/yield_curve",
    # ── EU Economic indicators ────────────────────────────────────────────────
    "EU_HICP":          "/oracle/econ/eu/hicp",
    "EU_HICP_CORE":     "/oracle/econ/eu/hicp_core",
    "EU_HICP_SERVICES": "/oracle/econ/eu/hicp_services",
    "EU_UNRATE":        "/oracle/econ/eu/unrate",
    "EU_GDP":           "/oracle/econ/eu/gdp",
    "EU_EMPLOYMENT":    "/oracle/econ/eu/employment",
    # ── Commodities ───────────────────────────────────────────────────────────
    "WTI":              "/oracle/econ/commodities/wti",
    "BRENT":            "/oracle/econ/commodities/brent",
    "NATGAS":           "/oracle/econ/commodities/natgas",
    "COPPER":           "/oracle/econ/commodities/copper",
    "DXY":              "/oracle/econ/commodities/dxy",
}

# ── Market index endpoints ────────────────────────────────────────────────────
INDEX_ENDPOINTS = {
    "MSVI_BTCUSD": "/oracle/volatility/btc/usd",
    "MSVI_ETHUSD": "/oracle/volatility/eth/usd",
    "MSXI_BTCUSD": "/oracle/sentiment/btc/usd",
    "MSXI_ETHUSD": "/oracle/sentiment/eth/usd",
    "MSSI_MARKET": "/oracle/stress/market",
}

INDEX_PREVIEW_ENDPOINTS = {
    "MSVI_BTCUSD": "/oracle/volatility/btc/usd/preview",
    "MSVI_ETHUSD": "/oracle/volatility/eth/usd/preview",
    "MSXI_BTCUSD": "/oracle/sentiment/btc/usd/preview",
    "MSXI_ETHUSD": "/oracle/sentiment/eth/usd/preview",
    "MSSI_MARKET": "/oracle/stress/market/preview",
}

# Pricing tiers — econ/commodities are $0.10, everything else is $0.01
ECON_COMMODITIES_PAIRS = {
    "US_CPI", "US_CPI_CORE", "US_UNRATE", "US_NFP", "US_FEDFUNDS",
    "US_GDP", "US_PCE", "US_YIELD_CURVE",
    "EU_HICP", "EU_HICP_CORE", "EU_HICP_SERVICES", "EU_UNRATE", "EU_GDP", "EU_EMPLOYMENT",
    "WTI", "BRENT", "NATGAS", "COPPER", "DXY",
}

VWAP_PAIRS = {"BTCUSD_VWAP", "BTCEUR_VWAP"}

# Human-readable descriptions for each pair
PAIR_DESCRIPTIONS = {
    # Crypto spot
    "BTCUSD":           "Bitcoin / US Dollar spot price (median of 9 sources)",
    "BTCEUR":           "Bitcoin / Euro spot price (cross-rate + direct feeds)",
    "BTCJPY":           "Bitcoin / Japanese Yen spot price",
    "ETHUSD":           "Ethereum / US Dollar spot price (median of 5 sources)",
    "ETHEUR":           "Ethereum / Euro spot price (hybrid: direct EUR + cross-rate)",
    "ETHJPY":           "Ethereum / Japanese Yen spot price",
    "SOLUSD":           "Solana / US Dollar spot price (median of 9 sources)",
    "SOLEUR":           "Solana / Euro spot price (hybrid: direct EUR + cross-rate)",
    "SOLJPY":           "Solana / Japanese Yen spot price",
    "XRPUSD":           "XRP / US Dollar spot price",
    "ADAUSD":           "Cardano / US Dollar spot price",
    "DOGEUSD":          "Dogecoin / US Dollar spot price",
    # Crypto VWAP
    "BTCUSD_VWAP":      "Bitcoin / US Dollar 5-minute volume-weighted average price",
    "BTCEUR_VWAP":      "Bitcoin / Euro 5-minute volume-weighted average price",
    # Precious metals
    "XAUUSD":           "Gold (XAU) / US Dollar spot price (median of 8 sources)",
    "XAUEUR":           "Gold (XAU) / Euro spot price (cross-rate: XAUUSD / EURUSD)",
    "XAUJPY":           "Gold (XAU) / Japanese Yen spot price",
    # FX
    "EURUSD":           "Euro / US Dollar (median of 8 sources incl. central banks)",
    "EURJPY":           "Euro / Japanese Yen",
    "EURGBP":           "Euro / British Pound",
    "EURCHF":           "Euro / Swiss Franc",
    "EURCNY":           "Euro / Chinese Yuan",
    "EURCAD":           "Euro / Canadian Dollar",
    "GBPUSD":           "British Pound / US Dollar",
    "GBPJPY":           "British Pound / Japanese Yen",
    "GBPCHF":           "British Pound / Swiss Franc",
    "GBPCNY":           "British Pound / Chinese Yuan",
    "GBPCAD":           "British Pound / Canadian Dollar",
    "USDJPY":           "US Dollar / Japanese Yen",
    "USDCHF":           "US Dollar / Swiss Franc",
    "USDCNY":           "US Dollar / Chinese Yuan",
    "USDCAD":           "US Dollar / Canadian Dollar",
    "CHFJPY":           "Swiss Franc / Japanese Yen",
    "CHFCAD":           "Swiss Franc / Canadian Dollar",
    "CNYJPY":           "Chinese Yuan / Japanese Yen",
    "CNYCAD":           "Chinese Yuan / Canadian Dollar",
    "CADJPY":           "Canadian Dollar / Japanese Yen",
    # US Economic
    "US_CPI":           "US Consumer Price Index (BLS)",
    "US_CPI_CORE":      "US CPI Core (ex food & energy)",
    "US_UNRATE":        "US Unemployment Rate (BLS)",
    "US_NFP":           "US Nonfarm Payrolls (BLS)",
    "US_FEDFUNDS":      "US Federal Funds Rate (FRED)",
    "US_GDP":           "US GDP (FRED/BEA)",
    "US_PCE":           "US PCE Price Index (FRED)",
    "US_YIELD_CURVE":   "US Yield Curve — 10Y minus 2Y spread (FRED)",
    # EU Economic
    "EU_HICP":          "EU HICP Inflation (Eurostat)",
    "EU_HICP_CORE":     "EU HICP Core Inflation",
    "EU_HICP_SERVICES": "EU HICP Services Inflation",
    "EU_UNRATE":        "EU Unemployment Rate (Eurostat)",
    "EU_GDP":           "EU GDP (Eurostat)",
    "EU_EMPLOYMENT":    "EU Employment (Eurostat)",
    # Commodities
    "WTI":              "WTI Crude Oil price (EIA/FRED)",
    "BRENT":            "Brent Crude Oil price",
    "NATGAS":           "Henry Hub Natural Gas price (EIA/FRED)",
    "COPPER":           "Copper price (FRED)",
    "DXY":              "US Dollar Index (DXY)",
}


def get_wallet_key() -> str | None:
    """Return the wallet private key from environment, or None if not set."""
    return os.environ.get("MYCELIA_WALLET_PRIVATE_KEY")


def is_paid_mode() -> bool:
    """Return True if a wallet key is configured (paid mode), False otherwise."""
    return get_wallet_key() is not None


def get_price_usd(pair: str) -> str:
    """Return the USD cost string for a given pair."""
    pair = pair.upper().replace("/", "").replace("-", "_")
    if pair in ECON_COMMODITIES_PAIRS:
        return "$0.10"
    if pair in VWAP_PAIRS:
        return "$0.02"
    return "$0.01"


def get_endpoint(pair: str) -> str:
    """Return the full API URL for a given pair."""
    pair = pair.upper().replace("/", "").replace("-", "_")
    if pair not in SUPPORTED_PAIRS:
        raise ValueError(
            f"Unsupported pair: '{pair}'. "
            f"Supported pairs: {', '.join(SUPPORTED_PAIRS.keys())}"
        )
    path = SUPPORTED_PAIRS[pair]
    if not is_paid_mode():
        path = path + "/preview"
    return API_BASE_URL + path
