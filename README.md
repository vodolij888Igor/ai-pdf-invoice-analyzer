# AI PDF / Invoice Analyzer API

## Project Overview

This project is a portfolio-ready FastAPI backend that accepts extracted invoice text and returns structured invoice analysis.  
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

## Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── schemas/
│   │   └── invoice_schema.py
│   └── services/
│       └── invoice_service.py
├── .env.example
├── .gitignore
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

3. (Optional) Copy environment template:

   ```bash
   copy .env.example .env
   ```

4. Run the API:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open docs:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoint

### `POST /analyze-invoice-text`

Accepts simulated extracted invoice text and returns structured invoice analysis.

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

## Current Limitations

- Uses placeholder regex-based logic (no real LLM integration yet)
- No PDF upload endpoint yet
- No real PDF text extraction pipeline yet
- Currency is currently defaulted to USD
- Category and priority are based on simple heuristics

## Future Improvements

- Integrate real LLM analysis (OpenAI or Azure OpenAI)
- Add PDF upload support and extraction layer
- Add OCR support for scanned invoices
- Store results in a database (PostgreSQL)
- Add authentication and role-based access
- Add unit/integration tests and CI pipeline

