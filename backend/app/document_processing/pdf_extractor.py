
import pymupdf


def extract_pdf_content(file_path):
    """
    Extract PDF text, metadata and word-level coordinates.

    Existing page text output is preserved for compatibility.
    Word coordinates are additionally stored for table analysis.
    """

    document = pymupdf.open(file_path)

    try:
        extracted_pages = []

        for page_number in range(document.page_count):

            page = document.load_page(page_number)

            # Existing text extraction
            page_text = page.get_text("text", sort=True)

            # Extract individual words with their coordinates
            raw_words = page.get_text("words", sort=True)

            words = []

            for word in raw_words:

                x0, y0, x1, y1, text, block_no, line_no, word_no = word

                words.append({
                    "text": text,
                    "x0": round(x0, 2),
                    "y0": round(y0, 2),
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "block_no": block_no,
                    "line_no": line_no,
                    "word_no": word_no
                })

            extracted_pages.append({
                "page_number": page_number + 1,
                "text": page_text,
                "words": words
            })

        return {
            "total_pages": document.page_count,
            "metadata": document.metadata,
            "pages": extracted_pages
        }

    finally:
        document.close()


if __name__ == "__main__":

    result = extract_pdf_content(
        "sample_documents/sample-docs/Document3.pdf"
    )

    print("\nPDF EXTRACTION RESULT")
    print("---------------------")

    print("Total pages:", result["total_pages"])

    print("\nMetadata:")
    print(result["metadata"])

    for page in result["pages"]:

        print("\nPage number:", page["page_number"])
        print("Extracted text:")
        print(page["text"])

        print("Total extracted words:", len(page["words"]))
