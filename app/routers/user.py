from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, Token
from app.utils.security import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    logout_user
)
from app.schemas.response import ResponseModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=ResponseModel[UserSchema])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        coins=user.coins
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"code": 200, "msg": "", "data": db_user}

@router.post("/token", response_model=ResponseModel)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 返回标准格式的响应
    return ResponseModel(
        data={"access_token": access_token, "token_type": "bearer"},
        msg="Login successful"
    )

@router.get("/me", response_model=ResponseModel[UserSchema])
def read_users_me(current_user = Depends(get_current_active_user)):
    return ResponseModel(data=current_user)

@router.get("/", response_model=ResponseModel[List[UserSchema]])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    users = db.query(User).offset(skip).limit(limit).all()
    return ResponseModel(data=users)

@router.get("/{user_id}", response_model=ResponseModel[UserSchema])
def read_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(data=db_user)

@router.put("/{user_id}", response_model=ResponseModel[UserSchema])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 只有自己或管理员可以更新用户信息
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = user.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return ResponseModel(data=db_user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 只有自己或管理员可以删除用户
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(db_user)
    db.commit()
    return None

@router.put("/{user_id}/coins", response_model=ResponseModel[UserSchema])
def update_user_coins(
    user_id: int, 
    coins_data: dict = Body(..., example={"amount": 100}),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """更新用户的 coins 余额"""
    # 只有自己或管理员可以更新用户的 coins
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    amount = coins_data.get("amount", 0)
    db_user.coins = amount
    
    db.commit()
    db.refresh(db_user)
    return ResponseModel(data=db_user)

@router.post("/{user_id}/coins/add", response_model=ResponseModel[UserSchema])
def add_user_coins(
    user_id: int, 
    coins_data: dict = Body(..., example={"amount": 50}),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """向用户账户添加 coins"""
    # 只有自己或管理员可以添加用户的 coins
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    amount = coins_data.get("amount", 0)
    if amount < 0:
        raise HTTPException(status_code=400, detail="Amount cannot be negative")
    
    db_user.coins += amount
    
    db.commit()
    db.refresh(db_user)
    return ResponseModel(data=db_user)

@router.post("/{user_id}/coins/deduct", response_model=ResponseModel[UserSchema])
def deduct_user_coins(
    user_id: int, 
    coins_data: dict = Body(..., example={"amount": 20}),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """从用户账户扣除 coins"""
    # 只有自己或管理员可以扣除用户的 coins
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    amount = coins_data.get("amount", 0)
    if amount < 0:
        raise HTTPException(status_code=400, detail="Amount cannot be negative")
    
    if db_user.coins < amount:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    
    db_user.coins -= amount
    
    db.commit()
    db.refresh(db_user)
    return ResponseModel(data=db_user)

@router.put("/me", response_model=ResponseModel[UserSchema])
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    update_data = user_update.dict(exclude_unset=True)
    
    # 确保 coins 字段是整数
    if "coins" in update_data and update_data["coins"] is None:
        update_data["coins"] = 0
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return ResponseModel(data=current_user)

@router.post("/logout", response_model=ResponseModel)
def logout(current_user = Depends(get_current_active_user)):
    """用户登出"""
    success = logout_user(current_user.username)
    if success:
        return ResponseModel(data=None, msg="Successfully logged out")
    else:
        return ResponseModel(data=None, msg="No active session found") 