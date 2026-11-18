
from backend.app.orchestrator.model_router import route_model


# Test 1: Extraction
result1 = route_model("extraction")
print("\nTEST 1 - EXTRACTION")
print(result1)


# Test 2: Classification
result2 = route_model("classification")
print("\nTEST 2 - CLASSIFICATION")
print(result2)


# Test 3: Summarization
result3 = route_model("summarization")
print("\nTEST 3 - SUMMARIZATION")
print(result3)


# Test 4: Question Answering
result4 = route_model("question_answering")
print("\nTEST 4 - QUESTION ANSWERING")
print(result4)


# Test 5: Comparison
result5 = route_model("comparison")
print("\nTEST 5 - COMPARISON")
print(result5)


# Test 6: Invalid intent
try:
    route_model("translation")
except ValueError as error:
    print("\nTEST 6 - INVALID INTENT")
    print(error)
