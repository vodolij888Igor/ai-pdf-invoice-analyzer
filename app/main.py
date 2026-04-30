from fastapi import FastAPI

from app.schemas.invoice_schema import InvoiceAnalysisRequest, InvoiceAnalysisResponse
from app.services.invoice_service import analyze_invoice_text


app = FastAPI(
    title="AI PDF / Invoice Analyzer API",
    description=(
        "Portfolio backend API that accepts extracted invoice text and returns "
        "structured, AI-style analysis."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    """Simple health endpoint for quick environment checks."""

    return {"status": "ok"}


@app.post("/analyze-invoice-text", response_model=InvoiceAnalysisResponse)
def analyze_invoice(payload: InvoiceAnalysisRequest) -> InvoiceAnalysisResponse:
    """
    Analyze extracted invoice text and return normalized structured fields.
    """

    return analyze_invoice_text(
        document_name=payload.document_name,
        invoice_text=payload.invoice_text,
    )
