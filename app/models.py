from sqlalchemy import TIMESTAMP, Column, Integer, String, Boolean, text, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship

from .database import Base

class Post(Base):
  __tablename__ = "posts"

  id = Column(Integer, primary_key=True, index=True, nullable=False)
  title = Column(String, index=True, nullable=False)
  content = Column(String, index=True, nullable=False)
  published = Column(Boolean, server_default=expression.true()) 
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
  owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  owner = relationship("User")


class User(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key=True, index=True, nullable=False)
  email = Column(String, unique=True, nullable=False, index=True)
  password = Column(String, nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Vote(Base):
  __tablename__ = "votes"
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
  post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))



