from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.story import Story, StoryChapter, StoryChoice, UserStory, UserStoryResponse, StoryType as ModelStoryType
from app.models.user import User
from app.schemas.story import (
    Story as StorySchema,
    StoryCreate,
    StoryUpdate,
    StoryChapter as StoryChapterSchema,
    StoryChapterCreate,
    StoryChapterUpdate,
    StoryChoice as StoryChoiceSchema,
    StoryChoiceCreate,
    StoryChoiceUpdate,
    UserStory as UserStorySchema,
    UserStoryCreate,
    UserStoryUpdate,
    UserStoryResponse as UserStoryResponseSchema,
    UserStoryResponseCreate,
    StoryType
)
from app.utils.security import get_current_active_user
from app.schemas.response import ResponseModel
from app.utils.response import error_response

router = APIRouter(
    prefix="/stories",
    tags=["stories"],
    responses={404: {"description": "Not found"}},
)

# 管理员路由 - 创建和管理故事
@router.post("/", response_model=ResponseModel[StorySchema])
def create_story(
    story: StoryCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """创建新故事"""
    db_story = Story(
        title=story.title,
        description=story.description,
        story_type=story.story_type,
        unlock_cost=story.unlock_cost,
        is_active=story.is_active
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return ResponseModel(data=db_story)

@router.get("/", response_model=ResponseModel[List[StorySchema]])
def read_stories(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取所有故事"""
    query = db.query(Story)
    if active_only:
        query = query.filter(Story.is_active == True)
    stories = query.offset(skip).limit(limit).all()
    return ResponseModel(data=stories)

@router.get("/{story_id}", response_model=ResponseModel[StorySchema])
def read_story(
    story_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取特定故事"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return ResponseModel(data=story)

@router.put("/{story_id}", response_model=ResponseModel[StorySchema])
def update_story(
    story_id: int, 
    story: StoryUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """更新故事（仅管理员）"""
    # 检查权限
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    update_data = story.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_story, key, value)
    
    db.commit()
    db.refresh(db_story)
    return ResponseModel(data=db_story)

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(
    story_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """删除故事（仅管理员）"""
    # 检查权限
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(db_story)
    db.commit()
    return None

# 章节管理
@router.post("/chapters", response_model=ResponseModel[StoryChapterSchema])
def create_chapter(
    chapter: StoryChapterCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """创建新的故事章节"""
    # 检查权限
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 检查故事是否存在
    story = db.query(Story).filter(Story.id == chapter.story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db_chapter = StoryChapter(
        story_id=chapter.story_id,
        title=chapter.title,
        content=chapter.content,
        order_num=chapter.order_num
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return ResponseModel(data=db_chapter)

@router.get("/chapters/{story_id}", response_model=ResponseModel[List[StoryChapterSchema]])
def read_story_chapters(
    story_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取故事的所有章节"""
    # 检查故事是否存在
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapters = db.query(StoryChapter).filter(
        StoryChapter.story_id == story_id
    ).order_by(StoryChapter.order_num).all()
    
    return ResponseModel(data=chapters)

@router.get("/chapters/{chapter_id}", response_model=ResponseModel[StoryChapterSchema])
def read_chapter(
    chapter_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取特定章节"""
    chapter = db.query(StoryChapter).filter(StoryChapter.id == chapter_id).first()
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ResponseModel(data=chapter)

@router.put("/chapters/{chapter_id}", response_model=ResponseModel[StoryChapterSchema])
def update_chapter(
    chapter_id: int, 
    chapter: StoryChapterUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """更新章节（仅管理员）"""
    # 检查权限
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_chapter = db.query(StoryChapter).filter(StoryChapter.id == chapter_id).first()
    if db_chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    update_data = chapter.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_chapter, key, value)
    
    db.commit()
    db.refresh(db_chapter)
    return ResponseModel(data=db_chapter)

@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(
    chapter_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """删除章节（仅管理员）"""
    # 检查权限
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_chapter = db.query(StoryChapter).filter(StoryChapter.id == chapter_id).first()
    if db_chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    db.delete(db_chapter)
    db.commit()
    return None

# 选择管理
@router.post("/choices", response_model=ResponseModel[StoryChoiceSchema])
def create_choice(
    choice: StoryChoiceCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """创建新的故事选择"""
    # 检查权限
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 检查章节是否存在
    chapter = db.query(StoryChapter).filter(StoryChapter.id == choice.chapter_id).first()
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # 如果指定了下一章节，检查它是否存在
    if choice.next_chapter_id:
        next_chapter = db.query(StoryChapter).filter(StoryChapter.id == choice.next_chapter_id).first()
        if next_chapter is None:
            raise HTTPException(status_code=404, detail="Next chapter not found")
    
    db_choice = StoryChoice(
        chapter_id=choice.chapter_id,
        text=choice.text,
        next_chapter_id=choice.next_chapter_id
    )
    db.add(db_choice)
    db.commit()
    db.refresh(db_choice)
    return ResponseModel(data=db_choice)

# 用户故事交互
@router.post("/unlock/{story_id}", response_model=ResponseModel[UserStorySchema])
def unlock_story(
    story_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """解锁故事"""
    # 检查故事是否存在
    story = db.query(Story).filter(Story.id == story_id, Story.is_active == True).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found or not active")
    
    # 检查用户是否已经解锁了这个故事
    existing_user_story = db.query(UserStory).filter(
        UserStory.user_id == current_user.id,
        UserStory.story_id == story_id
    ).first()
    
    if existing_user_story:
        return ResponseModel(data=existing_user_story)
    
    # 检查用户是否有足够的coins
    if current_user.coins < story.unlock_cost:
        raise HTTPException(status_code=400, detail="Not enough coins to unlock this story")
    
    # 扣除用户的coins
    current_user.coins -= story.unlock_cost
    
    # 获取故事的第一个章节
    first_chapter = db.query(StoryChapter).filter(
        StoryChapter.story_id == story_id
    ).order_by(StoryChapter.order_num).first()
    
    # 创建用户故事记录
    user_story = UserStory(
        user_id=current_user.id,
        story_id=story_id,
        current_chapter_id=first_chapter.id if first_chapter else None
    )
    
    db.add(user_story)
    db.commit()
    db.refresh(user_story)
    
    return ResponseModel(data=user_story)

@router.get("/my", response_model=ResponseModel[List[UserStorySchema]])
def read_my_stories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取用户解锁的所有故事"""
    user_stories = db.query(UserStory).filter(
        UserStory.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    print('user_stories===',user_stories)
    
    return ResponseModel(data=user_stories)

@router.get("/my/{story_id}", response_model=ResponseModel[UserStorySchema])
def read_my_story(
    story_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取用户特定的解锁故事"""
    user_story = db.query(UserStory).filter(
        UserStory.user_id == current_user.id,
        UserStory.story_id == story_id
    ).first()
    
    if user_story is None:
        raise error_response(404, "Story not unlocked")
    
    return ResponseModel(data=user_story)

@router.post("/my/{story_id}/respond", response_model=ResponseModel[UserStorySchema])
def respond_to_story(
    story_id: int,
    response: UserStoryResponseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """响应故事选项，推进故事进度"""
    # 检查用户是否解锁了这个故事
    user_story = db.query(UserStory).filter(
        UserStory.user_id == current_user.id,
        UserStory.story_id == story_id
    ).first()
    
    if user_story is None:
        raise HTTPException(status_code=404, detail="Story not unlocked")
    
    # 检查选项是否存在且属于当前章节
    choice = None
    if response.choice_id:
        choice = db.query(StoryChoice).filter(
            StoryChoice.id == response.choice_id,
            StoryChoice.chapter_id == user_story.current_chapter_id
        ).first()
        
        if choice is None:
            raise HTTPException(status_code=404, detail="Choice not found or not valid for current chapter")
    
    # 记录用户的选择
    db_response = UserStoryResponse(
        user_story_id=user_story.id,
        chapter_id=user_story.current_chapter_id,
        choice_id=response.choice_id,
        custom_response=response.custom_response
    )
    db.add(db_response)
    
    # 更新用户故事进度
    if choice and choice.next_chapter_id:
        user_story.current_chapter_id = choice.next_chapter_id
        
        # 检查是否是最后一个章节
        next_chapter = db.query(StoryChapter).filter(StoryChapter.id == choice.next_chapter_id).first()
        if next_chapter:
            # 检查这个章节是否有选择
            has_choices = db.query(StoryChoice).filter(StoryChoice.chapter_id == next_chapter.id).first() is not None
            if not has_choices:
                # 如果没有选择，标记故事为已完成
                user_story.is_completed = True
    
    db.commit()
    db.refresh(user_story)
    
    return ResponseModel(data=user_story)

@router.get("/my/{story_id}/current", response_model=ResponseModel[StoryChapterSchema])
def get_current_chapter(
    story_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取当前章节"""
    # 检查用户是否已解锁该故事
    user_story = db.query(UserStory).filter(
        UserStory.user_id == current_user.id,
        UserStory.story_id == story_id
    ).first()
    
    if user_story is None:
        raise HTTPException(status_code=404, detail="Story not unlocked")
    
    if user_story.current_chapter_id is None:
        raise HTTPException(status_code=404, detail="No current chapter")
    
    chapter = db.query(StoryChapter).filter(
        StoryChapter.id == user_story.current_chapter_id
    ).first()
    
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return ResponseModel(data=chapter) 