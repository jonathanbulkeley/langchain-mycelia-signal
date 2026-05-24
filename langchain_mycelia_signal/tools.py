"""
LangChain tools for Mycelia Signal oracle data.

Usage:
    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()
"""

from langchain_core.tools import tool

from .client import fetch_dlc_free, fetch_json, fetch_price, post_dlc_with_payment, _format_json
from .config import (
    API_BASE_URL, DERIVATIVES, GAS_CHAINS, INDICES, SUPPORTED_PAIRS,
    DEFI_YIELD_ENDPOINTS, COMPUTE_ENDPOINTS, get_generic_endpoint, is_paid_mode,
)


# ── PRICE / FX / MACRO / COMMODITIES ─────────────────────────────────────────

@tool
def get_mycelia_price(pair: str) -> str:
    """
    Get a real-time price attestation from Mycelia Signal oracle.

    Returns cryptographically signed price data for the requested pair.

    CRYPTO SPOT ($0.01): BTCUSD, BTCEUR, BTCJPY, ETHUSD, ETHEUR, ETHJPY,
        SOLUSD, SOLEUR, SOLJPY, XRPUSD, ADAUSD, DOGEUSD, USDTUSD, USDCUSD
    CRYPTO VWAP ($0.02): BTCUSD_VWAP, BTCEUR_VWAP
    PRECIOUS METALS ($0.01): XAUUSD, XAUEUR, XAUJPY
    FX ($0.01): EURUSD, EURJPY, EURGBP, EURCHF, EURCNY, EURCAD,
        GBPUSD, GBPJPY, GBPCHF, GBPCNY, GBPCAD, USDJPY, USDCHF, USDCNY,
        USDCAD, CHFJPY, CHFCAD, CNYJPY, CNYCAD, CADJPY
    US ECONOMIC ($0.10): US_CPI, US_CPI_CORE, US_UNRATE, US_NFP,
        US_FEDFUNDS, US_GDP, US_PCE, US_YIELD_CURVE
    EU ECONOMIC ($0.10): EU_HICP, EU_HICP_CORE, EU_HICP_SERVICES,
        EU_UNRATE, EU_GDP, EU_EMPLOYMENT
    COMMODITIES ($0.10): WTI, BRENT, NATGAS, COPPER, DXY

    Args:
        pair: Trading pair or indicator. Uppercase, no slash.
              e.g. 'BTCUSD', 'EURUSD', 'US_CPI', 'WTI'.
    """
    return fetch_price(pair)


# ── INDICES ───────────────────────────────────────────────────────────────────

@tool
def get_mycelia_index(index: str) -> str:
    """
    Get a Mycelia Signal market index reading.

    Four proprietary indices computed from cross-exchange derivatives data:

    MSVI_BTC — Bitcoin Volatility Index (RV/IV ratio, options flow, term structure)
    MSVI_ETH — Ethereum Volatility Index
    MSXI_BTC — Bitcoin Sentiment Index (funding rates, skew, PCR, basis). -100 to +100.
    MSXI_ETH — Ethereum Sentiment Index
    MSSI — Market Stress Index (vol acceleration, stablecoin peg, funding extremes, dispersion). 0-100.
    MSTI — Crypto-TradFi Contagion Index (BTC-equity correlation, equity vol, DXY). 0-100.

    Each returns: value, regime (e.g. CALM/ELEVATED/HIGH/EXTREME), confidence,
    component breakdown, and (in paid mode) cryptographic signature.
    $0.05 per query.

    Args:
        index: Index name. One of: MSVI_BTC, MSVI_ETH, MSXI_BTC, MSXI_ETH, MSSI, MSTI.
    """
    url = get_generic_endpoint(INDICES, index)
    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    lines = [f"{index.upper()} Index"]
    lines.append(f"Value:      {data.get('value', '?')}")
    lines.append(f"Regime:     {data.get('regime', '?')}")
    lines.append(f"Confidence: {data.get('confidence', '?')}")
    if data.get("components"):
        lines.append("Components:")
        for k, v in data["components"].items():
            if isinstance(v, dict):
                lines.append(f"  {k}: {v.get('value', '?')} (weight {v.get('weight', '?')})")
            else:
                lines.append(f"  {k}: {v}")
    lines.append(f"Signed:     {data.get('signed', False)}")
    return "\n".join(lines)


# ── DERIVATIVES DATA ──────────────────────────────────────────────────────────

@tool
def get_mycelia_funding(currency: str) -> str:
    """
    Get cross-exchange perpetual funding rate data from Mycelia Signal.

    Aggregates funding rates from 11 exchanges (Binance, Bybit, OKX, Deribit,
    Hyperliquid, dYdX, Bitget, Kraken, Bitstamp, Coinbase, Crypto.com).
    Returns composite rate, predicted next settlement, per-exchange breakdown,
    regime, and cross-exchange divergence. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL.
    """
    key = f"FUNDING_{currency.upper()}"
    url = get_generic_endpoint(DERIVATIVES, key)
    data = fetch_json(url)
    return _format_json(data, f"Funding Rate — {currency.upper()}/USD")


@tool
def get_mycelia_oi(currency: str) -> str:
    """
    Get cross-exchange open interest data from Mycelia Signal.

    Per-exchange OI breakdown with 1h/4h/24h deltas. $0.01 per query.

    Args:
        currency: One of BTC, ETH, SOL.
    """
    key = f"OI_{currency.upper()}"
    url = get_generic_endpoint(DERIVATIVES, key)
    data = fetch_json(url)
    return _format_json(data, f"Open Interest — {currency.upper()}/USD")


@tool
def get_mycelia_basis(currency: str) -> str:
    """
    Get cross-exchange basis/carry data from Mycelia Signal.

    Per-exchange basis (mark vs index), annualized carry, regime
    (CONTANGO/BACKWARDATION/FLAT). Identifies best carry trade venues. $0.02 per query.

    Args:
        currency: One of BTC, ETH, SOL.
    """
    key = f"BASIS_{currency.upper()}"
    url = get_generic_endpoint(DERIVATIVES, key)
    data = fetch_json(url)
    return _format_json(data, f"Basis/Carry — {currency.upper()}/USD")


# ── WEATHER ORACLE ────────────────────────────────────────────────────────────

@tool
def get_mycelia_weather(lat: float, lon: float, metric: str, window: str) -> str:
    """
    Get weather data from Mycelia Signal oracle (ERA5 reanalysis, 0.25° global).

    Used for parametric insurance triggers. $0.10 per query.

    Args:
        lat: Latitude (-90 to 90).
        lon: Longitude (-180 to 180).
        metric: One of 'wrsi' (crop water stress), 'rainfall', 'temperature', 'wind'.
        window: Time window. WRSI: '30d','60d','90d'. Rainfall: '7d','14d','30d','60d','90d'.
                Temperature: '7d','14d','30d','60d','90d'. Wind: '7d','14d','30d'.
    """
    path = f"/oracle/weather/{lat}/{lon}/{metric}/{window}"
    if not is_paid_mode():
        path += "/preview"
    url = API_BASE_URL + path
    data = fetch_json(url)
    return _format_json(data, f"Weather — {metric} at ({lat}, {lon}) over {window}")


# ── MARINE ORACLE ─────────────────────────────────────────────────────────────

@tool
def get_mycelia_marine_seastate(lat: float, lon: float) -> str:
    """
    Get sea state data at any ocean coordinate from Mycelia Signal.

    Returns significant wave height, swell, wind waves. $0.10 per query.

    Args:
        lat: Latitude (-90 to 90).
        lon: Longitude (-180 to 180).
    """
    path = f"/oracle/marine/{lat}/{lon}/seastate"
    if not is_paid_mode():
        path += "/preview"
    url = API_BASE_URL + path
    data = fetch_json(url)
    return _format_json(data, f"Sea State at ({lat}, {lon})")


# ── GAS ORACLE ────────────────────────────────────────────────────────────────

@tool
def get_mycelia_gas(chain: str) -> str:
    """
    Get real-time gas prices for EVM and non-EVM chains from Mycelia Signal.

    Single chain: $0.01. Cross-chain index: $0.05.

    Args:
        chain: One of ETHEREUM, BASE, ARBITRUM, POLYGON, OPTIMISM, SOLANA, INDEX.
               INDEX returns cross-chain comparison sorted cheapest-first.
    """
    key = chain.upper()
    url = get_generic_endpoint(GAS_CHAINS, key)
    data = fetch_json(url)
    return _format_json(data, f"Gas — {chain.upper()}")


# ── DEFI YIELD ORACLE ─────────────────────────────────────────────────────────

@tool
def get_mycelia_defi_yield(query: str) -> str:
    """
    Get on-chain DeFi lending rates from Mycelia Signal.

    Reads directly from smart contracts on 7 chains. Covers Aave V3, Spark,
    Compound V3, Venus, Benqi, Moonwell. Returns supply APR, borrow APR,
    and protocol/chain breakdown. $0.05 per query.

    Args:
        query: One of:
            'all' — all 40 rates across all protocols and chains
            'compare' — USDC rates ranked across all protocols
            'best_usdc' — best USDC supply yield
            'best_usdt' — best USDT supply yield
            'best_weth' — best WETH supply yield
            'best_dai' — best DAI supply yield
            'best_wbtc' — best WBTC supply yield
            'catalogue' — list all protocols and chains (free)
    """
    key = query.upper().replace(" ", "_")
    if key not in DEFI_YIELD_ENDPOINTS:
        return f"Unknown query '{query}'. Use: all, compare, best_usdc, best_usdt, best_weth, best_dai, best_wbtc, catalogue"
    path = DEFI_YIELD_ENDPOINTS[key]
    if key != "CATALOGUE" and not is_paid_mode():
        path += "/preview"
    url = API_BASE_URL + path
    data = fetch_json(url)
    return _format_json(data, f"DeFi Yield — {query}")



# ── GPU COMPUTE ORACLE ───────────────────────────────────────────────────────

@tool
def get_mycelia_compute(query: str) -> str:
    """
    Get real-time GPU compute pricing from Mycelia Signal.

    Aggregates pricing from AWS Spot, Vast.ai, RunPod, Akash Network.
    Normalized to $/GPU-hour. 80+ GPU models. $0.05 per query.

    Args:
        query: One of:
            'all' — all 575+ prices across 80+ models
            'compare' — cheapest price per model, ranked
            'best_h100_sxm' — best H100 SXM price
            'best_a100_sxm' — best A100 SXM price
            'best_h200' — best H200 price
            'best_rtx_4090' — best RTX 4090 price
            'best_l40s' — best L40S price
            'best_mi300x' — best MI300X price
            'best_v100' — best V100 price
            'best_t4' — best T4 price
            'catalogue' — list all models and sources (free)
    """
    key = query.upper().replace(" ", "_")
    if key not in COMPUTE_ENDPOINTS:
        return f"Unknown query '{query}'. Use: all, compare, best_h100_sxm, best_a100_sxm, best_h200, best_rtx_4090, best_l40s, catalogue"
    path = COMPUTE_ENDPOINTS[key]
    if key != "CATALOGUE" and not is_paid_mode():
        path += "/preview"
    url = API_BASE_URL + path
    data = fetch_json(url)
    return _format_json(data, f"GPU Compute — {query}")


# ── COT (COMMITMENTS OF TRADERS) ─────────────────────────────────────────────

@tool
def get_mycelia_cot() -> str:
    """
    Get CFTC Commitments of Traders data for Bitcoin CME futures.

    Weekly data: leveraged funds, asset managers, dealers positioning.
    Auto-refreshed Fridays at 19:40 UTC. $1.00 per query.
    """
    path = "/oracle/cot/btc"
    if not is_paid_mode():
        # COT has no preview — always returns 402 in free mode
        return (
            "COT data requires payment ($1.00 USDC). "
            "Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments. "
            "See: https://myceliasignal.com/docs/cot"
        )
    url = API_BASE_URL + path
    data = fetch_json(url)
    return _format_json(data, "CFTC COT — BTC CME Futures")


# ── DLC ORACLE ────────────────────────────────────────────────────────────────

@tool
def dlc_threshold_preview(pair: str, strike: float, direction: str, expiry: int | None = None) -> str:
    """
    Register a FREE DLC threshold contract preview with Mycelia Signal.

    Tests the full DLC flow without payment. Returns event ID and oracle R-points.

    Args:
        pair: Trading pair — e.g. 'BTCUSD', 'ETHUSD'. Uppercase, no slash.
        strike: Price level to monitor (integer). e.g. 90000.
        direction: 'above' or 'below'.
        expiry: Optional Unix timestamp. Defaults to 30 days from now.
    """
    import time as _time
    body = {
        "pair": pair.upper().replace("/", ""),
        "strike": int(strike),
        "direction": direction.lower(),
        "expiry": expiry or int(_time.time()) + 86400 * 30,
    }
    result = post_dlc_with_payment("/dlc/oracle/threshold/preview", body)
    if result.get("error"):
        return f"DLC preview failed: {result.get('message', result['error'])}"
    lines = [
        "DLC Threshold Preview Registered (free)",
        f"Event ID:      {result.get('eventid', '')}",
        f"Pair:          {result.get('pair', '')}",
        f"Strike:        {result.get('strike', '')}",
        f"Direction:     {result.get('direction', '')}",
        f"Expiry:        {result.get('expiry', '')}",
        f"Oracle pubkey: {str(result.get('oraclePubkey', ''))[:16]}...",
    ]
    return "\n".join(lines)


@tool
def dlc_register_threshold(pair: str, strike: float, direction: str, expiry: int | None = None, webhook_url: str | None = None) -> str:
    """
    Register a PRODUCTION DLC threshold contract. $7.00 USDC or 10,000 sats.

    Args:
        pair: Trading pair — e.g. 'BTCUSD'. Uppercase, no slash.
        strike: Price level to monitor (integer).
        direction: 'above' or 'below'.
        expiry: Optional Unix timestamp. Defaults to 30 days.
        webhook_url: Optional URL to receive attestation POST on breach/expiry.
    """
    import time as _time
    body = {
        "pair": pair.upper().replace("/", ""),
        "strike": int(strike),
        "direction": direction.lower(),
        "expiry": expiry or int(_time.time()) + 86400 * 30,
    }
    if webhook_url:
        body["webhookUrl"] = webhook_url
    result = post_dlc_with_payment("/dlc/oracle/threshold", body)
    if result.get("error"):
        return f"DLC registration failed: {result.get('message', result['error'])}"
    lines = [
        "DLC Threshold Contract Registered",
        f"Event ID:      {result.get('eventid', '')}",
        f"Pair:          {result.get('pair', '')}",
        f"Strike:        {result.get('strike', '')}",
        f"Direction:     {result.get('direction', '')}",
        f"Payment rail:  {result.get('rail', '')}",
    ]
    return "\n".join(lines)


@tool
def dlc_register_enum(outcomes: list[str], event_id: str, maturity: int, resolver_kind: str | None = None, resolver_url: str | None = None) -> str:
    """
    Register a DLC disjoint union (enum) contract. $7.00 USDC or 10,000 sats.

    Spec-compliant TLV format. Oracle attests to one of N discrete outcomes at maturity.

    Args:
        outcomes: List of possible outcomes, e.g. ['below_70k', '70k_75k', '75k_80k', 'above_80k'].
        event_id: Unique event identifier string.
        maturity: Unix timestamp when the oracle will attest.
        resolver_kind: Optional auto-resolution. 'price_buckets' or 'webhook'.
        resolver_url: URL for resolver (price source or webhook endpoint).
    """
    body = {"outcomes": outcomes, "eventid": event_id, "maturityTs": maturity}
    if resolver_kind and resolver_url:
        body["resolverConfig"] = {"kind": resolver_kind, "url": resolver_url}
    result = post_dlc_with_payment("/dlc/oracle/enum", body)
    if result.get("error"):
        return f"DLC enum registration failed: {result.get('message', result['error'])}"
    return _format_json(result, "DLC Enum Contract Registered")


@tool
def dlc_register_numeric(event_id: str, maturity: int, base: int = 10, nb_digits: int = 7, unit: str = "USD", resolver_kind: str | None = None, resolver_url: str | None = None, scale_factor: int = 1) -> str:
    """
    Register a DLC digit decomposition (numeric) contract. $7.00 USDC or 10,000 sats.

    Spec-compliant TLV format. Oracle decomposes a numeric value into digits at maturity.

    Args:
        event_id: Unique event identifier string.
        maturity: Unix timestamp when the oracle will attest.
        base: Number base (default 10).
        nb_digits: Number of digits (default 7, supports up to $9,999,999).
        unit: Unit label (default 'USD').
        resolver_kind: Optional. 'price_source' or 'webhook'.
        resolver_url: URL for resolver.
        scale_factor: Multiplier for sub-unit precision (100 for cents).
    """
    body = {
        "eventid": event_id, "maturityTs": maturity,
        "base": base, "nbDigits": nb_digits, "unit": unit,
    }
    if resolver_kind and resolver_url:
        body["resolverConfig"] = {"kind": resolver_kind, "url": resolver_url, "scaleFactor": scale_factor}
    result = post_dlc_with_payment("/dlc/oracle/numeric", body)
    if result.get("error"):
        return f"DLC numeric registration failed: {result.get('message', result['error'])}"
    return _format_json(result, "DLC Numeric Contract Registered")


@tool
def dlc_get_attestation(event_id: str) -> str:
    """
    Retrieve the cryptographic attestation for a settled DLC contract. FREE.

    Returns HTTP 425 if the contract has not yet settled.

    Args:
        event_id: The DLC event ID returned when the contract was registered.
    """
    result = fetch_dlc_free(f"/dlc/oracle/attestations/{event_id}")
    if not result:
        return f"No attestation found for event ID: {event_id}"
    if result.get("error") == "not_yet_attested":
        return f"Contract {event_id} has not been attested yet."
    if result.get("error"):
        return f"Error: {result.get('message', result['error'])}"
    lines = [
        "DLC Attestation",
        f"Event ID:    {result.get('eventid', event_id)}",
        f"Outcome:     {result.get('outcome', '')}",
        f"Attested at: {result.get('attestedAt', '')}",
    ]
    if result.get("signature"):
        lines.append(f"Signature:   {str(result['signature'])[:16]}...")
    return "\n".join(lines)


@tool
def dlc_list_announcements() -> str:
    """
    List all active DLC announcements from Mycelia Signal oracle. FREE.

    Returns event IDs, pairs, strikes, directions, and expiry times.
    """
    result = fetch_dlc_free("/dlc/oracle/announcements")
    if not result or result.get("error"):
        return f"Error: {result.get('message', 'Unable to fetch') if result else 'No response'}"
    announcements = result.get("announcements", [])
    if not announcements:
        return "No active DLC announcements found."
    lines = [f"Active DLC Announcements ({len(announcements)} total)"]
    for a in announcements[:15]:
        parts = [f"— {a.get('eventid', '')}"]
        if a.get("pair"):
            parts.append(f"| {a['pair']}")
        if a.get("strike"):
            parts.append(f"| strike: {a['strike']} {a.get('direction', '')}")
        if a.get("expiry"):
            parts.append(f"| expiry: {a['expiry']}")
        lines.append(" ".join(parts))
    if len(announcements) > 15:
        lines.append(f"...and {len(announcements) - 15} more")
    return "\n".join(lines)
