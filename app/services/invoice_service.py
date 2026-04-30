import re

from app.schemas.invoice_schema import InvoiceAnalysisResponse


def analyze_invoice_text(document_name: str, invoice_text: str) -> InvoiceAnalysisResponse:
    """
    Placeholder invoice analysis logic.

    This function intentionally uses deterministic pattern matching for the first
    portfolio version. Later, you can replace this with an LLM-backed service.
    """

    # Simple regex helpers to keep the logic readable and easy to upgrade.
    invoice_number_match = re.search(r"Invoice\s*#\s*([A-Za-z0-9\-]+)", invoice_text, re.IGNORECASE)
    vendor_match = re.search(r"Vendor:\s*([^\.]+)", invoice_text, re.IGNORECASE)
    customer_match = re.search(r"Customer:\s*([^\.]+)", invoice_text, re.IGNORECASE)
    total_match = re.search(r"Total:\s*\$?([0-9,]+(?:\.[0-9]{1,2})?)", invoice_text, re.IGNORECASE)
    due_date_match = re.search(r"Due\s*date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", invoice_text, re.IGNORECASE)
    items_match = re.search(r"Items:\s*([^\.]+)", invoice_text, re.IGNORECASE)

    invoice_number = invoice_number_match.group(1).strip() if invoice_number_match else "UNKNOWN"
    vendor_name = vendor_match.group(1).strip() if vendor_match else "Unknown Vendor"
    customer_name = customer_match.group(1).strip() if customer_match else "Unknown Customer"
    total_amount = float(total_match.group(1).replace(",", "")) if total_match else 0.0
    due_date = due_date_match.group(1) if due_date_match else "N/A"
    items_text = items_match.group(1).strip().lower() if items_match else ""

    # Basic category and priority heuristics for demo purposes.
    if any(keyword in items_text for keyword in ["chair", "desk", "office", "stationery", "supply"]):
        category = "office_supplies"
    elif any(keyword in items_text for keyword in ["software", "subscription", "license"]):
        category = "software_services"
    else:
        category = "general_expense"

    if total_amount >= 5000:
        priority = "high"
    elif total_amount >= 1000:
        priority = "medium"
    else:
        priority = "low"

    summary = (
        f"Invoice from {vendor_name} to {customer_name} "
        f"for {items_match.group(1).strip() if items_match else 'listed items'}."
    )
    recommended_action = (
        "Review and schedule payment before the due date."
        if due_date != "N/A"
        else "Review invoice details and assign a due date before payment scheduling."
    )

    return InvoiceAnalysisResponse(
        document_name=document_name,
        invoice_number=invoice_number,
        vendor_name=vendor_name,
        customer_name=customer_name,
        total_amount=total_amount,
        currency="USD",
        due_date=due_date,
        category=category,
        priority=priority,
        summary=summary,
        recommended_action=recommended_action,
    )
