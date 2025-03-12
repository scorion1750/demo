from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.task import Task as TaskModel, RepeatType
from app.models.task_completion import TaskCompletion as TaskCompletionModel
from app.models.user import User
from app.schemas.task import (
    Task as TaskSchema,
    TaskCreate,
    TaskUpdate,
    TaskCompletion as TaskCompletionSchema
)
from app.utils.security import get_current_active_user
from app.schemas.response import ResponseModel

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ResponseModel[TaskSchema])
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """创建新任务"""
    db_task = TaskModel(
        title=task.title,
        description=task.description,
        user_id=current_user.id,
        repeat_type=task.repeat_type,
        coins_reward=task.coins_reward,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return ResponseModel(data=db_task)

@router.get("/", response_model=ResponseModel[List[TaskSchema]])
def read_tasks(
    skip: int = 0, 
    limit: int = 100, 
    completed: Optional[bool] = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取当前用户的所有任务"""
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)
    
    if completed is not None:
        query = query.filter(TaskModel.is_completed == completed)
    
    tasks = query.offset(skip).limit(limit).all()
    return ResponseModel(data=tasks)

@router.get("/{task_id}", response_model=ResponseModel[TaskSchema])
def read_task(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """获取特定任务的详情"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return ResponseModel(data=task)

@router.put("/{task_id}", response_model=ResponseModel[TaskSchema])
def update_task(
    task_id: int, 
    task: TaskUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """更新任务"""
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 更新任务属性
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    
    return ResponseModel(data=db_task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """删除任务"""
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    
    return None

@router.post("/{task_id}/complete", response_model=ResponseModel[TaskSchema])
def complete_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """完成任务"""
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.is_completed:
        raise HTTPException(status_code=400, detail="Task is already completed")
    
    # 标记任务为已完成
    db_task.is_completed = True
    
    # 创建完成记录
    completion = TaskCompletionModel(
        task_id=db_task.id,
        user_id=current_user.id
    )
    db.add(completion)
    
    # 奖励用户 coins
    user = db.query(User).filter(User.id == current_user.id).first()
    user.coins += db_task.coins_reward
    
    # 如果是重复任务，创建新的任务实例
    if db_task.repeat_type != RepeatType.NONE:
        new_task = TaskModel(
            title=db_task.title,
            description=db_task.description,
            user_id=db_task.user_id,
            repeat_type=db_task.repeat_type,
            coins_reward=db_task.coins_reward,
            task_plan_id=db_task.task_plan_id
        )
        
        # 设置新任务的截止日期
        if db_task.due_date:
            if db_task.repeat_type == RepeatType.DAILY:
                new_task.due_date = db_task.due_date + timedelta(days=1)
            elif db_task.repeat_type == RepeatType.WEEKLY:
                new_task.due_date = db_task.due_date + timedelta(days=7)
            elif db_task.repeat_type == RepeatType.MONTHLY:
                # 简单处理，加30天
                new_task.due_date = db_task.due_date + timedelta(days=30)
        
        db.add(new_task)
    
    db.commit()
    db.refresh(db_task)
    
    return ResponseModel(data=db_task)

@router.post("/{task_id}/uncomplete", response_model=ResponseModel[TaskSchema])
def uncomplete_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """取消完成任务"""
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not db_task.is_completed:
        raise HTTPException(status_code=400, detail="Task is not completed")
    
    # 查找最近的完成记录
    completion = db.query(TaskCompletionModel).filter(
        TaskCompletionModel.task_id == db_task.id,
        TaskCompletionModel.user_id == current_user.id
    ).order_by(TaskCompletionModel.completed_at.desc()).first()
    
    if completion:
        # 删除完成记录
        db.delete(completion)
        
        # 扣除用户获得的 coins
        user = db.query(User).filter(User.id == current_user.id).first()
        user.coins -= db_task.coins_reward
        if user.coins < 0:
            user.coins = 0
    
    # 标记任务为未完成
    db_task.is_completed = False
    
    db.commit()
    db.refresh(db_task)
    
    return ResponseModel(data=db_task)

@router.get("/{task_id}/completions", response_model=ResponseModel[List[TaskCompletionSchema]])
def read_task_completions_by_task(
    task_id: int,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取特定任务的完成记录"""
    # 首先检查任务是否存在且属于当前用户
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == current_user.id
    ).first()
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 获取任务的完成记录
    completions = db.query(TaskCompletionModel).filter(
        TaskCompletionModel.task_id == task_id,
        TaskCompletionModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return ResponseModel(data=completions)

@router.get("/completions", response_model=ResponseModel[List[TaskCompletionSchema]])
def read_all_task_completions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取当前用户的所有任务完成记录"""
    print(current_user)
    completions = db.query(TaskCompletionModel).filter(
        TaskCompletionModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return ResponseModel(data=completions)

@router.get("/due/today", response_model=ResponseModel[List[TaskSchema]])
def read_tasks_due_today(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取今天到期的任务"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # 获取今天到期的非重复任务
    non_repeat_tasks = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id,
        TaskModel.repeat_type == RepeatType.NONE,
        TaskModel.due_date >= today,
        TaskModel.due_date < tomorrow,
        TaskModel.is_completed == False
    ).all()
    
    # 获取每日重复任务
    daily_tasks = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id,
        TaskModel.repeat_type == RepeatType.DAILY,
        TaskModel.is_completed == False
    ).all()
    
    # 获取每周重复任务（如果今天是任务创建的同一星期几）
    weekly_tasks = []
    weekly_tasks_query = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id,
        TaskModel.repeat_type == RepeatType.WEEKLY,
        TaskModel.is_completed == False
    ).all()
    
    for task in weekly_tasks_query:
        if task.created_at.weekday() == today.weekday():
            weekly_tasks.append(task)
    
    # 获取每月重复任务（如果今天是任务创建的同一日期）
    monthly_tasks = []
    monthly_tasks_query = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id,
        TaskModel.repeat_type == RepeatType.MONTHLY,
        TaskModel.is_completed == False
    ).all()
    
    for task in monthly_tasks_query:
        if task.created_at.day == today.day:
            monthly_tasks.append(task)
    
    # 合并所有任务
    all_tasks = non_repeat_tasks + daily_tasks + weekly_tasks + monthly_tasks
    return ResponseModel(data=all_tasks)
