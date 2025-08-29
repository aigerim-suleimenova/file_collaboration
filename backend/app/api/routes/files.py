import uuid
import os
from typing import List
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.api.deps import get_db, CurrentUser
from app.models import File as FileModel, FileCreate, FileUpdate, FilePublic
from app.crud import (
    create_file_for_user,
    get_files_for_user,
    get_file_by_id_for_user,
    update_file_for_user,
    delete_file_for_user
)
from app.services.s3_service import s3_service
from app.services.document_converter import document_converter
from app.core.security import create_share_token

router = APIRouter()


@router.post("/upload", response_model=FilePublic)
async def upload_file(
    file: UploadFile,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    description: str = None
):
    """Upload a file to S3 and save metadata to database"""

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Generate unique S3 key
    file_extension = os.path.splitext(file.filename)[1]
    s3_key = f"users/{current_user.id}/{uuid.uuid4()}{file_extension}"

    try:
        # Save file temporarily to get size and content
        temp_path = f"/tmp/{uuid.uuid4()}{file_extension}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Get file info
        file_size = len(content)
        mime_type = file.content_type or "application/octet-stream"

        # Handle document conversion for Quill editor
        original_format = None
        quill_content = None

        print(
            f"Upload: Processing file {file.filename} with mime_type {mime_type}")
        print(
            f"Upload: Document converter available: {document_converter is not None}")
        print("DEBUG >>> raw filename repr:", repr(file.filename))
        print("DEBUG >>> lowercased:", file.filename.lower())

        print("DEBUG >>> endswith .docx:",
              file.filename.lower().endswith(".docx"))
        if document_converter and document_converter.is_docx_file(file.filename):
            original_format = "docx"  # Always set for DOCX files
            try:
                # Convert DOCX to HTML for Quill editor
                html_content, plain_text = document_converter.docx_to_html(
                    content)
                quill_content = document_converter.get_quill_content(
                    html_content)
                print(
                    f"Converted DOCX to HTML: {len(quill_content)} characters")
            except Exception as e:
                print(f"Warning: Failed to convert DOCX to HTML: {e}")
                # Continue without conversion if it fails
                quill_content = None
        elif document_converter and document_converter.is_html_file(file.filename):
            # HTML files can be used directly in Quill
            try:
                quill_content = document_converter.get_quill_content(
                    content.decode('utf-8'))
                original_format = "html"
                print(
                    f"Processed HTML for Quill: {len(quill_content)} characters")
            except Exception as e:
                print(f"Warning: Failed to process HTML: {e}")

        # Upload to S3
        if not s3_service.upload_file(temp_path, s3_key):
            raise HTTPException(
                status_code=500, detail="Failed to upload file to S3")

        # Clean up temp file
        os.remove(temp_path)

        # Create file record in database
        print(
            f"Upload: Creating file record with original_format={original_format}, quill_content={'yes' if quill_content else 'no'}")
        file_data = FileCreate(
            filename=file.filename,
            s3_key=s3_key,
            file_size=file_size,
            mime_type=mime_type,
            original_format=original_format,
            quill_content=quill_content
        )

        db_file = create_file_for_user(
            session=db,
            owner_id=current_user.id,
            file_in=file_data
        )

        return FilePublic(
            id=db_file.id,
            filename=db_file.filename,
            s3_key=db_file.s3_key,
            file_size=db_file.file_size,
            mime_type=db_file.mime_type,
            original_format=db_file.original_format,
            quill_content=db_file.quill_content,
            owner_id=db_file.owner_id,
            created_at=db_file.created_at,
            updated_at=db_file.updated_at
        )

    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=List[FilePublic])
def get_user_files(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all files for the current user"""
    files = get_files_for_user(
        session=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return [
        FilePublic(
            id=file.id,
            filename=file.filename,
            s3_key=file.s3_key,
            file_size=file.file_size,
            mime_type=file.mime_type,
            original_format=file.original_format,
            quill_content=file.quill_content,
            owner_id=file.owner_id,
            created_at=file.created_at,
            updated_at=file.updated_at
        )
        for file in files
    ]


@router.get("/{file_id}", response_model=FilePublic)
def get_file(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get a specific file by ID"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return FilePublic(
        id=file.id,
        filename=file.filename,
        s3_key=file.s3_key,
        file_size=file.file_size,
        mime_type=file.mime_type,
        original_format=file.original_format,
        quill_content=file.quill_content,
        owner_id=file.owner_id,
        created_at=file.created_at,
        updated_at=file.updated_at
    )


@router.get("/{file_id}/download")
def download_file(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Generate a download URL for a file"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Generate presigned URL for S3 download
    download_url = s3_service.get_file_url(file.s3_key, expires_in=3600)

    if not download_url:
        raise HTTPException(
            status_code=500, detail="Failed to generate download URL")

    return {"download_url": download_url, "filename": file.filename}


@router.delete("/{file_id}")
def delete_file(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Delete a file from S3 and database"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from S3
    if file.s3_key:
        s3_service.delete_file(file.s3_key)

    # Delete from database
    if delete_file_for_user(db, owner_id=current_user.id, file_id=file_id):
        return {"message": "File deleted successfully"}

    raise HTTPException(status_code=500, detail="Failed to delete file")


@router.post("/{file_id}/share")
def create_share_token_for_file(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    expires_hours: int = Form(
        4, description="Token expiration in hours (default: 4)")
):
    """Create a share token for file collaboration"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Create share token
    expires_delta = timedelta(hours=expires_hours)
    share_token = create_share_token(str(file_id), expires_delta=expires_delta)

    return {
        "share_token": share_token,
        "expires_in_hours": expires_hours,
        "file_id": str(file_id),
        "filename": file.filename
    }


@router.get("/{file_id}/content")
def get_file_content(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get file content for editing (downloads from S3 temporarily)"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not file.s3_key:
        raise HTTPException(status_code=404, detail="File content not found")

    try:
        # Create temporary file path
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"

        # Download from S3
        if not s3_service.download_file(file.s3_key, temp_path):
            raise HTTPException(
                status_code=500, detail="Failed to download file from S3")

        # Read file content
        with open(temp_path, 'rb') as f:
            content = f.read()

        # Clean up temp file
        os.remove(temp_path)

        # Return file content with proper headers
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=file.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f"inline; filename={file.filename}",
                "Content-Length": str(file.file_size or len(content))
            }
        )

    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=500, detail=f"Failed to read file: {str(e)}")


@router.post("/{file_id}/content")
async def update_file_content(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    file: UploadFile = File(...)
):
    """Update file content (replaces existing file in S3)"""
    existing_file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not existing_file:
        raise HTTPException(status_code=404, detail="File not found")

    if not existing_file.s3_key:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Save new file temporarily
        temp_path = f"/tmp/{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Get new file info
        new_file_size = len(content)
        new_mime_type = file.content_type or existing_file.mime_type

        # Upload new content to S3 (overwrites existing)
        if not s3_service.upload_file(temp_path, existing_file.s3_key):
            raise HTTPException(
                status_code=500, detail="Failed to update file in S3")

        # Clean up temp file
        os.remove(temp_path)

        # Update database metadata
        update_data = FileUpdate(
            filename=file.filename or existing_file.filename,
            mime_type=new_mime_type
        )

        updated_file = update_file_for_user(
            session=db,
            owner_id=current_user.id,
            file_id=file_id,
            file_in=update_data
        )

        if not updated_file:
            raise HTTPException(
                status_code=500, detail="Failed to update file metadata")

        return {"message": "File content updated successfully", "filename": updated_file.filename}

    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=500, detail=f"Failed to update file: {str(e)}")


@router.post("/{file_id}/convert-to-docx")
async def convert_to_docx(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Convert file content back to DOCX format for download"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not file.quill_content:
        raise HTTPException(
            status_code=400, detail="No Quill content available for conversion")

    try:
        # Convert HTML content back to DOCX
        docx_content = document_converter.html_to_docx(
            file.quill_content,
            filename=file.filename.replace('.docx', '_converted.docx')
        )

        # Generate a new S3 key for the converted file
        new_s3_key = f"users/{current_user.id}/{uuid.uuid4()}_converted.docx"

        # Save DOCX temporarily and upload to S3
        temp_path = f"/tmp/{uuid.uuid4()}_converted.docx"
        with open(temp_path, "wb") as buffer:
            buffer.write(docx_content)

        # Upload converted DOCX to S3
        if not s3_service.upload_file(temp_path, new_s3_key):
            raise HTTPException(
                status_code=500, detail="Failed to upload converted DOCX")

        # Clean up temp file
        os.remove(temp_path)

        # Create a new file record for the converted version
        converted_file_data = FileCreate(
            filename=file.filename.replace('.docx', '_converted.docx'),
            s3_key=new_s3_key,
            file_size=len(docx_content),
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            original_format="docx",
            quill_content=file.quill_content  # Keep the original Quill content
        )

        converted_file = create_file_for_user(
            session=db,
            owner_id=current_user.id,
            file_in=converted_file_data
        )

        return FilePublic(
            id=converted_file.id,
            filename=converted_file.filename,
            s3_key=converted_file.s3_key,
            file_size=converted_file.file_size,
            mime_type=converted_file.mime_type,
            original_format=converted_file.original_format,
            quill_content=converted_file.quill_content,
            owner_id=converted_file.owner_id,
            created_at=converted_file.created_at,
            updated_at=converted_file.updated_at
        )

    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/{file_id}/update-quill-content")
async def update_quill_content(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    quill_content: str = Form(...)
):
    """Update the Quill editor content for a file (for live collaboration)"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Update the Quill content in the database
        updated_file = update_file_for_user(
            db,
            owner_id=current_user.id,
            file_id=file_id,
            file_in=FileUpdate(
                filename=file.filename,
                mime_type=file.mime_type
            )
        )

        if not updated_file:
            raise HTTPException(
                status_code=500, detail="Failed to update file")

        # Update the quill_content field directly
        file.quill_content = quill_content
        db.add(file)
        db.commit()
        db.refresh(file)

        return {"message": "Quill content updated successfully", "file_id": str(file_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.post("/{file_id}/convert-existing-to-quill")
async def convert_existing_to_quill(
    file_id: uuid.UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Convert an existing file to Quill format (for files uploaded before conversion was available)"""
    file = get_file_by_id_for_user(
        session=db,
        owner_id=current_user.id,
        file_id=file_id
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not file.s3_key:
        raise HTTPException(
            status_code=400, detail="No S3 content available for conversion")

    try:
        # Download the file from S3
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"

        if not s3_service.download_file(file.s3_key, temp_path):
            raise HTTPException(
                status_code=500, detail="Failed to download file from S3")

        try:
            # Read the file content
            with open(temp_path, 'rb') as f:
                content = f.read()

            # Convert based on file type
            if document_converter and document_converter.is_docx_file(file.filename):
                # Convert DOCX to HTML
                html_content, plain_text = document_converter.docx_to_html(
                    content)
                quill_content = document_converter.get_quill_content(
                    html_content)
                original_format = "docx"
                print(
                    f"Converted existing DOCX to HTML: {len(quill_content)} characters")

            elif document_converter and document_converter.is_html_file(file.filename):
                # Process HTML for Quill
                quill_content = document_converter.get_quill_content(
                    content.decode('utf-8'))
                original_format = "html"
                print(
                    f"Processed existing HTML for Quill: {len(quill_content)} characters")

            else:
                # For other file types, create a basic Quill content
                quill_content = f"<p>File: {file.filename}</p><p>Size: {file.file_size} bytes</p>"
                original_format = "other"
                print(f"Created basic Quill content for {file.filename}")

            # Update the file record with conversion results
            file.quill_content = quill_content
            file.original_format = original_format

            db.add(file)
            db.commit()
            db.refresh(file)

            return {
                "message": "File converted to Quill format successfully",
                "file_id": str(file_id),
                "original_format": original_format,
                "quill_content_length": len(quill_content) if quill_content else 0
            }

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Conversion failed: {str(e)}")
