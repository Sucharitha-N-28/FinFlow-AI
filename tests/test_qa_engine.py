
from backend.app.question_answering.qa_engine import answer_question


sample_text = """
FinFlow AI - Financial Report

Company: ABC Technologies

Financial Year: 2025

Total Revenue: 500000
Total Expenses: 320000
Net Profit: 180000

Department: Finance
Report Status: Completed
"""


# Test 1: Question about revenue
answer1 = answer_question(
    sample_text,
    "What is the total revenue?"
)

print("\nTEST 1 - REVENUE")
print(answer1)


# Test 2: Question about profit
answer2 = answer_question(
    sample_text,
    "What is the net profit?"
)

print("\nTEST 2 - NET PROFIT")
print(answer2)


# Test 3: Question about company name
answer3 = answer_question(
    sample_text,
    "What is the company name?"
)

print("\nTEST 3 - COMPANY NAME")
print(answer3)


# Test 4: Information not available
answer4 = answer_question(
    sample_text,
    "Who is the company CEO?"
)

print("\nTEST 4 - MISSING INFORMATION")
print(answer4)

# Test 5: Empty document
try:
    answer_question(
        "",
        "What is the total revenue?"
    )
except ValueError as error:
    print("\nTEST 5 - EMPTY DOCUMENT")
    print(error)


# Test 6: Empty question
try:
    answer_question(
        sample_text,
        ""
    )
except ValueError as error:
    print("\nTEST 6 - EMPTY QUESTION")
    print(error)
