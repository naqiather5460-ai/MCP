"""
invoice_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("invoice-tools")

# Simulated ERP data -- standing in for the real ERP database the
# Matching Agent reads from in the Task 4/5 case study.
_SIMULATED_ERP = {
    "INV-1001": {"vendor": "Acme Supplies", "amount": 4200.00, "status": "MATCHED", "po_number": "PO-77"},
    "INV-1002": {"vendor": "Beacon Freight", "amount": 980.50, "status": "MISMATCH", "po_number": "PO-81"},
    "INV-1003": {"vendor": "Coastal Materials", "amount": 15600.00, "status": "APPROVED", "po_number": "PO-92"},
}


@mcp.tool()
def get_invoice_status(invoice_id: str) -> dict:
    """Look up the current workflow status of an invoice by its ID.
    """
    record = _SIMULATED_ERP.get(invoice_id)
    if record is None:
        return {"found": False, "invoice_id": invoice_id}
    return {"found": True, "invoice_id": invoice_id, **record}


@mcp.tool()
def calculate_late_fee(amount: float, days_overdue: int) -> dict:
    """Calculate a late-payment fee for an overdue invoice.
    """
    if days_overdue <= 0:
        return {"late_fee": 0.0, "periods_overdue": 0}
    periods = -(-days_overdue // 30)  # ceiling division
    fee = round(amount * 0.015 * periods, 2)
    return {"late_fee": fee, "periods_overdue": periods}


if __name__ == "__main__":
    # stdio transport: the server reads/writes JSON-RPC 2.0 messages over
    # stdin/stdout, exactly as the MCP client below expects.
    mcp.run(transport="stdio")
