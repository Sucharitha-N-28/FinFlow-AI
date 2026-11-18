
import re

import ollama
from ollama import ResponseError


# Fields that can be answered directly from structured extraction.
FIELD_CONFIG = {
    "total_assets": {
        "label": "Total Assets",
        "aliases": [
            r"\btotal assets\b",
            r"\bassets\b"
        ]
    },
    "total_liabilities": {
        "label": "Total Liabilities",
        "aliases": [
            r"\btotal liabilities\b",
            r"\bliabilities\b"
        ]
    },
    "shareholders_funds": {
        "label": "Shareholders' Funds",
        "aliases": [
            r"shareholders'? funds",
            r"shareholders'? equity"
        ]
    },
    "proprietor_capital": {
        "label": "Proprietor Capital",
        "aliases": [
            r"proprietor'?s? capital",
            r"capital account",
            r"owner'?s? capital"
        ]
    },
    "share_capital": {
        "label": "Share Capital",
        "aliases": [
            r"\bshare capital\b"
        ]
    },
    "reserves_and_surplus": {
        "label": "Reserves and Surplus",
        "aliases": [
            r"\breserves and surplus\b"
        ]
    },
    "inventory": {
        "label": "Inventory",
        "aliases": [
            r"\binventory\b",
            r"\binventories\b",
            r"\bclosing stock\b"
        ]
    },
    "revenue": {
        "label": "Revenue",
        "aliases": [
            r"\btotal revenue\b",
            r"\brevenue\b",
            r"\bgross receipts\b",
            r"\bturnover\b"
        ]
    },
    "purchases": {
        "label": "Purchases",
        "aliases": [
            r"\bpurchases?\b"
        ]
    },
    "total_expenses": {
        "label": "Total Expenses",
        "aliases": [
            r"\btotal expenses\b",
            r"\btotal expenditure\b"
        ]
    },
    "net_profit_or_loss": {
        "label": "Net Profit / Loss",
        "aliases": [
            r"\bnet profit\b",
            r"\bnet loss\b",
            r"\bprofit or loss\b",
            r"\bprofit/loss\b",
            r"\bprofit for the year\b",
            r"\bloss for the year\b"
        ]
    },
    "eps": {
        "label": "Earnings Per Share (EPS)",
        "aliases": [
            r"\bearnings per share\b",
            r"\bearnings per equity share\b",
            r"\beps\b"
        ]
    }
}


def format_financial_value(value, currency=None, is_eps=False):
    """Format an extracted financial value without changing its meaning."""

    if value is None or value == "":
        return "Not available"

    if isinstance(value, bool):
        return str(value)

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if is_eps:
        formatted = f"{abs(number):,.2f}"
    elif number.is_integer():
        formatted = f"{abs(number):,.0f}"
    else:
        formatted = f"{abs(number):,.2f}"

    if number < 0:
        formatted = f"({formatted})"

    if currency == "INR" and not is_eps:
        formatted = f"₹{formatted}"

    return formatted


def identify_requested_fields(question):
    """Identify financial fields explicitly requested by the user."""

    question_lower = question.lower()
    requested = []

    for field, config in FIELD_CONFIG.items():
        for alias in config["aliases"]:
            if re.search(alias, question_lower, re.IGNORECASE):
                requested.append(field)
                break

    return requested


def answer_from_structured_data(question, financial_data):
    """Answer recognized financial questions using Python, not an LLM."""

    requested_fields = identify_requested_fields(question)

    if not requested_fields:
        return None

    currency = financial_data.get("currency")
    lines = []

    for field in requested_fields:
        label = FIELD_CONFIG[field]["label"]
        value = financial_data.get(field)

        formatted_value = format_financial_value(
            value,
            currency=currency,
            is_eps=(field == "eps")
        )

        lines.append(f"{label}: {formatted_value}")

    return "\n".join(lines)


def answer_question(
    document_text: str,
    question: str,
    model: str = "qwen2.5:7b",
    financial_data: dict | None = None
):
    """
    Answer financial questions.

    Recognized financial fields are answered directly from
    structured extraction data. Ollama is used only for
    questions outside the structured financial field schema.
    """

    if not document_text or not document_text.strip():
        raise ValueError("Document text cannot be empty.")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if financial_data is not None:
        if not isinstance(financial_data, dict):
            raise ValueError("Financial data must be a dictionary.")

        structured_answer = answer_from_structured_data(
            question,
            financial_data
        )

        if structured_answer is not None:
            return structured_answer

    # Fallback for questions outside the structured field schema.
    prompt = f"""
You are a financial document question-answering system.

Answer the question using only explicitly available information
in the supplied document.

STRICT RULES:
1. Do not use external knowledge.
2. Do not invent or estimate values.
3. Preserve financial figures and negative signs.
4. Distinguish totals from individual line items.
5. If information is unavailable, say so.
6. Do not confuse one financial field with another.
7. Give a short, direct answer.

DOCUMENT:
{document_text}

QUESTION:
{question}

Provide only the answer.
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
                "num_predict": 200
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

    return response["message"]["content"].strip()
