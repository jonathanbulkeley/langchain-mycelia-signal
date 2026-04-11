"""
langchain-mycelia-signal
========================
LangChain tools for Mycelia Signal — cryptographically signed price oracles
with automatic x402 (USDC on Base) and L402 (Lightning) payment support.

66 endpoints: price/FX/macro/commodity, MSVI/MSXI/MSSI market indices, plus Bitcoin DLC oracle.

Quick start (free tier — no config needed):
    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()

Paid tier (signed attestations — add wallet key to .env):
    MYCELIA_WALLET_PRIVATE_KEY=0x...

    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()
    # Payment handled automatically.
    # Price pairs: $0.01 USDC per query. Econ/commodities: $1.00 per query.
    # DLC threshold contracts: $7.00 USDC per registration.

Docs: https://myceliasignal.com/docs
DLC docs: https://myceliasignal.com/docs/dlc
"""

from .config import SUPPORTED_PAIRS, is_paid_mode
from .tools import (
    dlc_get_attestation,
    dlc_list_announcements,
    dlc_register_threshold,
    dlc_threshold_preview,
    get_mycelia_price,
    get_msvi,
    get_msxi,
    get_mssi,
)


class MyceliaSignalTools:
    """
    Container for Mycelia Signal LangChain tools.

    Includes 66 tools: price/FX/macro/commodity, MSVI/MSXI/MSSI market indices, plus 4 DLC oracle tools.

    Example:
        from langchain_mycelia_signal import MyceliaSignalTools
        from langchain.agents import AgentExecutor, create_tool_calling_agent

        tools = MyceliaSignalTools().as_list()
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
    """

    def as_list(self) -> list:
        """Return all Mycelia Signal tools as a list for use with LangChain agents."""
        return [
            get_mycelia_price,
            get_msvi,
            get_msxi,
            get_mssi,
            dlc_threshold_preview,
            dlc_register_threshold,
            dlc_get_attestation,
            dlc_list_announcements,
        ]
    def index_tools(self) -> list:
        """Return only the market index tools (MSVI, MSXI, MSSI)."""
        return [get_msvi, get_msxi, get_mssi]

    def price_tools(self) -> list:
        """Return only the price/FX/macro/commodity tools."""
        return [get_mycelia_price]

    def dlc_tools(self) -> list:
        """Return only the DLC oracle tools."""
        return [
            dlc_threshold_preview,
            dlc_register_threshold,
            dlc_get_attestation,
            dlc_list_announcements,
        ]

    @property
    def mode(self) -> str:
        """Return 'paid' if wallet key is configured, 'free' otherwise."""
        return "paid" if is_paid_mode() else "free"

    @property
    def supported_pairs(self) -> list[str]:
        """Return list of all supported trading pairs."""
        return list(SUPPORTED_PAIRS.keys())

    def __repr__(self) -> str:
        return (
            f"MyceliaSignalTools("
            f"mode={self.mode!r}, "
            f"pairs={len(self.supported_pairs)}, "
            f"tools={len(self.as_list())})"
        )


__all__ = [
    "MyceliaSignalTools",
    "get_mycelia_price",
    "dlc_threshold_preview",
    "dlc_register_threshold",
    "dlc_get_attestation",
    "dlc_list_announcements",
    "get_msvi",
    "get_msxi",
    "get_mssi",
    "is_paid_mode",
    "SUPPORTED_PAIRS",
]
__version__ = "1.3.2"
