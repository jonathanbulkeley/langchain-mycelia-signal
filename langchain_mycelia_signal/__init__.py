"""
langchain-mycelia-signal
========================
LangChain tools for Mycelia Signal — cryptographically signed oracle data
with automatic x402 (USDC on Base) and L402 (Lightning) payment support.

186 endpoints across four layers: prices, indices, derivatives, DeFi, compute, weather, marine, gas, COT,
LLM inference pricing, economic calendar, liquidation flow, signed history (Layer 1),
market synopsis, perp regime, TradFi regime, liquidity regime, equity indices (Layer 2),
macro risk, perp setup, DeFi opportunity, regime change, cross-asset divergence,
regime consensus, regime persistence (Layer 3).

Quick start (free tier — no config needed):
    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()

Paid tier (signed attestations — add wallet key to .env):
    MYCELIA_WALLET_PRIVATE_KEY=0x...

    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()
    # Payment handled automatically via x402 (USDC on Base).

Pricing:
    Crypto/FX/metals:  $0.01    Indices (MSVI/MSXI/MSSI/MSTI): $0.05
    VWAP:              $0.02    Equity indices (MESI/MNVI/MSLI/MSBI): $0.05
    Equity regime composite (MSERC): $0.10
    Equity rotation index (MSRI):    $0.10
    Basis/carry:       $0.02    Funding rates:                  $0.05
    Open interest:     $0.01    Econ/commodities:               $0.10
    Gas (single):      $0.01    Weather/marine:                 $0.10
    Gas (index):       $0.05    COT:                            $1.00
    Inference pricing: $0.02    Econ calendar/expiry:           $0.05
    DeFi metrics:      $0.05    Liq flow:                       $0.05
    History spot/fund: $0.05    History index:                  $0.10
    TradFi regime:     $0.10    Liquidity regime:               $0.10
    Synopsis:          $0.25    Perp regime (BTC/ETH/SOL):      $0.15
    Regime change:     $0.50    Divergence:                     $0.50
    Consensus:         $0.50    Regime persistence:             $0.15
    Macro risk:        $1.00    Perp setup:                     $1.00
    DeFi opportunity:  $0.75    DLC contracts:                  $7.00

Docs: https://myceliasignal.com/docs
"""

from .config import SUPPORTED_PAIRS, INDICES, DERIVATIVES, GAS_CHAINS, is_paid_mode
from .tools import (
    dlc_get_attestation,
    # Derivatives — extended surface/structure tools
    get_mycelia_greeks,
    get_mycelia_term_structure,
    get_mycelia_svi,
    get_mycelia_iv_surface,
    # Layer 2 — Oracle Information
    get_mycelia_synopsis,
    get_mycelia_perp_regime,
    get_mycelia_tradfi_regime,
    get_mycelia_equity_index,
    get_mycelia_equity_regime,
    get_mycelia_equity_rotation,
    # Layer 3 — Oracle Intelligence
    get_mycelia_macro_risk,
    get_mycelia_perp_setup,
    get_mycelia_defi_opportunity,
    get_mycelia_regime_change,
    get_mycelia_divergence,
    get_mycelia_consensus,
    get_mycelia_regime_persistence,
    dlc_list_announcements,
    dlc_register_enum,
    dlc_register_numeric,
    dlc_register_threshold,
    dlc_threshold_preview,
    get_mycelia_basis,
    get_mycelia_cot,
    get_mycelia_compute,
    get_mycelia_defi_yield,
    get_mycelia_defi_metrics,
    get_mycelia_econ_calendar,
    get_mycelia_funding,
    get_mycelia_gas,
    get_mycelia_history,
    get_mycelia_index,
    get_mycelia_inference,
    get_mycelia_liq_flow,
    get_mycelia_marine_seastate,
    get_mycelia_oi,
    get_mycelia_price,
    get_mycelia_weather,
)


class MyceliaSignalTools:
    """
    Container for all Mycelia Signal LangChain tools.

    Example:
        from langchain_mycelia_signal import MyceliaSignalTools
        from langchain.agents import AgentExecutor, create_tool_calling_agent

        tools = MyceliaSignalTools().as_list()
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
    """

    def as_list(self) -> list:
        """Return all Mycelia Signal tools for use with LangChain agents."""
        return [
            # Prices (58 pairs)
            get_mycelia_price,
            # Crypto indices (6 keys)
            get_mycelia_index,
            # Equity/TradFi indices (NEW S92)
            get_mycelia_equity_index,
            # Equity Regime Composite (NEW S102)
            get_mycelia_equity_regime,
            # Equity Rotation Index (NEW S102)
            get_mycelia_equity_rotation,
    get_mycelia_equity_rotation,
    get_mycelia_equity_regime,
    get_mycelia_equity_rotation,
            # Derivatives (funding, OI, basis)
            get_mycelia_funding,
            get_mycelia_oi,
            get_mycelia_basis,
            # Derivatives — options/surface/structure
            get_mycelia_greeks,
            get_mycelia_term_structure,
            get_mycelia_svi,
            get_mycelia_iv_surface,
            # Weather + Marine
            get_mycelia_weather,
            get_mycelia_marine_seastate,
            # Gas
            get_mycelia_gas,
            # GPU Compute
            get_mycelia_compute,
            # DeFi Yield + Metrics
            get_mycelia_defi_yield,
            get_mycelia_defi_metrics,
            # Inference Pricing
            get_mycelia_inference,
            # Economic Calendar
            get_mycelia_econ_calendar,
            # Liquidation Flow
            get_mycelia_liq_flow,
            # Signed Historical Data
            get_mycelia_history,
            # COT
            get_mycelia_cot,
            # Layer 2 — Oracle Information
            get_mycelia_synopsis,
            get_mycelia_perp_regime,
            get_mycelia_tradfi_regime,       # NEW S94
            # Layer 3 — Oracle Intelligence
            get_mycelia_macro_risk,
            get_mycelia_perp_setup,
            get_mycelia_defi_opportunity,
            get_mycelia_regime_change,       # NEW S91
            get_mycelia_divergence,          # NEW S94
            get_mycelia_consensus,           # NEW S94
            get_mycelia_regime_persistence,  # NEW S95
            # DLC oracle
            dlc_threshold_preview,
            dlc_register_threshold,
            dlc_register_enum,
            dlc_register_numeric,
            dlc_get_attestation,
            dlc_list_announcements,
        ]

    def price_tools(self) -> list:
        """Return only the price/FX/macro/commodity tool."""
        return [get_mycelia_price]

    def index_tools(self) -> list:
        """Return only the crypto index tools (MSVI, MSXI, MSSI, MSTI)."""
        return [get_mycelia_index]

    def equity_tools(self) -> list:
        """Return TradFi/equity index tools (MESI, MNVI/MSLI/MSBI/MSERC)."""
        return [get_mycelia_equity_index, get_mycelia_equity_regime]

    def derivatives_tools(self) -> list:
        """Return all derivatives tools: funding, OI, basis, Greeks, term structure, SVI, IV surface."""
        return [
            get_mycelia_funding,
            get_mycelia_oi,
            get_mycelia_basis,
            get_mycelia_greeks,
            get_mycelia_term_structure,
            get_mycelia_svi,
            get_mycelia_iv_surface,
        ]

    def data_tools(self) -> list:
        """Return weather, marine, gas, DeFi yield, compute, and COT tools."""
        return [
            get_mycelia_weather, get_mycelia_marine_seastate,
            get_mycelia_gas, get_mycelia_defi_yield,
            get_mycelia_compute, get_mycelia_cot,
        ]

    def regime_tools(self) -> list:
        """Return all regime classification tools (Layer 2)."""
        return [
            get_mycelia_synopsis,
            get_mycelia_perp_regime,
            get_mycelia_tradfi_regime,
        ]

    def intel_tools(self) -> list:
        """Return all Layer 2 + Layer 3 oracle intelligence tools."""
        return [
            get_mycelia_synopsis,
            get_mycelia_perp_regime,
            get_mycelia_tradfi_regime,
            get_mycelia_macro_risk,
            get_mycelia_perp_setup,
            get_mycelia_defi_opportunity,
            get_mycelia_regime_change,
            get_mycelia_divergence,
            get_mycelia_consensus,
            get_mycelia_regime_persistence,
        ]

    def dlc_tools(self) -> list:
        """Return all DLC oracle tools (threshold, enum, numeric, attestation, list)."""
        return [
            dlc_threshold_preview,
            dlc_register_threshold,
            dlc_register_enum,
            dlc_register_numeric,
            dlc_get_attestation,
            dlc_list_announcements,
        ]

    @property
    def mode(self) -> str:
        return "paid" if is_paid_mode() else "free"

    @property
    def supported_pairs(self) -> list[str]:
        return list(SUPPORTED_PAIRS.keys())

    def __repr__(self) -> str:
        return (
            f"MyceliaSignalTools("
            f"mode={self.mode!r}, "
            f"pairs={len(self.supported_pairs)}, "
            f"indices={len(INDICES)}, "
            f"derivatives={len(DERIVATIVES)}, "
            f"tools={len(self.as_list())})"
        )


__all__ = [
    "MyceliaSignalTools",
    "get_mycelia_price",
    "get_mycelia_index",
    "get_mycelia_equity_index",
    "get_mycelia_equity_regime",
    "get_mycelia_equity_rotation",
    "get_mycelia_funding",
    "get_mycelia_oi",
    "get_mycelia_basis",
    "get_mycelia_greeks",
    "get_mycelia_term_structure",
    "get_mycelia_svi",
    "get_mycelia_iv_surface",
    "get_mycelia_weather",
    "get_mycelia_marine_seastate",
    "get_mycelia_gas",
    "get_mycelia_compute",
    "get_mycelia_defi_yield",
    "get_mycelia_defi_metrics",
    "get_mycelia_econ_calendar",
    "get_mycelia_inference",
    "get_mycelia_liq_flow",
    "get_mycelia_history",
    "get_mycelia_cot",
    "dlc_threshold_preview",
    "dlc_register_threshold",
    "dlc_register_enum",
    "dlc_register_numeric",
    "dlc_get_attestation",
    "dlc_list_announcements",
    # Layer 2
    "get_mycelia_synopsis",
    "get_mycelia_perp_regime",
    "get_mycelia_tradfi_regime",
    # Layer 3
    "get_mycelia_macro_risk",
    "get_mycelia_perp_setup",
    "get_mycelia_defi_opportunity",
    "get_mycelia_regime_change",
    "get_mycelia_divergence",
    "get_mycelia_consensus",
    "get_mycelia_regime_persistence",
    "is_paid_mode",
    "SUPPORTED_PAIRS",
    "INDICES",
    "DERIVATIVES",
]
__version__ = "2.8.0"
