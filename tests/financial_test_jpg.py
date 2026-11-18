
from PIL import Image, ImageDraw, ImageFont

# Create a white image
img = Image.new("RGB", (1000, 650), "white")
draw = ImageDraw.Draw(img)

# Fonts
try:
    title_font = ImageFont.truetype("arial.ttf", 32)
    font = ImageFont.truetype("arial.ttf", 25)
except OSError:
    title_font = ImageFont.load_default()
    font = ImageFont.load_default()

# Financial document content
content = [
    "FINANCIAL STATEMENT",
    "",
    "Company Name: XYZ Finance Pvt Ltd",
    "Financial Year: 2024-25",
    "",
    "Total Assets: INR 900000",
    "Total Liabilities: INR 400000",
    "Revenue: INR 600000",
    "Total Expenses: INR 450000",
    "Net Profit: INR 150000"
]

# Draw content
y = 50
for i, line in enumerate(content):
    if i == 0:
        draw.text((60, y), line, fill="black", font=title_font)
    else:
        draw.text((60, y), line, fill="black", font=font)
    y += 55

# Save PNG
img.save("financial_test.jpg")

print("JPG created successfully: financial_test.jpg")
