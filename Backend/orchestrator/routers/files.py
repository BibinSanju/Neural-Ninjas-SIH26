from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
import os
import uuid
import subprocess

from database.db import get_db
from database.models import User, File
from orchestrator.routers.auth import router as auth_router, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
import jwt

router = APIRouter(prefix="/files", tags=["files"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        
    # Trigger ingest.py
    ingest_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "ingest.py")
    
    # Run the ingestion synchronously for simplicity in the prototype
    try:
        subprocess.run(
            ["python", ingest_script_path, "ingest", file_path, file_id, file.filename],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        # If ingestion fails, delete the file and raise error
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {e.stderr}")

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
def delete_file(file_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_record = db.query(File).filter(File.id == file_id, File.user_id == current_user.id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Delete from ChromaDB
    ingest_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "ingest.py")
    subprocess.run(["python", ingest_script_path, "delete", file_id])
    
    # Delete physical file
    if os.path.exists(file_record.file_path):
        os.remove(file_record.file_path)
        
    # Delete from DB
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted successfully"}
