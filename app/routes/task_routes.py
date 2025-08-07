from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import models, schemas, curd
from ..database import get_db
from ..auth import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from app.logger import logger
# Logger setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter(tags=["Tasks"])

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = await curd.get_user(db, user_id)
        if user is None:
            logger.warning(f"Token invalid: User with ID {user_id} not found.")
            raise credentials_exception
        logger.info(f"Authenticated user {user.email} (ID: {user.id})")
        return user
    except (JWTError, ValueError) as e:
        logger.error(f"Token decode failed: {str(e)}")
        raise credentials_exception

@router.post("/tasks", response_model=schemas.ShowTask)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    logger.info(f"Creating task for user {user.email} (ID: {user.id}): {task.dict()}")
    return await curd.create_task(db, task, user.id)

@router.get("/tasks", response_model=List[schemas.ShowTask])
async def get_tasks(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    logger.info(f"Fetching tasks for user {user.email} (ID: {user.id}) | Skip: {skip}, Limit: {limit}")
    return await curd.get_tasks(db, user.id, skip, limit)

@router.get("/tasks/{task_id}", response_model=schemas.ShowTask)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    task = await curd.get_task(db, task_id, user.id)
    if task is None:
        logger.warning(f"Task {task_id} not found for user ID {user.id}")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(f"Fetched task {task_id} for user {user.email}")
    return task

@router.put("/tasks/{task_id}", response_model=schemas.ShowTask)
async def update_task(task_id: int, task_data: schemas.TaskUpdate, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    logger.info(f"Updating task {task_id} for user {user.email}: {task_data}")
    task = await curd.update_task(db, task_id, task_data, user.id)
    if task is None:
        logger.warning(f"Update failed. Task {task_id} not found or not owned by user {user.id}")
        raise HTTPException(status_code=404, detail="Task not found or not yours")
    logger.info(f"Task {task_id} updated for user {user.email}")
    return task

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    task = await curd.delete_task(db, task_id, user.id)
    if task is None:
        logger.warning(f"Delete failed. Task {task_id} not found or not owned by user {user.id}")
        raise HTTPException(status_code=404, detail="Task not found or not yours")
    logger.info(f"Task {task_id} deleted for user {user.email}")
    return {"message": "Task deleted"}
