
import pymupdf

# Create a new PDF document
document = pymupdf.open()

# Add one page
page = document.new_page()

# Insert sample financial text
page.insert_text(
    (72, 72),
    "FinFlow AI - Financial Report\nTotal Revenue: 50000"
)

# Save the PDF
document.save("sample_documents/valid_test.pdf")

# Close the document
document.close()

print("Valid test PDF created successfully.")
