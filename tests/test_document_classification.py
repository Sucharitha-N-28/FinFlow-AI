
from backend.app.document_processing.document_processor import process_document
from backend.app.classification.classifier import classify_document


def test_classification(file_path, file_type):
    result = process_document(file_path, file_type)

    # Extract text from the processed document
    content = result["content"]

    if file_type == ".pdf":
        document_text = "\n".join(
            page["text"] for page in content["pages"]
        )
    elif file_type == ".txt":
        document_text = content["text"]
    else:
        document_text = content["text"]

    category = classify_document(document_text)

    print(f"\n{file_type.upper()} CLASSIFICATION")
    print("------------------")
    print("Filename:", result["filename"])
    print("Category:", category)


# Test PDF document
test_classification(
    "sample_documents/valid/valid_test.pdf",
    ".pdf"
)

# Test TXT document
test_classification(
    "sample_documents/valid/valid_test.txt",
    ".txt"
)

# Test image document
test_classification(
    "sample_documents/valid/financial_test2.png",
    ".png"
)
