
from backend.app.document_validation.financial_validator import (
    validate_financial_document
)


# Test 1: Financial document
financial_text = """
ABC Technologies
Financial Year: 2025
Total Revenue: 500000
Total Expenses: 320000
Net Profit: 180000
"""

# Test 2: Non-financial document
weather_text = """
Weather Report
Location: Bengaluru
Temperature: 28 degrees Celsius
Humidity: 65 percent
Rainfall: 10 mm
"""

# Test 3: Unclear document
uncertain_text = """
Annual Report
ABC Technologies
"""

test_cases = [
    ("Financial Document", financial_text),
    ("Weather Report", weather_text),
    ("Unclear Document", uncertain_text)
]

for test_name, document_text in test_cases:
    print(f"\nTesting: {test_name}")

    try:
        result = validate_financial_document(document_text)
        print("Validation Result:", result)

    except Exception as error:
        print("Error:", error)
