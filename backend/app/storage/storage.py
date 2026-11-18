import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


# Find the main project directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Main directory for uploaded documents
UPLOAD_ROOT = PROJECT_ROOT / "uploads"


def create_upload_session():
    """
    Create a unique folder for one upload request.
    """

    session_id = str(uuid4())

    session_dir = UPLOAD_ROOT / session_id

    session_dir.mkdir(parents=True, exist_ok=False)

    return session_id, session_dir


async def save_uploaded_file(
    file: UploadFile,
    session_dir: Path,
    extension: str
):
    """
    Save an uploaded document using a generated filename.
    """

    # Generate a unique document ID
    document_id = str(uuid4())

    # Use the generated ID instead of the original filename
    storage_path = session_dir / f"{document_id}{extension}"

    file_size = 0

    try:
        # Start reading from the beginning
        await file.seek(0)

        # Create the file without overwriting an existing file
        with storage_path.open("xb") as destination:

            while True:

                # Read 1 MB at a time
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                destination.write(chunk)

                file_size += len(chunk)

    except Exception:

        # Remove an incomplete file if saving fails
        storage_path.unlink(missing_ok=True)

        raise

    finally:
        # Reset the uploaded file position
        await file.seek(0)

    # Return document metadata
    return {
        "document_id": document_id,
        "original_filename": file.filename,
        "file_type": extension,
        "size_bytes": file_size,
        "storage_path": storage_path
    }
def delete_upload_session(session_dir: Path):
    """
    Delete an upload session and all files inside it.
    """

    if session_dir.exists():
        shutil.rmtree(session_dir)
