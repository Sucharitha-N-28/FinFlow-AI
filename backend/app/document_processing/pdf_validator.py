
import pymupdf


def validate_pdf(file_path):

    try:
        # Open the PDF document
        document = pymupdf.open(file_path)

        # Check whether the PDF contains pages
        if document.page_count == 0:
            document.close()
            return False

        # Close the PDF document
        document.close()

        return True

    except Exception as error:

        print("PDF validation failed:", error)

        return False
if __name__ == "__main__":

    valid_result = validate_pdf("sample_documents/valid_test.pdf")

    fake_result = validate_pdf("sample_documents/fake_test.pdf")

    print("Valid PDF result:", valid_result)
    print("Fake PDF result:", fake_result)