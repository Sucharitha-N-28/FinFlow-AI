
from backend.app.orchestrator.task_executor import extract_document_text


# Test TXT document
txt_document = {
    "file_name": "sample.txt",
    "file_type": ".txt",
    "extracted_content": {
        "filename": "sample.txt",
        "text": "Company: ABC Technologies\nRevenue: 500000"
    }
}

print("TXT OUTPUT:")
print(extract_document_text(txt_document))


# Test PDF document
pdf_document = {
    "file_name": "sample.pdf",
    "file_type": ".pdf",
    "extracted_content": {
        "total_pages": 2,
        "pages": [
            {"page_number": 1, "text": "Revenue: 500000"},
            {"page_number": 2, "text": "Expenses: 320000"}
        ]
    }
}

print("\nPDF OUTPUT:")
print(extract_document_text(pdf_document))


# Test image document
image_document = {
    "file_name": "sample.png",
    "file_type": ".png",
    "extracted_content": {
        "filename": "sample.png",
        "text": "Net Profit: 180000"
    }
}

print("\nIMAGE OUTPUT:")
print(extract_document_text(image_document))

from backend.app.orchestrator.task_executor import execute_task


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


# Test 1: Extraction
print("\nTEST 1: EXTRACTION")

result = execute_task(
    "extraction",
    documents[:1],
    "Extract the document content"
)

print(result)


# Test 2: Classification
print("\nTEST 2: CLASSIFICATION")

result = execute_task(
    "classification",
    documents[:1],
    "Classify the document"
)

print(result)


# Test 3: Summarization
print("\nTEST 3: SUMMARIZATION")

result = execute_task(
    "summarization",
    documents[:1],
    "Summarize the document"
)

print(result)


# Test 4: Question Answering
print("\nTEST 4: QUESTION ANSWERING")

result = execute_task(
    "question_answering",
    documents[:1],
    "What is the total revenue?"
)

print(result)


# Test 5: Comparison
print("\nTEST 5: COMPARISON")

result = execute_task(
    "comparison",
    documents,
    "Compare these documents"
)

print(result)
