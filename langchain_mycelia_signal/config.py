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
    "USDTEUR": "/oracle/price/usdt/eur",
    "USDTJPY": "/oracle/price/usdt/jpy",
    # Crypto VWAP
    "BTCUSD_VWAP": "/oracle/price/btc/usd/vwap",
    "BTCEUR_VWAP": "/oracle/price/btc/eur/vwap",
    "ETHUSD_VWAP": "/oracle/price/eth/usd/vwap",
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
    # Liquidation snapshot ($0.03) — distinct from liq-flow ($0.05)
    "LIQUIDATIONS_BTC": "/oracle/liquidations/btc/usd",
    "LIQUIDATIONS_ETH": "/oracle/liquidations/eth/usd",
    "LIQUIDATIONS_SOL": "/oracle/liquidations/sol/usd",
    # Order book imbalance ($0.03)
    "ORDERBOOK_BTC": "/oracle/orderbook/btc/usd",
    "ORDERBOOK_ETH": "/oracle/orderbook/eth/usd",
    # IV surface — single exchange Deribit ATM ($0.03)
    "IV_BTC": "/oracle/iv/btc/usd",
    "IV_ETH": "/oracle/iv/eth/usd",
    # Multi-exchange IV surface — 3 exchanges, cross-exchange divergence ($0.05)
    "IV_SURFACE_BTC": "/oracle/iv-surface/btc/usd",
    "IV_SURFACE_ETH": "/oracle/iv-surface/eth/usd",
    "IV_SURFACE_SOL": "/oracle/iv-surface/sol/usd",
    # SVI volatility surface — Gatheral arbitrage-free parameterization ($0.05)
    "SVI_BTC": "/oracle/svi/btc/usd",
    "SVI_ETH": "/oracle/svi/eth/usd",
    "SVI_SOL": "/oracle/svi/sol/usd",
    # Multi-exchange options Greeks ($0.05)
    "GREEKS_BTC": "/oracle/greeks/btc/usd",
    "GREEKS_ETH": "/oracle/greeks/eth/usd",
    "GREEKS_SOL": "/oracle/greeks/sol/usd",
    # Futures term structure ($0.05)
    "TERM_STRUCTURE_BTC": "/oracle/term-structure/btc/usd",
    "TERM_STRUCTURE_ETH": "/oracle/term-structure/eth/usd",
    "TERM_STRUCTURE_SOL": "/oracle/term-structure/sol/usd",
    # Options instrument discovery ($0.03)
    "INSTRUMENTS_BTC": "/oracle/instruments/btc/options",
    "INSTRUMENTS_ETH": "/oracle/instruments/eth/options",
    "INSTRUMENTS_SOL": "/oracle/instruments/sol/options",
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
VWAP_PAIRS = {"BTCUSD_VWAP", "BTCEUR_VWAP", "ETHUSD_VWAP"}
INDEX_KEYS = set(INDICES.keys())
FUNDING_KEYS = {"FUNDING_BTC", "FUNDING_ETH", "FUNDING_SOL"}
OI_KEYS = {"OI_BTC", "OI_ETH", "OI_SOL"}
BASIS_KEYS = {"BASIS_BTC", "BASIS_ETH", "BASIS_SOL"}
LIQUIDATION_KEYS = {"LIQUIDATIONS_BTC", "LIQUIDATIONS_ETH", "LIQUIDATIONS_SOL"}
ORDERBOOK_KEYS = {"ORDERBOOK_BTC", "ORDERBOOK_ETH"}
IV_KEYS = {"IV_BTC", "IV_ETH"}
INSTRUMENTS_KEYS = {"INSTRUMENTS_BTC", "INSTRUMENTS_ETH", "INSTRUMENTS_SOL"}
FIVE_CENT_DERIV_KEYS = {
    "IV_SURFACE_BTC", "IV_SURFACE_ETH", "IV_SURFACE_SOL",
    "SVI_BTC", "SVI_ETH", "SVI_SOL",
    "GREEKS_BTC", "GREEKS_ETH", "GREEKS_SOL",
    "TERM_STRUCTURE_BTC", "TERM_STRUCTURE_ETH", "TERM_STRUCTURE_SOL",
}


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
    if key in FIVE_CENT_DERIV_KEYS:
        return "$0.05"
    if key in BASIS_KEYS:
        return "$0.02"
    if key in OI_KEYS:
        return "$0.01"
    if key in LIQUIDATION_KEYS or key in ORDERBOOK_KEYS or key in IV_KEYS or key in INSTRUMENTS_KEYS:
        return "$0.03"
    if key == "COT_BTC":
        return "$1.00"
    # Regime / intel pricing
    if key in {"EQUITY", "LIQUIDITY"}:
        return "$0.10"
    if key in {"MESI", "MNVI", "MSLI", "MSBI"}:
        return "$0.05"
    if key == "EQUITY_REGIME":
        return "$0.10"
    if key in {"DIVERGENCE", "CONSENSUS", "REGIME_CHANGE"}:
        return "$0.50"
    if key == "PERSISTENCE":
        return "$0.15"
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

# ── GPU Compute Oracle ────────────────────────────────────────────────────────

COMPUTE_ENDPOINTS = {
    "ALL": "/oracle/compute/all",
    "COMPARE": "/oracle/compute/compare",
    "BEST_H100_SXM": "/oracle/compute/best/h100_sxm",
    "BEST_A100_SXM": "/oracle/compute/best/a100_sxm",
    "BEST_H200": "/oracle/compute/best/h200",
    "BEST_RTX_4090": "/oracle/compute/best/rtx_4090",
    "BEST_L40S": "/oracle/compute/best/l40s",
    "BEST_MI300X": "/oracle/compute/best/mi300x",
    "BEST_V100": "/oracle/compute/best/v100",
    "BEST_T4": "/oracle/compute/best/t4",
    "CATALOGUE": "/oracle/compute/catalogue",
}

# ── Inference Pricing Oracle (NEW S89) ───────────────────────────────────────

INFERENCE_ENDPOINTS = {
    "OPENAI":    "/oracle/inference/openai/pricing",
    "ANTHROPIC": "/oracle/inference/anthropic/pricing",
    "GROQ":      "/oracle/inference/groq/pricing",
    "TOGETHER":  "/oracle/inference/together/pricing",
    "FIREWORKS": "/oracle/inference/fireworks/pricing",
    "CEREBRAS":  "/oracle/inference/cerebras/pricing",
    "ALL":       "/oracle/inference/all",
    "COMPARE":   "/oracle/inference/compare",
    "TASK_CHAT":         "/oracle/inference/compare/task/chat",
    "TASK_CODE":         "/oracle/inference/compare/task/code",
    "TASK_REASONING":    "/oracle/inference/compare/task/reasoning",
    "TASK_LONG_CONTEXT": "/oracle/inference/compare/task/long_context",
    "TASK_FAST":         "/oracle/inference/compare/task/fast",
}

# ── Econ Calendar Oracle (NEW S89) ───────────────────────────────────────────

ECON_CALENDAR_ENDPOINTS = {
    "CALENDAR":         "/oracle/econ/calendar",
    "TODAY":            "/oracle/econ/calendar/today",
    "FOMC":             "/oracle/econ/calendar/fomc",
    "COUNTRY_US":       "/oracle/econ/calendar/country/us",
    "COUNTRY_EU":       "/oracle/econ/calendar/country/eu",
    "COUNTRY_GB":       "/oracle/econ/calendar/country/gb",
    "COUNTRY_JP":       "/oracle/econ/calendar/country/jp",
    "SURPRISES":        "/oracle/econ/surprises",
    "EXPIRY_BTC":       "/oracle/econ/expiry/btc",
    "EXPIRY_ETH":       "/oracle/econ/expiry/eth",
}

# ── DeFi Metrics Oracle (NEW S89) ────────────────────────────────────────────

DEFI_METRICS_ENDPOINTS = {
    "ALL":      "/oracle/defi/metrics",
    "AAVE":     "/oracle/defi/metrics/aave",
    "COMPOUND": "/oracle/defi/metrics/compound",
    "MORPHO":   "/oracle/defi/metrics/morpho",
    "SPARK":    "/oracle/defi/metrics/spark",
    "SKY":      "/oracle/defi/metrics/sky",
}

# ── Liquidation Flow Oracle (NEW S89) ────────────────────────────────────────

LIQ_FLOW_ENDPOINTS = {
    "BTC": "/oracle/liq-flow/btc",
    "ETH": "/oracle/liq-flow/eth",
    "SOL": "/oracle/liq-flow/sol",
}

# ── Signed Historical Data Oracle (NEW S89) ──────────────────────────────────

HISTORY_ENDPOINTS = {
    "SPOT_BTC_USD":   "/oracle/history/spot/btc/usd",
    "SPOT_ETH_USD":   "/oracle/history/spot/eth/usd",
    "SPOT_SOL_USD":   "/oracle/history/spot/sol/usd",
    "FUNDING_BTC":    "/oracle/history/funding/btc/usd",
    "FUNDING_ETH":    "/oracle/history/funding/eth/usd",
    "MSXI_BTCUSD":    "/oracle/history/index/msxi/btcusd",
    "MSXI_ETHUSD":    "/oracle/history/index/msxi/ethusd",
    "MSVI_BTCUSD":    "/oracle/history/index/msvi/btcusd",
    "MSVI_ETHUSD":    "/oracle/history/index/msvi/ethusd",
    "MSSI":           "/oracle/history/index/mssi",
    "MSTI":           "/oracle/history/index/msti",
}

# ── Layer 2 — Oracle Information ─────────────────────────────────────────────

SYNOPSIS_ENDPOINTS = {
    "MARKET": "/oracle/synopsis/market",
}

PERP_REGIME_ENDPOINTS = {
    "BTC": "/oracle/perp/btc",
    "ETH": "/oracle/perp/eth",
    "SOL": "/oracle/perp/sol",
}

TRADFI_REGIME_ENDPOINTS = {
    "EQUITY": "/oracle/regime/equity",        # RISK_ON / NEUTRAL / STRESS / PANIC. $0.10
    "LIQUIDITY": "/oracle/regime/liquidity",  # DEEP / NORMAL / THIN / FRAGILE. $0.10
}

# ── Equity/TradFi Indices ─────────────────────────────────────────────────────

EQUITY_INDICES = {
    "MESI": "/oracle/stress/equity",       # Equity Stress Index — VIX/credit/yield curve/DXY. $0.05
    "MNVI": "/oracle/volatility/nq/usd",   # NQ Volatility Index — RV/IV/TS/SK/PCR. $0.05
    "MSLI": "/oracle/leadership/equity",   # Leadership Index — ETF ratios (IVW/IVE, XLK/SPY, IWM/SPY, sectors). $0.05
    "MSBI": "/oracle/breadth/equity",      # Breadth Index — sector 20DMA participation, RSP/SPY momentum. $0.05
}

EQUITY_REGIME_ENDPOINT = "/oracle/regime/equity/composite"  # MSERC — $0.10
MSRI_ENDPOINT = "/oracle/rotation/equity"  # MSRI — $0.10

# ── Layer 3 — Oracle Intelligence ────────────────────────────────────────────

ORACLE_INTEL_ENDPOINTS = {
    "MACRO_RISK":        "/oracle/intel/macro/risk",
    "PERP_SETUP":        "/oracle/intel/perp/setup",
    "DEFI_OPPORTUNITY":  "/oracle/intel/defi/opportunity",
    "REGIME_CHANGE":     "/oracle/intel/regime/change",      # $0.50 — perp transition vs 2h ago
    "DIVERGENCE":        "/oracle/intel/divergence",          # $0.50 — cross-asset divergence NONE→EXTREME
    "CONSENSUS":         "/oracle/intel/consensus",           # $0.50 — weighted regime vote STRONG→CONFLICTED
    "PERSISTENCE":       "/oracle/intel/regime/persistence",  # $0.15 — duration/percentile/remaining. ?currency=BTC|ETH|SOL
}
