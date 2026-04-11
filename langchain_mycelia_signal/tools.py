"""
LangChain tools for Mycelia Signal oracle data.

Usage:
    from langchain_mycelia_signal import MyceliaSignalTools

    tools = MyceliaSignalTools().as_list()
    # Pass tools to your LangChain agent
"""

from langchain_core.tools import tool

from .client import fetch_dlc_free, fetch_price, post_dlc_with_payment
from .config import PAIR_DESCRIPTIONS, SUPPORTED_PAIRS


@tool
def get_mycelia_price(pair: str) -> str:
    """
    Get a real-time price attestation from Mycelia Signal oracle.

    Returns cryptographically signed price data for the requested trading pair.
    Each response includes the price, timestamp, sources, aggregation method,
    and (in paid mode) a cryptographic signature for on-chain verification.

    CRYPTO SPOT (10 sats / $0.01):
        BTCUSD, BTCEUR, BTCJPY
        ETHUSD, ETHEUR, ETHJPY
        SOLUSD, SOLEUR, SOLJPY
        XRPUSD, ADAUSD, DOGEUSD

    CRYPTO VWAP — 5-minute (20 sats / $0.02):
        BTCUSD_VWAP, BTCEUR_VWAP

    PRECIOUS METALS (10 sats / $0.01):
        XAUUSD, XAUEUR, XAUJPY

    FX PAIRS (10 sats / $0.01):
        EURUSD, EURJPY, EURGBP, EURCHF, EURCNY, EURCAD
        GBPUSD, GBPJPY, GBPCHF, GBPCNY, GBPCAD
        USDJPY, USDCHF, USDCNY, USDCAD
        CHFJPY, CHFCAD, CNYJPY, CNYCAD, CADJPY

    US ECONOMIC INDICATORS (1000 sats / $0.10):
        US_CPI, US_CPI_CORE, US_UNRATE, US_NFP
        US_FEDFUNDS, US_GDP, US_PCE, US_YIELD_CURVE

    EU ECONOMIC INDICATORS (1000 sats / $0.10):
        EU_HICP, EU_HICP_CORE, EU_HICP_SERVICES
        EU_UNRATE, EU_GDP, EU_EMPLOYMENT

    COMMODITIES (1000 sats / $0.10):
        WTI, BRENT, NATGAS, COPPER, DXY

    Args:
        pair: The trading pair or indicator to query. Use uppercase with no slash,
              e.g. 'BTCUSD', 'EURUSD', 'XAUUSD', 'US_CPI', 'WTI'.
              VWAP variants use underscore suffix: 'BTCUSD_VWAP'.

    Returns:
        Formatted string with price, timestamp, source count, method,
        and signature fields (signed attestation in paid mode).

    Examples:
        get_mycelia_price("BTCUSD")
        get_mycelia_price("EURUSD")
        get_mycelia_price("XAUUSD")
        get_mycelia_price("US_CPI")
        get_mycelia_price("WTI")
        get_mycelia_price("BTCUSD_VWAP")
    """
    return fetch_price(pair)


@tool
def dlc_threshold_preview(pair: str, strike: float, direction: str, expiry: int | None = None) -> str:
    """
    Register a FREE DLC threshold contract preview with Mycelia Signal.

    Tests the full DLC integration flow without requiring payment.
    Returns a real attestation event ID and oracle R-points for verification.
    Use this to verify your integration before registering a paid production contract.

    Args:
        pair:      Trading pair — e.g. 'BTCUSD', 'ETHUSD', 'XAUUSD'. Uppercase, no slash.
                   Supported: BTCUSD, BTCEUR, BTCJPY, ETHUSD, ETHEUR, ETHJPY,
                   SOLUSD, SOLEUR, SOLJPY, XAUUSD, XAUEUR, XAUJPY, XRPUSD, ADAUSD, DOGEUSD.
        strike:    Price level to monitor (integer). e.g. 90000 for BTC above $90,000.
        direction: 'above' or 'below' — direction of breach to attest.
        expiry:    Optional Unix timestamp for contract expiry. Defaults to 30 days from now.

    Returns:
        Event ID, oracle pubkey, R-points, and expiry for the registered preview contract.

    Example:
        dlc_threshold_preview("BTCUSD", 90000, "above")
        dlc_threshold_preview("ETHUSD", 3000, "below", 1780000000)
    """
    import time as _time
    body = {
        "pair": pair.upper().replace("/", ""),
        "strike": int(strike),
        "direction": direction.lower(),
        "expiry": expiry or int(_time.time()) + 86400 * 30,
    }
    result = post_dlc_with_payment("/dlc/oracle/threshold/preview", body)

    if result.get("error"):
        return (
            f"DLC preview failed: {result.get('message', result['error'])}\n"
            f"Docs: {result.get('docs', 'https://myceliasignal.com/docs/dlc')}"
        )

    lines = [
        "DLC Threshold Preview Registered (free — no payment)",
        f"Event ID:     {result.get('eventid', '')}",
        f"Pair:         {result.get('pair', '')}",
        f"Strike:       {result.get('strike', '')}",
        f"Direction:    {result.get('direction', '')}",
        f"Expiry:       {result.get('expiry', '')}",
        f"Oracle pubkey: {str(result.get('oraclePubkey', ''))[:16]}...",
        f"Docs: https://myceliasignal.com/docs/dlc",
    ]
    return "\n".join(lines)


@tool
def dlc_register_threshold(pair: str, strike: float, direction: str, expiry: int | None = None, webhook_url: str | None = None) -> str:
    """
    Register a PRODUCTION DLC threshold contract with Mycelia Signal oracle.

    Payment required: 10,000 sats (L402 Lightning) or $7.00 USDC (x402 on Base).
    Set MYCELIA_WALLET_PRIVATE_KEY for automatic x402 payment.

    The oracle monitors the specified price level and publishes a cryptographic
    attestation when the price breaches the threshold or at contract expiry.

    Args:
        pair:        Trading pair — e.g. 'BTCUSD', 'ETHUSD'. Uppercase, no slash.
                     Supported: BTCUSD, BTCEUR, BTCJPY, ETHUSD, ETHEUR, ETHJPY,
                     SOLUSD, SOLEUR, SOLJPY, XAUUSD, XAUEUR, XAUJPY, XRPUSD, ADAUSD, DOGEUSD.
        strike:      Price level to monitor (integer). e.g. 90000 for BTC above $90,000.
        direction:   'above' or 'below' — direction of breach to attest.
        expiry:      Optional Unix timestamp for contract expiry. Defaults to 30 days from now.
        webhook_url: Optional URL to receive attestation payload via POST on breach or expiry.

    Returns:
        Event ID, oracle pubkey, R-points, and expiry for the registered contract.

    Example:
        dlc_register_threshold("BTCUSD", 90000, "above")
        dlc_register_threshold("ETHUSD", 3000, "below", webhook_url="https://your-server.com/dlc")
    """
    import time as _time
    body = {
        "pair": pair.upper().replace("/", ""),
        "strike": int(strike),
        "direction": direction.lower(),
        "expiry": expiry or int(_time.time()) + 86400 * 30,
    }
    if webhook_url:
        body["webhookUrl"] = webhook_url

    result = post_dlc_with_payment("/dlc/oracle/threshold", body)

    if result.get("error") == "payment_required":
        return (
            f"Payment required to register DLC contract.\n"
            f"Cost: 10,000 sats (L402) or $7.00 USDC (x402)\n"
            f"Set MYCELIA_WALLET_PRIVATE_KEY for automatic payment.\n"
            f"Docs: {result.get('docs', 'https://myceliasignal.com/docs/dlc')}"
        )

    if result.get("error"):
        return (
            f"DLC registration failed: {result.get('message', result['error'])}\n"
            f"Docs: {result.get('docs', 'https://myceliasignal.com/docs/dlc')}"
        )

    lines = [
        "DLC Threshold Contract Registered",
        f"Event ID:     {result.get('eventid', '')}",
        f"Pair:         {result.get('pair', '')}",
        f"Strike:       {result.get('strike', '')}",
        f"Direction:    {result.get('direction', '')}",
        f"Expiry:       {result.get('expiry', '')}",
        f"Oracle pubkey: {str(result.get('oraclePubkey', ''))[:16]}...",
        f"Payment rail: {result.get('rail', '')}",
        f"Docs: https://myceliasignal.com/docs/dlc",
    ]
    if result.get("webhookUrl"):
        lines.append(f"Webhook:      {result['webhookUrl']}")
    return "\n".join(lines)


@tool
def dlc_get_attestation(event_id: str) -> str:
    """
    Retrieve the cryptographic attestation for a settled DLC contract. FREE endpoint.

    The oracle publishes an attestation when the price breaches the registered
    threshold or when the contract reaches its expiry. Use this to verify settlement
    and unlock DLC contract execution transactions (CETs).

    Returns HTTP 425 (not yet attested) if the contract has not yet settled.

    Args:
        event_id: The DLC event ID returned when the contract was registered.
                  e.g. 'BTCUSD-2026-04-07T00:00:00Z' or a UUID-style ID.

    Returns:
        Attestation outcome, timestamp, and cryptographic signature.

    Example:
        dlc_get_attestation("BTCUSD-2026-04-07T00:00:00Z")
    """
    result = fetch_dlc_free(f"/dlc/oracle/attestations/{event_id}")

    if not result:
        return f"No attestation found for event ID: {event_id}"

    if result.get("error") == "not_yet_attested":
        return f"Contract {event_id} has not been attested yet. Check back after the expiry time."

    if result.get("error"):
        return f"Error fetching attestation: {result.get('message', result['error'])}"

    lines = [
        "DLC Attestation",
        f"Event ID:    {result.get('eventid', event_id)}",
        f"Outcome:     {result.get('outcome', '')}",
        f"Attested at: {result.get('attestedAt', '')}",
    ]
    if result.get("signature"):
        lines.append(f"Signature:   {str(result['signature'])[:16]}...")
    if result.get("oraclePubkey"):
        lines.append(f"Oracle key:  {str(result['oraclePubkey'])[:16]}...")
    lines.append("Verify: https://myceliasignal.com/docs/verification")
    return "\n".join(lines)


@tool
def dlc_list_announcements() -> str:
    """
    List all active DLC announcements from Mycelia Signal oracle. FREE endpoint.

    Returns all active numeric and threshold contract announcements including
    event IDs, pairs, strike prices, directions, and expiry times. Use this
    to discover existing contracts and their event IDs for attestation retrieval.

    Returns:
        List of active DLC announcements with event IDs and contract details.

    Example:
        dlc_list_announcements()
    """
    result = fetch_dlc_free("/dlc/oracle/announcements")

    if not result:
        return "Unable to fetch DLC announcements. See https://myceliasignal.com/docs/dlc"

    if result.get("error"):
        return f"Error: {result.get('message', result['error'])}"

    announcements = result.get("announcements", [])
    if not announcements:
        return "No active DLC announcements found. See https://myceliasignal.com/docs/dlc"

    lines = [f"Active DLC Announcements ({len(announcements)} total)"]
    for a in announcements[:15]:
        parts = [f"— {a.get('eventid', '')}"]
        if a.get("pair"):
            parts.append(f"| {a['pair']}")
        if a.get("strike"):
            parts.append(f"| strike: {a['strike']} {a.get('direction', '')}")
        if a.get("expiry"):
            parts.append(f"| expiry: {a['expiry']}")
        lines.append(" ".join(parts))
    if len(announcements) > 15:
        lines.append(f"...and {len(announcements) - 15} more")
    lines.append("Docs: https://myceliasignal.com/docs/dlc")
    return "\n".join(lines)

@tool
def get_msvi(pair: str = "BTCUSD") -> str:
    """
    Get the Mycelia Signal Volatility Index (MSVI) for BTC or ETH.
    Five-component composite volatility index: Realized Volatility (Parkinson 30D, 30%),
    Implied Volatility (Deribit ATM, 25%), Term Structure 7D/90D (15%),
    Funding Rate signal (20%), Put/Call Ratio (10%). Output: 0-100 index.
    Cryptographically signed with Ed25519 on paid queries.
    Pricing: 500 sats (L402) / $0.05 USDC (x402).
    Args:
        pair: Asset pair — "BTCUSD" or "ETHUSD". Default: "BTCUSD".
    Returns:
        Formatted string with MSVI value, regime, components, and signature.
    Examples:
        get_msvi("BTCUSD")
        get_msvi("ETHUSD")
    """
    from .client import fetch_index
    return fetch_index("MSVI", pair)


@tool
def get_msxi(pair: str = "BTCUSD") -> str:
    """
    Get the Mycelia Signal Sentiment Index (MSXI) for BTC or ETH.
    Five-component market sentiment index: Funding Rate direction (30%),
    Options Skew 25D risk reversal (25%), Put/Call Ratio (20%),
    Term Structure slope (15%), Cross-exchange Basis (10%).
    Output: -100 to +100. Positive=bullish, negative=bearish.
    Regimes: EXTREMEBULLISH, BULLISH, NEUTRAL, BEARISH, EXTREMEBEARISH.
    Cryptographically signed with Ed25519 on paid queries.
    Pricing: 500 sats (L402) / $0.05 USDC (x402).
    Args:
        pair: Asset pair — "BTCUSD" or "ETHUSD". Default: "BTCUSD".
    Returns:
        Formatted string with MSXI value, regime, components, and signature.
    Examples:
        get_msxi("BTCUSD")
        get_msxi("ETHUSD")
    """
    from .client import fetch_index
    return fetch_index("MSXI", pair)


@tool
def get_mssi() -> str:
    """
    Get the Mycelia Signal Stress Index (MSSI) — market-wide systemic stress indicator.
    Three-component stress index: Volatility Regime via MSVI average BTC+ETH (35%),
    Stablecoin Stress — max USDT/USDC deviation from $1.00 (30%),
    Funding Extremity — absolute z-score of OI-weighted composite (35%).
    Output: 0-100. Regimes: CALM, ELEVATED, HIGH, EXTREME.
    Market-wide single number — not per-pair.
    Cryptographically signed with Ed25519 on paid queries.
    Pricing: 500 sats (L402) / $0.05 USDC (x402).
    Returns:
        Formatted string with MSSI value, regime, components, and signature.
    Examples:
        get_mssi()
    """
    from .client import fetch_index
    return fetch_index("MSSI", "MARKET")
