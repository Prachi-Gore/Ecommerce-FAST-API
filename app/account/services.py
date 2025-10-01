from app.account.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException,status

from app.account.schemas import UserCreate,UserLogin
from app.account.utils import hash_password,verify_password,create_email_verification_token

async def create_user(session:AsyncSession,user:UserCreate):
    # check whether this email has already in db
    stmt=select(User).where(User.email==user.email)
    result = await session.scalars(stmt)
    if(result.first()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Email alredy registered')
    
    new_user=User(
         **user.model_dump(exclude={"password","email"}),
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

# add() → stage object for insert

# commit() → persist it in the DB (transaction ends)

# refresh() → sync the object with the DB (get updated values)

# return new_user → now you have a fully saved & refreshed user object

async def authenticate_user(session:AsyncSession,user_login:UserLogin):
    stmt=select(User).where(User.email==user_login.email)
    result=await session.scalars(stmt)
    user=result.first()
    if(user and verify_password(user.hashed_password,user_login.password)):
        return user
    return None

async def email_verification_send(user:User):
    token= create_email_verification_token(user.id)
    link=f"http://localhost:8000/account/verify?token={token}"
    print('link',link)
    return {
        "message":"Verification email sent"
    }