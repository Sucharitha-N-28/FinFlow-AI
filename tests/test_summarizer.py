
from backend.app.summarization.summarizer import summarize_document


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

financial_data = {
    "company_name": "ABC Technologies",
    "financial_year": "2025",
    "document_type": "GENERAL",
    "total_revenue": 500000,
    "total_expenses": 320000,
    "net_profit_or_loss": 180000
}

summary = summarize_document(
    document_text=sample_text,
    financial_data=financial_data
)

print("\nGENERATED FINANCIAL SUMMARY")
print("---------------------------")
print(summary)
