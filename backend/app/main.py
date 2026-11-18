
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.openapi.utils import get_openapi

from backend.app.schemas.request import PromptRequest
from backend.app.storage.storage import (
    create_upload_session,
    save_uploaded_file,
    delete_upload_session
)
from fastapi.middleware.cors import CORSMiddleware

from backend.app.document_processing.document_processor import process_document
from backend.app.orchestrator.orchestrator import orchestrate_request



app = FastAPI(
    title="FinFlow AI",
    description="AI-Powered Financial Document Processing and Task Orchestration System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# CUSTOM OPENAPI CONFIGURATION
# --------------------------------------------------

def custom_openapi():

    # Reuse the schema if it has already been generated
    if app.openapi_schema:
        return app.openapi_schema

    # Generate the OpenAPI specification
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    # Use OpenAPI 3.0.3 for Swagger file-upload compatibility
    openapi_schema["openapi"] = "3.0.3"

    # Find all component schemas
    schemas = openapi_schema.get("components", {}).get("schemas", {})

    for schema in schemas.values():

        properties = schema.get("properties", {})

        for property_schema in properties.values():

            # Handle arrays of uploaded files
            items = property_schema.get("items", {})

            if items.get("contentMediaType") == "application/octet-stream":
                items.pop("contentMediaType", None)
                items["format"] = "binary"

            # Handle individual uploaded files
            if property_schema.get("contentMediaType") == "application/octet-stream":
                property_schema.pop("contentMediaType", None)
                property_schema["format"] = "binary"

    # Cache the corrected schema
    app.openapi_schema = openapi_schema

    return app.openapi_schema


# Replace the default OpenAPI generator
app.openapi = custom_openapi


# --------------------------------------------------
# UPLOAD CONFIGURATION
# --------------------------------------------------

# Allowed document extensions
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

# Maximum size of an individual file: 20 MB
MAX_FILE_SIZE = 20 * 1024 * 1024

# Maximum number of documents per request
MAX_FILES = 5

# Maximum combined size of all documents: 100 MB
MAX_TOTAL_UPLOAD_SIZE = 100 * 1024 * 1024


# --------------------------------------------------
# FILE CONTENT VALIDATION
# --------------------------------------------------

async def validate_file_content(file: UploadFile, extension: str):

    try:
        # Read the first 16 bytes of the file
        header = await file.read(16)

        # PDF signature validation
        if extension == ".pdf":
            return header.startswith(b"%PDF-")

        # PNG signature validation
        elif extension == ".png":
            return header.startswith(b"\x89PNG\r\n\x1a\n")

        # JPEG signature validation
        elif extension in {".jpg", ".jpeg"}:
            return header.startswith(b"\xff\xd8\xff")

        # Basic text-file validation
        elif extension == ".txt":
            return b"\x00" not in header

        return False

    finally:
        # Always reset the file pointer
        await file.seek(0)


# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to FinFlow AI!",
        "status": "Backend is running successfully"
    }


# --------------------------------------------------
# PROMPT ANALYSIS ENDPOINT
# --------------------------------------------------

@app.post("/api/v1/analyze")
def analyze_request(request: PromptRequest):

    return {
        "message": "Request received successfully",
        "received_prompt": request.prompt,
        "status": "Ready for task orchestration"
    }


# --------------------------------------------------
# DOCUMENT UPLOAD ENDPOINT
# --------------------------------------------------


@app.post("/api/v1/upload")
async def upload_documents(

    prompt: str = Form(..., min_length=3, max_length=2000),
    files: list[UploadFile] = File(...)

):

    # Validate the number of uploaded documents
    if len(files) > MAX_FILES:

        raise HTTPException(
            status_code=413,
            detail=f"Maximum {MAX_FILES} files are allowed per request."
        )

    # Create one storage folder for this upload request
    session_id, session_dir = create_upload_session()

    uploaded_files = []

    # Track the combined size of all uploaded documents
    total_upload_size = 0

    try:

        for file in files:

            # Check whether a filename exists
            if not file.filename:

                raise HTTPException(
                    status_code=400,
                    detail="A file with an empty filename was received."
                )

            # Extract the safe filename
            filename = file.filename.replace("\\", "/").rsplit("/", 1)[-1]

            # Extract the file extension
            extension = (
                "." + filename.rsplit(".", 1)[-1].lower()
                if "." in filename else ""
            )

            # Validate the file extension
            if extension not in ALLOWED_EXTENSIONS:

                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {filename}"
                )

            # Validate actual file content
            is_valid = await validate_file_content(file, extension)

            if not is_valid:

                raise HTTPException(
                    status_code=415,
                    detail=f"File content does not match its extension: {filename}"
                )

            # Initialize individual file size
            file_size = 0

            # Read the file in 1 MB chunks
            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                # Update individual file size
                file_size += len(chunk)

                # Update combined upload size
                total_upload_size += len(chunk)

                # Check individual file size
                if file_size > MAX_FILE_SIZE:

                    raise HTTPException(
                        status_code=413,
                        detail=f"{filename} exceeds the 20 MB size limit."
                    )

                # Check combined upload size
                if total_upload_size > MAX_TOTAL_UPLOAD_SIZE:

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"Combined document size exceeds the "
                            f"{MAX_TOTAL_UPLOAD_SIZE // (1024 * 1024)} MB limit."
                        )
                    )

            # Reject empty files
            if file_size == 0:

                raise HTTPException(
                    status_code=400,
                    detail=f"{filename} is empty."
                )

            # Save the document in temporary storage
            saved_file = await save_uploaded_file(
                file,
                session_dir,
                extension
            )

            # Process the saved document
            try:

                extracted_content = process_document(
                    saved_file["storage_path"],
                    extension
                )

            except ValueError as error:

                raise HTTPException(
                    status_code=415,
                    detail=str(error)
                )

            # Store document metadata, extracted content and classification
            # Store document metadata and extracted content
            uploaded_files.append({

            "document_id": saved_file["document_id"],
            "file_name": filename,
            "file_type": extension,
            "size_bytes": saved_file["size_bytes"],
            "extracted_content": extracted_content["content"]

})
        
        # Execute the user's requested tasks
        orchestration_result = orchestrate_request(
            prompt,
            uploaded_files
        )

        # Create a lightweight file response for the frontend
        # Keep extracted_content internally for orchestration
        # but do not send the raw extracted content to the frontend

        response_files = [
            {
                "document_id": document["document_id"],
                "file_name": document["file_name"],
                "file_type": document["file_type"],
                "size_bytes": document["size_bytes"]
            }
            for document in uploaded_files
        ]

        # Return successful upload response
        return {
            "message": "Documents received, validated, saved and processed successfully",
            "session_id": session_id,
            "received_prompt": prompt,
            "total_files": len(response_files),
            "files": response_files,
            "orchestration_result": orchestration_result,
            "status": orchestration_result["status"]
        }

    except Exception:

        # Delete the entire session if any upload operation fails
        delete_upload_session(session_dir)

        raise
