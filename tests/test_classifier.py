from backend.app.classification.classifier import classify_document

sample_text = """
BALANCE SHEET
Assets: 50000
Liabilities: 20000
Equity: 30000
"""

print("Predicted Category:", classify_document(sample_text))