from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from database import Base

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    deadline = Column(DateTime)
    text = Column(String)
    task_status = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)