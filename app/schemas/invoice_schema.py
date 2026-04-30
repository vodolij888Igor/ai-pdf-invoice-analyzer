from pydantic import BaseModel, Field


class InvoiceAnalysisRequest(BaseModel):
    """
    Incoming payload that simulates text already extracted from a PDF invoice.
    """

    document_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original invoice file name.",
        examples=["invoice_001.pdf"],
    )
    invoice_text: str = Field(
        ...,
        min_length=20,
        description="Raw invoice text extracted from the document.",
        examples=[
            "Invoice #INV-1001. Vendor: ABC Supplies. Customer: Northwind LLC. "
            "Total: $1,245.50. Due date: 2026-05-15. Items: Office chairs, desks, shipping."
        ],
    )


class InvoiceAnalysisResponse(BaseModel):
    """
    Structured analysis returned by the AI invoice analyzer service.
    """

    document_name: str
    invoice_number: str
    vendor_name: str
    customer_name: str
    total_amount: float
    currency: str
    due_date: str
    category: str
    priority: str
    summary: str
    recommended_action: str
