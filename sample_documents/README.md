# FinFlow AI – Sample Documents

This directory contains synthetic financial documents and test files used to evaluate the document processing, financial extraction, and input validation capabilities of FinFlow AI.

The samples are organized into two categories:

- `valid/` – Documents used to test successful processing and financial information extraction.
- `test_cases/` – Files used to test invalid inputs, unsupported formats, and error-handling mechanisms.

**Note:** These are synthetic testing documents. The original company-provided documents are not included in this repository.

---

## 1. Valid Sample Documents

The `valid/` directory contains documents in PDF, TXT, and PNG formats.

| File | Format | Testing Purpose | Expected Result |
|---|---|---|---|
| `financial_test.png` | PNG | Test financial information extraction from an image. | Extract financial details such as company name, financial year, assets, liabilities, revenue, expenses, and net profit, where available. |
| `financial_test2.png` | PNG | Test image processing using an additional financial image. | Process the image and return the financial information present in the document. |
| `invoice.txt` | TXT | Test extraction from a text-based invoice. | Identify available invoice details, such as invoice number, date, company information, and financial amounts. |
| `test_document.txt` | TXT | Test general text document processing. | Read and process the text content and identify relevant financial information, if available. |
| `valid_test.pdf` | PDF | Test PDF document processing. | Successfully read the PDF and extract the available document content. |
| `valid_test.txt` | TXT | Test structured financial data extraction. | Extract company name, financial year, revenue, expenses, assets, liabilities, and net profit where present. |

### How to Test Valid Documents

1. Start the FinFlow AI backend and frontend.
2. Open the application in your browser.
3. Select or upload a document from the `valid/` directory.
4. Enter an appropriate instruction in the prompt box.
5. Submit the request.
6. Review the detected intent, execution steps, selected module, model, and final result.

**Example prompts:**

| Testing Scenario | Example Prompt |
|---|---|
| Financial extraction | Extract all available financial information from this document. |
| Classification | Classify this financial document. |
| Summarization | Summarize this financial document and highlight the key figures. |
| Question answering | What are the total revenue, total expenses, and net profit? |
| Image processing | Extract the financial information from this image. |

**Expected behavior:** The application should process supported documents and return the relevant results based on the requested task and the information available in the document.

---

## 2. Error-Handling Test Cases

The `test_cases/` directory contains deliberately created files for testing input validation and error handling.

| File | Format | Testing Purpose | Expected Result |
|---|---|---|---|
| `empty.pdf` | PDF | Test an empty PDF file. | Reject the file and display an appropriate validation error. |
| `fake_test.pdf` | PDF | Test a file containing invalid PDF content. | Detect invalid PDF content and reject processing. |
| `oversized.txt` | TXT | Test the maximum file-size restriction. | Reject the file if it exceeds the configured size limit. |
| `uncertain_report.txt` | TXT | Test uncertain document validation. | Reject or flag the document when its financial relevance cannot be established. |
| `unsupported.docx` | DOCX | Test an unsupported file format. | Display an unsupported file type error. |
| `zerobyte_test.docx` | DOCX | Test a zero-byte unsupported file. | Reject the file without attempting document processing. |
| `weather_report.txt` | TXT | Test a non-financial document. | Identify the document as uncertain or non-financial and avoid inappropriate financial extraction. |

### How to Test Error Handling

1. Open the FinFlow AI application.
2. Select a file from the `test_cases/` directory.
3. Enter a suitable instruction, such as:

   `Extract financial information from this document.`

4. Submit the request.
5. Verify whether the application handles the input appropriately.

**Expected behavior:** Invalid, unsupported, empty, oversized, or irrelevant documents should be handled with appropriate validation messages instead of being processed as valid financial documents.

---

## 3. Supported Input Formats

The following input formats have been tested using the synthetic sample documents.

| Format | Sample File | Test Status |
|---|---|---|
| PDF | `valid_test.pdf` | Passed |
| TXT | `valid_test.txt` | Passed |
| PNG | `financial_test.png` | Passed |
| JPG/JPEG | `financial_test.jpg` | Passed |

**Note:** The JPG test was performed separately. The JPG sample is not currently listed in the `valid/` directory.

---

## 4. Supported Processing Modules

FinFlow AI provides the following processing capabilities:

| Module | Purpose |
|---|---|
| Document Extraction | Extract financial information from uploaded documents. |
| Document Classification | Identify the type of financial document. |
| Document Summarization | Generate concise summaries highlighting important financial information. |
| Question Answering | Answer user questions using the uploaded document content. |
| Document Comparison | Compare financial information across multiple documents. |

Users can provide instructions through the prompt interface to execute the required processing tasks.

---

## 5. Testing Notes

- Use the `valid/` directory to test successful document processing.
- Use the `test_cases/` directory to verify input validation and error handling.
- Expected results depend on the information actually present in each document.
- Missing financial values should not be assumed or treated as zero.
- The application may return unavailable fields when the requested information is not present in the source document.

---

## 6. Important Information

These sample files are provided for demonstration, development, and testing purposes.

The original company-provided financial documents used during project evaluation are intentionally excluded from this repository.