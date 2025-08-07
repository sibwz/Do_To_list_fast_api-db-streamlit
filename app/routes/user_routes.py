from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta


from .. import schemas, curd
from ..database import get_db
from ..auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.logger import logger
# Logger setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])

@router.post("/signup", response_model=schemas.ShowUser)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"🔐 Signup attempt with email: {user.email}")
    db_user = await curd.get_user_by_email(db, user.email)
    if db_user:
        logger.warning(f"❗ Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    created_user = await curd.create_user(db, user)
    logger.info(f"✅ User registered successfully: {created_user.email}")
    return created_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info(f"🔐 Login attempt for user: {form_data.username}")
    user = await curd.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"❌ Login failed for user: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": str(user.id)}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"✅ Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}
