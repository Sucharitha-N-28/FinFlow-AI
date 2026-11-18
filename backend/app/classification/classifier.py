
import re
import ollama
from ollama import ResponseError


def _get_representative_text(document_text: str) -> str:
    """
    Get representative portions of the document.

    Useful for long documents such as annual reports
    and bank statements.
    """

    text = re.sub(r"\s+", " ", document_text).strip()

    if len(text) <= 20000:
        return text

    first_part = text[:8000]

    middle_start = len(text) // 2 - 2000
    middle_part = text[middle_start:middle_start + 4000]

    last_part = text[-8000:]

    return " ".join([
        first_part,
        middle_part,
        last_part
    ])


def _contains(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def _classify_using_document_structure(text: str):
    """
    Identify common financial document types using
    their content and structure.

    Returns None when the document type is unclear.
    """

    # 1. Commercial Invoice
    invoice_score = sum([
        _contains(r"\bcommercial invoice\b", text),
        _contains(r"\binvoice\s*(no|number)\b", text),
        _contains(r"\bunit price\b", text),
        _contains(r"\bsales value\b", text),
        _contains(r"\bcustoms value\b", text),
        _contains(r"\bconsignor\b", text),
        _contains(r"\bconsignee\b", text)
    ])

    if invoice_score >= 3:
        return "Commercial Invoice"

    # 2. Bank Statement
    bank_score = sum([
        _contains(r"\btxn date\b|\btransaction date\b", text),
        _contains(r"\bvalue date\b", text),
        _contains(r"\bcheque no\b|\bcheck no\b", text),
        _contains(r"\bdebit\b", text),
        _contains(r"\bcredit\b", text),
        _contains(r"\bbalance\b", text),
        _contains(r"\bbranch code\b", text)
    ])

    if bank_score >= 5:
        return "Bank Statement"

    # 3. Cash Flow Statement
    cash_flow_score = sum([
        _contains(r"\bcash flow statement\b", text),
        _contains(r"\bcash flow from operating activities\b", text),
        _contains(r"\bcash flow from investing activities\b", text),
        _contains(r"\bcash flow from financing activities\b", text),
        _contains(r"\bnet increase.*cash\b", text),
        _contains(r"\bcash and cash equivalents\b", text)
    ])

    if cash_flow_score >= 2:
        return "Cash Flow Statement"

    # 4. Annual Report
    annual_report_score = sum([
        _contains(r"\bannual report\b", text),
        _contains(r"\bstandalone financial statements\b", text),
        _contains(r"\bconsolidated financial statements\b", text),
        _contains(r"\bboard of directors\b", text),
        _contains(r"\bnotes to financial statements\b", text),
        _contains(r"\bdirectors' report\b", text),
        _contains(r"\bmanagement discussion and analysis\b", text),
        _contains(r"\bcorporate governance report\b", text)
    ])
    #An explicit Annual Report title is sufficient.
    if _contains(r"\bannual report\b", text):
        return "Annual Report"

    if annual_report_score >= 3:
        return "Annual Report"

    # 5. Balance Sheet and Profit & Loss together
    has_balance_sheet = _contains(r"\bbalance sheet\b", text)

    has_profit_loss = _contains(
        r"\bprofit and loss\b|\bprofit & loss\b",
        text
    )

    if has_balance_sheet and has_profit_loss:
        return "Financial Statements - Balance Sheet and Profit & Loss"

    # 6. Auditor's Report / Financial Statements
    auditor_score = sum([
        _contains(r"\bindependent auditor'?s report\b", text),
        _contains(r"\bauditor'?s report\b", text),
        _contains(r"\baudit report\b", text),
        _contains(r"\bopinion on the financial statements\b", text),
        _contains(r"\bfinancial statements\b", text)
    ])

    if auditor_score >= 2:
        return "Financial Statements / Auditor's Report"

    # 7. Balance Sheet
    if has_balance_sheet:
        return "Balance Sheet"

    # 8. Profit and Loss Statement
    if has_profit_loss:
        return "Profit and Loss Statement"

    return None


def classify_document(
    document_text: str,
    model: str = "qwen2.5:3b"
) -> str:
    """
    Classify a financial document.

    First uses document-structure rules.
    If the document type is unclear, uses the
    local Ollama model as a fallback.
    """

    if not isinstance(document_text, str) or not document_text.strip():
        raise ValueError("Document text cannot be empty.")

    text = _get_representative_text(document_text)

    # First attempt: rule-based classification
    category = _classify_using_document_structure(text)

    if category is not None:
        return category

    # Second attempt: local LLM classification
    prompt = f"""
Classify the following financial document into exactly
one of these categories:

1. Commercial Invoice
2. Bank Statement
3. Balance Sheet
4. Profit and Loss Statement
5. Cash Flow Statement
6. Annual Report
7. Financial Statements / Auditor's Report
8. Other Financial Document
9. Unknown / Uncertain

Rules:
- Identify the document from its actual content and structure.
- Do not guess based only on a company name.
- Do not invent information.
- If the document does not clearly match a category,
  return Other Financial Document or Unknown / Uncertain.
- Return only one category name.

DOCUMENT:
{text}

CATEGORY:
"""

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 40
            }
        )

    except ConnectionError as error:
        raise RuntimeError(
            "Unable to connect to the Ollama server."
        ) from error

    except ResponseError as error:
        raise RuntimeError(
            f"Ollama model error: {error.error}"
        ) from error

    result = response["message"]["content"].strip()

    allowed_categories = {
        "Commercial Invoice",
        "Bank Statement",
        "Balance Sheet",
        "Profit and Loss Statement",
        "Cash Flow Statement",
        "Annual Report",
        "Financial Statements / Auditor's Report",
        "Other Financial Document",
        "Unknown / Uncertain"
    }

    # Accept only an exact allowed category
    if result not in allowed_categories:
        return "Unknown / Uncertain"

    return result
