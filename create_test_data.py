# 测试任务数据
from datetime import datetime, timedelta
from venv import logger
from app.database import SessionLocal
from app.models.task import RepeatType
from app.schemas.task import Task

today = datetime.now()
tomorrow = today + timedelta(days=1)
next_week = today + timedelta(days=7)

test_tasks = [
    {
        "title": "一次性任务",
        "description": "这是一个不重复的任务",
        "user_id": 1,  # admin 用户
        "repeat_type": RepeatType.NONE,
        "coins_reward": 1000,
        "due_date": tomorrow
    },
    {
        "title": "每日任务",
        "description": "这是一个每天重复的任务",
        "user_id": 1,
        "repeat_type": RepeatType.DAILY,
        "coins_reward": 500,
        "due_date": None
    },
    {
        "title": "每周任务",
        "description": "这是一个每周重复的任务",
        "user_id": 1,
        "repeat_type": RepeatType.WEEKLY,
        "coins_reward": 2000,
        "due_date": next_week
    },
    {
        "title": "每月任务",
        "description": "这是一个每月重复的任务",
        "user_id": 1,
        "repeat_type": RepeatType.MONTHLY,
        "coins_reward": 5000,
        "due_date": None
    },
    {
        "title": "用户2的任务",
        "description": "这是用户2的任务",
        "user_id": 2,  # user1 用户
        "repeat_type": RepeatType.NONE,
        "coins_reward": 1500,
        "due_date": tomorrow
    }
]

def create_test_tasks():
    db = SessionLocal()
    try:
        # 检查是否已有任务数据
        existing_tasks = db.query(Task).count()
        if existing_tasks > 0:
            logger.info(f"数据库中已有 {existing_tasks} 个任务，跳过测试数据创建")
            return
        
        # 创建测试任务
        for task_data in test_tasks:
            # 确保 coins_reward 不为 None
            coins_reward = task_data.get("coins_reward", 0)
            if coins_reward is None:
                coins_reward = 0
                
            db_task = Task(
                title=task_data["title"],
                description=task_data["description"],
                user_id=task_data["user_id"],
                repeat_type=task_data["repeat_type"],
                coins_reward=coins_reward,
                due_date=task_data["due_date"]
            )
            db.add(db_task)
            logger.info(f"创建任务: {task_data['title']} for user_id: {task_data['user_id']}")
        
        db.commit()
        logger.info(f"成功创建 {len(test_tasks)} 个测试任务")
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试任务时出错: {e}")
    finally:
        db.close()

# 测试任务计划数据
from app.models.task_plan import TaskPlan, TaskPlanStatus
from datetime import datetime, timedelta
from app.models.task import RepeatType  # 确保导入正确的枚举类型

today = datetime.now()
next_month = today + timedelta(days=30)

test_task_plans = [
    {
        "title": "每日健身计划",
        "description": "每天进行30分钟的健身锻炼",
        "user_id": 1,  # admin 用户
        "repeat_type": RepeatType.DAILY,  # 使用枚举对象，而不是字符串
        "coins_reward": 500,
        "status": TaskPlanStatus.ACTIVE,
        "start_date": today,
        "end_date": next_month
    },
    {
        "title": "每周阅读计划",
        "description": "每周阅读一本书",
        "user_id": 1,
        "repeat_type": RepeatType.WEEKLY,  # 使用枚举对象
        "coins_reward": 2000,
        "status": TaskPlanStatus.ACTIVE,
        "start_date": today,
        "end_date": None  # 无结束日期
    },
    {
        "title": "每月复习计划",
        "description": "每月复习所学知识",
        "user_id": 2,  # user1 用户
        "repeat_type": RepeatType.MONTHLY,  # 使用枚举对象
        "coins_reward": 5000,
        "status": TaskPlanStatus.ACTIVE,
        "start_date": today,
        "end_date": None
    }
]

def create_test_task_plans():
    db = SessionLocal()
    try:
        # 检查是否已有任务计划数据
        existing_plans = db.query(TaskPlan).count()
        if existing_plans > 0:
            logger.info(f"数据库中已有 {existing_plans} 个任务计划，跳过测试数据创建")
            return
        
        # 创建测试任务计划
        for plan_data in test_task_plans:
            db_plan = TaskPlan(
                title=plan_data["title"],
                description=plan_data["description"],
                user_id=plan_data["user_id"],
                repeat_type=plan_data["repeat_type"],
                coins_reward=plan_data["coins_reward"],
                status=plan_data["status"],
                start_date=plan_data["start_date"],
                end_date=plan_data["end_date"]
            )
            db.add(db_plan)
            logger.info(f"创建任务计划: {plan_data['title']} for user_id: {plan_data['user_id']}")
        
        db.commit()
        logger.info(f"成功创建 {len(test_task_plans)} 个测试任务计划")
        
        # 为每个计划生成第一个任务
        for plan in db.query(TaskPlan).all():
            from app.routers.task_plan import generate_tasks_from_plan
            generate_tasks_from_plan(plan.id, db)
            logger.info(f"为计划 {plan.title} 生成了初始任务")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试任务计划时出错: {e}")
    finally:
        db.close()

# 在主函数中调用
if __name__ == "__main__":
    logger.info("开始创建测试数据...")
    create_test_tasks()
    create_test_task_plans()
    logger.info("测试数据创建完成")