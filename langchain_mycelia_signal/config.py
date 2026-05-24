"""
Configuration for langchain-mycelia-signal.
Free mode:   No env var needed. Hits preview endpoints. Returns unsigned data.
Paid mode:   Set MYCELIA_WALLET_PRIVATE_KEY to a funded Base wallet private key.
             Tool pays automatically via x402 (USDC on Base).
             Returns fully cryptographically signed attestation.
"""
import os

API_BASE_URL = "https://api.myceliasignal.com"

# ── Price / FX / Macro / Commodity pairs ──────────────────────────────────────

SUPPORTED_PAIRS = {
    # Crypto spot
    "BTCUSD": "/oracle/price/btc/usd",
    "BTCEUR": "/oracle/price/btc/eur",
    "BTCJPY": "/oracle/price/btc/jpy",
    "ETHUSD": "/oracle/price/eth/usd",
    "ETHEUR": "/oracle/price/eth/eur",
    "ETHJPY": "/oracle/price/eth/jpy",
    "SOLUSD": "/oracle/price/sol/usd",
    "SOLEUR": "/oracle/price/sol/eur",
    "SOLJPY": "/oracle/price/sol/jpy",
    "XRPUSD": "/oracle/price/xrp/usd",
    "ADAUSD": "/oracle/price/ada/usd",
    "DOGEUSD": "/oracle/price/doge/usd",
    # Stablecoins
    "USDTUSD": "/oracle/price/usdt/usd",
    "USDCUSD": "/oracle/price/usdc/usd",
    # Crypto VWAP
    "BTCUSD_VWAP": "/oracle/price/btc/usd/vwap",
    "BTCEUR_VWAP": "/oracle/price/btc/eur/vwap",
    # Precious metals
    "XAUUSD": "/oracle/price/xau/usd",
    "XAUEUR": "/oracle/price/xau/eur",
    "XAUJPY": "/oracle/price/xau/jpy",
    # FX pairs
    "EURUSD": "/oracle/price/eur/usd",
    "EURJPY": "/oracle/price/eur/jpy",
    "EURGBP": "/oracle/price/eur/gbp",
    "EURCHF": "/oracle/price/eur/chf",
    "EURCNY": "/oracle/price/eur/cny",
    "EURCAD": "/oracle/price/eur/cad",
    "GBPUSD": "/oracle/price/gbp/usd",
    "GBPJPY": "/oracle/price/gbp/jpy",
    "GBPCHF": "/oracle/price/gbp/chf",
    "GBPCNY": "/oracle/price/gbp/cny",
    "GBPCAD": "/oracle/price/gbp/cad",
    "USDJPY": "/oracle/price/usd/jpy",
    "USDCHF": "/oracle/price/usd/chf",
    "USDCNY": "/oracle/price/usd/cny",
    "USDCAD": "/oracle/price/usd/cad",
    "CHFJPY": "/oracle/price/chf/jpy",
    "CHFCAD": "/oracle/price/chf/cad",
    "CNYJPY": "/oracle/price/cny/jpy",
    "CNYCAD": "/oracle/price/cny/cad",
    "CADJPY": "/oracle/price/cad/jpy",
    # US Economic indicators ($0.10 each)
    "US_CPI": "/oracle/econ/us/cpi",
    "US_CPI_CORE": "/oracle/econ/us/cpi_core",
    "US_UNRATE": "/oracle/econ/us/unrate",
    "US_NFP": "/oracle/econ/us/nfp",
    "US_FEDFUNDS": "/oracle/econ/us/fedfunds",
    "US_GDP": "/oracle/econ/us/gdp",
    "US_PCE": "/oracle/econ/us/pce",
    "US_YIELD_CURVE": "/oracle/econ/us/yield_curve",
    # EU Economic indicators ($0.10 each)
    "EU_HICP": "/oracle/econ/eu/hicp",
    "EU_HICP_CORE": "/oracle/econ/eu/hicp_core",
    "EU_HICP_SERVICES": "/oracle/econ/eu/hicp_services",
    "EU_UNRATE": "/oracle/econ/eu/unrate",
    "EU_GDP": "/oracle/econ/eu/gdp",
    "EU_EMPLOYMENT": "/oracle/econ/eu/employment",
    # Commodities ($0.10 each)
    "WTI": "/oracle/econ/commodities/wti",
    "BRENT": "/oracle/econ/commodities/brent",
    "NATGAS": "/oracle/econ/commodities/natgas",
    "COPPER": "/oracle/econ/commodities/copper",
    "DXY": "/oracle/econ/commodities/dxy",
}

# ── Indices ───────────────────────────────────────────────────────────────────

INDICES = {
    "MSVI_BTC": "/oracle/volatility/btc/usd",
    "MSVI_ETH": "/oracle/volatility/eth/usd",
    "MSXI_BTC": "/oracle/sentiment/btc/usd",
    "MSXI_ETH": "/oracle/sentiment/eth/usd",
    "MSSI": "/oracle/stress/market",
    "MSTI": "/oracle/contagion/market",
}

# ── Derivatives data ──────────────────────────────────────────────────────────

DERIVATIVES = {
    # Funding rates ($0.05)
    "FUNDING_BTC": "/oracle/funding/btc/usd",
    "FUNDING_ETH": "/oracle/funding/eth/usd",
    "FUNDING_SOL": "/oracle/funding/sol/usd",
    # Open interest ($0.01)
    "OI_BTC": "/oracle/oi/btc/usd",
    "OI_ETH": "/oracle/oi/eth/usd",
    "OI_SOL": "/oracle/oi/sol/usd",
    # Basis/carry ($0.02)
    "BASIS_BTC": "/oracle/basis/btc/usd",
    "BASIS_ETH": "/oracle/basis/eth/usd",
    "BASIS_SOL": "/oracle/basis/sol/usd",
    # Liquidations (preview only currently)
    "LIQUIDATIONS_BTC": "/oracle/liquidations/btc/usd",
    "LIQUIDATIONS_ETH": "/oracle/liquidations/eth/usd",
    "LIQUIDATIONS_SOL": "/oracle/liquidations/sol/usd",
    # Orderbook (preview only currently)
    "ORDERBOOK_BTC": "/oracle/orderbook/btc/usd",
    "ORDERBOOK_ETH": "/oracle/orderbook/eth/usd",
    # IV surface (preview only currently)
    "IV_BTC": "/oracle/iv/btc/usd",
    "IV_ETH": "/oracle/iv/eth/usd",
}

# ── Gas oracle ────────────────────────────────────────────────────────────────

GAS_CHAINS = {
    "ETHEREUM": "/oracle/gas/ethereum",
    "BASE": "/oracle/gas/base",
    "ARBITRUM": "/oracle/gas/arbitrum",
    "POLYGON": "/oracle/gas/polygon",
    "OPTIMISM": "/oracle/gas/optimism",
    "SOLANA": "/oracle/gas/solana",
    "INDEX": "/oracle/gas/index",
}

# ── DeFi Yield Oracle ─────────────────────────────────────────────────────────

DEFI_YIELD_ENDPOINTS = {
    "ALL": "/oracle/defi/yield/all",
    "COMPARE": "/oracle/defi/yield/compare",
    "BEST_USDC": "/oracle/defi/yield/best/usdc",
    "BEST_USDT": "/oracle/defi/yield/best/usdt",
    "BEST_WETH": "/oracle/defi/yield/best/weth",
    "BEST_DAI": "/oracle/defi/yield/best/dai",
    "BEST_WBTC": "/oracle/defi/yield/best/wbtc",
    "CATALOGUE": "/oracle/defi/yield/catalogue",
}

# ── Pricing tiers ─────────────────────────────────────────────────────────────

ECON_COMMODITIES_PAIRS = {
    "US_CPI", "US_CPI_CORE", "US_UNRATE", "US_NFP", "US_FEDFUNDS",
    "US_GDP", "US_PCE", "US_YIELD_CURVE",
    "EU_HICP", "EU_HICP_CORE", "EU_HICP_SERVICES", "EU_UNRATE", "EU_GDP", "EU_EMPLOYMENT",
    "WTI", "BRENT", "NATGAS", "COPPER", "DXY",
}
VWAP_PAIRS = {"BTCUSD_VWAP", "BTCEUR_VWAP"}
INDEX_KEYS = set(INDICES.keys())
FUNDING_KEYS = {"FUNDING_BTC", "FUNDING_ETH", "FUNDING_SOL"}
OI_KEYS = {"OI_BTC", "OI_ETH", "OI_SOL"}
BASIS_KEYS = {"BASIS_BTC", "BASIS_ETH", "BASIS_SOL"}


def get_wallet_key() -> str | None:
    return os.environ.get("MYCELIA_WALLET_PRIVATE_KEY")


def is_paid_mode() -> bool:
    return get_wallet_key() is not None


def get_price_usd(key: str) -> str:
    key = key.upper().replace("/", "").replace("-", "_")
    if key in ECON_COMMODITIES_PAIRS:
        return "$0.10"
    if key in VWAP_PAIRS:
        return "$0.02"
    if key in INDEX_KEYS or key in FUNDING_KEYS:
        return "$0.05"
    if key in BASIS_KEYS:
        return "$0.02"
    if key in OI_KEYS:
        return "$0.01"
    if key == "COT_BTC":
        return "$1.00"
    return "$0.01"


def get_endpoint(pair: str) -> str:
    pair = pair.upper().replace("/", "").replace("-", "_")
    if pair not in SUPPORTED_PAIRS:
        raise ValueError(
            f"Unsupported pair: '{pair}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_PAIRS.keys()))}"
        )
    path = SUPPORTED_PAIRS[pair]
    if not is_paid_mode():
        path = path + "/preview"
    return API_BASE_URL + path


def get_generic_endpoint(endpoint_map: dict, key: str) -> str:
    key = key.upper().replace("/", "").replace("-", "_")
    if key not in endpoint_map:
        raise ValueError(
            f"Unsupported key: '{key}'. "
            f"Supported: {', '.join(sorted(endpoint_map.keys()))}"
        )
    path = endpoint_map[key]
    if not is_paid_mode():
        path = path + "/preview"
    return API_BASE_URL + path
