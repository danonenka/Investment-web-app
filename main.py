from fastapi import FastAPI, UploadFile, File as FastAPIFile, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, AsyncSessionLocal, FileModel, Base
import pandas as pd
import numpy as np
from io import BytesIO
import uuid
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def process_excel(file_path: str) -> str:
    # Чтение Excel файла
    df = pd.read_excel(file_path)

    # Пример обработки: транспонирование матрицы и добавление колонки с суммой
    processed_df = df.T
    processed_df['Total'] = np.sum(processed_df, axis=1)

    # Сохранение обработанного файла
    output_path = os.path.join(UPLOAD_DIR, f"processed_{uuid.uuid4().hex}.xlsx")
    processed_df.to_excel(output_path, index=False)

    return output_path


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(
        request: Request,
        file: UploadFile = FastAPIFile(...),
        db: AsyncSession = Depends(get_db)
):
    # Сохраняем оригинальный файл
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Обработка файла
    processed_path = process_excel(file_path)

    # Сохраняем информацию в БД
    db_file = FileModel(
        original_name=file.filename,
        processed_path=processed_path  # Сохраняем путь к обработанному файлу
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return RedirectResponse(f"/download/{db_file.id}", status_code=303)


@app.get("/download/{file_id}")
async def download_file(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file = result.scalar_one_or_none()

    if not file or not os.path.exists(file.processed_path):
        return templates.TemplateResponse("error.html", {
            "request": Request,
            "message": "File not found"
        })

    return FileResponse(
        path=file.processed_path,
        filename=f"processed_{file.original_name}",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )