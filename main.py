from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends
from typing import Optional, List, Dict, Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from authx import AuthX, AuthXConfig, token

from models import Base, Task, User
from database import engine, session_local
from schemas import TaskCreate, TaskSchema, UserCreate, UserLoginSchema, UserSchema


app = FastAPI()
config = AuthXConfig()
config.JWT_SECRET_KEY = 'Jojopidr'
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['headers']

Base.metadata.create_all(bind=engine)


def ensure_task_user_id_column():
    inspector = inspect(engine)
    if 'task' not in inspector.get_table_names():
        return

    task_columns = {column['name'] for column in inspector.get_columns('task')}
    if 'user_id' not in task_columns:
        with engine.begin() as connection:
            connection.execute(text('ALTER TABLE task ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1'))


ensure_task_user_id_column()


security = AuthX(config=config)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

def get_user_id(credentials=Depends(security.access_token_required)):
    user_id = getattr(credentials, 'sub', None) or getattr(credentials, 'uid', None)
    if user_id is None:
        raise HTTPException(status_code=401, detail='Invalid authentication token')
    return int(user_id)
    
# Task endpoints
@app.get('/task', response_model=List[TaskSchema])
async def list_tasks(db: Session = Depends(get_db), user_id=Depends(get_user_id)) -> List[TaskSchema]:
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks

@app.post('/task/add', response_model=TaskSchema)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), user_id=Depends(get_user_id)) -> TaskCreate:
    db_task = Task(name = task.name, deadline = task.deadline, text = task.text, task_status = task.task_status, user_id = user_id)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@app.put('/task/edit/{task_id}', response_model=TaskSchema)
async def edit_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db), user_id=Depends(get_user_id)) -> TaskSchema:
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')

    db_task.name = task.name
    db_task.deadline = task.deadline
    db_task.text = task.text
    db_task.task_status = task.task_status

    db.commit()
    db.refresh(db_task)

    return db_task

@app.delete('/task/delete/{task_id}', response_model=TaskSchema)
async def delete_task(task_id: int, db: Session = Depends(get_db), user_id = Depends(get_user_id)) -> TaskSchema:
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')
    
    db.delete(db_task)
    db.commit()

    return db_task

#Users endpoints
@app.post('/register')
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')

    db_user = User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post('/login')
async def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail='Invalid email or password')

    access_token = security.create_access_token(uid=str(db_user.id))

    return {
        'uid': db_user.id,
        'email': db_user.email,
        'access_token': access_token,
        'token_type': 'bearer'
    }

@app.get('/users', response_model=List[UserSchema])
async def list_users(db: Session = Depends(get_db)) -> List[UserSchema]:
    users = db.query(User).all()
    return users