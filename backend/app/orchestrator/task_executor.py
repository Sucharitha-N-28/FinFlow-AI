
from backend.app.classification.classifier import classify_document
from backend.app.summarization.summarizer import summarize_document
from backend.app.question_answering.qa_engine import answer_question
from backend.app.comparison.comparison_engine import (
    extract_financial_data,
    compare_documents
)
from backend.app.orchestrator.model_router import route_model


def extract_document_text(document):
    """
    Convert extracted document content into plain text.
    Supports PDF, TXT and image documents.
    """

    extracted_content = document.get("extracted_content")

    if not isinstance(extracted_content, dict):
        raise ValueError("Invalid extracted document content.")

    file_type = document.get("file_type", "").lower()

    if file_type == ".pdf":

        pages = extracted_content.get("pages", [])

        document_text = "\n".join(
            page.get("text", "")
            for page in pages
        )

    elif file_type in {".txt", ".png", ".jpg", ".jpeg"}:

        document_text = extracted_content.get("text", "")

    else:
        raise ValueError(
            f"Unsupported document type: {file_type}"
        )

    if not document_text or not document_text.strip():
        raise ValueError(
            f"No extracted text available for "
            f"{document.get('file_name', 'document')}."
        )

    return document_text


def execute_task(
    intent,
    documents,
    user_prompt,
    document_texts=None,
    financial_records=None
):
    """
    Execute the requested task using the appropriate module
    and locally routed model.
    """

    # Extract document text if it was not supplied.
    if document_texts is None:
        document_texts = [
            extract_document_text(document)
            for document in documents
        ]

    if len(document_texts) != len(documents):
        raise ValueError(
            "The number of document texts must match "
            "the number of documents."
        )

    # Select the appropriate local model.
    routing_info = route_model(intent)
    selected_model = routing_info["model"]

    # --------------------------------------------------------
    # FINANCIAL EXTRACTION
    # --------------------------------------------------------

    if intent == "extraction":

        result = []

        for document, document_text in zip(
            documents, document_texts
        ):

            extracted_content = document.get(
                "extracted_content", {}
            )

            # Preserve PDF page information, including
            # word coordinates, for table-aware extraction.
            document_pages = (
                extracted_content.get("pages", [])
                if document.get("file_type", "").lower() == ".pdf"
                else None
            )

            financial_data = extract_financial_data(
                document_text=document_text,
                document_name=document.get(
                    "file_name", "Unknown document"
                ),
                model=selected_model,
                document_pages=document_pages
            )

            result.append({
                "file_name": document.get("file_name"),
                "financial_data": financial_data
            })

        module = "Financial Information Extraction"

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    elif intent == "classification":

        result = [
            {
                "file_name": document.get("file_name"),
                "category": classify_document(document_text)
            }
            for document, document_text in zip(
                documents, document_texts
            )
        ]

        module = "Document Classification"

    # --------------------------------------------------------
    # SUMMARIZATION
    # --------------------------------------------------------

    elif intent == "summarization":

        result = []

        # Generate structured financial data only when it
        # has not already been extracted by an earlier task.
        if financial_records is None:

            financial_records = []

            for document, document_text in zip(
                documents, document_texts
            ):

                extracted_content = document.get(
                    "extracted_content", {}
                )

                document_pages = (
                    extracted_content.get("pages", [])
                    if document.get("file_type", "").lower() == ".pdf"
                    else None
                )

                financial_data = extract_financial_data(
                    document_text=document_text,
                    document_name=document.get(
                        "file_name", "Unknown document"
                    ),
                    model=route_model("extraction")["model"],
                    document_pages=document_pages
                )

                financial_records.append({
                    "file_name": document.get("file_name"),
                    "financial_data": financial_data
                })

        # Match documents with financial data by their position.
        if len(financial_records) != len(documents):
            raise ValueError(
                "The number of financial records must match "
                "the number of documents."
    )

        for index, (document, document_text) in enumerate(
            zip(documents, document_texts)
    ):
            file_name = document.get("file_name")

            financial_data = financial_records[index]["financial_data"]

            summary = summarize_document(
                document_text,
                pages=(
                    document.get(
                        "extracted_content", {}
                    ).get("pages")
                    if document.get("file_type", "").lower() == ".pdf"
                    else None
                ),
                financial_data=financial_data
            )

            result.append({
                "file_name": file_name,
                "summary": summary
            })

        module = "Document Summarization"

    
    elif intent == "question_answering":

        # Extract structured financial data if it was not
        # already produced by an earlier orchestration task.
        if financial_records is None:

            financial_records = []

            for document, document_text in zip(
                documents, document_texts
            ):

                extracted_content = document.get(
                    "extracted_content", {}
                )

                document_pages = (
                    extracted_content.get("pages", [])
                    if document.get("file_type", "").lower() == ".pdf"
                    else None
                )

                financial_data = extract_financial_data(
                    document_text=document_text,
                    document_name=document.get(
                        "file_name", "Unknown document"
                    ),
                    model=route_model("extraction")["model"],
                    document_pages=document_pages
                )

                financial_records.append({
                    "file_name": document.get("file_name"),
                    "financial_data": financial_data
                })

        # Match documents with financial data by their position.
        if len(financial_records) != len(documents):
            raise ValueError(
                "The number of financial records must match "
                "the number of documents."
    )

        result = []

        for index, (document, document_text) in enumerate(
            zip(documents, document_texts)
        ):

            file_name = document.get("file_name")

            financial_data = financial_records[index]["financial_data"]
            answer = answer_question(
                document_text=document_text,
                question=user_prompt,
                model=selected_model,
                financial_data=financial_data
            )

            result.append({
                "file_name": file_name,
                "answer": answer
            })

        module = "Question Answering"



    # --------------------------------------------------------
    # DOCUMENT COMPARISON
    # --------------------------------------------------------

    elif intent == "comparison":

        if len(documents) < 2:
            raise ValueError(
                "At least two documents are required "
                "for comparison."
            )

        document_names = [
            document.get(
                "file_name", f"Document {index + 1}"
            )
            for index, document in enumerate(documents)
        ]

        # Reuse previously extracted financial records when available.
        if financial_records is None:

            financial_records = []

            for document, document_text in zip(
                documents, document_texts
            ):

                extracted_content = document.get(
                    "extracted_content", {}
                )

                document_pages = (
                    extracted_content.get("pages", [])
                    if document.get("file_type", "").lower() == ".pdf"
                    else None
                )

                financial_data = extract_financial_data(
                    document_text=document_text,
                    document_name=document.get(
                        "file_name", "Unknown document"
                    ),
                    model=selected_model,
                    document_pages=document_pages
                )

                financial_records.append({
                    "file_name": document.get("file_name"),
                    "financial_data": financial_data
                })

        if len(financial_records) != len(documents):
            raise ValueError(
                "The number of financial records must match "
                "the number of documents."
            )

        # Compare the extracted financial records.
        result = compare_documents(
            financial_records=financial_records,
            model=selected_model,
            document_names=document_names
        )

        module = "Document Comparison"

    else:
        raise ValueError(
            f"Unsupported task intent: {intent}"
        )


    # Return the result for every task.
    return {
        "intent": intent,
        "module": module,
        "model": selected_model,
        "result": result
    }
