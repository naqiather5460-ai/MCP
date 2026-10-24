"""
agent_client.py
"""

import asyncio
import json
import os
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools


def choose_tool_calls(user_request: str):
    """Stand-in for the LLM's tool-selection reasoning (see module docstring).
    """
    calls = []

    invoice_ids = re.findall(r"INV-\d+", user_request)
    if invoice_ids:
        for inv_id in invoice_ids:
            calls.append(("get_invoice_status", {"invoice_id": inv_id}))

    if "late fee" in user_request.lower() or "overdue" in user_request.lower():
        amount_match = re.search(r"\$([\d,]+\.?\d*)", user_request)
        days_match = re.search(r"(\d+)\s*days", user_request)
        amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0.0
        days = int(days_match.group(1)) if days_match else 0
        calls.append(("calculate_late_fee", {"amount": amount, "days_overdue": days}))

    return calls


async def run_agent(user_request: str):
    print("=" * 78)
    print(f"AI AGENT received user request:\n  \"{user_request}\"")
    print("=" * 78)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoice_mcp_server.py")],
    )

    # --- AI Agent -> MCP Client: open a real stdio connection to the server ---
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # --- MCP Client -> MCP Server: real `initialize` handshake ---
            init_result = await session.initialize()
            print(f"\n[MCP] Connected to server: "
                  f"{init_result.serverInfo.name} v{init_result.serverInfo.version}")

            # --- MCP Client -> MCP Server: real `tools/list` discovery ---
            tools_response = await session.list_tools()
            print(f"[MCP] Discovered {len(tools_response.tools)} tool(s) via tools/list:")
            for t in tools_response.tools:
                print(f"       - {t.name}: {t.description.strip().splitlines()[0]}")

            # Convert real MCP tool definitions into real LangChain Tool objects
            # (this is the langchain-mcp-adapters integration point referenced
            # in the LangChain MCP documentation)
            lc_tools = await load_mcp_tools(session)
            lc_tools_by_name = {t.name: t for t in lc_tools}
            print(f"[LangChain] Wrapped {len(lc_tools)} MCP tool(s) as LangChain Tool objects: "
                  f"{[t.name for t in lc_tools]}")

            # --- AI Agent: decide which tool(s) to call (see module docstring) ---
            tool_calls = choose_tool_calls(user_request)
            if not tool_calls:
                print("\n[AGENT] No matching tool call found for this request.")
                return

            print(f"\n[AGENT] Decided to call {len(tool_calls)} tool(s): "
                  f"{[c[0] for c in tool_calls]}")

            # --- MCP Client -> MCP Server -> Tool/Resource -> External System ---
            for tool_name, args in tool_calls:
                print(f"\n[MCP] --> tools/call  name={tool_name}  arguments={json.dumps(args)}")
                lc_tool = lc_tools_by_name[tool_name]
                result = await lc_tool.ainvoke(args)
                print(f"[MCP] <-- result: {result}")
                print(f"[AGENT] Incorporating tool result into its next decision / final answer.")

    print("\n" + "=" * 78)
    print("Flow complete: AI Agent -> MCP Client -> MCP Server -> Tool -> "
          "External System (simulated ERP) -> Result -> AI Agent")
    print("=" * 78)


if __name__ == "__main__":
    requests = [
        "What is the status of invoice INV-1002?",
        "Invoice INV-1003 is $15,600.00 and is 47 days overdue -- what is the late fee?",
    ]
    for req in requests:
        asyncio.run(run_agent(req))
        print("\n")
