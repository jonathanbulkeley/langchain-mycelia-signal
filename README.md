# langchain-mycelia-signal

LangChain tools for [Mycelia Signal](https://myceliasignal.com) — cryptographically signed oracle data with automatic [x402](https://x402.org) (USDC on Base) payment.

117 endpoints across prices, indices, derivatives, weather, marine, gas, COT, and DLC contracts. No API keys. No accounts. Install and go.

---

## Installation

```bash
pip install langchain-mycelia-signal
```

For paid mode (signed attestations with automatic x402 payment):

```bash
pip install langchain-mycelia-signal[paid]
```

---

## Quick Start

```python
from langchain_mycelia_signal import MyceliaSignalTools
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

tools = MyceliaSignalTools().as_list()  # 17 tools covering 117 endpoints

llm = ChatOpenAI(model="gpt-4o")
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "What is the Bitcoin price?"})
result = executor.invoke({"input": "What's the crypto market stress level?"})
result = executor.invoke({"input": "Show me BTC funding rates across exchanges"})
```

---

## Free vs Paid Mode

### Free mode (default — no config needed)

Returns data without cryptographic signature. Data may be up to 5 minutes stale.

```python
tools = MyceliaSignalTools()
print(tools.mode)  # "free"
```

### Paid mode — signed attestations

Add your Base wallet private key to `.env`:

```
MYCELIA_WALLET_PRIVATE_KEY=0x...
```

Payment is handled automatically via x402 (USDC on Base). No code changes required.

```python
tools = MyceliaSignalTools()
print(tools.mode)  # "paid"
```

---

## Tools (15 total)

### `get_mycelia_price` — Prices, FX, Macro, Commodities

56 pairs across crypto spot, VWAP, precious metals, FX, US/EU economic indicators, and commodities.

```python
get_mycelia_price.invoke({"pair": "BTCUSD"})      # $0.01
get_mycelia_price.invoke({"pair": "EURUSD"})       # $0.01
get_mycelia_price.invoke({"pair": "XAUUSD"})       # $0.01
get_mycelia_price.invoke({"pair": "BTCUSD_VWAP"})  # $0.02
get_mycelia_price.invoke({"pair": "US_CPI"})       # $0.10
get_mycelia_price.invoke({"pair": "WTI"})          # $0.10
```

**Crypto:** BTCUSD, BTCEUR, BTCJPY, ETHUSD, ETHEUR, ETHJPY, SOLUSD, SOLEUR, SOLJPY, XRPUSD, ADAUSD, DOGEUSD, USDTUSD, USDCUSD
**VWAP:** BTCUSD_VWAP, BTCEUR_VWAP
**Metals:** XAUUSD, XAUEUR, XAUJPY
**FX:** EURUSD, EURJPY, EURGBP, EURCHF, EURCNY, EURCAD, GBPUSD, GBPJPY, GBPCHF, GBPCNY, GBPCAD, USDJPY, USDCHF, USDCNY, USDCAD, CHFJPY, CHFCAD, CNYJPY, CNYCAD, CADJPY
**US Econ:** US_CPI, US_CPI_CORE, US_UNRATE, US_NFP, US_FEDFUNDS, US_GDP, US_PCE, US_YIELD_CURVE
**EU Econ:** EU_HICP, EU_HICP_CORE, EU_HICP_SERVICES, EU_UNRATE, EU_GDP, EU_EMPLOYMENT
**Commodities:** WTI, BRENT, NATGAS, COPPER, DXY

### `get_mycelia_index` — Market Indices ($0.05)

Four proprietary indices computed from cross-exchange derivatives data (11 exchanges).

```python
get_mycelia_index.invoke({"index": "MSVI_BTC"})   # Volatility index
get_mycelia_index.invoke({"index": "MSXI_BTC"})   # Sentiment index (-100 to +100)
get_mycelia_index.invoke({"index": "MSSI"})        # Stress index (0-100)
get_mycelia_index.invoke({"index": "MSTI"})        # Crypto-TradFi contagion (0-100)
```

**Keys:** MSVI_BTC, MSVI_ETH, MSXI_BTC, MSXI_ETH, MSSI, MSTI

### `get_mycelia_funding` — Funding Rates ($0.05)

Cross-exchange perpetual funding rates from 11 venues with per-exchange breakdown.

```python
get_mycelia_funding.invoke({"currency": "BTC"})  # Composite + 11 exchange rates
get_mycelia_funding.invoke({"currency": "ETH"})
get_mycelia_funding.invoke({"currency": "SOL"})
```

### `get_mycelia_oi` — Open Interest ($0.01)

Cross-exchange open interest with 1h/4h/24h deltas.

```python
get_mycelia_oi.invoke({"currency": "BTC"})
```

### `get_mycelia_basis` — Basis/Carry ($0.02)

Per-exchange basis (mark vs index), annualized carry, regime (CONTANGO/BACKWARDATION/FLAT).

```python
get_mycelia_basis.invoke({"currency": "BTC"})
```

### `get_mycelia_weather` — Weather Oracle ($0.10)

ERA5 reanalysis data at any global coordinate. Used for parametric insurance.

```python
get_mycelia_weather.invoke({"lat": 37.77, "lon": -122.41, "metric": "wrsi", "window": "30d"})
get_mycelia_weather.invoke({"lat": 1.35, "lon": 103.82, "metric": "rainfall", "window": "7d"})
```

**Metrics:** wrsi, rainfall, temperature, wind

### `get_mycelia_marine_seastate` — Marine Oracle ($0.10)

Significant wave height, swell, and wind waves at any ocean coordinate.

```python
get_mycelia_marine_seastate.invoke({"lat": 25.76, "lon": -80.19})
```

### `get_mycelia_gas` — Gas Oracle ($0.01-$0.05)

Real-time gas prices for EVM and non-EVM chains.

```python
get_mycelia_gas.invoke({"chain": "ETHEREUM"})  # $0.01
get_mycelia_gas.invoke({"chain": "INDEX"})     # $0.05 — cross-chain comparison
```

**Chains:** ETHEREUM, BASE, ARBITRUM, POLYGON, OPTIMISM, SOLANA, INDEX



### `get_mycelia_compute` — GPU Compute Oracle ($0.05)

Real-time GPU pricing from AWS Spot, Vast.ai, RunPod, Akash. 80+ models normalized to $/GPU-hour.

```python
get_mycelia_compute.invoke({"query": "compare"})        # Cheapest per model
get_mycelia_compute.invoke({"query": "best_h100_sxm"})  # Best H100 SXM price
get_mycelia_compute.invoke({"query": "all"})            # All 575+ prices
get_mycelia_compute.invoke({"query": "catalogue"})      # Free — list models
```

**Queries:** all, compare, best_h100_sxm, best_a100_sxm, best_h200, best_rtx_4090, best_l40s, best_mi300x, catalogue
**Sources:** AWS Spot, Vast.ai, RunPod, Akash Network

### `get_mycelia_defi_yield` — DeFi Yield Oracle ($0.05)

On-chain lending rates from 7 protocols across 7 chains. Direct smart contract reads.

```python
get_mycelia_defi_yield.invoke({"query": "compare"})     # USDC rates across all protocols
get_mycelia_defi_yield.invoke({"query": "best_usdc"})   # Best USDC supply yield
get_mycelia_defi_yield.invoke({"query": "all"})         # All 40 rates
get_mycelia_defi_yield.invoke({"query": "catalogue"})   # Free — list protocols
```

**Queries:** all, compare, best_usdc, best_usdt, best_weth, best_dai, best_wbtc, catalogue
**Protocols:** Aave V3, Spark, Compound V3, Venus, Benqi, Moonwell
**Chains:** Ethereum, Base, Arbitrum, Polygon, Optimism, Avalanche, BNB

### `get_mycelia_cot` — COT Data ($1.00)

CFTC Commitments of Traders for Bitcoin CME futures. Weekly data, auto-refreshed Fridays.

```python
get_mycelia_cot.invoke({})
```

### DLC Oracle Tools

Register and query Bitcoin DLC (Discreet Log Contract) oracle events.

```python
# Free preview
dlc_threshold_preview.invoke({"pair": "BTCUSD", "strike": 90000, "direction": "above"})

# Paid registration ($7.00)
dlc_register_threshold.invoke({"pair": "BTCUSD", "strike": 90000, "direction": "above"})
dlc_register_enum.invoke({"outcomes": ["below_70k", "70k_80k", "above_80k"], "event_id": "my-event", "maturity": 1750000000})
dlc_register_numeric.invoke({"event_id": "my-numeric", "maturity": 1750000000})

# Free queries
dlc_get_attestation.invoke({"event_id": "BTCUSD-2026-04-07T00:00:00Z"})
dlc_list_announcements.invoke({})
```

---

## Tool Subsets

```python
from langchain_mycelia_signal import MyceliaSignalTools

tools = MyceliaSignalTools()
tools.as_list()            # All 17 tools
tools.price_tools()        # Just price/FX/macro
tools.index_tools()        # Just MSVI/MSXI/MSSI/MSTI
tools.derivatives_tools()  # Funding, OI, basis
tools.data_tools()         # Weather, marine, gas, DeFi yield, COT
tools.dlc_tools()          # All 6 DLC tools
```

---

## Links

- [Documentation](https://myceliasignal.com/docs)
- [x402 Integration Guide](https://myceliasignal.com/docs/x402)
- [Signature Verification](https://myceliasignal.com/docs/verification)
- [All Endpoints](https://myceliasignal.com/docs/endpoints)
- [GitHub](https://github.com/jonathanbulkeley/langchain-mycelia-signal)

---

## License

MIT
