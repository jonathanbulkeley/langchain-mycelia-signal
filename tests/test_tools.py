"""Tests for langchain-mycelia-signal.

WHY THESE TESTS LOOK LIKE THIS. The suite they replace contained:

    assert get_price_usd("US_CPI") == "$0.10"
    assert get_price_usd("WTI")    == "$0.10"

The proxy charges $1.00 for both. But that assertion never even ran: the file had a
syntax error at line 178 -- an empty test body followed immediately by another def --
so pytest failed at collection and NOTHING in the suite executed, across six
releases. The file also still described itself as testing v2.2.0 and asserted
len(tools) == 17.

Two lessons, not one. A test that repeats the implementation's assumption confirms
the bug rather than catching it. And a suite nobody runs protects nothing at all.

So nothing here asserts a price from memory. Prices are checked against the LIVE
/.well-known/x402 document -- a source outside this package -- and the structural
tests check properties (no duplicates, every path resolvable, no prose prices) that
cannot be satisfied by copying a wrong value.
"""
import json
import os
import re
import urllib.request

import pytest

from langchain_mycelia_signal import MyceliaSignalTools
from langchain_mycelia_signal import config as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(HERE, "langchain_mycelia_signal")
DISCOVERY = "https://api.myceliasignal.com/.well-known/x402"


# ── the catalogue is whole ───────────────────────────────────────────────────

def test_route_count():
    """config.py is generated; a truncated write would silently shrink coverage
    and every lost route would read as 'unknown route' rather than as a bug."""
    assert C.TOTAL_ROUTES == 214
    assert len(C.ROUTES) == 214


def test_every_route_has_a_price_and_description():
    missing = [p for p, m in C.ROUTES.items() if not m.get("price") or not m.get("desc")]
    assert not missing, f"routes lacking price or description: {missing[:5]}"


# ── prices come from outside this package ────────────────────────────────────

def _live_prices() -> dict[str, str]:
    req = urllib.request.Request(DISCOVERY, headers={"User-Agent": "mycelia-tests"})
    with urllib.request.urlopen(req, timeout=20) as r:
        doc = json.loads(r.read())
    out = {}
    for entry in doc:
        res = entry.get("resource", "").replace("https://api.myceliasignal.com", "")
        for a in entry.get("accepts", []):
            amt = a.get("amount") or a.get("maxAmountRequired")
            if amt:
                out[res.split("?")[0]] = f"{int(amt) / 1_000_000:.2f}"
                break
    return out


@pytest.mark.network
def test_prices_match_the_live_proxy():
    """THE test this suite exists for.

    Diffs every price in ROUTES against what the proxy actually advertises. This is
    the check that would have failed on econ in April instead of passing until
    September.
    """
    try:
        live = _live_prices()
    except Exception as e:
        pytest.skip(f"discovery document unreachable: {e}")
    assert live, "discovery document returned no priced resources"

    wrong = []
    for path, meta in C.ROUTES.items():
        if ":" in path:          # templates are advertised with example values
            continue
        want = live.get(path)
        if want is None:
            continue             # advertised set differs by design (see surprises)
        if want != meta["price"]:
            wrong.append((path, meta["price"], want))
    assert not wrong, "ROUTES disagrees with the live proxy: " + "; ".join(
        f"{p} says ${ours} proxy says ${theirs}" for p, ours, theirs in wrong[:8])


# ── structure: properties a wrong value cannot satisfy ───────────────────────

def test_no_duplicate_tools():
    """2.8.0 shipped get_mycelia_equity_rotation three times and
    get_mycelia_equity_regime twice in as_list()."""
    tools = MyceliaSignalTools().as_list()
    names = [getattr(t, "name", None) or t.__name__ for t in tools]
    assert len(names) == len(set(names)), \
        f"duplicates: {[n for n in names if names.count(n) > 1]}"


def test_tool_count_is_reported_honestly():
    t = MyceliaSignalTools()
    assert len(t.as_list()) == 35
    assert "tools=35" in repr(t)


def test_core_is_a_subset_of_as_list():
    t = MyceliaSignalTools()
    assert set(id(x) for x in t.core()) <= set(id(x) for x in t.as_list())


def test_no_dollar_figures_in_tool_prose():
    """Prices live in ROUTES and are surfaced at call time. A price written into a
    docstring is a copy, and every copy found in the 2026-09-26 audit was wrong."""
    src = open(os.path.join(PKG, "tools.py"), encoding="utf-8").read()
    # $/M tokens and $/GPU-hour are units, not prices
    figures = re.findall(r'\$\d+\.\d\d', src)
    assert not figures, f"hardcoded prices in tools.py: {figures[:6]}"


# ── path construction ────────────────────────────────────────────────────────

def test_route_key_matches_templates():
    assert C.route_key("/oracle/prediction/fed/2026-12") == "/oracle/prediction/fed/:meeting_code"
    assert C.route_key("/oracle/marine/vessel/366999712") == "/oracle/marine/vessel/:mmsi"
    assert C.route_key("/oracle/price/btc/usd") == "/oracle/price/btc/usd"
    assert C.route_key("/oracle/nonsense") is None


def test_price_for_resolves_filled_paths():
    """get_price_usd is exact-key only; price_for must handle a filled template, or
    the 402 notice quotes 'a fee' for every parameterised route."""
    assert C.price_for("/oracle/prediction/fed/2026-12") == "$0.50"
    assert C.get_price_usd("/oracle/prediction/fed/2026-12") == ""
    assert C.price_for("/oracle/nonsense") == ""


def test_no_literal_colons_reach_a_url():
    """get_mycelia_marine once passed the route KEY to the fetcher, putting
    ':mmsi' in the URL. Vessel and seastate never worked."""
    from langchain_mycelia_signal import tools as T
    recorded = []
    real = T.fetch_json
    T.fetch_json = lambda url: recorded.append(url) or {}
    try:
        T.get_mycelia_marine.func(mmsi="366999712")
        T.get_mycelia_marine.func(lat="37.77", lon="-122.41")
        T.get_mycelia_prediction.func(kind="fed", code="2026-12")
    finally:
        T.fetch_json = real
    assert recorded, "no request was made"
    assert not any(":" in u.split("://", 1)[1] for u in recorded), \
        f"a route template reached the URL: {recorded}"


# ── the payment path must not silently succeed ───────────────────────────────

def test_free_mode_returns_a_payment_notice_not_data(monkeypatch):
    monkeypatch.delenv("MYCELIA_WALLET_PRIVATE_KEY", raising=False)
    from langchain_mycelia_signal.client import _payment_notice
    n = _payment_notice("/oracle/econ/us/cpi")
    assert n["error"] == "payment_required"
    assert n["price"] == "$1.00"          # from ROUTES, not from this test's memory


def test_client_does_not_sign_payments_itself():
    """Before 3.0.0 this package built an EIP-3009 payload by hand and produced a
    structure the facilitator could not verify. Signing belongs to the x402
    library."""
    src = open(os.path.join(PKG, "client.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.split("\n") if not l.strip().startswith("#"))
    body = code.split('"""', 2)[-1]        # drop the module docstring
    for banned in ("encode_defunct", "sign_message", "sign_typed_data"):
        assert banned not in body, f"{banned} is back in client.py"


def test_attestation_fields_survive_formatting():
    """A signed oracle whose signature never reaches the agent cannot be verified,
    which is the entire reason to call it rather than an exchange ticker."""
    from langchain_mycelia_signal.client import _format_json
    out = _format_json({
        "canonical": "v1|PRICE|BTCUSD|84000|USD|2|1790000000|abc|binance|median",
        "signature": "deadbeef", "pubkey": "cafebabe",
        "deep": {"a": {"b": {"c": list(range(50))}}},
    }, "title")
    assert "v1|PRICE|BTCUSD|84000" in out
    assert "deadbeef" in out and "cafebabe" in out


def test_version_has_one_home():
    """__version__ lived in both __init__.py and pyproject.toml until 3.0.1.
    pyproject now reads it from config.py via hatch's dynamic version."""
    import re
    cfg = open(os.path.join(PKG, "config.py"), encoding="utf-8").read()
    init = open(os.path.join(PKG, "__init__.py"), encoding="utf-8").read()
    proj = open(os.path.join(HERE, "pyproject.toml"), encoding="utf-8").read()
    assert re.search(r'^__version__ = "', cfg, re.M), "config.py must declare it"
    assert not re.search(r'^__version__ = "', init, re.M), "__init__ must import it"
    assert 'dynamic = ["version"]' in proj, "pyproject must not hardcode a version"
    assert re.search(r'^version = "', proj, re.M) is None


def test_requests_identify_the_package():
    """Without a User-Agent every call is an anonymous python-httpx and the
    operator cannot tell package traffic from anything else."""
    from langchain_mycelia_signal.config import USER_AGENT, __version__
    assert USER_AGENT.startswith("langchain-mycelia-signal/")
    assert __version__ in USER_AGENT
    src = open(os.path.join(PKG, "client.py"), encoding="utf-8").read()
    assert "USER_AGENT" in src and "User-Agent" in src
