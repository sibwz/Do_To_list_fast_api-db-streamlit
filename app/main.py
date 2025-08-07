from fastapi import FastAPI
from .database import Base, engine
from .routes import user_routes, task_routes

app = FastAPI(
    title="To-Do List API",
    description="A FastAPI project with JWT auth, user/task separation, and pagination.",
    version="1.0"
)

# ✅ Proper async DB table creation
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include Routers
app.include_router(user_routes.router)
app.include_router(task_routes.router)
