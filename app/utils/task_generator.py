from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal
from app.models.task_plan import TaskPlan, TaskPlanStatus
from app.routers.task_plan import generate_tasks_from_plan
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_tasks_for_all_active_plans():
    """为所有活跃的任务计划生成任务"""
    db = SessionLocal()
    try:
        # 获取所有活跃的任务计划
        active_plans = db.query(TaskPlan).filter(TaskPlan.status == TaskPlanStatus.ACTIVE).all()
        logger.info(f"找到 {len(active_plans)} 个活跃的任务计划")
        
        for plan in active_plans:
            try:
                new_tasks = generate_tasks_from_plan(plan.id, db)
                if new_tasks:
                    logger.info(f"为计划 {plan.id} ({plan.title}) 生成了 {len(new_tasks)} 个新任务")
            except Exception as e:
                logger.error(f"为计划 {plan.id} 生成任务时出错: {e}")
        
        logger.info("任务生成完成")
    except Exception as e:
        logger.error(f"生成任务时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始生成任务...")
    generate_tasks_for_all_active_plans() 