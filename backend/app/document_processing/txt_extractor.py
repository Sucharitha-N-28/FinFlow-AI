
from pathlib import Path


def extract_txt_content(file_path):

    # Convert the file path into a Path object
    file_path = Path(file_path)

    # Read the complete text file using UTF-8 encoding
    extracted_text = file_path.read_text(encoding="utf-8")

    # Return the extracted content
    return {
        "filename": file_path.name,
        "text": extracted_text
    }


if __name__ == "__main__":

    result = extract_txt_content(
        "sample_documents/valid_test.txt"
    )

    print("\nTXT EXTRACTION RESULT")
    print("---------------------")

    print("Filename:", result["filename"])

    print("\nExtracted content:")
    print(result["text"])
