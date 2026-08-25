from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
import os
import uuid
import asyncio

from database.db import get_db
from database.models import User, File
from orchestrator.routers.auth import router as auth_router, get_current_user

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_clearance_level(role_name: str) -> str:
    if not role_name:
        return "1"
    role = role_name.lower().strip()
    
    # Level 5: Admin, Super Admin, GM, Executive Director, CMD, E8, E9
    if any(k in role for k in ["admin", "director", "cmd", "e8", "e9", "general manager"]):
        return "5"
    # Level 4: Chief Engineer, DGM, Technical Authority, Plant Head, E6, E7
    elif any(k in role for k in ["chief", "dgm", "e6", "e7", "plant head", "technical authority"]):
        return "4"
    # Level 3: Manager, Senior Manager, Unit Lead, Safety Manager, E4, E5
    elif any(k in role for k in ["manager", "lead", "e4", "e5", "safety manager"]):
        return "3"
    # Level 2: Senior Engineer, Senior Officer, Shift In-Charge, E2, E3
    elif any(k in role for k in ["senior engineer", "senior officer", "shift in-charge", "e2", "e3"]):
        return "2"
    # Level 1: Assistant Engineer, Officer, Field Operator, Lab Tech, Employee, E0, E1
    else:
        return "1"

@router.post("/upload")
async def upload_file(file: UploadFile = FastAPIFile(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_id = str(uuid.uuid4())
    extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    # Save physical file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    # Trigger ingest.py asynchronously only for documents
    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
    if extension.lower() not in image_extensions:
        ingest_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "ingest.py")
        
        role_name = current_user.role.name if current_user.role else "Employee"
        clearance_level = get_clearance_level(role_name)

        try:
            process = await asyncio.create_subprocess_exec(
                "python", ingest_script_path, "ingest", file_path, file_id, file.filename, clearance_level,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=500, detail=f"Failed to ingest file: {stderr.decode('utf-8')}")
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to ingest file: {str(e)}")

    # Create DB record
    new_file = File(
        id=file_id,
        user_id=current_user.id,
        original_filename=file.filename,
        file_path=file_path
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return {"message": "File uploaded and ingested successfully", "file_id": file_id}

@router.get("/")
def list_files(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = db.query(File).filter(File.user_id == current_user.id).all()
    return files

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_record = db.query(File).filter(File.id == file_id, File.user_id == current_user.id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Delete from Neo4j/ChromaDB asynchronously
    ingest_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "ingest.py")
    process = await asyncio.create_subprocess_exec(
        "python", ingest_script_path, "delete", file_id,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    # Delete physical file
    if os.path.exists(file_record.file_path):
        os.remove(file_record.file_path)
        
    # Delete from DB
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted successfully"}

