from fastapi import FastAPI
from app.routers import files
from app.database import engine, Base

# uvicorn app.main:app --reload --port 8003
app = FastAPI()

app.include_router(files.router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
