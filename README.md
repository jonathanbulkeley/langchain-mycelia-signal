# langchain-mycelia-signal

LangChain tools for [Mycelia Signal](https://myceliasignal.com) — cryptographically
signed oracle data with automatic [x402](https://x402.org) payment (USDC on Base).

**35 tools covering 213 of the API's 214 priced endpoints.** No API key, no account.

```bash
pip install langchain-mycelia-signal          # free tier
pip install 'langchain-mycelia-signal[paid]'  # + automatic x402 payment
```

---

## Quick start

```python
from langchain_mycelia_signal import MyceliaSignalTools

tools = MyceliaSignalTools().as_list()        # all 35
tools = MyceliaSignalTools().core()           # the six an agent usually needs
```

Paid routes answer with a payment notice until a wallet key is set:

```bash
export MYCELIA_WALLET_PRIVATE_KEY=0x...
```

Payment is then handled by the `x402` library: an unpaid call returns a challenge,
the library signs an EIP-3009 authorization and the request is retried. One
settlement per call.

---

## What these tools do — and do not

They **measure** current market state. **They do not forecast.**

Out-of-sample testing on 2026-09-25 put MSVI's 24-hour forward correlation with BTC
returns at **−0.287**, against +0.104 in the fitting window and −0.020 over the full
period. A sign flip between fitting and holdout is what a dead signal looks like. No
Mycelia index has evidence of predicting direction at any magnitude the data can
detect, and nothing here should be read as a trade recommendation.

What you get instead is a **current, signed, independently verifiable measurement**:
attested at the moment it was taken, checkable offline against a published key, and
the same number for every caller.

---

## The tools

| group | tools |
|---|---|
| Prices | `get_mycelia_price` (40 pairs), `get_mycelia_vwap` |
| Indices | `get_mycelia_index` (MSVI, MSXI, MSSI, MSTI), `get_mycelia_equity_index` (MESI, MNVI, MSLI, MSBI, MSERC, MSRI) |
| Derivatives | `get_mycelia_funding`, `get_mycelia_oi`, `get_mycelia_basis`, `get_mycelia_liquidations`, `get_mycelia_liq_flow`, `get_mycelia_orderbook` |
| Options | `get_mycelia_iv`, `get_mycelia_iv_surface`, `get_mycelia_svi`, `get_mycelia_greeks`, `get_mycelia_term_structure`, `get_mycelia_instruments` |
| Macro | `get_mycelia_econ`, `get_mycelia_econ_calendar`, `get_mycelia_expiry`, `get_mycelia_cot`, `get_mycelia_prediction` |
| Regimes | `get_mycelia_perp_regime`, `get_mycelia_regime`, `get_mycelia_intel`, `get_mycelia_synopsis`, `get_mycelia_support_resistance` |
| Data | `get_mycelia_defi_yield`, `get_mycelia_defi_metrics`, `get_mycelia_compute`, `get_mycelia_inference`, `get_mycelia_gas` |
| Other | `get_mycelia_history`, `get_mycelia_weather`, `get_mycelia_marine`, `get_mycelia_dlc_info` |

**Prices are not listed here on purpose.** They live in `config.ROUTES`, generated
from the proxy's own route table, and are surfaced at call time and in every payment
notice. Every price this project ever wrote into prose eventually went stale — one by
a factor of ten.

```python
from langchain_mycelia_signal import ROUTES, get_price_usd
get_price_usd("/oracle/econ/us/cpi")     # the price the proxy charges, always current
```

---

## Alternative: the MCP server

If your framework speaks Model Context Protocol you do not need this package:

```
https://api.myceliasignal.com/mcp
```

Streamable HTTP. Attach the URL as a custom connector; the tools arrive with their
own descriptions and prices and your agent's own wallet settles x402. This package
remains the right choice for LangChain agents and anywhere you want the tools as
Python callables.

---

## Upgrading from 2.x

**3.0.0 is a breaking change.**

- `get_mycelia_marine_seastate` → `get_mycelia_marine(lat=, lon=)`
- DLC *registration* tools removed. They POST a $7.00 on-chain commitment, which is
  not something an agent should be able to do by picking a tool. `get_mycelia_dlc_info`
  describes the endpoints instead.
- `get_mycelia_index` now takes `index=` and `pair=` rather than one tool per index.
- Several `intel` kinds renamed to match the MCP server (`perp_state`,
  `defi_yield_snapshot`); the old names still work.

**Fixed in 3.0.0:** economic and commodity calls were quoted at $0.10 against a real
$1.00; `as_list()` returned three tools twice; marine endpoints sent a literal `:mmsi`
in the URL and never worked; and paid mode signed a payload the facilitator could not
verify, so no payment from this package had ever settled.

---

MIT. Issues: https://github.com/jonathanbulkeley/langchain-mycelia-signal/issues
