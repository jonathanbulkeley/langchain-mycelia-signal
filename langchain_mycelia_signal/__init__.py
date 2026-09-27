"""
langchain-mycelia-signal
========================
LangChain tools for Mycelia Signal -- cryptographically signed oracle data with
automatic x402 (USDC on Base) payment.

35 parameterised tools covering 213 of the API's 214 priced endpoints. One endpoint,
/oracle/econ/surprises, is deliberately not exposed: it is a stub returning 503, and
a tool that always errors teaches a model to distrust the package.

Prices and descriptions come from config.ROUTES, which is GENERATED from the proxy's
own routes.ts. Nothing in this package states a price of its own -- an audit on
2026-09-26 found econ calls quoted at $0.10 against a real $1.00, and every such
error was a hand-copied value.

Quick start (free tier -- no config needed, paid routes return a payment notice):
    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()

Paid tier:
    MYCELIA_WALLET_PRIVATE_KEY=0x...
    # x402 payment is then handled automatically.

Alternative: MCP server
    If your agent framework speaks Model Context Protocol, you do not need this
    package. Attach https://api.myceliasignal.com/mcp as a remote MCP server
    (Streamable HTTP) and the tools arrive with their own descriptions and prices;
    the MCP client handles x402 itself, so there is no wallet configuration here.
    This package remains the right choice for LangChain agents and for anything
    that wants the tools as Python callables.

What these tools do NOT do
    They MEASURE current market state. They do not forecast. Out-of-sample testing
    on 2026-09-25 put MSVI's 24-hour forward correlation with BTC returns at -0.287,
    against +0.104 in the fitting window -- a sign flip, which is what a dead signal
    looks like. No Mycelia index has evidence of predicting direction at any
    magnitude the data can detect.

Docs: https://myceliasignal.com/docs
"""

from .config import (ROUTES, TOTAL_ROUTES, __version__, describe, get_price_usd,
                     is_paid_mode, price_for, route_key)
from .tools import (
    get_mycelia_basis,
    get_mycelia_compute,
    get_mycelia_cot,
    get_mycelia_defi_metrics,
    get_mycelia_defi_yield,
    get_mycelia_dlc_info,
    get_mycelia_econ,
    get_mycelia_econ_calendar,
    get_mycelia_equity_index,
    get_mycelia_expiry,
    get_mycelia_funding,
    get_mycelia_gas,
    get_mycelia_greeks,
    get_mycelia_history,
    get_mycelia_index,
    get_mycelia_inference,
    get_mycelia_instruments,
    get_mycelia_iv,
    get_mycelia_iv_surface,
    get_mycelia_liq_flow,
    get_mycelia_liquidations,
    get_mycelia_marine,
    get_mycelia_oi,
    get_mycelia_orderbook,
    get_mycelia_perp_regime,
    get_mycelia_prediction,
    get_mycelia_price,
    get_mycelia_regime,
    get_mycelia_support_resistance,
    get_mycelia_svi,
    get_mycelia_synopsis,
    get_mycelia_term_structure,
    get_mycelia_vwap,
    get_mycelia_weather,
    get_mycelia_intel,
)

_ALL_TOOLS = [
    # Prices and FX
    get_mycelia_price, get_mycelia_vwap,
    # Indices
    get_mycelia_index, get_mycelia_equity_index,
    # Derivatives
    get_mycelia_funding, get_mycelia_oi, get_mycelia_basis,
    get_mycelia_liquidations, get_mycelia_liq_flow, get_mycelia_orderbook,
    get_mycelia_iv, get_mycelia_iv_surface, get_mycelia_svi, get_mycelia_greeks,
    get_mycelia_term_structure, get_mycelia_instruments,
    # Macro and prediction markets
    get_mycelia_econ, get_mycelia_econ_calendar, get_mycelia_expiry,
    get_mycelia_cot, get_mycelia_prediction,
    # Regimes and intelligence
    get_mycelia_perp_regime, get_mycelia_regime, get_mycelia_intel,
    get_mycelia_synopsis, get_mycelia_support_resistance,
    # DeFi, compute, inference, gas
    get_mycelia_defi_yield, get_mycelia_defi_metrics, get_mycelia_compute,
    get_mycelia_inference, get_mycelia_gas,
    # History, weather, marine, DLC
    get_mycelia_history, get_mycelia_weather, get_mycelia_marine,
    get_mycelia_dlc_info,
]


class MyceliaSignalTools:
    """Container for the Mycelia Signal LangChain tools.

        from langchain_mycelia_signal import MyceliaSignalTools
        tools = MyceliaSignalTools().as_list()
    """

    def as_list(self) -> list:
        """All 35 tools. The list is built from one source above, so a tool cannot
        appear twice -- the previous version shipped one tool three times."""
        return list(_ALL_TOOLS)

    def core(self) -> list:
        """The six tools that map to what the MCP server advertises by default.

        A desk running both surfaces should meet one product, not two pickers of
        different sizes. MCP advertises eight: price, sentiment, volatility, perp
        state, funding, basis, open interest and verify_attestation. Here sentiment
        and volatility are both reached through get_mycelia_index, and
        VERIFICATION IS NOT IN THIS PACKAGE -- verify_attestation exists only on the
        MCP server, because verification should be free and this package's transport
        is a paid HTTP client. Synopsis is deliberately absent, as it is on MCP: a
        tool costing 100x get_price should be opt-in, not the second thing a model
        sees.
        """
        return [get_mycelia_price, get_mycelia_index, get_mycelia_perp_regime,
                get_mycelia_funding, get_mycelia_basis, get_mycelia_oi]

    def price_tools(self) -> list:
        return [get_mycelia_price, get_mycelia_vwap]

    def index_tools(self) -> list:
        return [get_mycelia_index, get_mycelia_equity_index]

    def derivatives_tools(self) -> list:
        return [get_mycelia_funding, get_mycelia_oi, get_mycelia_basis,
                get_mycelia_liquidations, get_mycelia_liq_flow,
                get_mycelia_orderbook, get_mycelia_iv, get_mycelia_iv_surface,
                get_mycelia_svi, get_mycelia_greeks, get_mycelia_term_structure,
                get_mycelia_instruments]

    def macro_tools(self) -> list:
        return [get_mycelia_econ, get_mycelia_econ_calendar, get_mycelia_expiry,
                get_mycelia_cot, get_mycelia_prediction]

    def intel_tools(self) -> list:
        return [get_mycelia_perp_regime, get_mycelia_regime, get_mycelia_intel,
                get_mycelia_synopsis, get_mycelia_support_resistance]

    def data_tools(self) -> list:
        return [get_mycelia_defi_yield, get_mycelia_defi_metrics,
                get_mycelia_compute, get_mycelia_inference, get_mycelia_gas,
                get_mycelia_history, get_mycelia_weather, get_mycelia_marine,
                get_mycelia_dlc_info]

    @property
    def mode(self) -> str:
        return "paid" if is_paid_mode() else "free"

    def __repr__(self) -> str:
        return (f"MyceliaSignalTools(mode={self.mode!r}, tools={len(_ALL_TOOLS)}, "
                f"routes_covered={TOTAL_ROUTES - 1}/{TOTAL_ROUTES})")


def _tool_name(t) -> str:
    """LangChain's @tool returns a StructuredTool carrying .name; a plain function
    carries __name__. Reading only .name makes the package fail to import under any
    test harness that stubs the decorator."""
    return getattr(t, "name", None) or getattr(t, "__name__", "")


__all__ = ["MyceliaSignalTools", "ROUTES", "TOTAL_ROUTES", "__version__",
           "describe", "get_price_usd", "price_for", "route_key", "is_paid_mode"] + [_tool_name(t) for t in _ALL_TOOLS]
