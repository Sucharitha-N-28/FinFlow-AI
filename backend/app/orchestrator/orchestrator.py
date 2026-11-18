
import time

from backend.app.orchestrator.intent_detector import detect_intent
from backend.app.orchestrator.task_planner import create_task_plan
from backend.app.orchestrator.task_executor import (
    execute_task,
    extract_document_text
)
from backend.app.document_validation.financial_validator import (
    validate_financial_document
)


def orchestrate_request(user_prompt, documents):
    """
    Coordinate financial document validation,
    intent detection, task planning and task execution.
    Also measure the execution time of each stage.
    """

    total_start = time.perf_counter()

    # Step 1: Extract text from each document only once
    extraction_start = time.perf_counter()

    document_texts = [
        extract_document_text(document)
        for document in documents
    ]

    extraction_time = time.perf_counter() - extraction_start

    print(
        f"[FinFlow Timing] Document extraction: "
        f"{extraction_time:.2f} seconds"
    )

    # Step 2: Validate uploaded financial documents
    validation_start = time.perf_counter()

    for document, document_text in zip(documents, document_texts):

        validator_start = time.perf_counter()

        validation_result = validate_financial_document(
            document_text
        )

        validator_time = time.perf_counter() - validator_start

        print(
            f"[FinFlow Timing] Financial validation: "
            f"{validator_time:.2f} seconds"
        )

        if validation_result == "NON_FINANCIAL":
            print(
                "[FinFlow Timing] Request rejected: "
                "non-financial document"
            )

            return {
                "status": "unsupported_document",
                "message": (
                    "This document does not appear to be financial. "
                    "FinFlow AI supports financial documents only."
                ),
                "document_name": document.get("file_name")
            }

        if validation_result == "UNCERTAIN":
            print(
                "[FinFlow Timing] Request rejected: "
                "uncertain document"
            )

            return {
                "status": "uncertain_document",
                "message": (
                    "Unable to determine whether this is a financial "
                    "document. Please upload a clearer financial document."
                ),
                "document_name": document.get("file_name")
            }

    validation_total = time.perf_counter() - validation_start

    # Step 3: Detect user intent
    intent_start = time.perf_counter()

    intent_result = detect_intent(user_prompt)

    intent_time = time.perf_counter() - intent_start

    print(
        f"[FinFlow Timing] Intent detection: "
        f"{intent_time:.2f} seconds"
    )

    # Handle ambiguous requests
    if intent_result["status"] == "ambiguous":
        print("[FinFlow Timing] Request ended: ambiguous prompt")

        return {
            "status": "ambiguous",
            "message": intent_result["clarification_question"]
        }

    # Handle unsupported requests
    if intent_result["status"] == "unsupported":
        print("[FinFlow Timing] Request ended: unsupported prompt")

        return {
            "status": "unsupported",
            "message": (
                "The requested task is not supported by FinFlow AI."
            )
        }

    # Step 4: Create the task execution plan
    planning_start = time.perf_counter()

    task_plan = create_task_plan(intent_result)

    planning_time = time.perf_counter() - planning_start

    print(
        f"[FinFlow Timing] Task planning: "
        f"{planning_time:.2f} seconds"
    )

    # Step 5: Execute planned tasks using cached document text
    execution_results = []

    # Store structured financial extraction results
    # so subsequent tasks can reuse them.
    financial_records = None

    execution_total_start = time.perf_counter()

    for task in task_plan["tasks"]:

        task_start = time.perf_counter()

        execution_result = execute_task(
            task["intent"],
            documents,
            user_prompt,
            document_texts,
            financial_records
        )

        task_time = time.perf_counter() - task_start

        if execution_result is None:
            raise RuntimeError(
                f"execute_task returned None for intent: "
                f"{task['intent']}"
            )

        # Save extraction results for subsequent tasks.
        if task["intent"] == "extraction":
            financial_records = execution_result["result"]

        print(
            f"[FinFlow Timing] {task['intent']} execution: "
            f"{task_time:.2f} seconds"
        )

        execution_results.append({
            "step": task["step"],
            "intent": task["intent"],
            "module": execution_result["module"],
            "model": execution_result["model"],
            "result": execution_result["result"]
        })

    execution_total = (
        time.perf_counter() - execution_total_start
    )

    # Step 6: Return the complete orchestration result
    total_time = time.perf_counter() - total_start

    print("\n========== FINFLOW EXECUTION TIME ==========")
    print(f"Document extraction: {extraction_time:.2f} seconds")
    print(f"Financial validation: {validation_total:.2f} seconds")
    print(f"Intent detection:    {intent_time:.2f} seconds")
    print(f"Task planning:       {planning_time:.2f} seconds")
    print(f"Task execution:      {execution_total:.2f} seconds")
    print("--------------------------------------------")
    print(f"TOTAL TIME:          {total_time:.2f} seconds")
    print("============================================\n")

    return {
        "status": "completed",
        "detected_intents": intent_result["intents"],
        "steps_executed": execution_results
    }
