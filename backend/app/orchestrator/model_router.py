
# Model configuration
SIMPLE_MODEL = "qwen2.5:3b"
COMPLEX_MODEL = "qwen2.5:7b"


# Task complexity mapping
TASK_COMPLEXITY = {
    "extraction": "complex",
    "classification": "simple",
    "summarization": "simple",
    "question_answering": "complex",
    "comparison": "complex"
}


def route_model(intent: str):
    """
    Select an appropriate local open-source model
    based on the complexity of the requested task.
    """

    if intent not in TASK_COMPLEXITY:
        raise ValueError(
            f"Unsupported intent for model routing: {intent}"
        )

    complexity = TASK_COMPLEXITY[intent]

    if complexity == "simple":
        selected_model = SIMPLE_MODEL
    else:
        selected_model = COMPLEX_MODEL

    return {
        "intent": intent,
        "complexity": complexity,
        "model": selected_model
    }
