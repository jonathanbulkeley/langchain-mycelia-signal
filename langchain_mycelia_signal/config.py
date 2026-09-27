"""Route catalogue for langchain-mycelia-signal.

GENERATED from x402-proxy-ts/src/routes.ts. Regenerate with
scripts/gen_langchain_config.py after any route change; do not hand-edit.

WHY GENERATED. An audit on 2026-09-26 found econ and commodity calls quoted at
$0.10 when routes.ts charges $1.00 -- a 10x understatement of the price an agent is
told BEFORE it pays -- plus a synopsis price that was wrong by 4x, a triple-duplicated
tool in as_list(), and an endpoint count that had drifted. Every one was a hand-copied
value. routes.ts is what the proxy charges; anything else that states a price is a
claim about it, and claims rot.

214 priced routes across 36 families.
"""

# THE version. pyproject reads it from here via hatch's dynamic version, and
# __init__ and client import it. It lived in two files until 2026-09-27, which is
# the same drift that put four different endpoint counts in four documents.
__version__ = "3.0.1"

API_BASE_URL = "https://api.myceliasignal.com"
USER_AGENT = f"langchain-mycelia-signal/{__version__} (+https://myceliasignal.com)"

# path -> {"price": "0.01", "desc": "..."} exactly as routes.ts declares it.
ROUTES: dict[str, dict[str, str]] = {
    "/dlc/oracle/enum": {
        "desc": "Discreet log contract enum oracle — Bitcoin DLC attestation for enumerated outcome events",
        "price": "7.00"
    },
    "/dlc/oracle/numeric": {
        "desc": "Discreet log contract numeric oracle — Bitcoin DLC digit decomposition attestation",
        "price": "7.00"
    },
    "/dlc/oracle/threshold": {
        "desc": "Discreet log contract threshold oracle — Bitcoin DLC attestation for above/below price events",
        "price": "7.00"
    },
    "/oracle/basis/btc/usd": {
        "desc": "BTC/USD spot-futures basis and annualized carry across 5 exchanges",
        "price": "0.02"
    },
    "/oracle/basis/eth/usd": {
        "desc": "Ethereum spot-futures basis and annualized carry — cross-venue arbitrage signal",
        "price": "0.02"
    },
    "/oracle/basis/sol/usd": {
        "desc": "Solana spot-futures basis and annualized carry — cross-venue arbitrage signal",
        "price": "0.02"
    },
    "/oracle/breadth/equity": {
        "desc": "MSBI — Breadth Index. Sector participation (% above 20DMA), RSP/SPY breadth momentum",
        "price": "0.05"
    },
    "/oracle/compute/all": {
        "desc": "GPU cloud compute pricing across all providers — H100, A100, RTX 4090, L40S hourly rates",
        "price": "0.05"
    },
    "/oracle/compute/best/a100_sxm": {
        "desc": "Cheapest A100 SXM GPU rental — best hourly rate across major cloud providers",
        "price": "0.05"
    },
    "/oracle/compute/best/h100_sxm": {
        "desc": "Cheapest H100 SXM GPU rental — best hourly rate across Azure, GCP, AWS, Lambda, CoreWeave",
        "price": "0.05"
    },
    "/oracle/compute/best/h200": {
        "desc": "Cheapest H200 GPU rental — best hourly rate for large model inference",
        "price": "0.05"
    },
    "/oracle/compute/best/l40s": {
        "desc": "Cheapest L40S GPU rental — best hourly rate for inference-optimized NVIDIA GPU",
        "price": "0.05"
    },
    "/oracle/compute/best/rtx_4090": {
        "desc": "Cheapest RTX 4090 GPU rental — best hourly rate for cost-efficient inference",
        "price": "0.05"
    },
    "/oracle/compute/compare": {
        "desc": "GPU model comparison — cheapest per model across all sources",
        "price": "0.05"
    },
    "/oracle/contagion/market": {
        "desc": "MSTI crypto-TradFi contagion index — measures correlation spillover between crypto and traditional financial markets",
        "price": "0.05"
    },
    "/oracle/cot/btc": {
        "desc": "Bitcoin CME commitment of traders — institutional futures positioning from CFTC",
        "price": "1.00"
    },
    "/oracle/defi/metrics": {
        "desc": "DeFi protocol metrics — TVL, avg supply APR, utilization for Aave, Compound, Morpho, Spark, Sky",
        "price": "0.05"
    },
    "/oracle/defi/metrics/aave": {
        "desc": "Aave V3 protocol metrics — TVL, avg supply APR across all chains",
        "price": "0.05"
    },
    "/oracle/defi/metrics/compound": {
        "desc": "Compound V3 protocol metrics — TVL, utilization, avg supply APR",
        "price": "0.05"
    },
    "/oracle/defi/metrics/morpho": {
        "desc": "Morpho protocol metrics — TVL, avg supply APR across all markets",
        "price": "0.05"
    },
    "/oracle/defi/yield/:protocol/:chain/:asset": {
        "desc": "Supply and borrow APR for a single protocol/chain/asset triple — on-chain sourced, Ed25519 signed",
        "price": "0.05"
    },
    "/oracle/defi/yield/all": {
        "desc": "All DeFi lending rates — 9 protocols across 7 chains, 19 deployments, read on-chain",
        "price": "0.05"
    },
    "/oracle/defi/yield/best/dai": {
        "desc": "Best DAI supply yield across all protocols and chains",
        "price": "0.05"
    },
    "/oracle/defi/yield/best/usdc": {
        "desc": "Best USDC supply yield across all protocols and chains",
        "price": "0.05"
    },
    "/oracle/defi/yield/best/usdt": {
        "desc": "Best USDT supply yield across all protocols and chains",
        "price": "0.05"
    },
    "/oracle/defi/yield/best/wbtc": {
        "desc": "Best WBTC supply yield across all protocols and chains",
        "price": "0.05"
    },
    "/oracle/defi/yield/best/weth": {
        "desc": "Best WETH supply yield across all protocols and chains",
        "price": "0.05"
    },
    "/oracle/defi/yield/compare": {
        "desc": "USDC rate comparison across all DeFi lending protocols",
        "price": "0.05"
    },
    "/oracle/econ/calendar": {
        "desc": "Economic calendar — next 30 days, high/medium impact events for US, EU, GB, JP, CN",
        "price": "0.05"
    },
    "/oracle/econ/calendar/country/eu": {
        "desc": "EU economic events — next 30 days of Eurozone macro releases",
        "price": "0.05"
    },
    "/oracle/econ/calendar/country/us": {
        "desc": "US economic events — next 30 days of US macro releases",
        "price": "0.05"
    },
    "/oracle/econ/calendar/fomc": {
        "desc": "FOMC meeting schedule — upcoming Federal Reserve rate decision dates",
        "price": "0.05"
    },
    "/oracle/econ/calendar/today": {
        "desc": "Today's economic events — all high/medium impact releases scheduled for today",
        "price": "0.05"
    },
    "/oracle/econ/commodities/brent": {
        "desc": "Brent crude oil spot price — international benchmark for global energy markets and macro hedging",
        "price": "1.00"
    },
    "/oracle/econ/commodities/copper": {
        "desc": "Copper spot price — industrial metal bellwether for global growth and manufacturing activity",
        "price": "1.00"
    },
    "/oracle/econ/commodities/dxy": {
        "desc": "DXY US dollar index — broad USD strength measure for FX positioning and commodity hedging",
        "price": "1.00"
    },
    "/oracle/econ/commodities/natgas": {
        "desc": "Natural gas spot price — Henry Hub rate for energy market exposure and commodity inflation",
        "price": "1.00"
    },
    "/oracle/econ/commodities/wti": {
        "desc": "WTI crude oil spot price — West Texas Intermediate for energy trading and inflation modeling",
        "price": "1.00"
    },
    "/oracle/econ/eu/employment": {
        "desc": "EU employment change — eurozone jobs data for ECB policy and EUR macro exposure",
        "price": "1.00"
    },
    "/oracle/econ/eu/gdp": {
        "desc": "EU GDP implicit price deflator (2015=100) — Eurostat namq_10_gdp PD15_EUR",
        "price": "1.00"
    },
    "/oracle/econ/eu/hicp": {
        "desc": "EU HICP headline inflation — European Central Bank target for EUR rate trading",
        "price": "1.00"
    },
    "/oracle/econ/eu/hicp_core": {
        "desc": "EU Core HICP ex energy and food — ECB underlying inflation for rate policy forecasting",
        "price": "1.00"
    },
    "/oracle/econ/eu/hicp_services": {
        "desc": "EU Services HICP — sticky services inflation watched by ECB for rate decisions",
        "price": "1.00"
    },
    "/oracle/econ/eu/unrate": {
        "desc": "EU unemployment rate — eurozone labor market data for ECB policy and EUR macro trading",
        "price": "1.00"
    },
    "/oracle/econ/expiry/btc": {
        "desc": "BTC options expiry dates — next 8 Deribit expiries tagged daily/weekly/monthly/quarterly",
        "price": "0.05"
    },
    "/oracle/econ/expiry/eth": {
        "desc": "ETH options expiry dates — next 8 Deribit expiries tagged daily/weekly/monthly/quarterly",
        "price": "0.05"
    },
    "/oracle/econ/surprises": {
        "desc": "Macro surprise index — last 20 releases with actual vs estimate deviation. NOTE: currently 503, Finnhub dead",
        "price": "0.10"
    },
    "/oracle/econ/us/cpi": {
        "desc": "US Consumer Price Index — latest CPI inflation reading for Fed policy and macro trading",
        "price": "1.00"
    },
    "/oracle/econ/us/cpi_core": {
        "desc": "US Core CPI ex food and energy — key Fed inflation target for interest rate decisions",
        "price": "1.00"
    },
    "/oracle/econ/us/fedfunds": {
        "desc": "US Federal Reserve funds rate — current FOMC target for interest rate and bond trading",
        "price": "1.00"
    },
    "/oracle/econ/us/gdp": {
        "desc": "US real GDP level — FRED GDPC1, billions of chained 2017 dollars, quarterly",
        "price": "1.00"
    },
    "/oracle/econ/us/nfp": {
        "desc": "US Non-Farm Payrolls — monthly jobs report, most market-moving macro release for USD pairs",
        "price": "1.00"
    },
    "/oracle/econ/us/pce": {
        "desc": "US PCE inflation — Fed preferred inflation measure for rate policy forecasting",
        "price": "1.00"
    },
    "/oracle/econ/us/unrate": {
        "desc": "US unemployment rate — latest BLS jobs market reading for Fed dual mandate tracking",
        "price": "1.00"
    },
    "/oracle/econ/us/yield_curve": {
        "desc": "US Treasury yield curve 10Y-2Y spread — inversion signal for recession risk and rate regime",
        "price": "1.00"
    },
    "/oracle/funding/btc/usd": {
        "desc": "BTC/USD funding rate composite — 5 exchanges, OI-weighted + median, predicted rate, regime",
        "price": "0.05"
    },
    "/oracle/funding/btc/usd/term-structure": {
        "desc": "BTC perpetual-vs-futures funding term structure — carry curve and contango/backwardation regime",
        "price": "0.05"
    },
    "/oracle/funding/eth/usd": {
        "desc": "Ethereum perpetual funding rate — cross-exchange aggregated funding for carry trades",
        "price": "0.05"
    },
    "/oracle/funding/eth/usd/term-structure": {
        "desc": "ETH funding term structure — carry curve across maturities",
        "price": "0.05"
    },
    "/oracle/funding/sol/usd": {
        "desc": "Solana perpetual funding rate — cross-exchange aggregated funding for carry trades",
        "price": "0.05"
    },
    "/oracle/funding/sol/usd/term-structure": {
        "desc": "SOL funding term structure — carry curve and regime across maturities",
        "price": "0.05"
    },
    "/oracle/gas/arbitrum": {
        "desc": "Arbitrum L2 gas price — current transaction fee for Arbitrum One network",
        "price": "0.01"
    },
    "/oracle/gas/base": {
        "desc": "Base L2 gas price — current transaction fee for Coinbase Base network in Gwei",
        "price": "0.01"
    },
    "/oracle/gas/ethereum": {
        "desc": "Ethereum mainnet gas price — current base fee and priority fee in Gwei",
        "price": "0.01"
    },
    "/oracle/gas/index": {
        "desc": "Cross-chain gas index — normalized transaction cost across Ethereum, Base, Arbitrum, Polygon and Solana",
        "price": "0.05"
    },
    "/oracle/gas/optimism": {
        "desc": "Optimism L2 gas price — current transaction fee for Optimism network",
        "price": "0.01"
    },
    "/oracle/gas/polygon": {
        "desc": "Polygon gas price — current transaction fee for Polygon PoS network",
        "price": "0.01"
    },
    "/oracle/gas/solana": {
        "desc": "Solana transaction fee — current lamports per signature",
        "price": "0.01"
    },
    "/oracle/greeks/btc/usd": {
        "desc": "BTC options Greeks — cross-exchange consensus delta/gamma/theta/vega from 2130+ options",
        "price": "0.05"
    },
    "/oracle/greeks/eth/usd": {
        "desc": "ETH options Greeks — cross-exchange consensus from 1822+ options across 3 exchanges",
        "price": "0.05"
    },
    "/oracle/greeks/sol/usd": {
        "desc": "SOL options Greeks — Bybit native Greeks for 246+ options",
        "price": "0.05"
    },
    "/oracle/history/funding/btc/usd": {
        "desc": "BTC funding rate history — per-exchange rates, 18 days, batch Ed25519 signed",
        "price": "0.05"
    },
    "/oracle/history/funding/eth/usd": {
        "desc": "ETH funding rate history — per-exchange rates, 18 days",
        "price": "0.05"
    },
    "/oracle/history/index/mssi": {
        "desc": "MSSI stress index history — 56 days, per-row original signatures",
        "price": "0.10"
    },
    "/oracle/history/index/msti": {
        "desc": "MSTI contagion index history — 56 days with per-row Ed25519 signatures",
        "price": "0.10"
    },
    "/oracle/history/index/msvi/btcusd": {
        "desc": "MSVI volatility index history — 63 days, per-row original signatures",
        "price": "0.10"
    },
    "/oracle/history/index/msvi/ethusd": {
        "desc": "MSVI volatility index history for ETH — 63 days, per-row original signatures",
        "price": "0.10"
    },
    "/oracle/history/index/msxi/btcusd": {
        "desc": "MSXI sentiment index history — 60 days, per-row original signatures",
        "price": "0.10"
    },
    "/oracle/history/index/msxi/ethusd": {
        "desc": "MSXI sentiment index history for ETH — 60 days, per-row original signatures",
        "price": "0.10"
    },
    "/oracle/history/spot/btc/usd": {
        "desc": "BTC spot price history — signed OHLCV, 1m/5m/1h/4h/1d intervals, up to 60 days",
        "price": "0.05"
    },
    "/oracle/history/spot/eth/usd": {
        "desc": "ETH spot price history — signed OHLCV, 1m/5m/1h/4h/1d intervals, up to 60 days",
        "price": "0.05"
    },
    "/oracle/inference/all": {
        "desc": "All LLM inference pricing — 6 providers, 26 models, normalized to $/M tokens",
        "price": "0.02"
    },
    "/oracle/inference/anthropic/pricing": {
        "desc": "Anthropic Claude model pricing — input/output $/M tokens, context windows",
        "price": "0.02"
    },
    "/oracle/inference/cerebras/pricing": {
        "desc": "Cerebras model pricing — input/output $/M tokens, context windows",
        "price": "0.02"
    },
    "/oracle/inference/compare": {
        "desc": "Cheapest LLM per tier (frontier/efficient/fast/reasoning) across all providers",
        "price": "0.02"
    },
    "/oracle/inference/compare/task/chat": {
        "desc": "Best LLM for chat tasks — cheapest efficient/fast tier model",
        "price": "0.02"
    },
    "/oracle/inference/compare/task/long_context": {
        "desc": "Best LLM for long-context tasks — largest context window",
        "price": "0.02"
    },
    "/oracle/inference/compare/task/reasoning": {
        "desc": "Best LLM for reasoning tasks — cheapest reasoning tier model",
        "price": "0.02"
    },
    "/oracle/inference/fireworks/pricing": {
        "desc": "Fireworks AI model pricing — input/output $/M tokens, context windows",
        "price": "0.02"
    },
    "/oracle/inference/groq/pricing": {
        "desc": "Groq model pricing — input/output $/M tokens, context windows",
        "price": "0.02"
    },
    "/oracle/inference/openai/pricing": {
        "desc": "OpenAI model pricing — input/output $/M tokens, context windows",
        "price": "0.02"
    },
    "/oracle/inference/together/pricing": {
        "desc": "Together AI model pricing — input/output $/M tokens, context windows",
        "price": "0.02"
    },
    "/oracle/instruments/btc/options": {
        "desc": "BTC options instrument discovery — 2002+ contracts, 106 strikes, 11 expiries across 3 exchanges",
        "price": "0.03"
    },
    "/oracle/instruments/eth/options": {
        "desc": "ETH options instrument discovery across 3 exchanges",
        "price": "0.03"
    },
    "/oracle/instruments/sol/options": {
        "desc": "Solana options instruments — full contract listing across strikes and expiries",
        "price": "0.03"
    },
    "/oracle/intel/consensus": {
        "desc": "Regime Consensus — aggregates BTC/ETH/SOL perp, TradFi, MSSI, MSTI, Macro Risk into alignment score",
        "price": "0.50"
    },
    "/oracle/intel/defi/opportunity": {
        "desc": "Risk-adjusted DeFi yield — stress and contagion penalized APR ranking across 15+ protocols",
        "price": "0.75"
    },
    "/oracle/intel/divergence": {
        "desc": "Cross-Asset Divergence — disagreement between crypto and TradFi regimes. NONE/LOW/MODERATE/HIGH/EXTREME",
        "price": "0.50"
    },
    "/oracle/intel/macro/risk": {
        "desc": "Cross-domain macro risk — MSSI + MSTI + econ calendar. risk_score 0-100",
        "price": "1.00"
    },
    "/oracle/intel/perp/setup": {
        "desc": "Scans BTC+ETH+SOL perp regimes simultaneously with signal_alignment, edge and invalidation",
        "price": "1.00"
    },
    "/oracle/intel/prediction/divergence": {
        "desc": "Cross-venue prediction market divergence — Kalshi vs Polymarket spread with significance",
        "price": "1.00"
    },
    "/oracle/intel/regime/change": {
        "desc": "Detects perp regime transitions vs 2h ago for BTC, ETH, SOL with from_regime and to_regime",
        "price": "0.50"
    },
    "/oracle/intel/regime/persistence": {
        "desc": "Regime Persistence — historical context for current perp regime duration",
        "price": "0.15"
    },
    "/oracle/iv-surface/btc/usd": {
        "desc": "BTC multi-exchange IV surface — per-strike IV from 3 exchanges with divergence detection",
        "price": "0.05"
    },
    "/oracle/iv-surface/eth/usd": {
        "desc": "ETH multi-exchange IV surface with divergence detection",
        "price": "0.05"
    },
    "/oracle/iv-surface/sol/usd": {
        "desc": "Solana implied volatility surface — full strike and expiry IV grid",
        "price": "0.05"
    },
    "/oracle/iv/btc/usd": {
        "desc": "BTC implied volatility surface — ATM IV, 25-delta skew, term structure from 870+ Deribit options",
        "price": "0.03"
    },
    "/oracle/iv/eth/usd": {
        "desc": "ETH implied volatility surface — ATM IV, skew, term structure from 690+ Deribit options",
        "price": "0.03"
    },
    "/oracle/leadership/equity": {
        "desc": "MSLI — Leadership Index. Growth vs Value, Tech vs Market, Small vs Large, Offensive vs Defensive",
        "price": "0.05"
    },
    "/oracle/liq-flow/btc": {
        "desc": "BTC liquidation flow — 1h/4h/24h windows, long/short breakdown, dominant side, largest event",
        "price": "0.05"
    },
    "/oracle/liq-flow/eth": {
        "desc": "ETH liquidation flow — 1h/4h/24h windows, long/short breakdown, dominant side, largest event",
        "price": "0.05"
    },
    "/oracle/liq-flow/sol": {
        "desc": "SOL liquidation flow — 1h/4h/24h windows, long/short breakdown, dominant side, largest event",
        "price": "0.05"
    },
    "/oracle/liquidations/btc/usd": {
        "desc": "BTC liquidation flow — real-time across 4 exchanges with imbalance and clustering",
        "price": "0.03"
    },
    "/oracle/liquidations/eth/usd": {
        "desc": "ETH liquidation flow — real-time across 4 exchanges",
        "price": "0.03"
    },
    "/oracle/liquidations/sol/usd": {
        "desc": "SOL liquidation flow — real-time across 4 exchanges",
        "price": "0.03"
    },
    "/oracle/marine/:lat/:lon/seastate": {
        "desc": "Real-time sea state at GPS coordinates — wave height, period and conditions",
        "price": "0.10"
    },
    "/oracle/marine/route/summary": {
        "desc": "Voyage route sea state summary — wave conditions along shipping route",
        "price": "0.20"
    },
    "/oracle/marine/vessel/:mmsi": {
        "desc": "Vessel position and sea state — AIS ship tracking combined with wave conditions for maritime risk",
        "price": "0.50"
    },
    "/oracle/marine/voyage/forecast": {
        "desc": "Voyage weather forecast — multi-waypoint sea state prediction for maritime risk management",
        "price": "0.50"
    },
    "/oracle/market/support/all/btc": {
        "desc": "BTC/USD union of pivot+density+round with cross-method corroboration",
        "price": "0.15"
    },
    "/oracle/market/support/all/eth": {
        "desc": "ETH/USD union of pivot+density+round with cross-method corroboration",
        "price": "0.15"
    },
    "/oracle/market/support/all/sol": {
        "desc": "SOL/USD union of pivot+density+round with cross-method corroboration",
        "price": "0.15"
    },
    "/oracle/market/support/density/btc": {
        "desc": "BTC/USD dwell levels (where price spent time / acceptance)",
        "price": "0.15"
    },
    "/oracle/market/support/density/eth": {
        "desc": "ETH/USD dwell levels (where price spent time / acceptance)",
        "price": "0.15"
    },
    "/oracle/market/support/density/sol": {
        "desc": "SOL/USD dwell levels (where price spent time / acceptance)",
        "price": "0.15"
    },
    "/oracle/market/support/pivot/btc": {
        "desc": "BTC/USD swing-pivot levels (where price reversed), up to 120d of spot history",
        "price": "0.15"
    },
    "/oracle/market/support/pivot/eth": {
        "desc": "ETH/USD swing-pivot levels (where price reversed), up to 120d of spot history",
        "price": "0.15"
    },
    "/oracle/market/support/pivot/sol": {
        "desc": "SOL/USD swing-pivot levels (where price reversed), up to 120d of spot history",
        "price": "0.15"
    },
    "/oracle/market/support/round/btc": {
        "desc": "BTC/USD psychological round-number levels",
        "price": "0.15"
    },
    "/oracle/market/support/round/eth": {
        "desc": "ETH/USD psychological round-number levels",
        "price": "0.15"
    },
    "/oracle/market/support/round/sol": {
        "desc": "SOL/USD psychological round-number levels",
        "price": "0.15"
    },
    "/oracle/oi/btc/usd": {
        "desc": "BTC/USD open interest across 5 exchanges with 1h/4h/24h deltas",
        "price": "0.01"
    },
    "/oracle/oi/eth/usd": {
        "desc": "Ethereum open interest across 5 exchanges — aggregated OI with 1h/4h/24h deltas",
        "price": "0.01"
    },
    "/oracle/oi/sol/usd": {
        "desc": "Solana open interest across 5 exchanges — aggregated OI with deltas",
        "price": "0.01"
    },
    "/oracle/orderbook/btc/usd": {
        "desc": "BTC order book imbalance — depth, spread, sweep cost across 5 exchanges",
        "price": "0.03"
    },
    "/oracle/orderbook/eth/usd": {
        "desc": "ETH order book imbalance — depth and spread across 5 exchanges",
        "price": "0.03"
    },
    "/oracle/perp/btc": {
        "desc": "BTC perp trading regime — 10-signal classification with bias, confidence, risk",
        "price": "0.15"
    },
    "/oracle/perp/eth": {
        "desc": "ETH perp trading regime — 10-signal classification with bias, confidence, risk",
        "price": "0.15"
    },
    "/oracle/perp/sol": {
        "desc": "SOL perp trading regime — 10-signal classification with bias, confidence, risk",
        "price": "0.15"
    },
    "/oracle/prediction/btc/price": {
        "desc": "BTC same-day price distribution from Polymarket — median, quantiles (p10-p90), entropy",
        "price": "0.25"
    },
    "/oracle/prediction/cpi": {
        "desc": "CPI month-over-month probability distribution from Kalshi — expected value, entropy",
        "price": "0.25"
    },
    "/oracle/prediction/cpi/:period_code": {
        "desc": "CPI month-over-month probability for a single period",
        "price": "0.25"
    },
    "/oracle/prediction/eth/price": {
        "desc": "ETH same-day price distribution from Polymarket — median, quantiles (p10-p90), entropy",
        "price": "0.25"
    },
    "/oracle/prediction/fed": {
        "desc": "Fed rate probability distribution — market-implied FOMC rate path from Kalshi + Polymarket",
        "price": "0.50"
    },
    "/oracle/prediction/fed/:meeting_code": {
        "desc": "Fed rate probability for a single FOMC meeting — implied rate, prob cut/hold/hike",
        "price": "0.50"
    },
    "/oracle/prediction/gdp": {
        "desc": "GDP annualized growth probability distribution from Kalshi — expected value, entropy",
        "price": "0.25"
    },
    "/oracle/prediction/gdp/:period_code": {
        "desc": "GDP annualized growth probability for a single period",
        "price": "0.25"
    },
    "/oracle/prediction/options/btc": {
        "desc": "BTC risk-neutral price distributions at 12 horizons via Breeden-Litzenberger from SVI surfaces",
        "price": "0.50"
    },
    "/oracle/prediction/options/eth": {
        "desc": "ETH risk-neutral price distributions at 12 horizons via Breeden-Litzenberger from SVI surfaces",
        "price": "0.50"
    },
    "/oracle/price/ada/usd": {
        "desc": "Real-time Cardano ADA price in USD, aggregated from multiple exchanges",
        "price": "0.01"
    },
    "/oracle/price/brl/usd": {
        "desc": "BRL/USD — live Brazilian real to US dollar from exchange order books (USDT/USD ÷ USDT/BRL), 24/7; prices DePix",
        "price": "0.01"
    },
    "/oracle/price/btc/eur": {
        "desc": "Real-time Bitcoin price in EUR, multi-exchange aggregated oracle for European markets",
        "price": "0.01"
    },
    "/oracle/price/btc/eur/vwap": {
        "desc": "Bitcoin volume-weighted average price in EUR for European market execution",
        "price": "0.02"
    },
    "/oracle/price/btc/jpy": {
        "desc": "Real-time Bitcoin price in JPY, multi-exchange aggregated oracle for Japanese markets",
        "price": "0.01"
    },
    "/oracle/price/btc/usd": {
        "desc": "Real-time Bitcoin price in USD, a median across 10 exchanges including Binance, Coinbase, Kraken and Bullish",
        "price": "0.01"
    },
    "/oracle/price/btc/usd/vwap": {
        "desc": "Bitcoin volume-weighted average price in USD for order execution and fair value benchmarking",
        "price": "0.02"
    },
    "/oracle/price/cad/jpy": {
        "desc": "CAD/JPY forex exchange rate — Canadian dollar to Japanese yen",
        "price": "0.01"
    },
    "/oracle/price/chf/cad": {
        "desc": "CHF/CAD forex exchange rate — Swiss franc to Canadian dollar",
        "price": "0.01"
    },
    "/oracle/price/chf/jpy": {
        "desc": "CHF/JPY forex exchange rate — Swiss franc to Japanese yen",
        "price": "0.01"
    },
    "/oracle/price/cny/cad": {
        "desc": "CNY/CAD forex exchange rate — Chinese yuan to Canadian dollar",
        "price": "0.01"
    },
    "/oracle/price/cny/jpy": {
        "desc": "CNY/JPY forex exchange rate — Chinese yuan to Japanese yen",
        "price": "0.01"
    },
    "/oracle/price/doge/usd": {
        "desc": "Real-time Dogecoin price in USD, aggregated from multiple exchanges",
        "price": "0.01"
    },
    "/oracle/price/eth/eur": {
        "desc": "Real-time Ethereum price in EUR, multi-exchange aggregated oracle for European markets",
        "price": "0.01"
    },
    "/oracle/price/eth/jpy": {
        "desc": "Real-time Ethereum price in JPY, multi-exchange aggregated oracle for Japanese markets",
        "price": "0.01"
    },
    "/oracle/price/eth/usd": {
        "desc": "Real-time Ethereum price in USD, a median across 6 exchanges including Coinbase, Kraken, Bitstamp and Bullish",
        "price": "0.01"
    },
    "/oracle/price/eth/usd/vwap": {
        "desc": "Ethereum volume-weighted average price in USD for order execution and fair value",
        "price": "0.02"
    },
    "/oracle/price/eur/cad": {
        "desc": "EUR/CAD forex exchange rate — euro to Canadian dollar",
        "price": "0.01"
    },
    "/oracle/price/eur/chf": {
        "desc": "EUR/CHF forex exchange rate — euro to Swiss franc safe-haven rate",
        "price": "0.01"
    },
    "/oracle/price/eur/cny": {
        "desc": "EUR/CNY forex exchange rate — euro to Chinese yuan",
        "price": "0.01"
    },
    "/oracle/price/eur/gbp": {
        "desc": "EUR/GBP forex exchange rate — euro to British pound sterling",
        "price": "0.01"
    },
    "/oracle/price/eur/jpy": {
        "desc": "EUR/JPY forex exchange rate — euro to Japanese yen cross rate",
        "price": "0.01"
    },
    "/oracle/price/eur/usd": {
        "desc": "EUR/USD forex exchange rate — real-time euro to US dollar for FX trading and settlement",
        "price": "0.01"
    },
    "/oracle/price/gbp/cad": {
        "desc": "GBP/CAD forex exchange rate — British pound to Canadian dollar",
        "price": "0.01"
    },
    "/oracle/price/gbp/chf": {
        "desc": "GBP/CHF forex exchange rate — British pound to Swiss franc",
        "price": "0.01"
    },
    "/oracle/price/gbp/cny": {
        "desc": "GBP/CNY forex exchange rate — British pound to Chinese yuan",
        "price": "0.01"
    },
    "/oracle/price/gbp/jpy": {
        "desc": "GBP/JPY forex exchange rate — British pound to Japanese yen",
        "price": "0.01"
    },
    "/oracle/price/gbp/usd": {
        "desc": "GBP/USD forex exchange rate — British pound to US dollar cable rate",
        "price": "0.01"
    },
    "/oracle/price/sol/eur": {
        "desc": "Real-time Solana price in EUR, aggregated from multiple exchanges",
        "price": "0.01"
    },
    "/oracle/price/sol/jpy": {
        "desc": "Real-time Solana price in JPY, aggregated from multiple exchanges",
        "price": "0.01"
    },
    "/oracle/price/sol/usd": {
        "desc": "Real-time Solana price in USD, aggregated from multiple exchanges",
        "price": "0.01"
    },
    "/oracle/price/usd/cad": {
        "desc": "USD/CAD forex exchange rate — US dollar to Canadian dollar loonie rate",
        "price": "0.01"
    },
    "/oracle/price/usd/chf": {
        "desc": "USD/CHF forex exchange rate — US dollar to Swiss franc safe-haven rate",
        "price": "0.01"
    },
    "/oracle/price/usd/cny": {
        "desc": "USD/CNY forex exchange rate — US dollar to Chinese yuan",
        "price": "0.01"
    },
    "/oracle/price/usd/jpy": {
        "desc": "USD/JPY forex exchange rate — US dollar to Japanese yen, major FX pair",
        "price": "0.01"
    },
    "/oracle/price/usdc/usd": {
        "desc": "USDC stablecoin peg monitor — real-time Circle USDC deviation from $1.00 USD",
        "price": "0.01"
    },
    "/oracle/price/usdt/eur": {
        "desc": "USDT/EUR derived rate for stablecoin exposure in European markets",
        "price": "0.01"
    },
    "/oracle/price/usdt/jpy": {
        "desc": "USDT/JPY derived rate for stablecoin exposure in Japanese markets",
        "price": "0.01"
    },
    "/oracle/price/usdt/usd": {
        "desc": "USDT stablecoin peg monitor — real-time Tether deviation from $1.00 USD",
        "price": "0.01"
    },
    "/oracle/price/xau/eur": {
        "desc": "Real-time gold spot price in EUR for European commodity exposure",
        "price": "0.01"
    },
    "/oracle/price/xau/jpy": {
        "desc": "Real-time gold spot price in JPY for Asian commodity markets",
        "price": "0.01"
    },
    "/oracle/price/xau/usd": {
        "desc": "Real-time gold spot price in USD for commodity trading and macro hedging",
        "price": "0.01"
    },
    "/oracle/price/xrp/usd": {
        "desc": "Real-time XRP price in USD, aggregated from multiple exchanges",
        "price": "0.01"
    },
    "/oracle/regime/equity": {
        "desc": "TradFi Regime — classifies equity market regime from MESI, MNVI and US yield curve",
        "price": "0.10"
    },
    "/oracle/regime/equity/composite": {
        "desc": "MSERC — Equity Regime Composite. 2D framework: Health vs Stress",
        "price": "0.10"
    },
    "/oracle/regime/liquidity": {
        "desc": "Liquidity Regime — classifies BTC liquidity from funding, OI, basis, liquidation flow, orderbook",
        "price": "0.10"
    },
    "/oracle/rotation/equity": {
        "desc": "MSRI — Rotation Index. 11-sector ETF momentum: Offensive + Cyclical vs Defensive",
        "price": "0.10"
    },
    "/oracle/sentiment/btc/usd": {
        "desc": "MSXI Bitcoin market sentiment index — funding rate, long/short ratio, open interest momentum and liquidation skew",
        "price": "0.05"
    },
    "/oracle/sentiment/eth/usd": {
        "desc": "MSXI Ethereum market sentiment index — funding rate, long/short ratio, open interest momentum and liquidation skew",
        "price": "0.05"
    },
    "/oracle/stress/equity": {
        "desc": "MESI — Mycelia Equity Stress Index. VIX, VVIX, IV/RV ratio, credit stress, DXY momentum. 0-100",
        "price": "0.05"
    },
    "/oracle/stress/market": {
        "desc": "MSSI market stress index — composite systemic risk signal across crypto, equity, credit and volatility markets",
        "price": "0.05"
    },
    "/oracle/svi/btc/usd": {
        "desc": "BTC SVI surface — Gatheral 2004 arbitrage-free IV parameterization",
        "price": "0.05"
    },
    "/oracle/svi/eth/usd": {
        "desc": "ETH SVI surface — arbitrage-free fitted IV across all expiries",
        "price": "0.05"
    },
    "/oracle/svi/sol/usd": {
        "desc": "Solana SVI volatility surface parameters — stochastic vol interpolation",
        "price": "0.05"
    },
    "/oracle/synopsis/btc": {
        "desc": "BTC market state synopsis — stress and contagion context plus BTC funding, OI, liq flow, regime",
        "price": "0.50"
    },
    "/oracle/synopsis/eth": {
        "desc": "ETH market state synopsis — stress and contagion context plus ETH funding, OI, liq flow, regime",
        "price": "0.50"
    },
    "/oracle/synopsis/market": {
        "desc": "Market state synopsis for BTC, ETH and SOL — stress, contagion, macro risk and per-currency detail",
        "price": "1.00"
    },
    "/oracle/synopsis/sol": {
        "desc": "SOL market state synopsis — stress and contagion context plus SOL funding, OI, liq flow, regime",
        "price": "0.50"
    },
    "/oracle/term-structure/btc/usd": {
        "desc": "BTC futures term structure — basis, annualized carry, contango/backwardation across 3 exchanges",
        "price": "0.05"
    },
    "/oracle/term-structure/eth/usd": {
        "desc": "ETH futures term structure — carry curve across Deribit, OKX, Bybit",
        "price": "0.05"
    },
    "/oracle/term-structure/sol/usd": {
        "desc": "Solana futures term structure — basis, annualized carry, contango/backwardation",
        "price": "0.05"
    },
    "/oracle/volatility/btc/usd": {
        "desc": "MSVI Bitcoin volatility index — composite of realized vol, implied vol, term structure, funding stress and put/call",
        "price": "0.05"
    },
    "/oracle/volatility/eth/usd": {
        "desc": "MSVI Ethereum volatility index — composite of realized vol, implied vol, term structure, funding stress and put/call",
        "price": "0.05"
    },
    "/oracle/volatility/nq/usd": {
        "desc": "MNVI — Mycelia NQ Volatility Index. NDX RV30, VIX term structure, vol beta, VVIX, NDX momentum",
        "price": "0.05"
    },
    "/oracle/weather/:lat/:lon/:metric/:window": {
        "desc": "Weather risk index at GPS coordinates — temperature, precipitation and severe weather",
        "price": "0.10"
    }
}


def route_key(path: str) -> str | None:
    """The ROUTES key covering a path, or None.

    A filled parameterised path -- /oracle/prediction/fed/2026-12 -- is not a key;
    the key is /oracle/prediction/fed/:meeting_code. THE ONE COPY of this matcher:
    tools.py and client.py both had their own, and two copies of a rule is how the
    402 notice came to quote "a fee" for every parameterised route while the tool
    that fetched it resolved correctly.
    """
    if path in ROUTES:
        return path
    for key in ROUTES:
        if ":" not in key:
            continue
        kp, pp = key.split("/"), path.split("/")
        if len(kp) == len(pp) and all(k.startswith(":") or k == p
                                      for k, p in zip(kp, pp)):
            return key
    return None


def price_for(path: str) -> str:
    """Price for a path, filled or templated. Prefer this to get_price_usd."""
    key = route_key(path)
    return get_price_usd(key) if key else ""


def get_price_usd(path: str) -> str:
    """The price for an EXACT route path.

    Returns "" for an unknown path rather than guessing. The previous implementation
    inferred a price from key-set membership, which is how econ calls came to be
    quoted at a tenth of what they cost: a key fell in the wrong set and nothing
    checked it against the route table.
    """
    meta = ROUTES.get(path)
    return f"${meta['price']}" if meta else ""


def describe(path: str) -> str:
    """The proxy's own description for a route, verbatim."""
    return (ROUTES.get(path) or {}).get("desc", "")


def url_for(path: str) -> str:
    return API_BASE_URL + path


def paths_under(prefix: str) -> list[str]:
    """Every known route beginning with prefix, sorted. Used by the tools to
    enumerate what they can serve without a second hand-written list."""
    return sorted(p for p in ROUTES if p.startswith(prefix))


def is_paid_mode() -> bool:
    import os
    return bool(os.environ.get("MYCELIA_WALLET_PRIVATE_KEY"))


def get_wallet_key() -> str:
    import os
    return os.environ.get("MYCELIA_WALLET_PRIVATE_KEY", "")


# Convenience groupings, derived from ROUTES rather than declared separately, so a
# new route in routes.ts appears here the moment this file is regenerated.
PRICE_PATHS = [p for p in paths_under("/oracle/price/") if not p.endswith("/vwap")]
VWAP_PATHS = [p for p in paths_under("/oracle/price/") if p.endswith("/vwap")]
ECON_PATHS = [p for p in paths_under("/oracle/econ/")
              if "/calendar" not in p and "/expiry" not in p and "surprises" not in p]
CALENDAR_PATHS = [p for p in paths_under("/oracle/econ/calendar")] + \
                 [p for p in paths_under("/oracle/econ/expiry")]
INTEL_PATHS = paths_under("/oracle/intel/")
SUPPORT_PATHS = paths_under("/oracle/market/support/")
PREDICTION_PATHS = paths_under("/oracle/prediction/")
HISTORY_PATHS = paths_under("/oracle/history/")
DEFI_PATHS = paths_under("/oracle/defi/")
COMPUTE_PATHS = paths_under("/oracle/compute/")
INFERENCE_PATHS = paths_under("/oracle/inference/")
GAS_PATHS = paths_under("/oracle/gas/")
DLC_PATHS = paths_under("/dlc/oracle/")

TOTAL_ROUTES = len(ROUTES)

# The generator writes this file; this asserts it wrote all of it. A truncated
# catalogue would silently shrink coverage and every missing route would read as
# "unknown route" rather than as a bug.
assert TOTAL_ROUTES == 214, f"config.py is truncated: {TOTAL_ROUTES} routes, expected 214"
