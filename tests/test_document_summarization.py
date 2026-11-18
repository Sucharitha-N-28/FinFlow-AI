
from backend.app.document_processing.document_processor import process_document
from backend.app.summarization.summarizer import summarize_document
from backend.app.comparison.comparison_engine import extract_financial_data


def test_summarization(file_path, file_type):
    result = process_document(file_path, file_type)
    content = result["content"]

    if file_type == ".pdf":
        pages = content["pages"]
        document_text = "\n".join(
            page["text"] for page in pages
        )
    else:
        pages = None
        document_text = content["text"]

    financial_data = extract_financial_data(
        document_text=document_text,
        document_name=result["filename"],
        model="qwen2.5:7b",
        document_pages=pages
    )

    summary = summarize_document(
        document_text=document_text,
        pages=pages,
        financial_data=financial_data
    )

    print(f"\n{file_type.upper()} SUMMARY")
    print("------------------------")
    print("Filename:", result["filename"])
    print(summary)


# Test PDF
test_summarization(
    "sample_documents/valid/valid_test.pdf",
    ".pdf"
)

# Test TXT
test_summarization(
    "sample_documents/valid/valid_test.txt",
    ".txt"
)

# Test IMAGE
test_summarization(
    "sample_documents/valid/financial_test2.png",
    ".png"
)
