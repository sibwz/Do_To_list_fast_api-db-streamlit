from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Use asyncpg with PostgreSQL
DATABASE_URL = "postgresql+asyncpg://postgres:iq123%40Re@localhost:5432/todo"

# ✅ Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# ✅ Create async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ✅ Declare Base
Base = declarative_base()

# ✅ Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
