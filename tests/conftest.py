"""Shared fixtures and helpers for API tests (no real OpenAI calls)."""

import json
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_DOCUMENT_NAME = "invoice_001.pdf"
VALID_INVOICE_TEXT = (
    "Invoice #INV-1001. Vendor: ABC Supplies. Customer: Northwind LLC. "
    "Total: $1,245.50. Due date: 2026-05-15. Items: Office chairs, desks, shipping."
)

MOCK_OPENAI_JSON = {
    "invoice_number": "INV-1001",
    "vendor_name": "ABC Supplies",
    "customer_name": "Northwind LLC",
    "total_amount": 1245.5,
    "currency": "USD",
    "due_date": "2026-05-15",
    "category": "office_supplies",
    "priority": "medium",
    "summary": "Invoice from ABC Supplies to Northwind LLC for office items.",
    "recommended_action": "Review and schedule payment before the due date.",
}


def build_mock_openai_completion(content_dict: dict) -> MagicMock:
    """Return a completion-shaped mock matching openai SDK structure."""
    message = MagicMock()
    message.content = json.dumps(content_dict)

    choice = MagicMock()
    choice.message = message

    completion = MagicMock()
    completion.choices = [choice]
    return completion


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)
