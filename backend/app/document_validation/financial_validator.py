
import re


def _get_representative_text(document_text: str) -> str:
    """
    Get representative portions of a document.

    This avoids relying only on the first page of long PDFs.
    """

    text = re.sub(r"\s+", " ", document_text).strip()

    if len(text) <= 15000:
        return text

    first_part = text[:6000]
    middle_start = len(text) // 2 - 1500
    middle_part = text[middle_start:middle_start + 3000]
    last_part = text[-6000:]

    return " ".join([
        first_part,
        middle_part,
        last_part
    ])


def validate_financial_document(document_text: str) -> str:
    """
    Determine whether the uploaded document contains
    financial information.

    Returns:
        FINANCIAL
        NON_FINANCIAL
        UNCERTAIN
    """

    if not isinstance(document_text, str) or not document_text.strip():
        raise ValueError("Document text cannot be empty.")

    text = _get_representative_text(document_text).lower()

    # Strong financial-document indicators
    financial_patterns = [
        r"\bbalance sheet\b",
        r"\bprofit and loss\b",
        r"\bprofit & loss\b",
        r"\bcash flow statement\b",
        r"\bcommercial invoice\b",
        r"\binvoice no\b",
        r"\binvoice number\b",
        r"\bbank statement\b",
        r"\baccount statement\b",
        r"\bdebit\b",
        r"\bcredit\b",
        r"\baccount balance\b",
        r"\bopening balance\b",
        r"\bclosing balance\b",
        r"\bassets\b",
        r"\bliabilities\b",
        r"\bshareholders'? equity\b",
        r"\bcurrent assets\b",
        r"\bcurrent liabilities\b",
        r"\btrade receivables\b",
        r"\btrade payables\b",
        r"\brevenue\b",
        r"\bgross profit\b",
        r"\bnet profit\b",
        r"\boperating activities\b",
        r"\binvesting activities\b",
        r"\bfinancing activities\b",
        r"\bauditor'?s report\b",
        r"\bindependent auditor\b",
        r"\bfinancial statements\b",
        r"\bfinancial year\b",
        r"\baccounting policies\b",
        r"\bunit price\b",
        r"\bsales value\b",
        r"\bcustoms value\b",
        r"\btransaction date\b",
        r"\btxn date\b",
        r"\bvalue date\b"
    ]

    matches = sum(
        1
        for pattern in financial_patterns
        if re.search(pattern, text)
    )

    # Structured financial-table indicators
    table_patterns = [
        r"\bdebit\b.*\bcredit\b.*\bbalance\b",
        r"\bunit price\b.*\bqty\b",
        r"\bassets\b.*\bliabilities\b",
        r"\bparticulars\b.*\bamt\b",
        r"\bopening balance\b.*\bclosing balance\b"
    ]

    table_matches = sum(
        1
        for pattern in table_patterns
        if re.search(pattern, text)
    )

    # A clear financial document normally has multiple
    # financial indicators or a strong document structure.
    if matches >= 3 or table_matches >= 1:
        return "FINANCIAL"

    # A single weak reference is not enough to confirm
    # that the document itself is financial.
    if matches == 1 or matches == 2:
        return "UNCERTAIN"

    return "NON_FINANCIAL"
