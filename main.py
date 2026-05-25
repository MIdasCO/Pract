from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session
from authx import AuthX, AuthXConfig

from models import Base, Task, User
from database import engine, session_local
from schemas import TaskCreate, TaskSchema, UserCreate, UserLoginSchema, UserSchema


app = FastAPI()
config = AuthXConfig()
config.JWT_SECRET_KEY = 'Jojopidr'
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies']

Base.metadata.create_all(bind=engine)


security = AuthX(config=config)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# Task endpoints
@app.get('/task', response_model=List[TaskSchema])
async def list_tasks(db: Session = Depends(get_db)) -> List[TaskSchema]:
    tasks = db.query(Task).all()
    return tasks

@app.post('/task/add', response_model=TaskSchema)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskCreate:
    db_task = Task(name = task.name, deadline = task.deadline, text = task.text, task_status = task.task_status)
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@app.put('/task/edit/{task_id}', response_model=TaskSchema)
async def edit_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)) -> TaskSchema:
    db_task = db.query(Task).filter(Task.id == task_id).first()
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
async def delete_task(task_id: int, db: Session = Depends(get_db)) -> TaskSchema:
    db_task = db.query(Task).filter(Task.id == task_id).first()
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

    return {"access_token": access_token, "uid": db_user.id}

# @app.post('/users/add', response_model=UserSchema)
# async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
#     db_user = User(name=user.name, email=user.email, password=user.password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)

#     return db_user

@app.get('/users', response_model=List[UserSchema])
async def list_users(db: Session = Depends(get_db)) -> List[UserSchema]:
    users = db.query(User).all()
    return users

# @app.post('/users/add', response_model=DBUser)
# async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
#     db_user = User(name=user.name, age=user.age)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)

#     return db_user

# @app.post('/post/add', response_model=PostResponse)
# async def create_post(post: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
#     db_user = db.query(User).filter(User.id == post.author_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail='Not found user')

#     db_post = Post(title=post.title, body=post.body, author_id = post.author_id)
#     db.add(db_post)
#     db.commit()
#     db.refresh(db_post)

#     return db_post









# # @app.get("/")
# # async def home() -> list:
# #     return [1,2,3,4]

# # @app.get("/contacts")
# # async def home_index() -> int:
# #     return 55

# # @app.get("/numbers")
# # async def home_contacts() -> int:
# #     return 55

# # @app.get('/items')
# # async def get_items() -> List[Post]:
# #     return [Post(**post) for post in posts]

# # @app.get('/items/{id}')
# # async def get_item_by_id(id: Annotated[int, Path(..., title = 'Здесь id post', ge = 1, lt = 100)]) -> Post:
# #     for post in posts:
# #         if post['id'] == id:
# #             return Post(**post)
        
# #     raise HTTPException(status_code=404, detail="Post not found")


# # @app.get('/search')
# # async def search(post_id: Annotated[Optional[int], Path(title='Поиск клиента по id'), Query()])->Dict[str, Optional[Post]]:
# #     if post_id:
# #         for post in posts:
# #             if post['id'] == post_id:
# #                 return {'data' : Post(**post)}
# #         raise HTTPException(status_code=404, detail='Not Found Post ID')
# #     else:
# #         return {'data': None}
    
# # @app.post('/items/add')
# # async def add_item(post: PostCreate) -> Post:
# #     author = next((u for u in users if u['id'] == post.author_id), None)
# #     if not author:
# #         raise HTTPException(status_code=404, detail="Author not found")

# #     new_post_id = len(posts) + 1
# #     new_post = {'id': new_post_id, 'title': post.title, 'body': post.body, 'author': author}
# #     posts.append(new_post)
# #     return Post(**new_post)

# # @app.post('/user/add')
# # async def add_user(post: Annotated[UserCreate, Body(..., example={"name":"UserName", "age": 1})]) -> User:
# #     new_user_id = len(users) + 1
# #     new_user = {'id': new_user_id, 'name': users.name, 'age': users.age}
# #     users.append(new_user)
