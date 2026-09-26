"""LangChain tools for Mycelia Signal.

NO DOLLAR FIGURES IN THESE DOCSTRINGS. Prices live in config.ROUTES, generated from
the proxy's routes.ts, and are surfaced at call time in the result title and in the
402 notice. A price written into prose is a copy, and the 2026-09-26 audit found
exactly that class of copy wrong by 10x on econ and 4x on synopsis.

35 parameterised tools covering all 214 priced routes.

WHY PARAMETERISED, NOT ONE TOOL PER ROUTE. 214 entries in an agent's tool list is
unusable: descriptions consume context on every call and a picker that long makes the
model choose badly. Each tool below takes the arguments that select a route and looks
the price up from ROUTES by exact path -- so coverage is complete without the list
being unreadable.

Every price and description comes from config.ROUTES, which is generated from the
proxy's own routes.ts. Nothing here states a price of its own.
"""
from __future__ import annotations

from langchain_core.tools import tool

from .client import fetch_json, _format_json
from .config import ROUTES, describe, price_for, route_key, url_for

_UNKNOWN = ("Unknown route: {path}. This package covers {n} priced endpoints; "
            "see ROUTES in config.py for the full list.")


def _call(path: str, title: str = "") -> str:
    """Fetch one route, or say plainly that it is not a route we know.

    A wrong path must not silently become a request the proxy rejects with an
    unhelpful 404 -- the caller gets the reason here instead.
    """
    key = route_key(path)
    if key is None:
        return _UNKNOWN.format(path=path, n=len(ROUTES))
    data = fetch_json(url_for(path))
    return _format_json(data, title or f"{path}  ({price_for(path)})")


# ── Prices, FX, metals ───────────────────────────────────────────────────────

@tool
def get_mycelia_price(base: str, quote: str) -> str:
    """Signed spot price, median across up to 10 exchanges. 40 pairs: crypto
    (btc, eth, sol, xrp, ada, doge), stablecoin pegs (usdt, usdc), gold (xau) and
    27 FX crosses. base and quote are both required, e.g. base='btc', quote='usd'. Returns a canonical string and Ed25519 signature verifiable offline."""
    return _call(f"/oracle/price/{base.lower().strip()}/{quote.lower().strip()}")


@tool
def get_mycelia_vwap(base: str, quote: str) -> str:
    """Volume-weighted average price and its premium to spot, for execution
    benchmarking. Available for btc/usd, btc/eur and eth/usd."""
    return _call(f"/oracle/price/{base.lower().strip()}/{quote.lower().strip()}/vwap")


# ── Crypto indices ───────────────────────────────────────────────────────────

_INDEX_PATHS = {
    "msvi": "/oracle/volatility/{pair}",
    "msxi": "/oracle/sentiment/{pair}",
    "mssi": "/oracle/stress/market",
    "msti": "/oracle/contagion/market",
}


@tool
def get_mycelia_index(index: str, pair: str = "btc/usd") -> str:
    """A Mycelia crypto index, MEASURED not forecast. index is one of:
    msvi (volatility 0-100, per pair), msxi (sentiment -100..+100, per pair),
    mssi (market-wide stress), msti (crypto-TradFi contagion).
    pair applies to msvi and msxi only: btc/usd or eth/usd. Price from the route table.

    These describe the current state of the market. Out-of-sample testing found no
    Mycelia index predicts 24h forward returns at a detectable magnitude."""
    k = index.lower().strip()
    if k not in _INDEX_PATHS:
        return f"Unknown index '{index}'. Use one of: {', '.join(_INDEX_PATHS)}."
    return _call(_INDEX_PATHS[k].format(pair=pair.lower().strip()))


@tool
def get_mycelia_equity_index(index: str) -> str:
    """A Mycelia equity/TradFi index. index is one of:
    mesi (equity stress: VIX, VVIX, IV/RV, credit, DXY), mnvi (NQ volatility),
    msli (leadership: growth vs value, tech vs market), msbi (breadth: sector
    participation), mserc (regime composite: health vs stress), msri (sector
    rotation across 11 ETFs). mserc and msri cost more than the four component
    indices; see the price in the result title."""
    m = {"mesi": "/oracle/stress/equity", "mnvi": "/oracle/volatility/nq/usd",
         "msli": "/oracle/leadership/equity", "msbi": "/oracle/breadth/equity",
         "mserc": "/oracle/regime/equity/composite", "msri": "/oracle/rotation/equity"}
    k = index.lower().strip()
    if k not in m:
        return f"Unknown equity index '{index}'. Use one of: {', '.join(m)}."
    return _call(m[k])


# ── Derivatives ──────────────────────────────────────────────────────────────

@tool
def get_mycelia_funding(pair: str, term_structure: bool = False) -> str:
    """Perpetual funding rate composite across 5 exchanges, with OI-weighted and
    median rates, the venue-published next scheduled rate, z-score and regime.
    pair: btc/usd, eth/usd or sol/usd. Set term_structure=True for the carry curve
    across maturities instead."""
    p = pair.lower().strip()
    return _call(f"/oracle/funding/{p}/term-structure" if term_structure
                 else f"/oracle/funding/{p}")


@tool
def get_mycelia_oi(pair: str) -> str:
    """Open interest across 5 exchanges with 1h/4h/24h deltas. Native per-venue
    units are NOT comparable between exchanges; use the USD figures to aggregate.
    pair: btc/usd, eth/usd or sol/usd."""
    return _call(f"/oracle/oi/{pair.lower().strip()}")


@tool
def get_mycelia_basis(pair: str) -> str:
    """Spot-futures basis and annualised carry across 5 exchanges, with per-exchange
    mark and index prices. pair: btc/usd, eth/usd or sol/usd."""
    return _call(f"/oracle/basis/{pair.lower().strip()}")


@tool
def get_mycelia_liquidations(pair: str) -> str:
    """Real-time liquidation events across 4 exchanges with imbalance and clustering.
    pair: btc/usd, eth/usd or sol/usd. For windowed aggregates use
    get_mycelia_liq_flow instead."""
    return _call(f"/oracle/liquidations/{pair.lower().strip()}")


@tool
def get_mycelia_liq_flow(currency: str) -> str:
    """Liquidation flow aggregated over 1h/4h/24h windows: long/short breakdown,
    dominant side and largest single event. currency: btc, eth or sol."""
    return _call(f"/oracle/liq-flow/{currency.lower().strip()}")


@tool
def get_mycelia_orderbook(pair: str) -> str:
    """Order book imbalance across 5 exchanges: depth, spread, sweep cost and
    collapse detection. pair: btc/usd or eth/usd."""
    return _call(f"/oracle/orderbook/{pair.lower().strip()}")


@tool
def get_mycelia_iv(pair: str) -> str:
    """Implied volatility summary: ATM IV, 25-delta skew and term structure from
    Deribit options. pair: btc/usd or eth/usd. For the full per-strike grid
    across exchanges use get_mycelia_iv_surface."""
    return _call(f"/oracle/iv/{pair.lower().strip()}")


@tool
def get_mycelia_iv_surface(pair: str) -> str:
    """Multi-exchange IV surface: per-strike IV from 3 exchanges with cross-exchange
    divergence. A measurement of where quotes differ between venues, not a trading
    signal. pair: btc/usd, eth/usd or sol/usd."""
    return _call(f"/oracle/iv-surface/{pair.lower().strip()}")


@tool
def get_mycelia_svi(pair: str) -> str:
    """SVI surface parameters (Gatheral 2004 arbitrage-free parameterisation) for
    smooth smile interpolation. pair: btc/usd, eth/usd or sol/usd."""
    return _call(f"/oracle/svi/{pair.lower().strip()}")


@tool
def get_mycelia_greeks(pair: str) -> str:
    """Options Greeks: cross-exchange consensus delta, gamma, theta and vega.
    pair: btc/usd (2130+ options), eth/usd (1822+) or sol/usd (246+)."""
    return _call(f"/oracle/greeks/{pair.lower().strip()}")


@tool
def get_mycelia_term_structure(pair: str) -> str:
    """Futures term structure: basis, annualised carry and contango/backwardation
    across 3 exchanges. pair: btc/usd, eth/usd or sol/usd."""
    return _call(f"/oracle/term-structure/{pair.lower().strip()}")


@tool
def get_mycelia_instruments(currency: str) -> str:
    """Options instrument discovery: every listed contract with strikes and expiries
    across 3 exchanges. currency: btc, eth or sol."""
    return _call(f"/oracle/instruments/{currency.lower().strip()}/options")


# ── Macro, economics, prediction markets ─────────────────────────────────────

_ECON = {
    "us": ("cpi", "cpi_core", "pce", "nfp", "unrate", "gdp", "fedfunds", "yield_curve"),
    "eu": ("hicp", "hicp_core", "hicp_services", "gdp", "unrate", "employment"),
    "commodities": ("wti", "brent", "natgas", "copper", "dxy"),
}


@tool
def get_mycelia_econ(region: str, indicator: str) -> str:
    """A signed economic indicator carrying ITS OWN OBSERVATION DATE -- the date the
    statistic refers to, not the date it was fetched.

    region='us':          cpi, cpi_core, pce, nfp, unrate, gdp, fedfunds, yield_curve
    region='eu':          hicp, hicp_core, hicp_services, gdp, unrate, employment
    region='commodities': wti, brent, natgas, copper, dxy

    An illegal combination errors rather than returning empty data."""
    r, i = region.lower().strip(), indicator.lower().strip()
    if r not in _ECON or i not in _ECON[r]:
        return (f"Unknown combination region='{r}' indicator='{i}'. Valid: "
                + "; ".join(f"{k}: {', '.join(v)}" for k, v in _ECON.items()))
    return _call(f"/oracle/econ/{r}/{i}")


@tool
def get_mycelia_econ_calendar(scope: str = "upcoming") -> str:
    """Economic calendar. scope is one of: 'upcoming' (next 30 days, high/medium
    impact for US, EU, GB, JP, CN), 'today', 'fomc' (Fed decision dates), 'us', 'eu'. For options expiries use get_mycelia_expiry."""
    m = {"upcoming": "/oracle/econ/calendar", "today": "/oracle/econ/calendar/today",
         "fomc": "/oracle/econ/calendar/fomc", "us": "/oracle/econ/calendar/country/us",
         "eu": "/oracle/econ/calendar/country/eu"}
    k = scope.lower().strip()
    if k not in m:
        return f"Unknown scope '{scope}'. Use one of: {', '.join(m)}."
    return _call(m[k])


@tool
def get_mycelia_expiry(currency: str) -> str:
    """Options expiry dates: the next 8 Deribit expiries tagged daily, weekly,
    monthly or quarterly. currency: btc or eth."""
    return _call(f"/oracle/econ/expiry/{currency.lower().strip()}")


@tool
def get_mycelia_cot(asset: str = "btc") -> str:
    """CFTC Commitments of Traders: institutional CME futures positioning.
    Currently btc only."""
    return _call(f"/oracle/cot/{asset.lower().strip()}")


@tool
def get_mycelia_prediction(kind: str, code: str = "") -> str:
    """Prediction-market implied probabilities -- a reading of what a market is
    priced at, not a directional call.

    kind='fed'            Fed rate path from Kalshi + Polymarket. Optional
                          code selects one FOMC meeting.
    kind='btc'/'eth'      Same-day price distribution from Polymarket
    kind='options_btc'    Risk-neutral distribution at 12 horizons via
    kind='options_eth'    Breeden-Litzenberger from the SVI surface
    kind='cpi'/'gdp'      Kalshi distribution. Optional code selects a period.
    """
    k = kind.lower().strip()
    c = code.strip()
    base = {"fed": "/oracle/prediction/fed", "btc": "/oracle/prediction/btc/price",
            "eth": "/oracle/prediction/eth/price",
            "options_btc": "/oracle/prediction/options/btc",
            "options_eth": "/oracle/prediction/options/eth",
            "cpi": "/oracle/prediction/cpi", "gdp": "/oracle/prediction/gdp"}
    if k not in base:
        return f"Unknown kind '{kind}'. Use one of: {', '.join(base)}."
    if c and k in ("fed", "cpi", "gdp"):
        return _call(f"{base[k]}/{c}")
    return _call(base[k])


# ── Regimes and intelligence ─────────────────────────────────────────────────

@tool
def get_mycelia_perp_regime(currency: str) -> str:
    """Perpetual-futures regime for one currency: a 10-signal classification with
    bias, confidence and risk (SQUEEZE_SETUP, LONG_TRAP, VOLATILITY_EXPANSION and
    others). currency: btc, eth or sol. A classification of the current
    state, not a prediction of the next one."""
    return _call(f"/oracle/perp/{currency.lower().strip()}")


@tool
def get_mycelia_regime(kind: str) -> str:
    """A regime classification. kind is one of:
    'equity'    TradFi regime from MESI, MNVI and the US yield curve
    'liquidity' BTC liquidity from funding, OI, basis, liquidations, orderbook
    'composite' MSERC equity regime composite, health vs stress"""
    m = {"equity": "/oracle/regime/equity", "liquidity": "/oracle/regime/liquidity",
         "composite": "/oracle/regime/equity/composite"}
    k = kind.lower().strip()
    if k not in m:
        return f"Unknown regime '{kind}'. Use one of: {', '.join(m)}."
    return _call(m[k])


@tool
def get_mycelia_intel(kind: str) -> str:
    """Layer-3 cross-domain analysis. kind is one of:
    'macro_risk'            MSSI + MSTI + econ calendar, risk_score 0-100
    'perp_setup'            BTC+ETH+SOL perp scan with signal alignment, edge and
                            the conditions that invalidate the label
    'prediction_divergence' Kalshi vs Polymarket spread with significance
    'defi_opportunity'      Stress-penalised APR ranking, 15+ protocols
    'regime_change'         Perp regime transitions vs 2h ago
    'divergence'            Crypto vs TradFi disagreement
    'consensus'             Alignment across perp, TradFi, MSSI, MSTI, macro
    'persistence'           How long the current regime has held, and the historical
                            median remainder for past runs of this age -- a
                            description of what happened before, not an expectation
                            for this run"""
    # MCP renamed perp_setup -> perp_state and defi_opportunity ->
    # defi_yield_snapshot, because "setup" and "opportunity" read to a model as
    # trade instructions. Both names are accepted here so a desk using both
    # surfaces does not learn two vocabularies for one endpoint.
    m = {"macro_risk": "/oracle/intel/macro/risk", "perp_setup": "/oracle/intel/perp/setup",
         "perp_state": "/oracle/intel/perp/setup",
         "defi_yield_snapshot": "/oracle/intel/defi/opportunity",
         "prediction_divergence": "/oracle/intel/prediction/divergence",
         "defi_opportunity": "/oracle/intel/defi/opportunity",
         "regime_change": "/oracle/intel/regime/change",
         "divergence": "/oracle/intel/divergence", "consensus": "/oracle/intel/consensus",
         "persistence": "/oracle/intel/regime/persistence"}
    k = kind.lower().strip()
    if k not in m:
        return f"Unknown intel kind '{kind}'. Use one of: {', '.join(m)}."
    return _call(m[k])


@tool
def get_mycelia_synopsis(scope: str = "market") -> str:
    """Whole-market state in ONE signed call: stress and contagion indices, macro
    risk, and per currency the funding z-score, OI change, liquidation flow, basis
    carry, perp regime and the run it sits in, order book, futures curve and IV/RV.
    From 51 sources, cached 60s.

    scope='market' covers BTC, ETH and SOL. scope='btc', 'eth' or 'sol'
    narrows it to one currency (priced separately on the API, not because it
    contains more). Use this instead of twenty individual calls."""
    s = scope.lower().strip()
    return _call("/oracle/synopsis/market" if s == "market" else f"/oracle/synopsis/{s}")


@tool
def get_mycelia_support_resistance(currency: str, method: str = "all") -> str:
    """Price levels MEASURED from up to 120 days of spot history, with a parameter
    hash for reproducibility.

    method='pivot'   swing points where price reversed
    method='density' dwell levels where price spent time
    method='round'   psychological round numbers
    method='all'     the union, with cross-method corroboration

    currency: btc, eth or sol. 'No level' means no measured structure at that price,
    not that price will not stop there."""
    c, m = currency.lower().strip(), method.lower().strip()
    return _call(f"/oracle/market/support/{m}/{c}")


# ── DeFi, compute, inference, gas ────────────────────────────────────────────

@tool
def get_mycelia_defi_yield(asset: str = "", protocol: str = "", chain: str = "") -> str:
    """DeFi lending rates read on-chain from 9 protocols across 7 chains.

    No arguments        every rate, all deployments
    asset only          best supply yield for that asset: usdc, usdt, weth, dai, wbtc
    asset='compare'     USDC rate comparison across all protocols
    all three           supply and borrow APR for one protocol/chain/asset triple,
                        e.g. protocol='aave', chain='base', asset='usdc'"""
    a, p, c = asset.lower().strip(), protocol.lower().strip(), chain.lower().strip()
    if p and c and a:
        return _call(f"/oracle/defi/yield/{p}/{c}/{a}")
    if a == "compare":
        return _call("/oracle/defi/yield/compare")
    if a:
        return _call(f"/oracle/defi/yield/best/{a}")
    return _call("/oracle/defi/yield/all")


@tool
def get_mycelia_defi_metrics(protocol: str = "") -> str:
    """DeFi protocol metrics: TVL, average supply APR and utilisation.
    No argument returns all protocols; protocol='aave', 'compound' or 'morpho'
    narrows it to one."""
    p = protocol.lower().strip()
    return _call(f"/oracle/defi/metrics/{p}" if p else "/oracle/defi/metrics")


@tool
def get_mycelia_compute(model: str = "") -> str:
    """GPU cloud rental pricing across Azure, GCP, AWS, Lambda and CoreWeave, in
    $/GPU-hour.

    No argument         every provider and model
    model='compare'     cheapest per model across all sources
    model='h100_sxm' | 'a100_sxm' | 'h200' | 'rtx_4090' | 'l40s'
                        the cheapest rate for that GPU"""
    m = model.lower().strip()
    if not m:
        return _call("/oracle/compute/all")
    if m == "compare":
        return _call("/oracle/compute/compare")
    return _call(f"/oracle/compute/best/{m}")


@tool
def get_mycelia_inference(provider: str = "", task: str = "") -> str:
    """LLM inference pricing: 6 providers, 26 models, normalised to $/M tokens.

    No arguments        all providers and models
    provider='anthropic' | 'openai' | 'groq' | 'together' | 'fireworks' | 'cerebras'
    provider='compare'  cheapest per tier: frontier, efficient, fast, reasoning
    task='chat' | 'reasoning' | 'long_context'
                        the cheapest model suited to that task"""
    p, t = provider.lower().strip(), task.lower().strip()
    if t:
        return _call(f"/oracle/inference/compare/task/{t}")
    if p == "compare":
        return _call("/oracle/inference/compare")
    if p:
        return _call(f"/oracle/inference/{p}/pricing")
    return _call("/oracle/inference/all")


@tool
def get_mycelia_gas(chain: str = "index") -> str:
    """Gas price for one chain, or the cross-chain index. chain: ethereum, base,
    arbitrum, polygon, optimism, solana ( each), or 'index' for a normalised
    comparison across all of them."""
    return _call(f"/oracle/gas/{chain.lower().strip()}")


# ── History ──────────────────────────────────────────────────────────────────

@tool
def get_mycelia_history(series: str, pair: str = "btc/usd") -> str:
    """Signed historical series, each row carrying its ORIGINAL signature from the
    moment it was recorded -- not re-signed at query time.

    series='spot'     OHLCV, 1m/5m/1h/4h/1d, up to 60 days. pair: btc/usd, eth/usd

    series='funding'  per-exchange funding, 18 days. pair: btc/usd, eth/usd
    series='msxi'     sentiment index, 60 days. pair: btcusd, ethusd
    series='msvi'     volatility index, 63 days. pair: btcusd, ethusd
    series='mssi'     stress index, 56 days
    series='msti'     contagion index, 56 days"""
    s, p = series.lower().strip(), pair.lower().strip()
    if s in ("spot", "funding"):
        return _call(f"/oracle/history/{s}/{p}")
    if s in ("mssi", "msti"):
        return _call(f"/oracle/history/index/{s}")
    if s in ("msxi", "msvi"):
        return _call(f"/oracle/history/index/{s}/{p.replace('/', '')}")
    return f"Unknown series '{series}'. Use spot, funding, msxi, msvi, mssi or msti."


# ── Weather and marine ───────────────────────────────────────────────────────

@tool
def get_mycelia_weather(lat: str, lon: str, metric: str = "wrsi", window: str = "30d") -> str:
    """Weather risk index at GPS coordinates: temperature, precipitation and severe
    weather for location-based risk. Example: lat='37.77', lon='-122.41'."""
    return _call(f"/oracle/weather/{lat}/{lon}/{metric}/{window}")


@tool
def get_mycelia_marine(lat: str = "", lon: str = "", mmsi: str = "", route: str = "") -> str:
    """Sea state and vessel tracking.

    lat and lon      real-time sea state at those coordinates: wave height, period
                     and conditions
    mmsi             vessel position combined with sea state, from AIS
    route='summary'  wave conditions along a shipping route
    route='forecast' multi-waypoint sea state prediction"""
    # The route KEYS are templates (/oracle/marine/vessel/:mmsi). Passing a key
    # straight to _call put the literal colon in the URL, so vessel and seastate
    # never worked. _known matches the template; the request must carry the
    # FILLED path.
    if mmsi:
        return _call(f"/oracle/marine/vessel/{mmsi.strip()}")
    r = route.lower().strip()
    if r == "summary":
        return _call("/oracle/marine/route/summary")
    if r == "forecast":
        return _call("/oracle/marine/voyage/forecast")
    if lat and lon:
        return _call(f"/oracle/marine/{lat.strip()}/{lon.strip()}/seastate")
    return "Provide lat and lon, or mmsi, or route='summary'/'forecast'."


# ── DLC oracle ───────────────────────────────────────────────────────────────

@tool
def get_mycelia_dlc_info(kind: str = "threshold") -> str:
    """Information about the Discreet Log Contract oracle. kind: threshold (above
    or below a price), enum (enumerated outcomes) or numeric (digit decomposition
    for price ranges).

    NOTE: registering a DLC event costs and CREATES an on-chain commitment --
    it is not a read. This tool describes the endpoint; registration is deliberately
    not exposed as an agent-callable tool."""
    k = kind.lower().strip()
    path = f"/dlc/oracle/{k}"
    if path not in ROUTES:
        return "Unknown DLC kind. Use threshold, enum or numeric."
    return (f"{path}  ({get_price_usd(path)})\n{describe(path)}\n\n"
            f"Registration is a POST that creates a commitment. See "
            f"https://myceliasignal.com/docs/dlc")
