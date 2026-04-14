"""
Demo 8 – Resumable AI Procurement Agent (LangGraph Persistence + Interrupt)

Scenario: An AI agent handles purchase requests. When a purchase exceeds
€10,000 it must pause for manager approval — which may come hours or days later.

The graph:

  START → lookup_vendors → fetch_pricing → compare_quotes
        → request_approval (INTERRUPTS here — process exits!)
        → submit_purchase_order → notify_employee → END

To simulate a real-world "late second invocation" across process restarts,
we use SqliteSaver (file-based checkpoint) and two CLI modes:

  python demo8.1-purchase-agent.py              # First run  — steps 1-3, then suspends
  python demo8.1-purchase-agent.py --resume     # Second run — manager approves, steps 5-6

Between the two runs the Python process exits completely.  The full agent
state (vendor data, pricing, chosen quote) survives on disk in SQLite.
"""

import sys
import os
import sqlite3
import time
import re
import requests
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command
from langchain_google_genai import ChatGoogleGenerativeAI

# ─── State ────────────────────────────────────────────────────────────────────

class ProcurementState(TypedDict):
    request: str
    vendors: list[dict]
    quotes: list[dict]
    best_quote: dict
    approval_status: str
    po_number: str
    notification: str


# ─── LLM (used only for the notification step to make it feel "agentic") ─────

""" muokkaus"""
def get_unit_price(vendor: str) -> dict:
    """Fetch real laptop price from dummyjson API."""
    try:
        response = requests.get("https://dummyjson.com/products/category/laptops")
        data = response.json()
        products = data.get("products", [])

        # Filter by vendor name (brand match)
        matching = [
            p for p in products
            if vendor.lower() in p.get("brand", "").lower()
        ]

        # Filter availability (simulate: stock > 0)
        matching = [p for p in matching if p.get("stock", 0) > 0]

        if matching:
            # Pick cheapest
            best = min(matching, key=lambda p: p["price"])
            return {
                "price": best["price"],
                "product": best["title"],
                "delivery_days": 7  # simulate ≤ 2 weeks
            }

        # fallback
        print(f"⚠ No product match for {vendor}, using fallback price")
        return {"price": 250, "product": "Generic Laptop", "delivery_days": 7}

    except Exception as e:
        print(f"⚠ API error: {e}")
        return {"price": 250, "product": "Generic Laptop", "delivery_days": 7}


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite").bind_tools([get_unit_price])


# ─── Node functions ──────────────────────────────────────────────────────────

def lookup_vendors(state: ProcurementState) -> dict:
    """Step 1: Look up approved vendors for laptops."""
    print("\n[Step 1] Looking up approved vendors...")
    time.sleep(1)  # simulate API call
    vendors = [
        {"name": "Dell", "id": "V-001", "category": "laptops", "rating": 4.5},
        {"name": "Lenovo", "id": "V-002", "category": "laptops", "rating": 4.3},
        {"name": "HP", "id": "V-003", "category": "laptops", "rating": 4.1},
    ]
    for v in vendors:
        print(f"   Found vendor: {v['name']} (rating {v['rating']})")
    return {"vendors": vendors}




""" muokkaus"""
def extract_quantity(request: str) -> int:
    match = re.search(r"\b(\d+)\b", request)
    return int(match.group(1)) if match else 1


def fetch_pricing(state: ProcurementState) -> dict:
    """Step 2: Fetch pricing dynamically using tool calls."""
    print("\n[Step 2] Fetching pricing from suppliers...")
    time.sleep(1)

    quantity = extract_quantity(state["request"])
    quotes = []

    for vendor in state["vendors"]:
        vendor_name = vendor["name"]

        # Ask LLM to call the tool
        product_data = get_unit_price(vendor_name)

        unit_price = product_data["price"]
        product_name = product_data["product"]
        delivery_days = product_data["delivery_days"]

        total = unit_price * quantity

        quote = {
            "vendor": vendor_name,
            "unit_price": unit_price,
            "total": total,
            "delivery_days": delivery_days,
            "product": product_name
        }  # keep static for now


        print(f"   {vendor_name}: {product_name} - €{unit_price}/unit x {quantity} = €{total:,}")
        quotes.append(quote)

    return {"quotes": quotes}


def compare_quotes(state: ProcurementState) -> dict:
    """Step 3: Compare quotes and pick the best one."""
    print("\n[Step 3] Comparing quotes...")
    time.sleep(0.5)
    best = min(state["quotes"], key=lambda q: q["total"])
    print(f"   Best quote: {best['vendor']} at €{best['total']:,}")
    print(f"   (Saves €{max(q['total'] for q in state['quotes']) - best['total']:,} "
          f"vs most expensive option)")
    return {"best_quote": best}

""" muokkaus"""
def route_approval(state: ProcurementState) -> str:
    total = state["best_quote"]["total"]
    if total > 10_000:
        return "approval"
    else:
        return "auto_approve"

"""muokkaus"""
def route_post_approval(state: ProcurementState) -> str:
    status = state["approval_status"].lower()

    if "reject" in status:
        return "rejected"
    else:
        return "approved"

def request_approval(state: ProcurementState) -> dict:
    """Step 4: Human-in-the-loop — request manager approval for orders > €10,000."""
    best = state["best_quote"]
    print("\n[Step 4] Order exceeds €10,000 — manager approval required!")
    print(f"   Sending approval request to manager...")
    amount_str = f"€{best['total']:,}"
    delivery_str = f"{best['delivery_days']} business days"
    print(f"   ┌─────────────────────────────────────────────┐")
    print(f"   │  APPROVAL NEEDED                            │")
    print(f"   │  Vendor:   {best['vendor']:<33}│")
    print(f"   │  Amount:   {amount_str:<33}│")
    print(f"   │  Items:    {best.get('product', 'laptops')}  │")
    print(f"   │  Delivery: {delivery_str:<33}│")
    print(f"   └─────────────────────────────────────────────┘")

    # ── THIS IS WHERE THE MAGIC HAPPENS ──
    # interrupt() freezes the entire graph state into the checkpoint store.
    # The process can now exit completely. When resumed later (even days later),
    # execution continues right here with the resume value.
    decision = interrupt({
        "message": f"Approve purchase of {best.get('product', 'laptops')} from {best['vendor']}",
        "vendor": best["vendor"],
        "amount": best["total"],
    })

    print(f"\n[Step 4] Manager responded: {decision}")
    return {"approval_status": decision}


def submit_purchase_order(state: ProcurementState) -> dict:
    """Step 5: Submit the purchase order to the ERP system."""
    if "reject" in state["approval_status"].lower():
        print("\n[Step 5] Purchase REJECTED by manager. Aborting.")
        return {"po_number": "REJECTED"}

    print("\n[Step 5] Submitting purchase order to ERP system...")
    time.sleep(1)
    po_number = "PO-2026-00342"
    print(f"   Purchase order created: {po_number}")
    print(f"   Vendor: {state['best_quote']['vendor']}")
    print(f"   Amount: €{state['best_quote']['total']:,}")
    return {"po_number": po_number}


def notify_employee(state: ProcurementState) -> dict:
    """Step 6: Use LLM to draft and send a notification to the employee."""
    print("\n[Step 6] Notifying employee...")

    if state["po_number"] == "REJECTED":
        prompt = (
            f"Write a brief, professional notification (2-3 sentences) to an employee "
            f"that their purchase request for 50 laptops was rejected by the manager. "
            f"Be empathetic but concise."
        )
    else:
        prompt = (
            f"Write a brief, professional notification (2-3 sentences) to an employee "
            f"that their purchase request has been approved and processed. "
            f"Details: 50 laptops from {state['best_quote']['vendor']}, "
            f"€{state['best_quote']['total']:,}, PO number {state['po_number']}, "
            f"delivery in {state['best_quote']['delivery_days']} business days."
        )

    response = llm.invoke(prompt)
    notification = response.content
    print(f"   Employee notification sent:")
    print(f"   \"{notification}\"")
    return {"notification": notification}




# ─── Build the graph ─────────────────────────────────────────────────────────
#
#   START → lookup_vendors → fetch_pricing → compare_quotes
#         → request_approval (INTERRUPT)
#         → submit_purchase_order → notify_employee → END

builder = StateGraph(ProcurementState)

builder.add_node("lookup_vendors", lookup_vendors)
builder.add_node("fetch_pricing", fetch_pricing)
builder.add_node("compare_quotes", compare_quotes)
builder.add_node("request_approval", request_approval)
builder.add_node("submit_purchase_order", submit_purchase_order)
builder.add_node("notify_employee", notify_employee)

builder.add_edge(START, "lookup_vendors")
builder.add_edge("lookup_vendors", "fetch_pricing")
builder.add_edge("fetch_pricing", "compare_quotes")
builder.add_conditional_edges(
    "compare_quotes",
    route_approval,
    {
        "approval": "request_approval",
        "auto_approve": "submit_purchase_order",
    }
)
#builder.add_edge("compare_quotes", "request_approval")
#builder.add_edge("request_approval", "submit_purchase_order")
builder.add_conditional_edges(
    "request_approval",
    route_post_approval,
    {
        "approved": "submit_purchase_order",
        "rejected": "notify_employee",
    }
)
builder.add_edge("submit_purchase_order", "notify_employee")
builder.add_edge("notify_employee", END)


# ─── Checkpointer (SQLite — survives process restarts!) ──────────────────────

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "procurement_checkpoints.db")
THREAD_ID = "procurement-thread-1"
config = {"configurable": {"thread_id": THREAD_ID}}


# ─── Main ────────────────────────────────────────────────────────────────────

def run_first_invocation(graph):
    """First run: employee submits request, agent does steps 1-3, then suspends."""
    print("=" * 60)
    print("  FIRST INVOCATION — Employee submits purchase request")
    print("=" * 60)
    print("\nEmployee request: \"Order 50 laptops for the new engineering team\"")

    result = graph.invoke(
        {"request": "Order 50 laptops for the new engineering team"},
        config,
    )

    # After interrupt, the graph returns with __interrupt__ info
    print("\n" + "=" * 60)
    print("AGENT SUSPENDED — waiting for manager approval")
    print("=" * 60)
    print("\n  The agent process can now exit completely.")
    print("  All state (vendors, pricing, best quote) is frozen in SQLite.")
    print(f"  Checkpoint DB: {DB_PATH}")
    print(f"  Thread ID: {THREAD_ID}")
    print("\n  In a real system, the manager gets a Slack/email notification.")
    print("  They might respond hours or even days later.\n")
    print("  To resume, run:")
    print(f"    python {os.path.basename(__file__)} --resume\n")


def run_second_invocation(graph):
    """Second run: manager approves, agent wakes up at step 5 with full context."""
    print("=" * 60)
    print("  SECOND INVOCATION — Manager approves (maybe days later!)")
    print("=" * 60)

    # Show that the state survived the process restart
    saved_state = graph.get_state(config)
    if not saved_state or not saved_state.values:
        print("\nNo saved state found! Run without --resume first.")
        return

    print("\nLoading state from checkpoint...")
    print(f"  ✓ Request: {saved_state.values.get('request', 'N/A')}")
    print(f"  ✓ Vendors found: {len(saved_state.values.get('vendors', []))}")
    print(f"  ✓ Quotes received: {len(saved_state.values.get('quotes', []))}")
    best = saved_state.values.get("best_quote", {})
    print(f"  ✓ Best quote: {best.get('vendor', 'N/A')} at €{best.get('total', 0):,}")
    print(f"\n  Steps 1-3 are NOT re-executed — their output is in the checkpoint!\n")

    # Resume with the manager's approval
    print("Manager clicks [APPROVE] ...")
    time.sleep(1)

    result = graph.invoke(
        Command(resume="Approved — go ahead with the purchase."),
        config,
    )

    print("\n" + "=" * 60)
    print("PROCUREMENT COMPLETE")
    print("=" * 60)
    print(f"\n  PO Number:    {result.get('po_number', 'N/A')}")
    print(f"  Vendor:       {result.get('best_quote', {}).get('vendor', 'N/A')}")
    print(f"  Total:        €{result.get('best_quote', {}).get('total', 0):,}")
    print(f"  Approval:     {result.get('approval_status', 'N/A')}")
    print()


if __name__ == "__main__":
    resume_mode = "--resume" in sys.argv

    # Clean start if not resuming
    if not resume_mode and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"(Cleaned up old checkpoint DB)")

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = builder.compile(checkpointer=checkpointer)

    try:
        if resume_mode:
            run_second_invocation(graph)
        else:
            run_first_invocation(graph)
    finally:
        conn.close()
