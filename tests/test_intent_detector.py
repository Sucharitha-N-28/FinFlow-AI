
from backend.app.orchestrator.intent_detector import detect_intent


# Test 1: Classification
result1 = detect_intent(
    "Classify this financial document."
)

print("\nTEST 1 - CLASSIFICATION")
print(result1)


# Test 2: Multiple intents
result2 = detect_intent(
    "Classify and summarize this financial report."
)

print("\nTEST 2 - MULTIPLE INTENTS")
print(result2)


# Test 3: Question answering
result3 = detect_intent(
    "What is the total revenue in this report?"
)

print("\nTEST 3 - QUESTION ANSWERING")
print(result3)


# Test 4: Comparison
result4 = detect_intent(
    "Compare these two financial reports."
)

print("\nTEST 4 - COMPARISON")
print(result4)


# Test 5: Unsupported request
result5 = detect_intent(
    "Create a weather forecast for Bengaluru."
)

print("\nTEST 5 - UNSUPPORTED REQUEST")
print(result5)


# Test 6: Empty prompt
try:
    detect_intent("")
except ValueError as error:
    print("\nTEST 6 - EMPTY PROMPT")
    print(error)
# Test 7: Ambiguous request
result7 = detect_intent(
    "Process this financial document."
)

print("\nTEST 7 - AMBIGUOUS REQUEST")
print(result7)