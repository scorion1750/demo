from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenData
import os
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "300"))

# 存储活跃会话
active_sessions: Dict[str, datetime] = {}
# 会话清理间隔（秒）
SESSION_CLEANUP_INTERVAL = 3600  # 1小时清理一次
last_cleanup_time = datetime.utcnow()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    print(f"Getting user with username: {username}")
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # 记录活跃会话
    username = data.get("sub")
    if username:
        active_sessions[username] = expire
    
    return encoded_jwt

def cleanup_expired_sessions():
    """清理过期的会话"""
    global last_cleanup_time
    now = datetime.utcnow()
    
    # 检查是否需要清理
    if (now - last_cleanup_time).total_seconds() < SESSION_CLEANUP_INTERVAL:
        return
    
    logger.info("开始清理过期会话...")
    expired_users = []
    for username, expire_time in active_sessions.items():
        if now > expire_time:
            expired_users.append(username)
    
    for username in expired_users:
        logger.info(f"清理用户 {username} 的过期会话")
        active_sessions.pop(username, None)
    
    last_cleanup_time = now
    logger.info(f"会话清理完成，移除了 {len(expired_users)} 个过期会话")

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 尝试解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # 检查令牌是否过期
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            # 令牌已过期，从活跃会话中移除
            active_sessions.pop(username, None)
            logger.warning(f"用户 {username} 的令牌已过期 | IP: {client_ip}")
            raise credentials_exception
        
        token_data = TokenData(username=username)
        
        # 更新会话活跃时间（如果是正常请求）
        path = request.url.path
        if not path.endswith("/token") and not path.endswith("/logout"):
            # 延长会话过期时间
            new_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            active_sessions[username] = new_expire
            logger.debug(f"更新用户 {username} 的会话过期时间为 {new_expire} | IP: {client_ip}")
        
        # 定期清理过期会话
        cleanup_expired_sessions()
        
    except ExpiredSignatureError:
        # 令牌已过期
        logger.warning(f"令牌已过期 | IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # 令牌无效
        logger.error(f"JWT错误: {str(e)} | IP: {client_ip}")
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        logger.warning(f"找不到用户: {token_data.username} | IP: {client_ip}")
        raise credentials_exception
    
    logger.info(f"用户 {username} 认证成功 | IP: {client_ip}")
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def logout_user(username: str):
    """登出用户，从活跃会话中移除"""
    if username in active_sessions:
        active_sessions.pop(username)
        logger.info(f"用户 {username} 已登出")
        return True
    return False 