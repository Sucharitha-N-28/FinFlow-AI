
import re
import time
import ollama

from ollama import ResponseError


# =========================================================
# 1. REMOVE SENSITIVE INFORMATION
# =========================================================

def remove_sensitive_information(text: str) -> str:
    """Remove sensitive Indian identifiers."""

    if not text:
        return text

    # PAN
    text = re.sub(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "[REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    # Aadhaar
    text = re.sub(
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "[REDACTED]",
        text
    )

    return text


# =========================================================
# 2. FORMAT FINANCIAL VALUES
# =========================================================

def format_indian_number(value):
    """Format numbers using Indian comma notation."""

    if value is None:
        return "Not available"

    try:
        number = float(value)

        if number.is_integer():
            number = int(number)
            sign = "-" if number < 0 else ""
            number = str(abs(number))

            if len(number) <= 3:
                return sign + number

            last_three = number[-3:]
            remaining = number[:-3]
            groups = []

            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]

            if remaining:
                groups.insert(0, remaining)

            return sign + ",".join(groups + [last_three])

        return f"{number:,.2f}"

    except (ValueError, TypeError):
        return str(value)


def format_financial_value(value, currency):
    """Format a financial value without inventing currency."""

    formatted = format_indian_number(value)

    if value is None:
        return formatted

    if currency == "INR":
        return f"₹{formatted}"

    if currency:
        return f"{currency} {formatted}"

    return formatted


# =========================================================
# 3. GENERATE A SHORT DOCUMENT OVERVIEW USING OLLAMA
# =========================================================

def generate_document_overview(document_text: str, financial_data: dict):
    """
    Generate a short qualitative overview.

    Financial figures are deliberately excluded from this
    model-generated overview. Python formats those separately.
    """

    company = financial_data.get("company_name") or "the entity"
    document_type = (
        financial_data.get("document_type")
        or "financial document"
    )

    prompt = f"""
You are a financial document summarization assistant.

Write only one or two short sentences describing the
uploaded document.

Entity: {company}
Document type: {document_type}

Rules:
1. Describe the purpose and nature of the document.
2. Do not generate financial amounts or percentages.
3. Do not calculate or estimate anything.
4. Do not discuss accounting policies or lengthy notes.
5. Do not invent facts.
6. Do not repeat financial figures.
7. Keep the overview concise.

Return only the overview.
"""

    try:
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 100
            }
        )

        overview = response["message"]["content"].strip()

        # Remove sensitive identifiers
        overview = remove_sensitive_information(overview)

        # Reject an overview containing generated numerical claims
        if re.search(r"\d|₹|Rs\.?", overview, re.IGNORECASE):
            return ""

        # Keep the overview short
        if len(overview) > 400:
            overview = overview[:400].rsplit(" ", 1)[0]

        return overview

    except (ConnectionError, ResponseError, KeyError, TypeError):
        # Financial summary can still be generated from Python
        return ""


# =========================================================
# 4. BUILD THE AUTHORITATIVE FINANCIAL SUMMARY
# =========================================================

def build_financial_summary(financial_data: dict, overview: str = ""):
    """
    Build a structured summary using extracted financial data.

    The extraction result is the source of truth for all
    displayed financial values.
    """

    currency = financial_data.get("currency")

    company = financial_data.get("company_name")
    financial_year = financial_data.get("financial_year")
    document_type = financial_data.get("document_type")

    summary = []

    # -----------------------------------------------------
    # Document information
    # -----------------------------------------------------

    summary.append("FINANCIAL DOCUMENT SUMMARY")
    summary.append("")

    summary.append(
        f"**Entity Name:** {company or 'Not available'}"
    )

    summary.append(
        f"**Financial Year:** {financial_year or 'Not available'}"
    )

    summary.append(
        f"**Document Type:** {document_type or 'Not available'}"
    )

    # -----------------------------------------------------
    # Short overview
    # -----------------------------------------------------

    if overview:
        summary.append("")
        summary.append("**DOCUMENT OVERVIEW:**")
        summary.append(overview)

    # -----------------------------------------------------
    # Balance Sheet
    # -----------------------------------------------------

    summary.append("")
    summary.append("**BALANCE SHEET:**")

    summary.append(
        "- **Total Assets:** "
        + format_financial_value(
            financial_data.get("total_assets"),
            currency
        )
    )

    summary.append(
        "- **Total Liabilities:** "
        + format_financial_value(
            financial_data.get("total_liabilities"),
            currency
        )
    )

    summary.append(
        "- **Shareholders' Funds:** "
        + format_financial_value(
            financial_data.get("shareholders_funds"),
            currency
        )
    )

    summary.append(
        "- **Proprietor Capital:** "
        + format_financial_value(
            financial_data.get("proprietor_capital"),
            currency
        )
    )

    # -----------------------------------------------------
    # Profit and Loss Account
    # -----------------------------------------------------

    summary.append("")
    summary.append("**PROFIT AND LOSS ACCOUNT:**")

    summary.append(
        "- **Revenue:** "
        + format_financial_value(
            financial_data.get("revenue"),
            currency
        )
    )

    summary.append(
        "- **Purchases:** "
        + format_financial_value(
            financial_data.get("purchases"),
            currency
        )
    )

    summary.append(
        "- **Total Expenses:** "
        + format_financial_value(
            financial_data.get("total_expenses"),
            currency
        )
    )

    summary.append(
        "- **Net Profit / Loss:** "
        + format_financial_value(
            financial_data.get("net_profit_or_loss"),
            currency
        )
    )

    # -----------------------------------------------------
    # Earnings Per Share
    # -----------------------------------------------------

    summary.append("")
    summary.append("**ADDITIONAL FINANCIAL INFORMATION:**")

    eps = financial_data.get("eps")

    if eps is None:
        eps_value = "Not available"
    else:
        eps_value = format_indian_number(eps)

    summary.append(f"- **Earnings Per Share (EPS):** {eps_value}")

    # -----------------------------------------------------
    # Currency
    # -----------------------------------------------------

    summary.append(
        f"- **Currency:** {currency or 'Not available'}"
    )

    return "\n".join(summary)


# =========================================================
# 5. MAIN SUMMARIZATION FUNCTION
# =========================================================

def summarize_document(
    document_text: str,
    pages=None,
    financial_data=None
):
    """
    Generate a concise financial summary.

    Uses Qwen 2.5 3B for a qualitative overview and Python
    for accurate presentation of extracted financial values.
    """

    if not document_text or not document_text.strip():
        raise ValueError("Document text cannot be empty.")

    if not financial_data:
        raise ValueError(
            "Structured financial data is required for "
            "accurate financial summarization."
        )

    start_time = time.perf_counter()

    # -----------------------------------------------------
    # Prepare document content
    # -----------------------------------------------------

    if pages:
        document_content = "\n\n".join(
            f"PAGE {page['page_number']}:\n{page['text']}"
            for page in pages
        )
    else:
        document_content = document_text

    # Remove sensitive information
    document_content = remove_sensitive_information(
        document_content
    )
    #Route commercial invoices separately.
    is_commercial_invoice = bool(
        re.search(
            r"commercial\s+invoice|invoice\s+number|invoice\s+no\.?",
            document_content,
            re.IGNORECASE
        )
    )
    if is_commercial_invoice:
        return summarize_commercial_invoice(document_content)

    # Generate short qualitative overview
    overview = generate_document_overview(
        document_content,
        financial_data
    )

    # Build the authoritative financial summary
    summary = build_financial_summary(
        financial_data,
        overview
    )

    generation_time = time.perf_counter() - start_time

    # -----------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------

    print("\n========== SUMMARIZATION DIAGNOSTICS ==========")
    print(f"Generation time: {generation_time:.2f} seconds")
    print("Financial values: Structured extraction data")
    print("Overview model: qwen2.5:3b")
    print("Summary generation: Python")
    print("================================================\n")

    return summary

import re
import time
import ollama

from ollama import ResponseError


# =========================================================
# 1. REMOVE SENSITIVE INFORMATION
# =========================================================

def remove_sensitive_information(text: str) -> str:
    """Remove sensitive Indian identifiers."""

    if not text:
        return text

    # PAN
    text = re.sub(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "[REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    # Aadhaar
    text = re.sub(
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "[REDACTED]",
        text
    )

    return text


# =========================================================
# 2. FORMAT FINANCIAL VALUES
# =========================================================

def format_indian_number(value):
    """Format numbers using Indian comma notation."""

    if value is None:
        return "Not available"

    try:
        number = float(value)

        if number.is_integer():
            number = int(number)
            sign = "-" if number < 0 else ""
            number = str(abs(number))

            if len(number) <= 3:
                return sign + number

            last_three = number[-3:]
            remaining = number[:-3]
            groups = []

            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]

            if remaining:
                groups.insert(0, remaining)

            return sign + ",".join(groups + [last_three])

        return f"{number:,.2f}"

    except (ValueError, TypeError):
        return str(value)


def format_financial_value(value, currency):
    """Format a financial value without inventing currency."""

    formatted = format_indian_number(value)

    if value is None:
        return formatted

    if currency == "INR":
        return f"₹{formatted}"

    if currency:
        return f"{currency} {formatted}"

    return formatted


# =========================================================
# 3. GENERATE A SHORT DOCUMENT OVERVIEW USING OLLAMA
# =========================================================

def generate_document_overview(document_text: str, financial_data: dict):
    """
    Generate a short qualitative overview.

    Financial figures are deliberately excluded from this
    model-generated overview. Python formats those separately.
    """

    company = financial_data.get("company_name") or "the entity"
    document_type = (
        financial_data.get("document_type")
        or "financial document"
    )

    prompt = f"""
You are a financial document summarization assistant.

Write only one or two short sentences describing the
uploaded document.

Entity: {company}
Document type: {document_type}

Rules:
1. Describe the purpose and nature of the document.
2. Do not generate financial amounts or percentages.
3. Do not calculate or estimate anything.
4. Do not discuss accounting policies or lengthy notes.
5. Do not invent facts.
6. Do not repeat financial figures.
7. Keep the overview concise.

Return only the overview.
"""

    try:
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 100
            }
        )

        overview = response["message"]["content"].strip()

        # Remove sensitive identifiers
        overview = remove_sensitive_information(overview)

        # Reject an overview containing generated numerical claims
        if re.search(r"\d|₹|Rs\.?", overview, re.IGNORECASE):
            return ""

        # Keep the overview short
        if len(overview) > 400:
            overview = overview[:400].rsplit(" ", 1)[0]

        return overview

    except (ConnectionError, ResponseError, KeyError, TypeError):
        # Financial summary can still be generated from Python
        return ""


# =========================================================
# 4. BUILD THE AUTHORITATIVE FINANCIAL SUMMARY
# =========================================================

def build_financial_summary(financial_data: dict, overview: str = ""):
    """
    Build a structured summary using extracted financial data.

    The extraction result is the source of truth for all
    displayed financial values.
    """

    currency = financial_data.get("currency")

    company = financial_data.get("company_name")
    financial_year = financial_data.get("financial_year")
    document_type = financial_data.get("document_type")

    summary = []

    # -----------------------------------------------------
    # Document information
    # -----------------------------------------------------

    summary.append("FINANCIAL DOCUMENT SUMMARY")
    summary.append("")

    summary.append(
        f"**Entity Name:** {company or 'Not available'}"
    )

    summary.append(
        f"**Financial Year:** {financial_year or 'Not available'}"
    )

    summary.append(
        f"**Document Type:** {document_type or 'Not available'}"
    )

    # -----------------------------------------------------
    # Short overview
    # -----------------------------------------------------

    if overview:
        summary.append("")
        summary.append("**DOCUMENT OVERVIEW:**")
        summary.append(overview)

    # -----------------------------------------------------
    # Balance Sheet
    # -----------------------------------------------------

    summary.append("")
    summary.append("**BALANCE SHEET:**")

    summary.append(
        "- **Total Assets:** "
        + format_financial_value(
            financial_data.get("total_assets"),
            currency
        )
    )

    summary.append(
        "- **Total Liabilities:** "
        + format_financial_value(
            financial_data.get("total_liabilities"),
            currency
        )
    )

    summary.append(
        "- **Shareholders' Funds:** "
        + format_financial_value(
            financial_data.get("shareholders_funds"),
            currency
        )
    )

    summary.append(
        "- **Proprietor Capital:** "
        + format_financial_value(
            financial_data.get("proprietor_capital"),
            currency
        )
    )

    # -----------------------------------------------------
    # Profit and Loss Account
    # -----------------------------------------------------

    summary.append("")
    summary.append("**PROFIT AND LOSS ACCOUNT:**")

    summary.append(
        "- **Revenue:** "
        + format_financial_value(
            financial_data.get("revenue"),
            currency
        )
    )

    summary.append(
        "- **Purchases:** "
        + format_financial_value(
            financial_data.get("purchases"),
            currency
        )
    )

    summary.append(
        "- **Total Expenses:** "
        + format_financial_value(
            financial_data.get("total_expenses"),
            currency
        )
    )

    summary.append(
        "- **Net Profit / Loss:** "
        + format_financial_value(
            financial_data.get("net_profit_or_loss"),
            currency
        )
    )

    # -----------------------------------------------------
    # Earnings Per Share
    # -----------------------------------------------------

    summary.append("")
    summary.append("**ADDITIONAL FINANCIAL INFORMATION:**")

    eps = financial_data.get("eps")

    if eps is None:
        eps_value = "Not available"
    else:
        eps_value = format_indian_number(eps)

    summary.append(f"- **Earnings Per Share (EPS):** {eps_value}")

    # -----------------------------------------------------
    # Currency
    # -----------------------------------------------------

    summary.append(
        f"- **Currency:** {currency or 'Not available'}"
    )

    return "\n".join(summary)


# =========================================================
# 5. MAIN SUMMARIZATION FUNCTION
# =========================================================

def summarize_document(
    document_text: str,
    pages=None,
    financial_data=None
):
    """
    Generate a concise financial summary.

    Uses Qwen 2.5 3B for a qualitative overview and Python
    for accurate presentation of extracted financial values.
    """

    if not document_text or not document_text.strip():
        raise ValueError("Document text cannot be empty.")

    if not financial_data:
        raise ValueError(
            "Structured financial data is required for "
            "accurate financial summarization."
        )

    start_time = time.perf_counter()

    # -----------------------------------------------------
    # Prepare document content
    # -----------------------------------------------------

    if pages:
        document_content = "\n\n".join(
            f"PAGE {page['page_number']}:\n{page['text']}"
            for page in pages
        )
    else:
        document_content = document_text

    # Remove sensitive information
    document_content = remove_sensitive_information(
        document_content
    )

    # Generate short qualitative overview
    overview = generate_document_overview(
        document_content,
        financial_data
    )

    # Build the authoritative financial summary
    summary = build_financial_summary(
        financial_data,
        overview
    )

    generation_time = time.perf_counter() - start_time

    # -----------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------

    print("\n========== SUMMARIZATION DIAGNOSTICS ==========")
    print(f"Generation time: {generation_time:.2f} seconds")
    print("Financial values: Structured extraction data")
    print("Overview model: qwen2.5:3b")
    print("Summary generation: Python")
    print("================================================\n")

    return summary

def summarize_commercial_invoice(document_text: str) -> str:
    """Generate a structured summary specifically for commercial invoices."""

    prompt = f"""
You are a commercial invoice analysis assistant.

Extract the following information from the invoice:

- Seller
- Buyer
- Invoice Number
- Invoice Date
- Currency
- Total Sales Value
- Total Customs Value
- Freight Value

Rules:
1. Use only information explicitly available in the document.
2. Do not invent or calculate values.
3. Use "Not available" when information is missing.
4. Preserve the original currency and amount.
5. Return valid JSON with exactly these keys:
seller, buyer, invoice_number, invoice_date, currency,
total_sales_value, total_customs_value, freight_value.

DOCUMENT:
{document_text}
"""

    try:
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            format="json",
            options={
                "temperature": 0,
                "num_predict": 500,
            },
        )

        import json
        data = json.loads(response["message"]["content"])

        fields = [
            ("Seller", "seller"),
            ("Buyer", "buyer"),
            ("Invoice Number", "invoice_number"),
            ("Invoice Date", "invoice_date"),
            ("Currency", "currency"),
            ("Total Sales Value", "total_sales_value"),
            ("Total Customs Value", "total_customs_value"),
            ("Freight Value", "freight_value"),
        ]

        summary = ["COMMERCIAL INVOICE SUMMARY", ""]

        for label, key in fields:
            value = data.get(key) or "Not available"
            summary.append(f"- **{label}:** {value}")

        return "\n".join(summary)

    except (ConnectionError, ResponseError, KeyError,
            TypeError, ValueError) as error:
        print("[FinFlow] Invoice summarization failed:", error)
        return "Commercial invoice summarization failed."
