"""
HTTP client for Mycelia Signal API.

Handles:
- Free endpoint requests (preview, no payment)
- x402 v2 payment flow (automatic USDC on Base payment)
- DLC oracle endpoints (free and paid)
- Generic JSON endpoint fetching (indices, derivatives, weather, marine, gas, COT)
"""

import json
import time
from typing import Any

import httpx

from .config import API_BASE_URL, get_endpoint, get_price_usd, get_wallet_key, is_paid_mode

REQUEST_TIMEOUT = 30


def _parse_canonical(canonical: str) -> dict:
    """Parse canonical string per Oracle Attestation Spec v0.4."""
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
    """Parse oracle response into a structured dict."""
    canonical = data.get("canonical") or data.get("canonicalstring", "")
    if canonical:
        parsed = _parse_canonical(canonical)
        return {
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
    """Format the parsed result as a clean string for LangChain."""
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


def _handle_x402_payment(response: httpx.Response, wallet_key: str) -> dict | None:
    """
    Handle x402 v2 payment flow.

    Reads payment requirements from the PAYMENT-REQUIRED response header (v2 format),
    constructs and signs an EIP-712 payment, returns headers for the retry request.
    """
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct

        account = Account.from_key(wallet_key)

        # v2: requirements in payment-required header (base64 JSON)
        import base64
        pr_header = response.headers.get("payment-required", "")
        if pr_header:
            try:
                payment_required = json.loads(base64.b64decode(pr_header))
            except Exception:
                payment_required = response.json()
        else:
            payment_required = response.json()

        # Extract from v2 format (accepts array) or v1 fallback
        accepts = payment_required if isinstance(payment_required, list) else payment_required.get("accepts", [payment_required])
        # Find the x402/exact scheme
        req = None
        for a in accepts:
            if isinstance(a, dict) and a.get("scheme") in ("exact", None):
                req = a
                break
        if not req:
            req = accepts[0] if accepts else payment_required

        amount = req.get("amount", req.get("maxAmountRequired", "10000"))
        to = req.get("payTo", "")
        asset = req.get("asset", "")
        network = req.get("network", "eip155:8453")

        payload = {
            "scheme": "exact",
            "network": network,
            "asset": asset,
            "amount": str(amount),
            "payTo": to,
            "from": account.address,
            "nonce": str(int(time.time())),
            "accepted": req,
        }

        message = encode_defunct(text=json.dumps(payload, separators=(",", ":")))
        signed = account.sign_message(message)

        return {
            "PAYMENT-SIGNATURE": json.dumps({
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
    """Fetch a price attestation from Mycelia Signal."""
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
                        f"Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments. "
                        f"See: https://myceliasignal.com/docs/x402"
                    )

                payment_headers = _handle_x402_payment(response, wallet_key)
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
            return f"Request timed out after {REQUEST_TIMEOUT}s."
        except httpx.RequestError as e:
            return f"Network error: {e}"
        except Exception as e:
            return f"Unexpected error fetching {pair}: {e}"


def fetch_json(url: str) -> dict:
    """
    Generic JSON endpoint fetch with x402 payment support.

    Used by indices, derivatives, weather, marine, gas, COT tools.
    Returns the parsed JSON dict, or an error dict.
    """
    wallet_key = get_wallet_key()
    paid = is_paid_mode()

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = client.get(url)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 402:
                if not paid:
                    return {
                        "error": "payment_required",
                        "message": (
                            "Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments. "
                            "See: https://myceliasignal.com/docs/x402"
                        ),
                    }

                payment_headers = _handle_x402_payment(response, wallet_key)
                if payment_headers is None:
                    return {"error": "payment_failed", "message": "Could not construct x402 payment."}

                retry = client.get(url, headers=payment_headers)
                if retry.status_code == 200:
                    return retry.json()
                return {"error": f"http_{retry.status_code}", "message": retry.text[:200]}

            return {"error": f"http_{response.status_code}", "message": response.text[:200]}

        except httpx.TimeoutException:
            return {"error": "timeout", "message": f"Request timed out after {REQUEST_TIMEOUT}s."}
        except httpx.RequestError as e:
            return {"error": "network_error", "message": str(e)}
        except Exception as e:
            return {"error": "unexpected", "message": str(e)}


def _format_json(data: dict, title: str = "") -> str:
    """Format a JSON response dict as a readable string for LangChain."""
    if data.get("error"):
        return f"Error: {data.get('message', data['error'])}"

    lines = [title] if title else []
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for k2, v2 in v.items():
                lines.append(f"  {k2}: {v2}")
        elif isinstance(v, list):
            lines.append(f"{k}: {', '.join(str(i) for i in v[:10])}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


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
    """POST to a paid DLC endpoint with automatic x402 v2 payment."""
    url = API_BASE_URL + endpoint
    wallet_key = get_wallet_key()
    headers = {"Content-Type": "application/json"}

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        try:
            r = client.post(url, json=body, headers=headers)

            if r.status_code == 200:
                return r.json()

            if r.status_code == 402:
                if wallet_key:
                    try:
                        payment_headers = _handle_x402_payment(r, wallet_key)
                        if payment_headers:
                            retry = client.post(url, json=body, headers={**headers, **payment_headers})
                            if retry.status_code == 200:
                                return retry.json()
                    except Exception as pay_err:
                        return {"error": "payment_failed", "message": str(pay_err)}

                return {
                    "error": "payment_required",
                    "message": (
                        "DLC contract registration requires payment (10,000 sats or $7.00 USDC). "
                        "Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic payment."
                    ),
                    "docs": "https://myceliasignal.com/docs/dlc",
                }

            return {"error": f"http_{r.status_code}", "message": r.text[:200]}

        except httpx.TimeoutException:
            return {"error": "timeout", "message": f"Request timed out after {REQUEST_TIMEOUT}s."}
        except Exception as e:
            return {"error": "request_error", "message": str(e)}
