
from pathlib import Path
import pytesseract
from PIL import Image


def extract_image_content(file_path):

    # Convert the file path into a Path object
    file_path = Path(file_path)

    # Open the image
    image = Image.open(file_path)

    # Extract text from the image using Tesseract OCR
    extracted_text = pytesseract.image_to_string(image)

    # Return the extracted content
    return {
        "filename": file_path.name,
        "text": extracted_text
    }


if __name__ == "__main__":

    result = extract_image_content(
        "sample_documents/financial_test2.png"
    )

    print("\nIMAGE OCR RESULT")
    print("---------------------")

    print("Filename:", result["filename"])

    print("\nExtracted text:")
    print(result["text"])
