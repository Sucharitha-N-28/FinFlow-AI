from PIL import Image, ImageDraw

# Create a white image
image = Image.new("RGB", (1000, 500), "white")

# Create a drawing object
draw = ImageDraw.Draw(image)

# Financial report content
text = """QUARTERLY FINANCIAL REPORT

Company: XYZ Solutions

Quarter: Q1 2025

Revenue: 750000
Expenses: 450000
Profit: 300000
"""

# Draw text on the image
draw.text((50, 50), text, fill="black")

# Save as PNG
image.save("sample_documents/financial_test2.png")

print("Second test image created successfully.")