# langchain-mycelia-signal

LangChain tools for [Mycelia Signal](https://myceliasignal.com) — cryptographically signed price oracles with automatic [x402](https://x402.org) (USDC on Base) payment.

56 endpoints across crypto, FX, precious metals, US/EU macro, and commodities. No API keys. No accounts. Install and go.

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

# Get tools
tools = MyceliaSignalTools().as_list()

# Build your agent
llm = ChatOpenAI(model="gpt-4o")
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Ask naturally
result = executor.invoke({"input": "What is the Bitcoin price right now?"})
result = executor.invoke({"input": "What is the current US CPI?"})
result = executor.invoke({"input": "What is the EUR/USD rate?"})
```

---

## Free vs Paid Mode

### Free mode (default — no config needed)

Returns price data without a cryptographic signature. Data may be up to 5 minutes stale.

```python
tools = MyceliaSignalTools()
print(tools.mode)  # "free"
```

### Paid mode — signed attestations

Add your Base wallet private key to your `.env`:

```
MYCELIA_WALLET_PRIVATE_KEY=0x...
```

The tool detects the key automatically and switches to paid endpoints. Payment is handled internally via x402. No code changes required.

```python
tools = MyceliaSignalTools()
print(tools.mode)  # "paid"
```

Signed responses include a cryptographic signature (Ed25519) verifiable against the published public key. See [verification docs](https://myceliasignal.com/docs/verification).

---

## Supported Pairs (56 endpoints)

### Crypto Spot — $0.01 per query
| Pair | Description |
|------|-------------|
| `BTCUSD` | Bitcoin / USD (median, 9 sources) |
| `BTCEUR` | Bitcoin / EUR (cross-rate + direct feeds) |
| `BTCJPY` | Bitcoin / JPY |
| `ETHUSD` | Ethereum / USD (median, 5 sources) |
| `ETHEUR` | Ethereum / EUR (hybrid) |
| `ETHJPY` | Ethereum / JPY |
| `SOLUSD` | Solana / USD (median, 9 sources) |
| `SOLEUR` | Solana / EUR (hybrid) |
| `SOLJPY` | Solana / JPY |
| `XRPUSD` | XRP / USD |
| `ADAUSD` | Cardano / USD |
| `DOGEUSD` | Dogecoin / USD |

### Crypto VWAP — $0.02 per query
| Pair | Description |
|------|-------------|
| `BTCUSD_VWAP` | Bitcoin / USD 5-min VWAP |
| `BTCEUR_VWAP` | Bitcoin / EUR 5-min VWAP |

### Precious Metals — $0.01 per query
| Pair | Description |
|------|-------------|
| `XAUUSD` | Gold / USD (median, 8 sources) |
| `XAUEUR` | Gold / EUR |
| `XAUJPY` | Gold / JPY |

### FX Pairs — $0.01 per query
| Pairs |
|-------|
| `EURUSD`, `EURJPY`, `EURGBP`, `EURCHF`, `EURCNY`, `EURCAD` |
| `GBPUSD`, `GBPJPY`, `GBPCHF`, `GBPCNY`, `GBPCAD` |
| `USDJPY`, `USDCHF`, `USDCNY`, `USDCAD` |
| `CHFJPY`, `CHFCAD`, `CNYJPY`, `CNYCAD`, `CADJPY` |

### US Economic Indicators — $0.10 per query
| Indicator | Description |
|-----------|-------------|
| `US_CPI` | Consumer Price Index (BLS) |
| `US_CPI_CORE` | CPI Core (ex food & energy) |
| `US_UNRATE` | Unemployment Rate |
| `US_NFP` | Nonfarm Payrolls |
| `US_FEDFUNDS` | Federal Funds Rate |
| `US_GDP` | GDP |
| `US_PCE` | PCE Price Index |
| `US_YIELD_CURVE` | 10Y-2Y Yield Spread |

### EU Economic Indicators — $0.10 per query
| Indicator | Description |
|-----------|-------------|
| `EU_HICP` | HICP Inflation (Eurostat) |
| `EU_HICP_CORE` | HICP Core |
| `EU_HICP_SERVICES` | HICP Services |
| `EU_UNRATE` | Unemployment Rate |
| `EU_GDP` | GDP |
| `EU_EMPLOYMENT` | Employment |

### Commodities — $0.10 per query
| Indicator | Description |
|-----------|-------------|
| `WTI` | WTI Crude Oil |
| `BRENT` | Brent Crude Oil |
| `NATGAS` | Henry Hub Natural Gas |
| `COPPER` | Copper |
| `DXY` | US Dollar Index |

---

## Example Response

**Free mode:**
```
Pair:      BTC/USD
Price:     84231.50 USD
Timestamp: 1741521600
Sources:   binance,binance_us,bitfinex,bitstamp,coinbase,gateio,gemini,kraken,okx
Method:    median
Signed:    False
```

**Paid mode:**
```
Pair:      BTCUSD
Price:     84231.50 USD
Timestamp: 1741521600
Sources:   binance,binance_us,bitfinex,bitstamp,coinbase,gateio,gemini,kraken,okx
Method:    median
Signed:    True
Signature: MEUCIQD...
Pubkey:    03c1955b8c543494c4ecd86d167105bcc7ca9a91b8e06cb9d6601f2f55a89abfbf
Canonical: v1|PRICE|BTCUSD|84231.50|USD|2|1741521600|562204|binance,binance_us,...|median
```

---

## Direct Tool Use

```python
from langchain_mycelia_signal import get_mycelia_price

result = get_mycelia_price.invoke({"pair": "BTCUSD"})
result = get_mycelia_price.invoke({"pair": "US_CPI"})
result = get_mycelia_price.invoke({"pair": "WTI"})
print(result)
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
