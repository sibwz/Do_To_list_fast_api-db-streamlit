
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas
from .auth import hash_password
from app.logger import logger
# Configure logger

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"User created: {db_user.email}")
    return db_user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if user:
        logger.info(f"User found by email: {email}")
    else:
        logger.warning(f"User not found by email: {email}")
    return user

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter_by(id=user_id))
    user = result.scalar_one_or_none()
    if user:
        logger.info(f"User fetched by ID: {user_id}")
    else:
        logger.warning(f"User not found by ID: {user_id}")
    return user

async def create_task(db: AsyncSession, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    logger.info(f"Task created: {db_task.title} by user {user_id}")
    return db_task

async def get_tasks(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(models.Task)
        .filter_by(owner_id=user_id)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()
    logger.info(f"Fetched {len(tasks)} tasks for user {user_id} (skip={skip}, limit={limit})")
    return tasks

async def get_task(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(
        select(models.Task)
        .filter_by(id=task_id, owner_id=user_id)
    )
    task = result.scalar_one_or_none()
    if task:
        logger.info(f"Task fetched: ID {task_id} for user {user_id}")
    else:
        logger.warning(f"Task not found: ID {task_id} for user {user_id}")
    return task

async def update_task(db: AsyncSession, task_id: int, task_data: schemas.TaskUpdate, user_id: int):
    task = await get_task(db, task_id, user_id)
    if task:
        updates = task_data.dict(exclude_unset=True)
        logger.info(f"Updating task {task_id} for user {user_id}: {updates}")
        for field, value in updates.items():
            setattr(task, field, value)
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task updated: ID {task_id} for user {user_id}")
    else:
        logger.warning(f"Task to update not found: ID {task_id} for user {user_id}")
    return task

async def delete_task(db: AsyncSession, task_id: int, user_id: int):
    task = await get_task(db, task_id, user_id)
    if task:
        await db.delete(task)
        await db.commit()
        logger.info(f"Task deleted: ID {task_id} for user {user_id}")
    else:
        logger.warning(f"Task to delete not found: ID {task_id} for user {user_id}")
    return task
