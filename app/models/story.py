from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class StoryType(str, enum.Enum):
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    SCIFI = "scifi"
    FANTASY = "fantasy"
    HORROR = "horror"

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    story_type = Column(Enum(StoryType), default=StoryType.ADVENTURE)
    unlock_cost = Column(BigInteger, nullable=False, default=5000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    chapters = relationship("StoryChapter", back_populates="story", cascade="all, delete-orphan")
    user_stories = relationship("UserStory", back_populates="story", cascade="all, delete-orphan")

class StoryChapter(Base):
    __tablename__ = "story_chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    order_num = Column(Integer, default=1)  # 章节顺序
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    story = relationship("Story", back_populates="chapters")
    choices = relationship("StoryChoice", back_populates="chapter", foreign_keys="StoryChoice.chapter_id", cascade="all, delete-orphan")
    next_for_choices = relationship("StoryChoice", foreign_keys="StoryChoice.next_chapter_id")

class StoryChoice(Base):
    __tablename__ = "story_choices"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("story_chapters.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(500), nullable=False)
    next_chapter_id = Column(Integer, ForeignKey("story_chapters.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    chapter = relationship("StoryChapter", back_populates="choices", foreign_keys=[chapter_id])
    next_chapter = relationship("StoryChapter", foreign_keys=[next_chapter_id])

class UserStory(Base):
    __tablename__ = "user_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    current_chapter_id = Column(Integer, ForeignKey("story_chapters.id", ondelete="SET NULL"), nullable=True)
    is_completed = Column(Boolean, default=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User")
    story = relationship("Story", back_populates="user_stories")
    current_chapter = relationship("StoryChapter")
    responses = relationship("UserStoryResponse", back_populates="user_story", cascade="all, delete-orphan")

class UserStoryResponse(Base):
    __tablename__ = "user_story_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_story_id = Column(Integer, ForeignKey("user_stories.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("story_chapters.id", ondelete="CASCADE"), nullable=False)
    choice_id = Column(Integer, ForeignKey("story_choices.id", ondelete="SET NULL"), nullable=True)
    custom_response = Column(Text, nullable=True)  # 用户自定义回应
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user_story = relationship("UserStory", back_populates="responses")
    chapter = relationship("StoryChapter")
    choice = relationship("StoryChoice") 