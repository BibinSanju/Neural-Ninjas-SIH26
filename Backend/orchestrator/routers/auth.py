from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import bcrypt
import jwt
import datetime

from database.db import get_db
from database.models import User, Role, Department

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "super_secret_airgapped_key" # In production, load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

class UserCreate(BaseModel):
    username: str
    password: str
    employee_id: str | None = None
    department_id: int | None = None
    role_id: int | None = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # By default, if no role is provided, try to find the "Employee" role
    assigned_role_id = user.role_id
    if not assigned_role_id:
        default_role = db.query(Role).filter(Role.name == "Employee").first()
        if default_role:
            assigned_role_id = default_role.id
            
    new_user = User(
        username=user.username, 
        password_hash=hashed_password,
        employee_id=user.employee_id,
        department_id=user.department_id,
        role_id=assigned_role_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    # Get role and permissions for JWT
    role_name = db_user.role.name if db_user.role else "None"
    department_name = db_user.department.name if db_user.department else "None"
    permissions = [p.name for p in db_user.role.permissions] if db_user.role else []
        
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": db_user.username, 
            "user_id": db_user.id,
            "role": role_name,
            "department": department_name,
            "permissions": permissions
        }, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permissions(required_permissions: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        if "ADMIN" in user_permissions: # Super Admin bypass
            return current_user
        for perm in required_permissions:
            if perm not in user_permissions:
                raise HTTPException(status_code=403, detail=f"Operation not permitted. Missing permission: {perm}")
        return current_user
    return role_checker

