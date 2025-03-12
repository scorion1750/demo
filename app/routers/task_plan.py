from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, class_mapper
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models.task_plan import TaskPlan as TaskPlanModel, TaskPlanStatus
from app.models.task import Task as TaskModel, RepeatType
from app.schemas.task_plan import (
    TaskPlan as TaskPlanSchema,
    TaskPlanCreate,
    TaskPlanUpdate,
    TaskPlanWithInitialTask
)
from app.utils.security import get_current_active_user
from app.schemas.response import ResponseModel

router = APIRouter(
    prefix="/task-plans",
    tags=["task-plans"],
    responses={404: {"description": "Not found"}},
)

# 配置日志
logger = logging.getLogger(__name__)

def to_dict(model):
    """将 SQLAlchemy 模型转换为字典"""
    if model is None:
        return None
    
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return {c: getattr(model, c) for c in columns}

@router.post("/", response_model=ResponseModel)
def create_task_plan(
    task_plan: TaskPlanCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """创建新的任务计划，并立即生成第一个任务"""
    try:
        # 创建任务计划
        db_task_plan = TaskPlanModel(
            title=task_plan.title,
            description=task_plan.description,
            user_id=current_user.id,
            repeat_type=task_plan.repeat_type,
            coins_reward=task_plan.coins_reward,
            status=task_plan.status,
            start_date=task_plan.start_date,
            end_date=task_plan.end_date
        )
        db.add(db_task_plan)
        db.commit()
        db.refresh(db_task_plan)
        
        # 尝试创建初始任务
        try:
            initial_task = create_initial_task_from_plan(db_task_plan.id, db)
        except Exception as e:
            logger.error(f"Error creating initial task: {e}")
            initial_task = None
        
        # 使用 to_dict 方法转换
        result = {
            "task_plan": to_dict(db_task_plan),
            "initial_task": to_dict(initial_task)
        }
        
        msg = "任务计划创建成功"
        if initial_task:
            msg += "，并已生成第一个任务"
        else:
            msg += "，但初始任务创建失败"
        
        return ResponseModel(data=result, msg=msg)
    
    except Exception as e:
        logger.error(f"Error creating task plan: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建任务计划失败: {str(e)}")

@router.get("/", response_model=ResponseModel[List[TaskPlanSchema]])
def read_task_plans(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取当前用户的所有任务计划"""
    task_plans = db.query(TaskPlanModel).filter(
        TaskPlanModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return ResponseModel(data=task_plans)

@router.get("/{plan_id}", response_model=ResponseModel[TaskPlanSchema])
def read_task_plan(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """获取特定任务计划的详情"""
    task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    return ResponseModel(data=task_plan)

@router.put("/{plan_id}", response_model=ResponseModel[TaskPlanSchema])
def update_task_plan(
    plan_id: int, 
    task_plan: TaskPlanUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """更新任务计划"""
    db_task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if db_task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    # 更新任务计划属性
    for key, value in task_plan.dict(exclude_unset=True).items():
        setattr(db_task_plan, key, value)
    
    db.commit()
    db.refresh(db_task_plan)
    
    return ResponseModel(data=db_task_plan)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_plan(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """删除任务计划"""
    db_task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if db_task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    db.delete(db_task_plan)
    db.commit()
    
    return None

@router.post("/{plan_id}/pause", response_model=ResponseModel[TaskPlanSchema])
def pause_task_plan(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """暂停任务计划"""
    db_task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if db_task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    db_task_plan.status = TaskPlanStatus.PAUSED
    db.commit()
    db.refresh(db_task_plan)
    
    return ResponseModel(data=db_task_plan)

@router.post("/{plan_id}/activate", response_model=ResponseModel[TaskPlanSchema])
def activate_task_plan(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """激活任务计划"""
    db_task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if db_task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    db_task_plan.status = TaskPlanStatus.ACTIVE
    db.commit()
    db.refresh(db_task_plan)
    
    return ResponseModel(data=db_task_plan)

@router.post("/{plan_id}/complete", response_model=ResponseModel[TaskPlanSchema])
def complete_task_plan(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """完成任务计划"""
    db_task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if db_task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    db_task_plan.status = TaskPlanStatus.COMPLETED
    db.commit()
    db.refresh(db_task_plan)
    
    return ResponseModel(data=db_task_plan)

@router.post("/{plan_id}/generate-tasks", response_model=ResponseModel[TaskPlanSchema])
def manually_generate_tasks(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """手动生成任务"""
    db_task_plan = db.query(TaskPlanModel).filter(
        TaskPlanModel.id == plan_id,
        TaskPlanModel.user_id == current_user.id
    ).first()
    
    if db_task_plan is None:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    if db_task_plan.status != TaskPlanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Task plan is not active")
    
    generate_tasks_from_plan(plan_id, db)
    
    db.refresh(db_task_plan)
    return ResponseModel(data=db_task_plan)

# 辅助函数：根据计划生成任务
def generate_tasks_from_plan(plan_id: int, db: Session):
    """根据任务计划生成任务"""
    task_plan = db.query(TaskPlanModel).filter(TaskPlanModel.id == plan_id).first()
    if not task_plan or task_plan.status != TaskPlanStatus.ACTIVE:
        return
    
    now = datetime.now()
    
    # 检查是否已经结束
    if task_plan.end_date and task_plan.end_date < now:
        task_plan.status = TaskPlanStatus.COMPLETED
        db.commit()
        return
    
    # 检查上次生成时间，避免重复生成
    # 注意：对于新创建的计划，我们应该跳过这个检查，确保立即生成第一个任务
    if task_plan.last_generated:
        if task_plan.repeat_type == RepeatType.DAILY:
            # 如果今天已经生成过，则跳过
            if task_plan.last_generated.date() == now.date():
                return
        elif task_plan.repeat_type == RepeatType.WEEKLY:
            # 如果本周已经生成过，则跳过
            days_since_last = (now.date() - task_plan.last_generated.date()).days
            if days_since_last < 7:
                return
        elif task_plan.repeat_type == RepeatType.MONTHLY:
            # 如果本月已经生成过，则跳过
            if task_plan.last_generated.month == now.month and task_plan.last_generated.year == now.year:
                return
    
    # 生成新任务
    new_task = TaskModel(
        title=task_plan.title,
        description=task_plan.description,
        user_id=task_plan.user_id,
        repeat_type=task_plan.repeat_type,
        coins_reward=task_plan.coins_reward,
        task_plan_id=task_plan.id
    )
    
    # 设置截止日期
    if task_plan.repeat_type == RepeatType.DAILY:
        new_task.due_date = now + timedelta(days=1)
    elif task_plan.repeat_type == RepeatType.WEEKLY:
        new_task.due_date = now + timedelta(days=7)
    elif task_plan.repeat_type == RepeatType.MONTHLY:
        # 简单处理，加30天
        new_task.due_date = now + timedelta(days=30)
    
    db.add(new_task)
    
    # 更新上次生成时间
    task_plan.last_generated = now
    
    db.commit()
    
    # 返回新创建的任务，以便调用者可以使用
    return new_task

def create_initial_task_from_plan(plan_id: int, db: Session):
    """为新创建的任务计划创建第一个任务"""
    logger.info(f"Creating initial task for plan {plan_id}")
    
    task_plan = db.query(TaskPlanModel).filter(TaskPlanModel.id == plan_id).first()
    if not task_plan:
        logger.error(f"Task plan {plan_id} not found")
        return None
    
    # 即使计划不是活动状态，也创建初始任务
    now = datetime.now()
    
    # 创建新任务
    new_task = TaskModel(
        title=task_plan.title,
        description=task_plan.description,
        user_id=task_plan.user_id,
        repeat_type=task_plan.repeat_type,
        coins_reward=task_plan.coins_reward,
        task_plan_id=task_plan.id
    )
    
    # 设置截止日期，基于重复类型和开始日期
    if task_plan.repeat_type == RepeatType.NONE:
        # 对于非重复任务，使用计划的结束日期作为截止日期
        new_task.due_date = task_plan.end_date if task_plan.end_date else (now + timedelta(days=7))
    elif task_plan.repeat_type == RepeatType.DAILY:
        # 每日任务，截止日期为明天
        new_task.due_date = now + timedelta(days=1)
    elif task_plan.repeat_type == RepeatType.WEEKLY:
        # 每周任务，截止日期为一周后
        new_task.due_date = now + timedelta(days=7)
    elif task_plan.repeat_type == RepeatType.MONTHLY:
        # 每月任务，截止日期为30天后
        new_task.due_date = now + timedelta(days=30)
    
    db.add(new_task)
    
    # 更新上次生成时间
    task_plan.last_generated = now
    
    db.commit()
    db.refresh(new_task)
    
    return new_task 