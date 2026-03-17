"""
HTTP client for Mycelia Signal API.

Handles:
- Free endpoint requests (no payment)
- x402 payment flow (automatic USDC on Base payment)
- Response parsing and error handling
"""

import json
import time
from typing import Any

import httpx

from .config import get_endpoint, get_price_usd, get_wallet_key, is_paid_mode

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
        # Econ/commodities: v1|REGION|INDICATOR|VALUE|UNIT|...|NONCE
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
    # Paid response — parse from canonical string
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

    # Free/preview response — flat JSON fields
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
        # Import eth_account here so it's optional for free-tier users
        from eth_account import Account
        from eth_account.messages import encode_defunct

        account = Account.from_key(wallet_key)

        # Extract payment details from the 402 response
        payment_required = payment_info.get("x402_payment_required", {})
        amount = payment_required.get("maxAmountRequired", "10000")  # atomic USDC units ($0.01)
        to = payment_required.get("payTo", "")
        asset = payment_required.get("asset", "")
        chain_id = payment_required.get("extra", {}).get("chainId", "8453")  # Base mainnet

        # Build payment authorization payload
        payload = {
            "from":    account.address,
            "to":      to,
            "value":   amount,
            "asset":   asset,
            "chainId": chain_id,
            "nonce":   str(int(time.time())),
        }

        # Sign the payment payload
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

            # 200 — success (free/preview endpoint or already paid)
            if response.status_code == 200:
                data = response.json()
                parsed = _parse_response(data)
                return _format_result(parsed)

            # 402 — payment required
            if response.status_code == 402:
                if not paid:
                    return (
                        f"This endpoint requires payment ({cost} USDC per query on Base). "
                        f"Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments "
                        f"and receive cryptographically signed attestations. "
                        f"See: https://myceliasignal.com/docs/x402"
                    )

                # Paid mode — handle x402 payment and retry
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
