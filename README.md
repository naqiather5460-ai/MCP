# MCP Proof of Concept: Invoice Tools with LangChain

A minimal, runnable demo of the **Model Context Protocol (MCP)**. An agent starts an MCP server over stdio, discovers its tools at runtime, wraps them as LangChain tools, and calls them to answer invoice questions.

Practical proof of concept for **Part B: MCP Exploration**.

| | |
|---|---|
| **Language** | Python 3.10+ |
| **Transport** | stdio (JSON-RPC 2.0) |
| **API key needed** | No |
| **Runs offline** | Yes |

---

## 1. Architecture

```mermaid
flowchart LR
    U([User request]) --> A[AI Agent<br/>agent_client.py]
    A --> C[MCP Client<br/>ClientSession]
    C <-->|stdio<br/>JSON-RPC 2.0| S[MCP Server<br/>invoice_mcp_server.py]
    S --> T1[get_invoice_status]
    S --> T2[calculate_late_fee]
    T1 --> E[(Simulated ERP<br/>Python dict)]
    T2 --> M[Late-fee formula]
    E --> R([Result])
    M --> R
    R --> A
```

The client launches the server as a **subprocess**. You never start the server yourself.

---

## 2. Message flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant C as MCP Client
    participant S as MCP Server

    U->>A: "INV-1003 is $15,600 and 47 days overdue. Late fee?"
    A->>C: open stdio session
    C->>S: initialize
    S-->>C: server info (invoice-tools)
    C->>S: tools/list
    S-->>C: get_invoice_status, calculate_late_fee
    Note over C: Tools wrapped as LangChain tools
    A->>A: choose_tool_calls() selects tools
    A->>C: get_invoice_status(INV-1003)
    C->>S: tools/call
    S-->>C: vendor, amount, status, PO
    A->>C: calculate_late_fee(15600, 47)
    C->>S: tools/call
    S-->>C: late_fee = 468.0, periods = 2
    C-->>A: results
    A-->>U: answer
```

---

## 3. Tools

| Tool | Input | Output |
|---|---|---|
| `get_invoice_status` | `invoice_id: str` | `{found, invoice_id, vendor, amount, status, po_number}` or `{found: false, invoice_id}` |
| `calculate_late_fee` | `amount: float`, `days_overdue: int` | `{late_fee, periods_overdue}` |

### Late-fee rule

```mermaid
flowchart LR
    D{days_overdue<br/>&le; 0?} -->|yes| Z[fee = 0<br/>periods = 0]
    D -->|no| P["periods = ceil(days / 30)"]
    P --> F["fee = amount x 1.5% x periods"]
```

Example: 47 days gives 2 started periods, so $15,600.00 x 1.5% x 2 = **$468.00**.

### Simulated ERP data

| Invoice | Vendor | Amount | Status | PO |
|---|---|---|---|---|
| `INV-1001` | Acme Supplies | 4,200.00 | MATCHED | PO-77 |
| `INV-1002` | Beacon Freight | 980.50 | MISMATCH | PO-81 |
| `INV-1003` | Coastal Materials | 15,600.00 | APPROVED | PO-92 |

---

## 4. Project structure

```
.
├── invoice_mcp_server.py   MCP server (FastMCP), exposes 2 tools
├── agent_client.py         Agent + MCP client + LangChain wrapping
├── make_diagrams.py        Generates PNG diagrams (matplotlib)
├── requirements.txt        mcp, langchain-mcp-adapters, matplotlib
├── run_output.txt          Captured output of a successful run
├── diagram_architecture.png
└── diagram_workflow.png
```

---

## 5. Run it

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python agent_client.py
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python agent_client.py
```

Optional: `python make_diagrams.py` regenerates the PNG diagrams.

### Expected output (abridged)

```
[MCP] Connected to server: invoice-tools v<sdk version>
[MCP] Discovered 2 tool(s) via tools/list:
       - get_invoice_status: Look up the current workflow status of an invoice by its ID.
       - calculate_late_fee: Calculate a late-payment fee for an overdue invoice.
[LangChain] Wrapped 2 MCP tool(s) as LangChain Tool objects
[AGENT] Decided to call 2 tool(s): ['get_invoice_status', 'calculate_late_fee']
[MCP] --> tools/call  name=calculate_late_fee  arguments={"amount": 15600.0, "days_overdue": 47}
[MCP] <-- result: {"late_fee": 468.0, "periods_overdue": 2}
```

Full run: see `run_output.txt`.

---

## 6. What is real and what is simulated

| Component | Status |
|---|---|
| MCP server (FastMCP), stdio transport | Real |
| `initialize`, `tools/list`, `tools/call` over JSON-RPC 2.0 | Real |
| MCP tools wrapped as LangChain tools | Real |
| ERP data | **Simulated** (in-memory dict) |
| Tool selection ("agent brain") | **Simulated** (regex rules, not an LLM) |

### Limitation: the agent is not an LLM

`choose_tool_calls()` in `agent_client.py` uses regular expressions to pick tools. It stands in for an LLM so the demo runs offline and deterministically.

```mermaid
flowchart LR
    subgraph Now[Current demo]
        R1[User request] --> R2[choose_tool_calls<br/>regex rules] --> R3[MCP tools]
    end
    subgraph Next[Full agent]
        L1[User request] --> L2[LLM agent<br/>e.g. LangGraph ReAct] --> L3[MCP tools]
    end
```

To upgrade, pass `lc_tools` to an LLM-driven agent instead of calling `choose_tool_calls()`. The server needs no changes. Check the current LangChain/LangGraph docs for exact imports, as they change between versions.

---

## 7. Possible extensions

- [ ] Add an MCP **resource** (e.g. `erp://invoices/{id}`) and an MCP **prompt** to cover all three primitives
- [ ] Replace the in-memory dict with a real database
- [ ] Serve over Streamable HTTP with authorisation instead of stdio
- [ ] Add input validation and automated tests

---

## References

- Model Context Protocol: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- LangChain MCP adapters: https://github.com/langchain-ai/langchain-mcp-adapters
