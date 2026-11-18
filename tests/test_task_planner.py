
from backend.app.orchestrator.task_planner import create_task_plan


# Test 1: Single intent
result1 = create_task_plan({
    "status": "supported",
    "intents": ["classification"]
})

print("\nTEST 1 - SINGLE INTENT")
print(result1)


# Test 2: Multiple intents
result2 = create_task_plan({
    "status": "supported",
    "intents": [
        "summarization",
        "classification",
        "extraction"
    ]
})

print("\nTEST 2 - MULTIPLE INTENTS")
print(result2)


# Test 3: Question answering and summarization
result3 = create_task_plan({
    "status": "supported",
    "intents": [
        "question_answering",
        "summarization"
    ]
})

print("\nTEST 3 - TASK PRIORITY")
print(result3)


# Test 4: Duplicate intents
result4 = create_task_plan({
    "status": "supported",
    "intents": [
        "classification",
        "classification",
        "summarization"
    ]
})

print("\nTEST 4 - DUPLICATE INTENTS")
print(result4)


# Test 5: Unsupported status
try:
    create_task_plan({
        "status": "unsupported",
        "intents": []
    })
except ValueError as error:
    print("\nTEST 5 - UNSUPPORTED STATUS")
    print(error)


# Test 6: Invalid intent
try:
    create_task_plan({
        "status": "supported",
        "intents": ["translation"]
    })
except ValueError as error:
    print("\nTEST 6 - INVALID INTENT")
    print(error)
