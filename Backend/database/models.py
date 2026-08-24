from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
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
