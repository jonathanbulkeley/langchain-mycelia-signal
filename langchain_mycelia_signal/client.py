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

from .config import get_endpoint, get_wallet_key, is_paid_mode

# Request timeout in seconds
REQUEST_TIMEOUT = 30


def _parse_response(data: dict) -> dict:
    """Parse and clean the oracle response into a structured dict."""
    result = {
        "pair":      data.get("pair", ""),
        "price":     data.get("price", ""),
        "currency":  data.get("currency", ""),
        "timestamp": data.get("timestamp", ""),
        "sources":   data.get("sources", ""),
        "method":    data.get("method", ""),
        "signed":    False,
    }

    # Paid responses include signature fields
    if "signature" in data:
        result.update({
            "signed":    True,
            "signature": data.get("signature", ""),
            "pubkey":    data.get("pubkey", ""),
            "canonical": data.get("canonical", ""),
        })

    return result


def _format_result(parsed: dict) -> str:
    """Format the parsed result as a clean string for LangChain to use."""
    lines = [
        f"Pair:      {parsed['pair']}",
        f"Price:     {parsed['price']} {parsed['currency']}",
        f"Timestamp: {parsed['timestamp']}",
        f"Sources:   {parsed['sources']}",
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
        # x402 protocol: WWW-Authenticate header contains payment details
        payment_required = payment_info.get("x402_payment_required", {})
        amount = payment_required.get("maxAmountRequired", "1000")  # atomic USDC units
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
    In paid mode: automatically pays $0.001 USDC on Base via x402,
                  returns fully signed attestation.
    """
    url = get_endpoint(pair)
    wallet_key = get_wallet_key()
    paid = is_paid_mode()

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = client.get(url)

            # 200 — success (free endpoint or already paid)
            if response.status_code == 200:
                data = response.json()
                parsed = _parse_response(data)
                return _format_result(parsed)

            # 402 — payment required
            if response.status_code == 402:
                if not paid:
                    # Free mode — return a helpful message explaining how to upgrade
                    return (
                        f"This endpoint requires payment. "
                        f"Set MYCELIA_WALLET_PRIVATE_KEY to enable automatic x402 payments "
                        f"and receive cryptographically signed attestations. "
                        f"Cost: $0.001 USDC per query on Base. "
                        f"See: https://myceliasignal.com/docs/x402"
                    )

                # Paid mode — handle x402 payment and retry
                payment_info = response.json()
                payment_headers = _handle_x402_payment(payment_info, wallet_key)

                if payment_headers is None:
                    return "Payment failed: could not construct x402 payment."

                # Retry with payment header
                retry = client.get(url, headers=payment_headers)
                if retry.status_code == 200:
                    data = retry.json()
                    parsed = _parse_response(data)
                    return _format_result(parsed)
                else:
                    return f"Payment accepted but request failed: HTTP {retry.status_code}"

            # Other errors
            return f"API error: HTTP {response.status_code} — {response.text[:200]}"

        except httpx.TimeoutException:
            return f"Request timed out after {REQUEST_TIMEOUT}s. The API may be temporarily unavailable."
        except httpx.RequestError as e:
            return f"Network error: {e}"
        except Exception as e:
            return f"Unexpected error fetching {pair}: {e}"
