
from backend.app.comparison.comparison_engine import compare_documents


# Test financial records
financial_records = [
    {
        "file_name": "Document1.txt",
        "financial_data": {
            "document_type": "GENERAL",
            "financial_year": "2024",
            "total_revenue": 500000,
            "total_expenses": 320000,
            "net_profit_or_loss": 180000
        }
    },
    {
        "file_name": "Document2.txt",
        "financial_data": {
            "document_type": "GENERAL",
            "financial_year": "2025",
            "total_revenue": 650000,
            "total_expenses": 400000,
            "net_profit_or_loss": 250000
        }
    }
]


# Test 1: Compare two documents
comparison = compare_documents(
    financial_records=financial_records,
    model="qwen2.5:7b",
    document_names=["Document1.txt", "Document2.txt"]
)

print("\nTEST 1 - DOCUMENT COMPARISON")
print("----------------------------")
print(comparison)


# Test 2: Only one document
try:
    compare_documents(financial_records[:1])
except ValueError as error:
    print("\nTEST 2 - SINGLE DOCUMENT")
    print(error)


# Test 3: Empty document list
try:
    compare_documents([])
except ValueError as error:
    print("\nTEST 3 - EMPTY DOCUMENT LIST")
    print(error)


# Test 4: Invalid financial data
try:
    compare_documents([
        {"file_name": "Document1.txt", "financial_data": {}},
        {"file_name": "Document2.txt", "financial_data": None}
    ])
except ValueError as error:
    print("\nTEST 4 - INVALID FINANCIAL DATA")
    print(error)
