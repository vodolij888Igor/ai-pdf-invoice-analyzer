"""Tests for POST /analyze-invoice-text (OpenAI client mocked; no network)."""

from unittest.mock import patch

import pytest
from openai import OpenAIError

from tests.conftest import (
    MOCK_OPENAI_JSON,
    VALID_DOCUMENT_NAME,
    VALID_INVOICE_TEXT,
    build_mock_openai_completion,
)

REQUIRED_RESPONSE_FIELDS = (
    "document_name",
    "invoice_number",
    "vendor_name",
    "customer_name",
    "total_amount",
    "currency",
    "due_date",
    "category",
    "priority",
    "summary",
    "recommended_action",
)

ALLOWED_PRIORITIES = {"low", "medium", "high"}


@pytest.fixture(autouse=True)
def _ensure_fake_openai_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Default: pretend a key is set so import-time .env does not trigger real calls.
    Tests that need missing key override this with delenv.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-a-real-key")


class TestAnalyzeInvoiceTextSuccess:
    @patch("app.services.invoice_service.OpenAI")
    def test_success_returns_200(
        self,
        mock_openai_cls: object,
        api_client,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-a-real-key")

        mock_instance = mock_openai_cls.return_value
        mock_instance.chat.completions.create.return_value = build_mock_openai_completion(
            MOCK_OPENAI_JSON
        )

        response = api_client.post(
            "/analyze-invoice-text",
            json={
                "document_name": VALID_DOCUMENT_NAME,
                "invoice_text": VALID_INVOICE_TEXT,
            },
        )

        assert response.status_code == 200
        data = response.json()

        for field in REQUIRED_RESPONSE_FIELDS:
            assert field in data, f"Missing field: {field}"

        assert isinstance(data["total_amount"], (int, float))
        assert data["priority"] in ALLOWED_PRIORITIES
        assert data["document_name"] == VALID_DOCUMENT_NAME


class TestAnalyzeInvoiceTextValidation:
    def test_missing_invoice_text_returns_422(self, api_client) -> None:
        response = api_client.post(
            "/analyze-invoice-text",
            json={"document_name": VALID_DOCUMENT_NAME},
        )
        assert response.status_code == 422

    def test_missing_document_name_returns_422(self, api_client) -> None:
        response = api_client.post(
            "/analyze-invoice-text",
            json={"invoice_text": VALID_INVOICE_TEXT},
        )
        assert response.status_code == 422

    def test_invoice_text_too_short_returns_422(self, api_client) -> None:
        response = api_client.post(
            "/analyze-invoice-text",
            json={
                "document_name": VALID_DOCUMENT_NAME,
                "invoice_text": "short text",
            },
        )
        assert response.status_code == 422

    def test_empty_document_name_returns_422(self, api_client) -> None:
        response = api_client.post(
            "/analyze-invoice-text",
            json={"document_name": "", "invoice_text": VALID_INVOICE_TEXT},
        )
        assert response.status_code == 422


class TestAnalyzeInvoiceTextServiceErrors:
    def test_missing_openai_api_key_returns_503(
        self,
        api_client,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        response = api_client.post(
            "/analyze-invoice-text",
            json={
                "document_name": VALID_DOCUMENT_NAME,
                "invoice_text": VALID_INVOICE_TEXT,
            },
        )

        assert response.status_code == 503
        detail = response.json().get("detail", "")
        assert "OPENAI_API_KEY" in detail

    @patch("app.services.invoice_service.OpenAI")
    def test_openai_api_failure_returns_502(
        self,
        mock_openai_cls: object,
        api_client,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-a-real-key")

        mock_instance = mock_openai_cls.return_value
        mock_instance.chat.completions.create.side_effect = OpenAIError("upstream failure")

        response = api_client.post(
            "/analyze-invoice-text",
            json={
                "document_name": VALID_DOCUMENT_NAME,
                "invoice_text": VALID_INVOICE_TEXT,
            },
        )

        assert response.status_code == 502
        assert "OpenAI" in response.json().get("detail", "")
