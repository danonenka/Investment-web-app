from fastapi import FastAPI, UploadFile, File as FastAPIFile, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, AsyncSessionLocal, FileModel, Base

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(
        request: Request,
        file: UploadFile = FastAPIFile(...),
        db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    processed_content = content.decode().upper()

    db_file = FileModel(
        original_name=file.filename,
        processed_content=processed_content
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return RedirectResponse(f"/download/{db_file.id}", status_code=303)


@app.get("/download/{file_id}", response_class=HTMLResponse)
async def download_file(
        request: Request,
        file_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "File not found"
        })

    return templates.TemplateResponse("download.html", {
        "request": request,
        "filename": file.original_name,
        "content": file.processed_content
    })