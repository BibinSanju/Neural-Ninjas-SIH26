from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    users = relationship("User", back_populates="department")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    role_type = Column(String, nullable=True) # e.g. "Computer-Based", "Field-Oriented"
    
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # e.g. "VIEW", "CREATE"
    
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

# Association Table for Many-to-Many between Roles and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Active")
    
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    
    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    
    files = relationship("File", back_populates="user")
    chats = relationship("Chat", back_populates="user")

class File(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(Integer, ForeignKey("users.id"))
    original_filename = Column(String, nullable=False)
    ingested_time = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String, nullable=False)
    
    user = relationship("User", back_populates="files")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, index=True, nullable=True)
    user_msg = Column(Text, nullable=False)
    chatbot_msg = Column(Text, nullable=False)
    routing_flow = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="chats")
