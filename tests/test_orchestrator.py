
from backend.app.orchestrator.orchestrator import orchestrate_request


documents = [
    {
        "document_id": "doc-001",
        "file_name": "report1.txt",
        "file_type": ".txt",
        "extracted_content": {
            "filename": "report1.txt",
            "text": (
                "Company: ABC Technologies\n"
                "Financial Year: 2025\n"
                "Revenue: 500000\n"
                "Expenses: 320000\n"
                "Net Profit: 180000"
            )
        }
    },
    {
        "document_id": "doc-002",
        "file_name": "report2.txt",
        "file_type": ".txt",
        "extracted_content": {
            "filename": "report2.txt",
            "text": (
                "Company: XYZ Technologies\n"
                "Financial Year: 2025\n"
                "Revenue: 650000\n"
                "Expenses: 400000\n"
                "Net Profit: 250000"
            )
        }
    }
]


# Test 1: Single intent
print("\nTEST 1: SUMMARIZATION")

result = orchestrate_request(
    "Summarize the financial report.",
    documents[:1]
)

print(result)


# Test 2: Multiple intents
print("\nTEST 2: CLASSIFICATION AND SUMMARIZATION")

result = orchestrate_request(
    "Classify and summarize the financial report.",
    documents[:1]
)

print(result)


# Test 3: Ambiguous request
print("\nTEST 3: AMBIGUOUS REQUEST")

result = orchestrate_request(
    "Process this financial document.",
    documents[:1]
)

print(result)


# Test 4: Unsupported request
print("\nTEST 4: UNSUPPORTED REQUEST")

result = orchestrate_request(
    "Tell me the weather forecast.",
    documents[:1]
)

print(result)
