from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, select
from sqlalchemy.sql import func

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/file_converter_db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    original_name = Column(String(255))
    processed_path = Column(String(500))  # Путь к обработанному файлу
    created_at = Column(TIMESTAMP, server_default=func.now())