
# Supported execution order
TASK_PRIORITY = {
    "extraction": 1,
    "classification": 2,
    "summarization": 3,
    "question_answering": 4,
    "comparison": 5
}


def create_task_plan(intent_result: dict):
    """
    Create an ordered execution plan from detected intents.
    """

    # Validate the intent detection result
    if not isinstance(intent_result, dict):
        raise ValueError("Invalid intent detection result.")

    status = intent_result.get("status")
    intents = intent_result.get("intents")

    if status != "supported":
        raise ValueError(
            "Task planning requires supported intents."
        )

    if not isinstance(intents, list) or not intents:
        raise ValueError("No valid intents provided.")

    # Validate supported intents
    for intent in intents:
        if intent not in TASK_PRIORITY:
            raise ValueError(
                f"Unsupported intent: {intent}"
            )

    # Remove duplicate intents
    unique_intents = list(set(intents))

    # Sort intents according to execution priority
    ordered_intents = sorted(
        unique_intents,
        key=lambda intent: TASK_PRIORITY[intent]
    )

    # Create the execution plan
    tasks = []

    for step, intent in enumerate(ordered_intents, start=1):
        tasks.append({
            "step": step,
            "intent": intent
        })

    return {
        "tasks": tasks
    }
