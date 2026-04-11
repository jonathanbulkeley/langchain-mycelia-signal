"""
HTTP client for Mycelia Signal API.

Handles:
- Free endpoint requests (no payment)
- x402 payment flow (automatic USDC on Base payment)
- DLC oracle endpoints (free and paid)
- Response parsing and error handling
"""

import json
import time
from typing import Any

import httpx

from .config import get_endpoint, get_price_usd, get_wallet_key, is_paid_mode, API_BASE_URL

# Request timeout in seconds — cross-rate pairs (BTC/EUR etc.) take 6-7s
REQUEST_TIMEOUT = 30


def _parse_canonical(canonical: str) -> dict:
    """
    Parse canonical string per Oracle Attestation Spec v0.4.

    Price format:   v1|PRICE|PAIR|PRICE|CURRENCY|DECIMALS|TIMESTAMP|NONCE|SOURCES|METHOD
    Econ format:    v1|REGION|INDICATOR|VALUE|UNIT|...|NONCE
    """
    parts = canonical.split("|")
    if len(parts) < 4:
        return {"raw": canonical}

    result = {"version": parts[0], "type": parts[1]}

    if parts[1] == "PRICE":
        result.update({
            "pair":      parts[2] if len(parts) > 2 else "",
            "price":     parts[3] if len(parts) > 3 else "",
            "currency":  parts[4] if len(parts) > 4 else "",
            "decimals":  parts[5] if len(parts) > 5 else "",
            "timestamp": parts[6] if len(parts) > 6 else "",
            "nonce":     parts[7] if len(parts) > 7 else "",
            "sources":   parts[8].split(",") if len(parts) > 8 else [],
            "method":    parts[9] if len(parts) > 9 else "",
        })
    else:
        result.update({
            "indicator": parts[2] if len(parts) > 2 else "",
            "value":     parts[3] if len(parts) > 3 else "",
            "unit":      parts[4] if len(parts) > 4 else "",
        })

    return result


def _parse_response(data: dict) -> dict:
    """
    Parse oracle response into a structured dict.

    Paid responses contain a canonical string (spec v0.4) with all fields.
    Free/preview responses contain flat JSON fields directly.
    """
    canonical = data.get("canonical") or data.get("canonicalstring", "")
    if canonical:
        parsed = _parse_canonical(canonical)
        result = {
            "pair":      parsed.get("pair") or data.get("pair", ""),
            "price":     parsed.get("price") or data.get("price", ""),
            "currency":  parsed.get("currency") or data.get("currency", ""),
            "timestamp": parsed.get("timestamp") or data.get("timestamp", ""),
            "sources":   parsed.get("sources") or data.get("sources", []),
            "method":    parsed.get("method") or data.get("method", ""),
            "signed":    True,
            "signature": data.get("signature", ""),
            "pubkey":    data.get("pubkey", ""),
            "canonical": canonical,
        }
        return result

    return {
        "pair":      data.get("pair", ""),
        "price":     data.get("price", ""),
        "currency":  data.get("currency", ""),
        "timestamp": data.get("timestamp", ""),
        "sources":   data.get("sources", []),
        "method":    data.get("method", ""),
        "signed":    False,
    }


def _format_result(parsed: dict) -> str:
    """Format the parsed result as a clean string for LangChain to use."""
    sources = parsed.get("sources", [])
    sources_str = ",".join(sources) if isinstance(sources, list) else sources

    lines = [
        f"Pair:      {parsed['pair']}",
        f"Price:     {parsed['price']} {parsed['currency']}",
        f"Timestamp: {parsed['timestamp']}",
        f"Sources:   {sources_str}",
        f"Method:    {parsed['method']}",
        f"Signed:    {parsed['signed']}",
    ]
    if parsed.get("signed"):
        lines += [
            f"Signature: {parsed['signature']}",
            f"Pubkey:    {parsed['pubkey']}",
            f"Canonical: {parsed['canonical']}",
        ]
    return "\n".join(lines)


def _handle_x402_payment(payment_info: dict, wallet_key: str) -> dict | None:
    """
    Handle x402 payment flow.

    Constructs and signs an x402 payment header using the wallet private key,
    then returns the payment header dict to include in the retry request.

    Returns None if payment cannot be completed.
    """
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct

        account = Account.from_key(wallet_key)

        payment_required = payment_info.get("x402_payment_required", {})
        amount = payment_required.get("maxAmountRequired", "10000")
        to = payment_required.get("payTo", "")
        asset = payment_required.get("asset", "")
        chain_id = payment_required.get("extra", {}).get("chainId", "8453")

        payload = {
            "from":    account.address,
            "to":      to,
            "value":   amount,
            "asset":   asset,
            "chainId": chain_id,
            "nonce":   str(int(time.time())),
        }

        message = encode_defunct(text=json.dumps(payload, separators=(",", ":")))
        signed = account.sign_message(message)

        return {
            "X-PAYMENT": json.dumps({
                **payload,
                "signature": signed.signature.hex(),
            })
        }

    except ImportError:
        raise ImportError(
            "Paid mode requires eth_account. "
            "Install with: pip install langchain-mycelia-signal[paid]"
        )
    except Exception as e:
        raise RuntimeError(f"x402 payment failed: {e}") from e


def fetch_price(pair: str) -> str:
    """
    Fetch a price attestation from Mycelia Signal.

    In free mode: returns price data without cryptographic signature.
    In paid mode: automatically pays via x402 (USDC on Base),
                  returns fully signed attestation.
    """
    url = get_endpoint(pair)
    cost = get_price_usd(pair)
    wallet_key = get_wallet_key()
    paid = is_paid_mode()

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = client.get(url)

            if response.status_code == 200:
                data = response.json()
                parsed = _parse_response(data)
                return _format_result(parsed)

            if response.status_code == 402:
                if not paid:
                    return (
                        f"This endpoint requires payment ({cost} USDC per query on Base). "
                        f"Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments "
                        f"and receive cryptographically signed attestations. "
                        f"See: https://myceliasignal.com/docs/x402"
                    )

                payment_info = response.json()
                payment_headers = _handle_x402_payment(payment_info, wallet_key)

                if payment_headers is None:
                    return "Payment failed: could not construct x402 payment."

                retry = client.get(url, headers=payment_headers)
                if retry.status_code == 200:
                    data = retry.json()
                    parsed = _parse_response(data)
                    return _format_result(parsed)
                else:
                    return f"Payment accepted but request failed: HTTP {retry.status_code}"

            return f"API error: HTTP {response.status_code} — {response.text[:200]}"

        except httpx.TimeoutException:
            return f"Request timed out after {REQUEST_TIMEOUT}s. The API may be temporarily unavailable."
        except httpx.RequestError as e:
            return f"Network error: {e}"
        except Exception as e:
            return f"Unexpected error fetching {pair}: {e}"


# ── DLC ORACLE ───────────────────────────────────────────────────────────────

def fetch_dlc_free(endpoint: str) -> dict | None:
    """Fetch a free DLC endpoint (no payment required)."""
    url = API_BASE_URL + endpoint
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        try:
            r = client.get(url)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 425:
                return {"error": "not_yet_attested", "message": "Contract has not been attested yet."}
            return {"error": f"http_{r.status_code}", "message": r.text[:200]}
        except Exception as e:
            return {"error": "request_error", "message": str(e)}


def post_dlc_with_payment(endpoint: str, body: dict) -> dict:
    """
    POST to a paid DLC endpoint with automatic x402 payment.

    Falls back to unpaid attempt for preview endpoints.
    Returns the response dict or an error dict.
    """
    url = API_BASE_URL + endpoint
    wallet_key = get_wallet_key()
    headers = {"Content-Type": "application/json"}

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        try:
            r = client.post(url, json=body, headers=headers)

            if r.status_code == 200:
                return r.json()

            if r.status_code == 402:
                data = r.json()

                # Try x402 payment if wallet configured
                if wallet_key and data.get("x402"):
                    try:
                        payment_headers = _handle_x402_payment(data, wallet_key)
                        if payment_headers:
                            retry = client.post(url, json=body, headers={**headers, **payment_headers})
                            if retry.status_code == 200:
                                return retry.json()
                    except Exception as pay_err:
                        return {
                            "error": "payment_failed",
                            "message": str(pay_err),
                            "docs": data.get("docs", "https://myceliasignal.com/docs/dlc"),
                        }

                # No wallet — return 402 details with docs link
                return {
                    "error": "payment_required",
                    "accepts": data.get("accepts", ["L402", "x402"]),
                    "message": (
                        "DLC contract registration requires payment (10,000 sats or $7.00 USDC). "
                        "Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic payment."
                    ),
                    "docs": data.get("docs", "https://myceliasignal.com/docs/dlc"),
                }

            return {"error": f"http_{r.status_code}", "message": r.text[:200]}

        except httpx.TimeoutException:
            return {"error": "timeout", "message": f"Request timed out after {REQUEST_TIMEOUT}s."}
        except Exception as e:
            return {"error": "request_error", "message": str(e)}

def fetch_index(index_type: str, pair: str) -> str:
    """
    Fetch a market index (MSVI, MSXI, MSSI) from Mycelia Signal.
    Uses preview endpoint in free mode, paid endpoint with wallet key.
    """
    from .config import INDEX_ENDPOINTS, INDEX_PREVIEW_ENDPOINTS, API_BASE_URL
    key = f"{index_type}_{pair}"
    wallet_key = os.environ.get("MYCELIA_WALLET_PRIVATE_KEY", "").strip()

    if wallet_key:
        endpoint = INDEX_ENDPOINTS.get(key)
    else:
        endpoint = INDEX_PREVIEW_ENDPOINTS.get(key)

    if not endpoint:
        return f"Unknown index: {index_type} {pair}. Valid: MSVI/MSXI (BTCUSD/ETHUSD), MSSI (MARKET)."

    url = f"{API_BASE_URL}{endpoint}"
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            r = client.get(url)
            if r.status_code == 200:
                data = r.json()
                canonical = data.get("canonical", "")
                parts = canonical.split("|") if canonical else []
                value   = data.get("value", parts[4] if len(parts) > 4 else "?")
                regime  = data.get("regime", parts[7].replace("REGIME:", "") if len(parts) > 7 else "?")
                conf    = data.get("confidence", "?")
                sig     = data.get("signature", "")
                scope   = data.get("pair", data.get("scope", pair))
                lines = [
                    f"{index_type} {scope}: {value} — {regime}",
                    f"Confidence: {conf}",
                ]
                if len(parts) > 6:
                    lines.append(f"Components: {parts[6]}")
                if sig:
                    lines.append(f"Signature: {sig[:16]}... (Ed25519)")
                lines.append("Docs: https://myceliasignal.com/docs/indices/")
                return "\n".join(lines)

            if r.status_code == 402:
                return (
                    f"{index_type} {pair}: Payment required (500 sats / $0.05 USDC). "
                    "Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic payment. "
                    "Docs: https://myceliasignal.com/docs/indices/"
                )
            return f"Error {r.status_code}: {r.text[:200]}"
    except httpx.TimeoutException:
        return f"Timeout fetching {index_type} {pair}."
    except Exception as e:
        return f"Error: {e}"
