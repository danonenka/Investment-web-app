from fastapi import FastAPI
from app.routers import files
from app.database import engine, Base

# uvicorn app.main:app --reload
app = FastAPI()

app.include_router(files.router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
