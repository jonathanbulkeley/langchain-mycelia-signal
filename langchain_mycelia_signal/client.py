"""HTTP client for Mycelia Signal, with x402 payment handled by the x402 library.

WHY THE LIBRARY AND NOT OUR OWN SIGNING. Until 3.0.0 this file built a payment by
hand: it signed a flat JSON blob with personal_sign (encode_defunct) and sent it as a
raw-JSON PAYMENT-SIGNATURE header. The proxy base64-decodes that header and reads
payload.authorization.from -- the EIP-3009 transferWithAuthorization shape. The two
never matched, so paid mode could not settle, and because logRevenue only fires on a
200 the failures left no row anywhere. It was invisible until an audit on 2026-09-26.

x402 2.9.0 already implements the exact-EVM scheme the facilitator verifies:
build_typed_data_for_signing, ExactEIP3009Authorization, nonce and validity window,
chain id lookup. Reimplementing that is how the bug happened. So: delegate.

x402HTTPClientSync.handle_402_response(headers, body) parses the challenge, signs the
payment and returns the headers to retry with. One call, the correct structure.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

from .config import (API_BASE_URL, describe, get_wallet_key, is_paid_mode,
                     price_for, route_key)

REQUEST_TIMEOUT = 30
_PAID_CLIENT: Any = None


def _paid_client():
    """An x402 HTTP client bound to MYCELIA_WALLET_PRIVATE_KEY, or None.

    Built once and cached. If construction fails -- missing extra, bad key -- we
    remember that and stop retrying, so a misconfigured wallet does not pay an import
    cost on every call.
    """
    global _PAID_CLIENT
    if _PAID_CLIENT is not None:
        return _PAID_CLIENT
    key = get_wallet_key()
    if not key:
        return None
    try:
        from eth_account import Account
        from x402.client import x402ClientSync
        from x402.http.x402_http_client import x402HTTPClientSync
        from x402.mechanisms.evm.exact.register import register_exact_evm_client

        account = Account.from_key(key)          # auto-wrapped by the scheme
        core = x402ClientSync()
        register_exact_evm_client(core, account)
        _PAID_CLIENT = x402HTTPClientSync(core)
        return _PAID_CLIENT
    except ImportError as e:
        raise ImportError(
            "Paid mode needs the x402 and eth-account packages. Install with:\n"
            "    pip install 'langchain-mycelia-signal[paid]'"
        ) from e
    except Exception:
        # NOT cached as a permanent failure: a key fixed mid-process should work on
        # the next call rather than leaving the agent silently in free mode forever.
        raise


def _payment_notice(path: str, key: str | None = None) -> dict:
    cost = price_for(path) or "a fee"
    return {
        "error": "payment_required",
        "path": path,
        "price": cost,
        "message": (
            f"{path} costs {cost} per call (USDC on Base). Set "
            f"MYCELIA_WALLET_PRIVATE_KEY to pay automatically via x402, or call the "
            f"MCP server at https://api.myceliasignal.com/mcp and let your agent's "
            f"own wallet settle it."
        ),
        "docs": "https://myceliasignal.com/docs/x402",
    }


def fetch_json(url: str) -> dict:
    """GET a Mycelia endpoint, paying via x402 if the wallet key is set.

    Returns the parsed JSON, or an error dict. Never a plausible-looking stub: a
    caller must be able to tell a real answer from a failed one.
    """
    path = url[len(API_BASE_URL):] if url.startswith(API_BASE_URL) else url
    with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as http:
        try:
            r = http.get(url)
            if r.status_code == 200:
                return r.json()

            if r.status_code != 402:
                return {"error": f"http_{r.status_code}", "path": path,
                        "message": r.text[:200]}

            # --- 402: pay and retry ---
            key = route_key(path)
            if not is_paid_mode():
                return _payment_notice(path, key)
            try:
                client = _paid_client()
            except ImportError:
                raise
            except Exception as e:
                return {"error": "wallet_invalid", "path": path,
                        "message": (f"MYCELIA_WALLET_PRIVATE_KEY could not be used: "
                                    f"{str(e)[:150]}. Fix the key and call again -- "
                                    f"paid mode is retried, not disabled.")}
            if client is None:
                return _payment_notice(path, key)

            pay_headers, _payload = client.handle_402_response(
                dict(r.headers), r.content)
            retry = http.get(url, headers=pay_headers)
            if retry.status_code == 200:
                return retry.json()
            # A settlement that fails leaves no trace server-side unless it is
            # reported here, so say what happened rather than "request failed".
            return {"error": "settlement_failed", "path": path,
                    "status": retry.status_code,
                    "message": (f"Payment was constructed and sent but the request "
                                f"returned {retry.status_code}. Common causes: "
                                f"insufficient USDC on Base, an authorization nonce "
                                f"already used, or a clock skew outside the validity "
                                f"window. Detail: {retry.text[:160]}")}

        except ImportError:
            raise
        except httpx.TimeoutException:
            return {"error": "timeout", "path": path,
                    "message": f"No response after {REQUEST_TIMEOUT}s."}
        except httpx.RequestError as e:
            return {"error": "network_error", "path": path, "message": str(e)[:200]}
        except Exception as e:
            return {"error": "payment_error", "path": path,
                    "message": f"x402 payment could not be completed: {str(e)[:200]}"}


_ATTESTATION_KEYS = ("canonical", "signature", "pubkey", "signingScheme",
                     "signing_scheme", "method_version", "methodVersion")
_MAX_CHARS = 6000


def _format_json(data: dict, title: str = "") -> str:
    """Render a response for a LangChain agent to read.

    The attestation fields are emitted FIRST and never truncated. The previous
    version flattened one level and cut lists at 10, which quietly dropped
    canonical and signature from deep objects like synopsis -- and a signed oracle
    whose signature never reaches the agent cannot be verified, which is the entire
    reason to call it rather than an exchange ticker.
    """
    if data.get("error"):
        parts = [f"Error ({data['error']}): {data.get('message', '')}"]
        if data.get("docs"):
            parts.append(f"Docs: {data['docs']}")
        return "\n".join(parts)

    import json as _json
    head = [title] if title else []
    for k in _ATTESTATION_KEYS:
        if data.get(k):
            head.append(f"{k}: {data[k]}")
    if len(head) > (1 if title else 0):
        head.append("(verify the canonical string against the published per-node key)")

    body = {k: v for k, v in data.items() if k not in _ATTESTATION_KEYS}
    rendered = _json.dumps(body, indent=2, default=str, ensure_ascii=False)
    if len(rendered) > _MAX_CHARS:
        rendered = rendered[:_MAX_CHARS] + f"\n... (truncated at {_MAX_CHARS} chars; "
        rendered += "the attestation fields above are complete)"
    return "\n".join(head + [rendered])


def describe_route(path: str) -> str:
    """The proxy's own description and price for a route, without calling it."""
    key = route_key(path)
    d = describe(key) if key else ""
    return f"{path} ({price_for(path) or 'unknown'}): {d}" if d else f"{path}: unknown route"
