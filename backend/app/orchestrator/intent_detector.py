
import json
import ollama
from ollama import ResponseError


# Intents supported by FinFlow AI
SUPPORTED_INTENTS = [
    "extraction",
    "classification",
    "summarization",
    "question_answering",
    "comparison"
]


def detect_intent(user_prompt: str):
    """
    Identify one or more intents from the user's prompt
    using the Qwen 2.5 3B model.
    """

    if not user_prompt or not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    prompt = f"""
You are the intent detector for FinFlow AI,
a financial document processing system.

Identify every operation explicitly requested by the user.

SUPPORTED INTENTS:

- extraction: Extract text or information from a document.
- classification: Identify the financial document category.
- summarization: Summarize document information.
- question_answering: Answer specific questions using document content.
- comparison: Compare two or more financial documents.

RULES:

1. Identify all explicitly requested supported operations.
2. A request can contain multiple intents.
3. Asking for a specific financial value is question_answering.
4. Asking for a document category is classification.
5. Asking to summarize is summarization.
6. Asking to compare documents is comparison.
7. Asking to extract document text is extraction.
8. Do not invent additional intents.

STATUS:

- supported: One or more supported operations are clear.
- ambiguous: The requested operation itself is unclear.
- unsupported: The requested operation is outside FinFlow AI capabilities.

EXAMPLES:

"Classify this document" -> supported, classification
"Classify and summarize" -> supported, classification, summarization
"What is the total revenue?" -> supported, question_answering
"Extract all text" -> supported, extraction
"Compare these reports" -> supported, comparison
"Tell me the weather" -> unsupported
"Process this document" -> ambiguous

Return a valid JSON object with exactly these fields:

{{
    "status": "supported, ambiguous or unsupported",
    "intents": [],
    "clarification_question": null
}}

For supported requests, include all identified intents.
For ambiguous requests, provide one specific clarification question.
For unsupported requests, use an empty intents list and null clarification.

USER PROMPT:
{user_prompt}
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
            format="json",
            options={
                "temperature": 0,
                "num_predict": 100
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

    try:
        result = json.loads(response["message"]["content"])
    except (json.JSONDecodeError, TypeError) as error:
        raise RuntimeError(
            "Invalid JSON response from the intent detection model."
        ) from error

    # Validate returned status
    valid_statuses = [
        "supported",
        "ambiguous",
        "unsupported"
    ]

    if result.get("status") not in valid_statuses:
        raise RuntimeError("Invalid intent detection status.")

    # Validate detected intents
    intents = result.get("intents")

    if not isinstance(intents, list):
        raise RuntimeError("Invalid intent list returned by the model.")

    if any(intent not in SUPPORTED_INTENTS for intent in intents):
        raise RuntimeError("Unsupported intent returned by the model.")

    if result["status"] == "supported" and not intents:
        raise RuntimeError("No valid intents detected.")

    if result["status"] != "supported" and intents:
        raise RuntimeError(
            "Non-supported request cannot contain executable intents."
        )

    clarification_question = result.get("clarification_question")

    if result["status"] == "ambiguous":
        if not isinstance(clarification_question, str) or not clarification_question.strip():
            raise RuntimeError("Ambiguous request requires a clarification question.")

    if result["status"] == "unsupported":
        clarification_question = None

    return {
        "status": result["status"],
        "intents": intents,
        "clarification_question": clarification_question
    }
