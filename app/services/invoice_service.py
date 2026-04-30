import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app.schemas.invoice_schema import InvoiceAnalysisResponse

# Load .env once when this module is imported (safe for uvicorn reload workers).
load_dotenv()

ALLOWED_CATEGORIES = frozenset(
    {
        "office_supplies",
        "software",
        "contractor_services",
        "utilities",
        "shipping",
        "marketing",
        "travel",
        "other",
    }
)
ALLOWED_PRIORITIES = frozenset({"low", "medium", "high"})


class InvoiceAnalysisConfigError(Exception):
    """Raised when required configuration is missing (maps to HTTP 503)."""


class InvoiceAnalysisOpenAIError(Exception):
    """Raised when the OpenAI API call fails (maps to HTTP 502)."""


def _normalize_category(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_").replace("-", "_")
    if cleaned in ALLOWED_CATEGORIES:
        return cleaned
    aliases = {
        "software_services": "software",
        "it": "software",
        "saas": "software",
        "freight": "shipping",
        "logistics": "shipping",
    }
    return aliases.get(cleaned, "other")


def _normalize_priority(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned in ALLOWED_PRIORITIES:
        return cleaned
    return "medium"


def _build_messages(document_name: str, invoice_text: str) -> list[dict[str, str]]:
    system = (
        "You are an invoice analysis assistant. Extract structured data from the invoice text. "
        "Respond with a single JSON object only (no markdown fences). "
        "Use these exact keys: invoice_number, vendor_name, customer_name, total_amount, "
        "currency, due_date, category, priority, summary, recommended_action.\n\n"
        "Rules:\n"
        "- total_amount: numeric only (no currency symbols).\n"
        "- currency: ISO-like code (e.g. USD, EUR); infer from text if possible.\n"
        "- due_date: YYYY-MM-DD if known, else a short string like N/A or Unknown.\n"
        "- category must be exactly one of: office_supplies, software, contractor_services, "
        "utilities, shipping, marketing, travel, other.\n"
        "- priority must be exactly one of: low, medium, high (use amount and urgency cues).\n"
        "- summary: one concise sentence.\n"
        "- recommended_action: one actionable sentence for accounts payable.\n"
    )
    user = f"Document name: {document_name}\n\nInvoice text:\n{invoice_text}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _parse_openai_json(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise InvoiceAnalysisOpenAIError(
            "OpenAI returned invalid JSON; cannot complete invoice analysis."
        ) from exc


def analyze_invoice_text(document_name: str, invoice_text: str) -> InvoiceAnalysisResponse:
    """
    Analyze invoice text using OpenAI and return a validated structured response.

    Raises InvoiceAnalysisConfigError if OPENAI_API_KEY is not set.
    Raises InvoiceAnalysisOpenAIError if the OpenAI request fails or output is unusable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        raise InvoiceAnalysisConfigError(
            "Invoice analysis is unavailable: OPENAI_API_KEY is not set. "
            "Add it to your environment or .env file."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key.strip())

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=_build_messages(document_name, invoice_text),
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except OpenAIError as exc:
        raise InvoiceAnalysisOpenAIError(
            "OpenAI request failed; invoice analysis could not be completed. "
            "Please try again later."
        ) from exc

    choice = completion.choices[0] if completion.choices else None
    if not choice or not choice.message or not choice.message.content:
        raise InvoiceAnalysisOpenAIError(
            "OpenAI returned an empty response; invoice analysis could not be completed."
        )

    raw = _parse_openai_json(choice.message.content.strip())

    try:
        return InvoiceAnalysisResponse(
            document_name=document_name,
            invoice_number=str(raw.get("invoice_number", "")).strip() or "UNKNOWN",
            vendor_name=str(raw.get("vendor_name", "")).strip() or "Unknown Vendor",
            customer_name=str(raw.get("customer_name", "")).strip() or "Unknown Customer",
            total_amount=float(raw.get("total_amount", 0) or 0),
            currency=str(raw.get("currency", "USD")).strip() or "USD",
            due_date=str(raw.get("due_date", "N/A")).strip() or "N/A",
            category=_normalize_category(str(raw.get("category", "other"))),
            priority=_normalize_priority(str(raw.get("priority", "medium"))),
            summary=str(raw.get("summary", "")).strip() or "No summary available.",
            recommended_action=str(raw.get("recommended_action", "")).strip()
            or "Review the invoice and take appropriate action.",
        )
    except (TypeError, ValueError) as exc:
        raise InvoiceAnalysisOpenAIError(
            "OpenAI returned data that could not be mapped to the invoice schema."
        ) from exc
