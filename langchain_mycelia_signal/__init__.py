"""
langchain-mycelia-signal
========================
LangChain tools for Mycelia Signal — cryptographically signed price oracles
with automatic x402 (USDC on Base) and L402 (Lightning) payment support.

56 endpoints across crypto, FX, precious metals, US/EU macro, and commodities.

Quick start (free tier — no config needed):
    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()

Paid tier (signed attestations — add wallet key to .env):
    MYCELIA_WALLET_PRIVATE_KEY=0x...

    from langchain_mycelia_signal import MyceliaSignalTools
    tools = MyceliaSignalTools().as_list()
    # Payment handled automatically.
    # Price pairs: $0.01 USDC per query. Econ/commodities: $0.10 per query.

Docs: https://myceliasignal.com/docs
"""

from .config import SUPPORTED_PAIRS, is_paid_mode
from .tools import get_mycelia_price


class MyceliaSignalTools:
    """
    Container for Mycelia Signal LangChain tools.

    Example:
        from langchain_mycelia_signal import MyceliaSignalTools
        from langchain.agents import AgentExecutor, create_tool_calling_agent

        tools = MyceliaSignalTools().as_list()
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
    """

    def as_list(self) -> list:
        """Return all Mycelia Signal tools as a list for use with LangChain agents."""
        return [get_mycelia_price]

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


__all__ = ["MyceliaSignalTools", "get_mycelia_price", "is_paid_mode", "SUPPORTED_PAIRS"]
__version__ = "1.2.0"
