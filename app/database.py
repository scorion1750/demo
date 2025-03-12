import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# 获取数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

logger.info(f"Connecting to database: {DATABASE_URL}")

# 修改连接字符串格式
# 使用 mysql-connector-python 而不是 pymysql
if DATABASE_URL.startswith('mysql+pymysql'):
    DATABASE_URL = DATABASE_URL.replace('mysql+pymysql', 'mysql+mysqlconnector')
    logger.info(f"Updated connection string to: {DATABASE_URL}")

try:
    # 创建引擎时不使用额外参数
    engine = create_engine(
        DATABASE_URL,
        echo=False  # 设置为True可以查看SQL语句
    )
    # 测试连接
    with engine.connect() as conn:
        logger.info("Database connection successful")
except Exception as e:
    logger.error(f"Database connection error: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 