# backend/database/db.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite — a simple file based database, no server needed
# The file rag_app.db is created automatically on first run
DATABASE_URL = "sqlite:///./rag_app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ── DATABASE TABLES ────────────────────────────────────────────────

class ChatMessage(Base):
    """
    Stores every question and answer permanently.
    One row = one message (user or assistant).
    """
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    """Stores user feedback on answers."""
    __tablename__ = "feedback"

    id            = Column(Integer, primary_key=True, index=True)
    session_id    = Column(String(100), index=True, nullable=False)
    message_index = Column(Integer, nullable=False)
    rating        = Column(String(20), nullable=False)
    comment       = Column(Text, nullable=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)


class UploadedDocument(Base):
    """Tracks uploaded and processed documents."""
    __tablename__ = "uploaded_documents"

    id          = Column(Integer, primary_key=True, index=True)
    filename    = Column(String(255), nullable=False)
    num_chunks  = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status      = Column(String(20), default="processed")


def create_tables():
    """Creates all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI dependency — gives each endpoint a database session.
    Automatically closes the session when the endpoint finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── HELPER FUNCTIONS ───────────────────────────────────────────────

def save_message(db, session_id: str, role: str, content: str):
    """Saves one message to the database."""
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db, session_id: str):
    """Returns all messages for a session, oldest first."""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
        .all()
    )


def save_feedback(db, session_id: str, message_index: int,
                  rating: str, comment):
    """Saves feedback for one answer."""
    fb = Feedback(
        session_id=session_id,
        message_index=message_index,
        rating=rating,
        comment=comment
    )
    db.add(fb)
    db.commit()
    return fb


def log_document(db, filename: str, num_chunks: int):
    """Records a newly processed document."""
    doc = UploadedDocument(filename=filename, num_chunks=num_chunks)
    db.add(doc)
    db.commit()
    return doc