from langchain_core.tools import tool


# ── Layer 1 — Oracle Data tools ───────────────────────────────────────────────

@tool
def get_mycelia_price(pair: str) -> str:
    """
    Get a cryptographically signed price attestation from Mycelia Signal.

    Supports 58 pairs across crypto spot, VWAP, precious metals, FX pairs,
    stablecoins, US/EU economic indicators, and commodities.

    Pricing: $0.01 (spot/FX/metals), $0.02 (VWAP), $0.10 (econ/commodities).
    Free preview (unsigned, stale) requires no config.

    Args:
        pair: Asset pair key e.g. BTCUSD, EURUSD, XAUUSD, BTCUSD_VWAP,
              US_CPI, WTI. See SUPPORTED_PAIRS for full list.

    Returns:
        Signed price attestation with pair, price, sources, method, timestamp.
        In paid mode: includes Ed25519 signature, pubkey, and canonical string.
    """
    from .client import fetch_price
    return fetch_price(pair)


@tool
def get_mycelia_index(index: str) -> str:
    """
    Get a Mycelia Signal proprietary market index.

    Four indices computed from cross-exchange derivatives data (10+ venues):
    - MSVI: Volatility Index (0-100). Components: RV, IV, term structure, funding, PCR.
    - MSXI: Sentiment Index (-100 to +100). Components: funding, skew, PCR, term structure, basis.
    - MSSI: Stress Index (0-100). Components: vol regime, stablecoin stress, funding extremity, dispersion.
    - MSTI: Crypto-TradFi Contagion (0-100). Components: BTC-equity correlation, equity vol, DXY, beta.

    $0.05 per query. Free preview available (unsigned, stale).

    Args:
        index: One of MSVI_BTC, MSVI_ETH, MSXI_BTC, MSXI_ETH, MSSI, MSTI.

    Returns:
        Signed index value with component breakdown, regime, and confidence.
    """
    from .config import INDICES, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = index.upper().strip()
    if key not in INDICES:
        return f"Unsupported index: '{index}'. Supported: {', '.join(sorted(INDICES.keys()))}"

    path = INDICES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Mycelia {key}")


@tool
def get_mycelia_equity_index(index: str) -> str:
    """
    Get the Mycelia Signal equity/TradFi indices.

    Four indices available:
    - MESI: Equity Stress Index (0-100). Components: VIX (25%), credit spreads (25%),
      yield curve (20%), FRED STLFSI4 (15%), DXY (15%). 306s cadence. $0.05.
    - MNVI: NQ Volatility Index (0-100). Components: RV (28%), IV (28%),
      term structure (17%), skew (17%), PCR (10%). 114s cadence. $0.05.
    - MSLI: Leadership Index (0-100). 5-component ETF ratio composite: Growth vs Value
      (IVW/IVE, 25%), Tech vs Market (XLK/SPY, 25%), Small vs Large (IWM/SPY, 20%),
      Offensive vs Defensive sectors (15%), Cyclical vs Defensive sectors (15%).
      >50 = risk-on leadership. Regimes: RISK_ON/MILD_RISK_ON/NEUTRAL/MILD_DEFENSIVE/DEFENSIVE.
      300s cache. $0.05.
    - MSBI: Breadth Index (0-100). 3-component breadth composite: Sector participation
      % above 20DMA (40%), RSP/SPY equal-weight vs cap-weight momentum (35%), SPY vs
      20DMA deviation (25%). >50 = expanding breadth.
      Regimes: EXPANDING/IMPROVING/NEUTRAL/DETERIORATING/CONTRACTING. 300s cache. $0.05.

    Args:
        index: One of MESI, MNVI, MSLI, or MSBI (case-insensitive).

    Returns:
        Signed equity index value with component breakdown.
    """
    from .config import EQUITY_INDICES, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = index.upper().strip()
    if key not in EQUITY_INDICES:
        return f"Unsupported index: '{index}'. Supported: MESI, MNVI, MSLI, MSBI."

    path = EQUITY_INDICES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_equity_regime() -> str:
    """
    Get the MSERC — Mycelia Equity Regime Composite.

    2D equity regime framework preserving both market health and stress dimensions:
    - Health = MSLI × 0.6 + MSBI × 0.4 (internal market health — leadership and breadth)
    - Stress = MESI × 0.6 + MNVI × 0.4 (external stress — equity stress and NQ volatility)
    - Net = Health - Stress (range: -100 to +100)

    Regimes (7 states):
    - RISK_ON:       Health ≥55, Stress <45 — strong health, low stress
    - VOLATILE_BULL: Health ≥55, Stress ≥45 — strong health, high stress
    - MILD_RISK_ON:  Net >10 (middle band)
    - NEUTRAL:       Net between -10 and +10
    - MILD_STRESS:   Net <-10 (middle band)
    - DEFENSIVE:     Health <45, Stress <45 — weak health, low stress (calm bearish)
    - STRESS:        Health <45, Stress ≥45 — weak health, high stress

    Returns health score, stress score, net score, regime, and component breakdown.
    300s cache. Ed25519 signed. $0.10 per query.

    Returns:
        JSON with net, health, stress, regime, components (health/stress breakdown).
    """
    from .config import EQUITY_REGIME_ENDPOINT, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = EQUITY_REGIME_ENDPOINT
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_equity_rotation() -> str:
    """
    Get the MSRI — Mycelia Signal Rotation Index.

    Measures sector rotation momentum across 11 SPDR sector ETFs vs SPY:
    - Offensive: XLK (Technology), XLY (Consumer Disc), XLC (Communication)
    - Cyclical:  XLF (Financials), XLI (Industrials), XLB (Materials), XLE (Energy)
    - Defensive: XLP (Staples), XLU (Utilities), XLRE (Real Estate), XLV (Health Care)

    For each sector: excess 5d return (60%) + excess 20d return (40%) vs SPY = momentum.
    Acceleration = rs_5d - rs_20d (positive = gaining leadership).

    risk_on  = mean(offensive + cyclical momentum)
    risk_off = mean(defensive momentum)
    net      = risk_on - risk_off

    Regimes:
    - STRONG_OFFENSE: net > +1.5
    - MILD_OFFENSE:   net > +0.5
    - NEUTRAL:        net > -0.5
    - MILD_DEFENSE:   net > -1.5
    - STRONG_DEFENSE: net <= -1.5

    Returns net rotation, risk_on, risk_off, regime, top 2 leaders, bottom 2 laggards,
    and full per-sector breakdown with momentum and acceleration.
    300s cache. Ed25519 signed. $0.10 per query.

    Returns:
        JSON with net_rotation, risk_on, risk_off, regime, leaders, laggards, sectors.
    """
    from .config import MSRI_ENDPOINT, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = MSRI_ENDPOINT
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_funding(currency: str) -> str:
    """
    Get cross-exchange perpetual funding rates for BTC, ETH, or SOL.

    Composite from 10 venues (Binance, Bybit, OKX, Deribit, Hyperliquid, dYdX,
    Bitget, Kraken, Coinbase, Crypto.com). OI-weighted median, z-score vs 3-day
    history, regime classification, per-exchange breakdown. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed funding rate composite with per-exchange breakdown and regime.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = f"FUNDING_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Funding {currency.upper()}/USD")


@tool
def get_mycelia_oi(currency: str) -> str:
    """
    Get aggregate open interest for BTC, ETH, or SOL.

    Cross-exchange OI with 1h/4h/24h deltas showing positioning changes.
    Per-exchange breakdown. $0.01 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed open interest with deltas and per-exchange breakdown.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = f"OI_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Open Interest {currency.upper()}/USD")


@tool
def get_mycelia_basis(currency: str) -> str:
    """
    Get spot-futures basis and annualized carry for BTC, ETH, or SOL.

    Per-exchange basis (mark vs index price spread) and annualized carry
    across 5 exchanges. Regime: CONTANGO / BACKWARDATION / FLAT. $0.02 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed basis with per-exchange carry comparison and regime.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = f"BASIS_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Basis {currency.upper()}/USD")


@tool
def get_mycelia_greeks(currency: str) -> str:
    """
    Get multi-exchange consensus options Greeks for BTC, ETH, or SOL.

    Cross-exchange consensus delta, gamma, theta, vega, rho computed from
    2130+ BTC, 1822+ ETH, and 246+ SOL options across Deribit, OKX, and Bybit.
    Black-Scholes with custom norm_cdf. Returns ATM summary, 25-delta skew,
    and per-expiry breakdown. 30s cache. Ed25519 signed. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed Greeks with ATM summary, skew, and per-expiry breakdown.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = f"GREEKS_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_term_structure(currency: str) -> str:
    """
    Get the futures term structure for BTC, ETH, or SOL.

    Multi-exchange futures term structure with basis, annualized carry, and
    contango/backwardation regime detection across Deribit, OKX, and Bybit.
    Per-maturity breakdown with days-to-expiry. Ed25519 signed. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed term structure with per-maturity basis, carry, and regime.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = f"TERM_STRUCTURE_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_svi(currency: str) -> str:
    """
    Get the SVI volatility surface for BTC, ETH, or SOL.

    Gatheral 2004 Stochastic Volatility Inspired (SVI) arbitrage-free IV
    parameterization. Returns 5 fitted parameters (a, b, rho, m, sigma) per
    expiry with smooth smile interpolation. Correct negative skew (rho ~ -0.20).
    Ed25519 signed. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed SVI parameters per expiry with smile interpolation.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = f"SVI_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_iv_surface(currency: str) -> str:
    """
    Get the multi-exchange IV surface for BTC, ETH, or SOL.

    Per-strike implied volatility from Deribit, OKX, and Bybit with
    cross-exchange divergence detection and mispricing alerts. 1040+ strikes
    across 11 expiries. ATM term structure from near to far DTE. Max divergence
    signals actionable arbitrage. Ed25519 signed. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed multi-exchange IV surface with divergence and mispricing alerts.
    """
    from .config import DERIVATIVES, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = f"IV_SURFACE_{currency.upper().strip()}"
    if key not in DERIVATIVES:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = DERIVATIVES[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_liq_flow(currency: str, window: str = "1h") -> str:
    """
    Get liquidation flow for BTC, ETH, or SOL.

    Historical liquidation event flow from live WebSocket logger (94K+ events,
    31 days history). Long/short notional breakdown, dominant side, largest
    single liquidation, by-exchange split. $0.05 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).
        window: Time window — 1h, 4h, or 24h (default: 1h).

    Returns:
        Signed liquidation flow with long/short breakdown and dominant side.
    """
    from .config import LIQ_FLOW_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = currency.upper().strip()
    if key not in LIQ_FLOW_ENDPOINTS:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = LIQ_FLOW_ENDPOINTS[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = f"{API_BASE_URL}{path}?window={window}"

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_weather(lat: float, lon: float, metric: str = "wrsi", window: str = "30d") -> str:
    """
    Get parametric weather data at any global coordinate.

    ERA5 reanalysis via Open-Meteo. 0.25° global resolution. Used for
    parametric crop insurance, agricultural DeFi, and climate risk. $0.10 per query.

    Args:
        lat: Latitude (-90 to 90).
        lon: Longitude (-180 to 180).
        metric: One of wrsi, rainfall, temperature, wind.
        window: Time window e.g. 30d, 60d, 90d (wrsi); 7d, 14d, 30d (others).

    Returns:
        Signed weather measurement with parametric trigger status.
    """
    from .config import API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    path = f"/oracle/weather/{lat}/{lon}/{metric}/{window}"
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Weather {metric} @ ({lat},{lon})")


@tool
def get_mycelia_marine_seastate(lat: float, lon: float) -> str:
    """
    Get signed sea state at any ocean coordinate.

    Significant wave height, swell, and wind waves from Open-Meteo Marine API.
    Sea states: CALM (<0.5m) through EXTREME (≥9m). Parametric trigger thresholds
    included. $0.10 per query.

    Args:
        lat: Latitude of ocean location.
        lon: Longitude of ocean location.

    Returns:
        Signed sea state with wave height, swell, and parametric trigger status.
    """
    from .config import API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    path = f"/oracle/marine/{lat}/{lon}/seastate"
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Sea State @ ({lat},{lon})")


@tool
def get_mycelia_gas(chain: str) -> str:
    """
    Get real-time gas prices for EVM and non-EVM chains.

    Queries 3 public RPCs per chain, computes median gas price in gwei,
    normalizes to USD transaction cost using live ETH price.
    $0.01 per chain, $0.05 for cross-chain index.

    Args:
        chain: One of ETHEREUM, BASE, ARBITRUM, POLYGON, OPTIMISM, SOLANA, INDEX.

    Returns:
        Signed gas price with gwei, base fee, USD tx cost, and native price.
    """
    from .config import GAS_CHAINS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = chain.upper().strip()
    if key not in GAS_CHAINS:
        return f"Unsupported chain: '{chain}'. Supported: {', '.join(sorted(GAS_CHAINS.keys()))}"

    path = GAS_CHAINS[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Gas Oracle — {key}")


@tool
def get_mycelia_compute(query: str = "compare") -> str:
    """
    Get real-time GPU compute pricing across cloud providers.

    Aggregates AWS Spot, Vast.ai, RunPod, Akash, Azure, GCP. 81 GPU models,
    1341 prices. Normalized to $/GPU-hour. $0.05 per query.

    Args:
        query: One of all, compare, best_h100_sxm, best_a100_sxm, best_h200,
               best_rtx_4090, best_l40s, best_mi300x, best_v100, best_t4,
               catalogue (free).

    Returns:
        Signed GPU pricing with provider comparison and best-price ranking.
    """
    from .config import COMPUTE_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = query.upper().strip()
    if key not in COMPUTE_ENDPOINTS:
        return f"Unsupported query: '{query}'. Supported: {', '.join(sorted(COMPUTE_ENDPOINTS.keys()))}"

    path = COMPUTE_ENDPOINTS[key]
    if key != "CATALOGUE" and not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"GPU Compute — {query}")


@tool
def get_mycelia_defi_yield(query: str = "compare") -> str:
    """
    Get on-chain DeFi lending rates from 10 protocols across 7 chains.

    Direct smart contract reads (no API intermediaries). Protocols: Aave V3,
    Morpho Blue, Euler v2, Spark, Compound V3, Venus, Benqi, Moonwell, Sky DSR.
    Chains: Ethereum, Base, Arbitrum, Polygon, Optimism, Avalanche, BNB.
    53 rates. 15-min refresh. $0.05 per query.

    Args:
        query: One of all, compare, best_usdc, best_usdt, best_weth, best_dai,
               best_wbtc, catalogue (free).

    Returns:
        Signed DeFi yield rates with protocol and chain breakdown.
    """
    from .config import DEFI_YIELD_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = query.upper().strip()
    if key not in DEFI_YIELD_ENDPOINTS:
        return f"Unsupported query: '{query}'. Supported: {', '.join(sorted(DEFI_YIELD_ENDPOINTS.keys()))}"

    path = DEFI_YIELD_ENDPOINTS[key]
    if key != "CATALOGUE" and not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"DeFi Yield — {query}")


@tool
def get_mycelia_defi_metrics(protocol: str = "ALL") -> str:
    """
    Get DeFi protocol TVL, avg APR, and utilization metrics.

    8 protocols, ~$25B TVL coverage: Aave, Compound, Morpho, Spark, Sky,
    Euler, Venus, Benqi. DeFiLlama + on-chain reads. 30-min refresh. $0.05 per query.

    Args:
        protocol: One of ALL, AAVE, COMPOUND, MORPHO, SPARK, SKY (case-insensitive).

    Returns:
        Signed DeFi protocol metrics with TVL, avg APR, and utilization.
    """
    from .config import DEFI_METRICS_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = protocol.upper().strip()
    if key not in DEFI_METRICS_ENDPOINTS:
        return f"Unsupported protocol: '{protocol}'. Supported: {', '.join(sorted(DEFI_METRICS_ENDPOINTS.keys()))}"

    path = DEFI_METRICS_ENDPOINTS[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"DeFi Metrics — {key}")


@tool
def get_mycelia_inference(query: str = "compare") -> str:
    """
    Get normalized LLM inference pricing across 6 providers.

    Providers: OpenAI, Anthropic, Groq, Together, Fireworks, Cerebras.
    26 models, input/output $/M tokens, context windows, tier classification.
    Updated weekly. $0.02 per query.

    Args:
        query: One of OPENAI, ANTHROPIC, GROQ, TOGETHER, FIREWORKS, CEREBRAS,
               ALL, COMPARE, TASK_CHAT, TASK_CODE, TASK_REASONING,
               TASK_LONG_CONTEXT, TASK_FAST (case-insensitive).

    Returns:
        Signed inference pricing with per-model breakdown and tier classification.
    """
    from .config import INFERENCE_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = query.upper().strip()
    if key not in INFERENCE_ENDPOINTS:
        return f"Unsupported query: '{query}'. Supported: {', '.join(sorted(INFERENCE_ENDPOINTS.keys()))}"

    path = INFERENCE_ENDPOINTS[key]
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Inference Pricing — {key}")


@tool
def get_mycelia_econ_calendar(query: str = "TODAY") -> str:
    """
    Get the economic calendar and crypto options expiry schedule.

    Forward-looking macro events from Finnhub. Next 30 days, high/medium impact
    for US, EU, GB, JP, CN. Actual vs estimate where released. Surprise index.
    BTC/ETH options expiry from Deribit. 1h refresh. $0.05 per query.

    Args:
        query: One of CALENDAR, TODAY, FOMC, COUNTRY_US, COUNTRY_EU, COUNTRY_GB,
               COUNTRY_JP, SURPRISES ($0.10), EXPIRY_BTC, EXPIRY_ETH
               (case-insensitive).

    Returns:
        Signed economic calendar events with impact ratings and surprise index.
    """
    from .config import ECON_CALENDAR_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = query.upper().strip()
    if key not in ECON_CALENDAR_ENDPOINTS:
        return f"Unsupported query: '{query}'. Supported: {', '.join(sorted(ECON_CALENDAR_ENDPOINTS.keys()))}"

    path = ECON_CALENDAR_ENDPOINTS[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    return _format_json(data, title=f"Econ Calendar — {key}")


@tool
def get_mycelia_history(dataset: str, from_ts: str = "", to_ts: str = "") -> str:
    """
    Get cryptographically signed historical data with batch Ed25519 signatures.

    Index rows include original per-row signatures from collection time — unique
    cryptographic provenance. Max 1440 rows per query. $0.05 (spot/funding),
    $0.10 (index history).

    Args:
        dataset: One of SPOT_BTC_USD, SPOT_ETH_USD, SPOT_SOL_USD,
                 FUNDING_BTC, FUNDING_ETH, MSXI_BTCUSD, MSXI_ETHUSD,
                 MSVI_BTCUSD, MSVI_ETHUSD, MSSI, MSTI (case-insensitive).
        from_ts: ISO timestamp start (optional) e.g. 2026-06-01T00:00:00Z.
        to_ts: ISO timestamp end (optional).

    Returns:
        Signed historical data rows with batch signature and per-row provenance.
    """
    from .config import HISTORY_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    key = dataset.upper().strip()
    if key not in HISTORY_ENDPOINTS:
        return f"Unsupported dataset: '{dataset}'. Supported: {', '.join(sorted(HISTORY_ENDPOINTS.keys()))}"

    path = HISTORY_ENDPOINTS[key]
    if not is_paid_mode():
        path = path + "/preview"

    params = []
    if from_ts:
        params.append(f"from={from_ts}")
    if to_ts:
        params.append(f"to={to_ts}")
    url = API_BASE_URL + path + (f"?{'&'.join(params)}" if params else "")

    data = fetch_json(url)
    return _format_json(data, title=f"History — {key}")


@tool
def get_mycelia_cot() -> str:
    """
    Get CFTC Commitments of Traders data for Bitcoin CME futures.

    CFTC TFF report for BITCOIN - CHICAGO MERCANTILE EXCHANGE (code 133741).
    Returns leveraged fund, asset manager, and dealer net positions — long,
    short, net, % of open interest, and week-on-week changes.
    Weekly cadence: data as of prior Tuesday, published Friday 15:30 EST.
    $1.00 per query. No preview — data is weekly, not real-time.

    Returns:
        Signed COT positioning with leveraged fund, asset manager, and dealer breakdown.
    """
    from .config import API_BASE_URL, is_paid_mode
    from .client import fetch_json, _format_json

    if not is_paid_mode():
        return (
            "COT data requires payment ($1.00 USDC per query). "
            "Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments. "
            "No preview available — data is weekly, not real-time."
        )

    url = API_BASE_URL + "/oracle/cot/btc"
    data = fetch_json(url)
    return _format_json(data, title="CME BTC COT — Institutional Positioning")


# ── DLC Oracle tools ──────────────────────────────────────────────────────────

@tool
def dlc_threshold_preview(pair: str, strike: float, direction: str) -> str:
    """
    Preview a DLC threshold contract without registering (free).

    Shows what the oracle announcement would look like for a threshold event.
    No payment required. Useful for validating parameters before paying $7.00.

    Args:
        pair: Asset pair e.g. BTCUSD, ETHUSD, XAUUSD.
        strike: Strike price e.g. 90000.
        direction: One of above or below.

    Returns:
        Preview announcement with event ID format and maturity info.
    """
    from .config import API_BASE_URL
    from .client import fetch_dlc_free

    result = fetch_dlc_free(f"/dlc/oracle/threshold/preview?pair={pair}&strike={strike}&direction={direction}")
    if result is None:
        return "Preview unavailable."
    import json
    return json.dumps(result, indent=2)


@tool
def dlc_register_threshold(pair: str, strike: float, direction: str, expiry: str) -> str:
    """
    Register a DLC threshold contract with the Mycelia Signal oracle. $7.00.

    Creates a spec-compliant BIP-340 Schnorr oracle announcement for a binary
    threshold event (above/below a price at expiry). Wire format compatible with
    kormir, dlcdevkit, rust-dlc, bitcoin-s, and any spec-compliant DLC library.

    Args:
        pair: Asset pair e.g. BTCUSD, ETHUSD, XAUUSD.
        strike: Strike price e.g. 90000.
        direction: One of above or below.
        expiry: ISO 8601 expiry e.g. 2026-12-31T00:00:00Z.

    Returns:
        Signed oracle announcement with event ID, nonce, and TLV blob.
    """
    from .client import post_dlc_with_payment
    import json
    result = post_dlc_with_payment("/dlc/oracle/threshold", {
        "pair": pair, "strike": strike, "direction": direction, "expiry": expiry
    })
    return json.dumps(result, indent=2)


@tool
def dlc_register_enum(outcomes: list, event_id: str, maturity: int) -> str:
    """
    Register a DLC enum (disjoint union) event with the Mycelia Signal oracle. $7.00.

    Creates a spec-compliant oracle announcement for a multi-outcome event.
    Supports 2-100 outcomes. Wire format: TLV type 55302 (enum_event_descriptor).

    Args:
        outcomes: List of 2-100 outcome strings e.g. ["below_70k", "70k_80k", "above_80k"].
        event_id: Unique event identifier string.
        maturity: Unix timestamp of event maturity.

    Returns:
        Signed oracle announcement with TLV blob for DLC client ingestion.
    """
    from .client import post_dlc_with_payment
    import json
    result = post_dlc_with_payment("/dlc/oracle/enum", {
        "outcomes": outcomes, "event_id": event_id, "maturity": maturity
    })
    return json.dumps(result, indent=2)


@tool
def dlc_register_numeric(event_id: str, maturity: int, base: int = 2, digits: int = 20) -> str:
    """
    Register a DLC numeric (digit decomposition) event with Mycelia Signal. $7.00.

    Creates a spec-compliant oracle announcement for a numeric outcome event.
    Configurable base (2-256), digits (1-32). Wire format: TLV type 55306.
    Optional scaleFactor for sub-unit precision (100=cents, 10000=bps).

    Args:
        event_id: Unique event identifier string.
        maturity: Unix timestamp of event maturity.
        base: Digit decomposition base 2-256 (default: 2).
        digits: Number of digits 1-32 (default: 20).

    Returns:
        Signed oracle announcement with digit decomposition parameters.
    """
    from .client import post_dlc_with_payment
    import json
    result = post_dlc_with_payment("/dlc/oracle/numeric", {
        "event_id": event_id, "maturity": maturity, "base": base, "digits": digits
    })
    return json.dumps(result, indent=2)


@tool
def dlc_get_attestation(event_id: str) -> str:
    """
    Get the BIP-340 Schnorr attestation for a settled DLC event (free).

    Returns the oracle's signed attestation once an event has matured and
    been attested. Returns 404/not_yet_attested if event is still pending.

    Args:
        event_id: Event ID returned at registration e.g. BTCUSD-2026-04-07T00:00:00Z.

    Returns:
        BIP-340 Schnorr attestation for DLC contract settlement.
    """
    from .client import fetch_dlc_free
    import json
    result = fetch_dlc_free(f"/dlc/oracle/announcements/{event_id}/attestation")
    if result is None:
        return "Attestation not available."
    return json.dumps(result, indent=2)


@tool
def dlc_list_announcements() -> str:
    """
    List all active DLC oracle announcements (free).

    Returns all active threshold, enum, and numeric event announcements
    registered with the Mycelia Signal DLC oracle. No payment required.

    Returns:
        List of active oracle announcements with event IDs and maturity dates.
    """
    from .client import fetch_dlc_free
    import json
    result = fetch_dlc_free("/dlc/oracle/announcements")
    if result is None:
        return "Could not retrieve announcements."
    return json.dumps(result, indent=2)


# ── Layer 2 — Oracle Information tools ───────────────────────────────────────

@tool
def get_mycelia_synopsis(query: str = "market") -> str:
    """
    Get the Mycelia Signal Market Synopsis — a 15-signal market state snapshot.

    Layer 2 Oracle Information. Internally aggregates all four indices (MSVI, MSXI,
    MSSI, MSTI), BTC/ETH/SOL spot prices, funding rate, OI delta, liquidation flow,
    VWAP, basis regime, and economic calendar context into a single signed snapshot.
    $0.25 per query. 60s cache.

    Args:
        query: Always "market" (only supported value).

    Returns:
        Signed market state snapshot with all 15 signals.
    """
    from .config import SYNOPSIS_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = SYNOPSIS_ENDPOINTS.get("MARKET", "/oracle/synopsis/market")
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_perp_regime(currency: str) -> str:
    """
    Get the Mycelia Signal perp trading regime for BTC, ETH, or SOL.

    Layer 2 Oracle Information. Returns a regime classification with directional
    bias, confidence score, and risk level.
    BTC/ETH: 10 signals (MSXI, MSVI, funding, OI, basis, liq flow, orderbook, IV, price, term structure).
    SOL: 8 signals (no MSXI/MSVI for SOL).
    Regimes: BULLISH_MOMENTUM, MILD_BULLISH, NEUTRAL_CHOPPY, MILD_BEARISH,
    BEARISH_MOMENTUM, BEARISH_FUNDING_EXTREME, SQUEEZE_SETUP, LONG_TRAP, VOLATILITY_SPIKE.
    $0.15 per query. 30s cache.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed perp regime classification with bias, confidence, risk, and signal notes.
    """
    from .config import PERP_REGIME_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = currency.upper().strip()
    if key not in PERP_REGIME_ENDPOINTS:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = PERP_REGIME_ENDPOINTS[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_tradfi_regime(regime: str = "EQUITY") -> str:
    """
    Get the Mycelia Signal TradFi regime classification.

    Layer 2 Oracle Information. Two regimes available:
    - EQUITY: TradFi equity stress regime (RISK_ON / NEUTRAL / STRESS / PANIC).
      Inputs: MESI equity stress index, MNVI NQ volatility, FRED T10Y2Y yield curve.
      300s cache. $0.10.
    - LIQUIDITY: Market liquidity regime (DEEP / NORMAL / THIN / FRAGILE).
      Inputs: funding rates, OI, basis, liq-flow, orderbook depth.
      60s cache. $0.10.

    Args:
        regime: One of EQUITY or LIQUIDITY (case-insensitive).

    Returns:
        Signed regime classification with confidence, dominant_signal, and inputs.
    """
    from .config import TRADFI_REGIME_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = regime.upper().strip()
    if key not in TRADFI_REGIME_ENDPOINTS:
        return f"Unsupported regime: '{regime}'. Supported: EQUITY, LIQUIDITY."

    path = TRADFI_REGIME_ENDPOINTS[key]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


# ── Layer 3 — Oracle Intelligence tools ──────────────────────────────────────

@tool
def get_mycelia_macro_risk(query: str = "market") -> str:
    """
    Get the Mycelia Signal macro risk score — cross-domain risk 0-100.

    Layer 3 Oracle Intelligence. Combines MSSI crypto stress (40%), MSTI
    contagion (30%), and economic calendar events (30%) into a single risk score.
    Regimes: LOW (0-19), MODERATE (20-39), ELEVATED (40-59), HIGH (60-79),
    CRITICAL (80-100). Includes disclaimer field. $1.00 per query. 60s cache.

    Args:
        query: Always "market" (only supported value).

    Returns:
        Signed macro risk score with factor breakdown and disclaimer.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = ORACLE_INTEL_ENDPOINTS["MACRO_RISK"]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_perp_setup(query: str = "scan") -> str:
    """
    Get the Mycelia Signal perp setup scanner — best setup across BTC, ETH, SOL.

    Layer 3 Oracle Intelligence. Scans all three currencies simultaneously,
    scores setups by confidence and regime type, applies MSSI market bias overlay.
    Returns highest_confidence_setup with signal_alignment (not buy/sell),
    edge, invalidation_conditions. Includes disclaimer. $1.00 per query. 30s cache.

    Args:
        query: Always "scan" (only supported value).

    Returns:
        Signed perp setup scan with highest-confidence setup and disclaimer.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = ORACLE_INTEL_ENDPOINTS["PERP_SETUP"]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_defi_opportunity(query: str = "usdc") -> str:
    """
    Get the Mycelia Signal DeFi opportunity — risk-adjusted yield ranking.

    Layer 3 Oracle Intelligence. Fetches 15+ DeFi protocols and penalizes raw APR
    by MSSI stress regime (up to -4%) and MSTI contagion for cross-chain protocols
    (up to -2%). Returns highest_opportunity with raw_apr, stress_penalty,
    risk_adjusted_apr. Includes disclaimer. $0.75 per query. 60s cache.

    Args:
        query: Always "usdc" (primary asset tracked).

    Returns:
        Signed risk-adjusted DeFi opportunity with penalty breakdown and disclaimer.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = ORACLE_INTEL_ENDPOINTS["DEFI_OPPORTUNITY"]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_regime_change(currency: str = "BTC") -> str:
    """
    Get the Mycelia Signal regime change detector for BTC, ETH, or SOL.

    Layer 3 Oracle Intelligence. Compares current perp regime vs 2 hours ago
    from perp_history.db. Returns transition type, from/to regimes, duration,
    and change magnitude. 30s cache. Includes disclaimer. $0.50 per query.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed regime transition with from/to regimes and change metadata.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = currency.upper().strip()
    if key not in {"BTC", "ETH", "SOL"}:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = ORACLE_INTEL_ENDPOINTS["REGIME_CHANGE"]
    if not is_paid_mode():
        path = path + "/preview"
    url = f"{API_BASE_URL}{path}?currency={key}"

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_divergence(query: str = "market") -> str:
    """
    Get the Mycelia Signal cross-asset divergence score.

    Layer 3 Oracle Intelligence. Measures divergence between crypto and TradFi
    regimes. Levels: NONE / LOW / MODERATE / HIGH / EXTREME.
    Directions: aligned, crypto_bullish_tradfi_stressed,
    crypto_bearish_tradfi_complacent, crypto_leads_recovery,
    crypto_ignores_risk, tradfi_stressed_crypto_unmoved.
    Includes disclaimer. 60s cache. $0.50 per query.

    Args:
        query: Always "market" (only supported value).

    Returns:
        Signed cross-asset divergence level, direction, and contagion flag.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = ORACLE_INTEL_ENDPOINTS["DIVERGENCE"]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_consensus(query: str = "market") -> str:
    """
    Get the Mycelia Signal regime consensus score.

    Layer 3 Oracle Intelligence. Weighted vote aggregation across all regime
    classifiers. Strength: STRONG / MODERATE / WEAK / CONFLICTED.
    Theme: BULLISH / STRESSED / BEARISH / NEUTRAL / MIXED.
    Weights: BTC/ETH/SOL perp (1.0×), TradFi (1.5×), MSSI (1.0×),
    MSTI (0.5×), Macro (1.5×). Includes disclaimer. 60s cache. $0.50 per query.

    Args:
        query: Always "market" (only supported value).

    Returns:
        Signed consensus strength, dominant theme, and weighted vote breakdown.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    path = ORACLE_INTEL_ENDPOINTS["CONSENSUS"]
    if not is_paid_mode():
        path = path + "/preview"
    url = API_BASE_URL + path

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)


@tool
def get_mycelia_regime_persistence(currency: str = "BTC") -> str:
    """
    Get the Mycelia Signal regime persistence statistics for BTC, ETH, or SOL.

    Layer 3 Oracle Intelligence. Reads perp_history.db directly — no upstream
    HTTP calls. Returns how long the current regime has been running, where it
    sits historically (percentile), and how much longer it typically lasts.
    Includes disclaimer. 30s cache. $0.15 per query.

    Output: current_regime, bias, duration_hours, historical_percentile,
    typical_remaining_hours, longest/shortest_run_hours.

    Args:
        currency: One of BTC, ETH, SOL (case-insensitive).

    Returns:
        Signed regime persistence stats with historical percentile and remaining estimate.
    """
    from .config import ORACLE_INTEL_ENDPOINTS, API_BASE_URL, is_paid_mode
    from .client import fetch_json

    key = currency.upper().strip()
    if key not in {"BTC", "ETH", "SOL"}:
        return f"Unsupported currency: '{currency}'. Supported: BTC, ETH, SOL."

    path = ORACLE_INTEL_ENDPOINTS["PERSISTENCE"]
    if not is_paid_mode():
        path = path + "/preview"
    url = f"{API_BASE_URL}{path}?currency={key}"

    data = fetch_json(url)
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    import json
    return json.dumps(data, indent=2)
