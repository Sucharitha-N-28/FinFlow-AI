
from pathlib import Path

from backend.app.document_processing.pdf_validator import validate_pdf
from backend.app.document_processing.pdf_extractor import extract_pdf_content
from backend.app.document_processing.txt_extractor import extract_txt_content
from backend.app.document_processing.image_extractor import extract_image_content


def process_document(file_path, file_type):

    # Convert the file path into a Path object
    file_path = Path(file_path)

    # Normalize the document extension
    file_type = file_type.lower()

    # Process PDF documents
    if file_type == ".pdf":

        # Validate the PDF before extraction
        if not validate_pdf(file_path):
            raise ValueError("Invalid PDF document.")

        extracted_content = extract_pdf_content(file_path)

    # Process TXT documents
    elif file_type == ".txt":

        extracted_content = extract_txt_content(file_path)

    # Process image documents
    elif file_type in {".png", ".jpg", ".jpeg"}:

        extracted_content = extract_image_content(file_path)

    # Handle unsupported document types
    else:

        raise ValueError(
            f"Unsupported document type: {file_type}"
        )

    # Return the extracted document information
    return {
        "filename": file_path.name,
        "file_type": file_type,
        "content": extracted_content
    }
