# AI PDF / Invoice Analyzer API

[![Tests](https://github.com/vodolij888Igor/ai-pdf-invoice-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/vodolij888Igor/ai-pdf-invoice-analyzer/actions/workflows/tests.yml)

## Project Overview

This project is a portfolio-ready FastAPI backend that accepts extracted invoice text and returns structured invoice analysis using the **OpenAI API** (real LLM calls, not placeholder regex).  
It demonstrates backend API design, input/output validation, and AI-ready service architecture for automation workflows.

## Business Use Case

Accounts payable teams often receive invoices in inconsistent formats.  
This API standardizes invoice data into predictable fields so downstream systems can automate:

- invoice triage
- payment scheduling
- finance dashboard reporting
- approval routing

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- OpenAI Python SDK
- python-dotenv
- pytest, httpx (automated tests)

## Running Tests

Tests mock the OpenAI client and do not call the real API (safe without a key).

```bash
pip install -r requirements.txt
pytest
```

## Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── schemas/
│   │   └── invoice_schema.py
│   └── services/
│       └── invoice_service.py
├── tests/
│   ├── conftest.py
│   └── test_analyze_invoice_text.py
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

## Setup Instructions

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template and set your OpenAI key:

   ```bash
   copy .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY` to a valid key. Without it, `POST /analyze-invoice-text` returns **503** with a clear error message.

4. Run the API:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open docs:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoint

### `POST /analyze-invoice-text`

Accepts simulated extracted invoice text and returns structured invoice analysis produced by OpenAI. If the OpenAI API fails, the server returns **502** with a clear error detail.

### Sample Request

```json
{
  "document_name": "invoice_001.pdf",
  "invoice_text": "Invoice #INV-1001. Vendor: ABC Supplies. Customer: Northwind LLC. Total: $1,245.50. Due date: 2026-05-15. Items: Office chairs, desks, shipping."
}
```

### Sample Response

```json
{
  "document_name": "invoice_001.pdf",
  "invoice_number": "INV-1001",
  "vendor_name": "ABC Supplies",
  "customer_name": "Northwind LLC",
  "total_amount": 1245.5,
  "currency": "USD",
  "due_date": "2026-05-15",
  "category": "office_supplies",
  "priority": "medium",
  "summary": "Invoice from ABC Supplies to Northwind LLC for Office chairs, desks, shipping.",
  "recommended_action": "Review and schedule payment before the due date."
}
```

## Screenshot

The screenshot below shows a successful POST /analyze-invoice-text request in FastAPI Swagger UI with a 200 response.

![Swagger UI successful invoice analysis response](docs/images/swagger-invoice-analysis-code-200.png)

## API Usage Examples

**Scenario:** A company receives invoice PDFs from vendors. Text is extracted upstream (for example with a PDF library or OCR pipeline). That extracted text is sent to this API so finance teams obtain **structured payment-ready fields**—amounts, parties, due dates, and suggested actions—in a consistent JSON shape.

### cURL (`POST /analyze-invoice-text`)

With the server running locally (`uvicorn app.main:app --reload`), send a JSON body that includes `document_name` and `invoice_text`:

```bash
curl -X POST "http://127.0.0.1:8000/analyze-invoice-text" \
  -H "Content-Type: application/json" \
  -d '{
  "document_name": "invoice_001.pdf",
  "invoice_text": "Invoice #INV-1001. Vendor: ABC Supplies. Customer: Northwind LLC. Total: $1,245.50. Due date: 2026-05-15. Items: Office chairs, desks, shipping."
}'
```

Ensure `OPENAI_API_KEY` is configured; otherwise the API responds with **503**.

### Example successful JSON response

When analysis succeeds, the response matches the API schema (values reflect the model’s interpretation of your text):

```json
{
  "document_name": "invoice_001.pdf",
  "invoice_number": "INV-1001",
  "vendor_name": "ABC Supplies",
  "customer_name": "Northwind LLC",
  "total_amount": 1245.50,
  "currency": "USD",
  "due_date": "2026-05-15",
  "category": "office_supplies",
  "priority": "medium",
  "summary": "Invoice from ABC Supplies to Northwind LLC for office furniture and related charges.",
  "recommended_action": "Review and schedule payment before the due date."
}
```

### Postman

1. Create a new request with **Method:** `POST` and **URL:** `http://127.0.0.1:8000/analyze-invoice-text`.
2. Under **Headers**, add `Content-Type` with value `application/json`.
3. Under **Body**, choose **raw** and **JSON**, then paste a payload with `document_name` and `invoice_text` (same structure as the cURL example).
4. Click **Send**. In the response, verify key fields for payment workflows: `invoice_number`, `vendor_name`, `total_amount`, `due_date`, `category`, `priority`, `summary`, and `recommended_action`.

## Architecture

- FastAPI app exposes a `POST /analyze-invoice-text` endpoint.
- Pydantic schemas validate request and response data.
- Service layer handles OpenAI invoice analysis logic.
- Environment variables are loaded from `.env`.
- Swagger UI provides interactive API testing.
- Tests mock the AI layer and verify API behavior safely.
- The current version simulates extracted PDF invoice text through JSON input.

```text
Client / Swagger / Postman
        ↓
FastAPI route: POST /analyze-invoice-text
        ↓
Pydantic validation
        ↓
Invoice analysis service layer
        ↓
OpenAI API
        ↓
JSON response: invoice_number, vendor_name, total_amount, due_date, category, priority, recommended_action
```

## Limitations

- This is a backend portfolio project, not a complete invoice management platform yet.
- It does not upload PDF files yet.
- It does not extract text from real PDF files yet.
- It does not store analyzed invoices in a database yet.
- It does not include authentication yet.
- It does not include a frontend dashboard yet.
- It is designed as a clean local API demo.
- Requires a valid `OPENAI_API_KEY` (no local/offline model).
- Category and priority are guided by the model and normalized to allowed values when needed.
- Future versions could add PDF upload, OCR/text extraction, database storage, authentication, deployment, scheduled invoice processing, and a frontend dashboard.

## Future Improvements

- Optional Azure OpenAI or multi-provider support
- Add PDF upload support and extraction layer
- Add OCR support for scanned invoices
- Store results in a database (PostgreSQL)
- Add authentication and role-based access
- Expand CI pipeline (e.g. GitHub Actions running `pytest`)

