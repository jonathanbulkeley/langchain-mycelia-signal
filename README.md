# langchain-mycelia-signal

LangChain tools for [Mycelia Signal](https://myceliasignal.com) — cryptographically signed price oracles with automatic [x402](https://x402.org) (USDC on Base) payment.

No API keys. No accounts. Install and go.

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
```

---

## Free vs Paid Mode

### Free mode (default — no config needed)

Returns price data without a cryptographic signature. Useful for testing and display.

```python
tools = MyceliaSignalTools()
print(tools.mode)  # "free"
```

### Paid mode — signed attestations

Add your Base wallet private key to your `.env`:

```
MYCELIA_WALLET_PRIVATE_KEY=0x...
```

The tool detects the key automatically and switches to paid endpoints. Payment is handled internally — `$0.001 USDC` per query on Base via x402. No code changes required.

```python
tools = MyceliaSignalTools()
print(tools.mode)  # "paid"
```

Signed responses include a cryptographic signature verifiable on-chain. See [verification docs](https://myceliasignal.com/docs/verification).

---

## Supported Pairs

| Pair | Description | Cost |
|------|-------------|------|
| `BTCUSD` | Bitcoin / USD spot (median, 9 sources) | $0.001 |
| `BTCUSD_VWAP` | Bitcoin / USD 5-min VWAP | $0.002 |
| `ETHUSD` | Ethereum / USD spot (median, 5 sources) | $0.001 |
| `EURUSD` | Euro / USD spot (median, 8 sources incl. central banks) | $0.001 |
| `XAUUSD` | Gold / USD spot (median, 8 sources) | $0.001 |
| `SOLUSD` | Solana / USD spot (median, 9 sources) | $0.001 |
| `BTCEUR` | Bitcoin / EUR spot (cross-rate + direct feeds) | $0.001 |
| `BTCEUR_VWAP` | Bitcoin / EUR 5-min VWAP | $0.002 |
| `ETHEUR` | Ethereum / EUR spot (hybrid) | $0.001 |
| `SOLEUR` | Solana / EUR spot (hybrid) | $0.001 |
| `XAUEUR` | Gold / EUR spot (cross-rate) | $0.001 |

---

## Example Response

**Free mode:**
```
Pair:      BTCUSD
Price:     84231.50 USD
Timestamp: 2026-03-05T12:00:00Z
Sources:   Coinbase,Kraken,Bitstamp,Gemini,Bitfinex,Binance,BinanceUS,OKX,Gate.io
Method:    median
Signed:    False
```

**Paid mode:**
```
Pair:      BTCUSD
Price:     84231.50 USD
Timestamp: 2026-03-05T12:00:00Z
Sources:   Coinbase,Kraken,Bitstamp,Gemini,Bitfinex,Binance,BinanceUS,OKX,Gate.io
Method:    median
Signed:    True
Signature: MEUCIQD...
Pubkey:    02abc...
Canonical: v1|BTCUSD|84231.50|USD|2|2026-03-05T12:00:00Z|abc123|Coinbase,...|median
```

---

## Direct Tool Use

```python
from langchain_mycelia_signal import get_mycelia_price

# Call directly
result = get_mycelia_price.invoke({"pair": "BTCUSD"})
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
