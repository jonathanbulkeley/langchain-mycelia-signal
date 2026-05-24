"""
langchain-mycelia-signal
========================
LangChain tools for Mycelia Signal — cryptographically signed oracle data
with automatic x402 (USDC on Base) and L402 (Lightning) payment support.

117 endpoints: prices, indices, derivatives, weather, marine, gas, COT, DLC.

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
    VWAP:              $0.02    Funding rates:                  $0.05
    Basis/carry:       $0.02    Econ/commodities:               $0.10
    Open interest:     $0.01    Weather/marine:                 $0.10
    Gas (single):      $0.01    COT:                            $1.00
    Gas (index):       $0.05    DLC contracts:                  $7.00

Docs: https://myceliasignal.com/docs
"""

from .config import SUPPORTED_PAIRS, INDICES, DERIVATIVES, GAS_CHAINS, is_paid_mode
from .tools import (
    dlc_get_attestation,
    dlc_list_announcements,
    dlc_register_enum,
    dlc_register_numeric,
    dlc_register_threshold,
    dlc_threshold_preview,
    get_mycelia_basis,
    get_mycelia_cot,
    get_mycelia_defi_yield,
    get_mycelia_funding,
    get_mycelia_gas,
    get_mycelia_index,
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
            # Prices (56 pairs)
            get_mycelia_price,
            # Indices (6 keys)
            get_mycelia_index,
            # Derivatives (funding, OI, basis)
            get_mycelia_funding,
            get_mycelia_oi,
            get_mycelia_basis,
            # Weather + Marine
            get_mycelia_weather,
            get_mycelia_marine_seastate,
            # Gas
            get_mycelia_gas,
            # DeFi Yield
            get_mycelia_defi_yield,
            # COT
            get_mycelia_cot,
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
        """Return only the index tools (MSVI, MSXI, MSSI, MSTI)."""
        return [get_mycelia_index]

    def derivatives_tools(self) -> list:
        """Return funding rate, open interest, and basis/carry tools."""
        return [get_mycelia_funding, get_mycelia_oi, get_mycelia_basis]

    def data_tools(self) -> list:
        """Return weather, marine, gas, and COT tools."""
        return [get_mycelia_weather, get_mycelia_marine_seastate, get_mycelia_gas, get_mycelia_defi_yield, get_mycelia_cot]

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
    "get_mycelia_funding",
    "get_mycelia_oi",
    "get_mycelia_basis",
    "get_mycelia_weather",
    "get_mycelia_marine_seastate",
    "get_mycelia_gas",
    "get_mycelia_defi_yield",
    "get_mycelia_cot",
    "dlc_threshold_preview",
    "dlc_register_threshold",
    "dlc_register_enum",
    "dlc_register_numeric",
    "dlc_get_attestation",
    "dlc_list_announcements",
    "is_paid_mode",
    "SUPPORTED_PAIRS",
    "INDICES",
    "DERIVATIVES",
]
__version__ = "2.1.0"
