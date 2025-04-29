from fastapi import APIRouter, UploadFile, File, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.database import get_db, FileModel
from app.utils.file_processing import process_excel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload")
async def upload_file(
        request: Request,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    processed_filename, processed_path = process_excel(content)

    db_file = FileModel(
        original_name=file.filename,
        processed_path=processed_path
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return RedirectResponse(f"/download/{db_file.id}", status_code=303)


@router.get("/download/{file_id}")
async def download_file(
        file_id: int,
        db: AsyncSession = Depends(get_db)
):
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
