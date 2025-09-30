# from passlib.context import CryptContext
# from passlib.hash import argon2
from sqlalchemy.ext.asyncio import AsyncSession
from app.account.models import User,RefreshToken
from argon2 import PasswordHasher
from datetime import timedelta,datetime,timezone
from decouple import config
from jose import ExpiredSignatureError, JWTError, jwt
import uuid
from fastapi import HTTPException,status
from sqlalchemy import select

# pwd_context=CryptContext(schemes=["bcrypt"],deprecated='auto')
argon2 = PasswordHasher()

JWT_ACCESS_TOKEN_TIME_MIN=config("JWT_ACCESS_TOKEN_TIME_MIN",cast=int)
JWT_SECRETE_KEY=config("JWT_SECRETE_KEY")
JWT_ALGORITHM=config("JWT_ALGORITHM")
JWT_REFRESH_TOKEN_TIME_DAY=config("JWT_REFRESH_TOKEN_TIME_DAY",cast=int)
EMAIL_VERIFICATION_TOKEN_TIME_HR=config("EMAIL_VERIFICATION_TOKEN_TIME_HR",cast=int)

def hash_password(password:str):
     return argon2.hash(password)

def verify_password(stored_hash: str, plain_password: str) -> bool:
    try:
        return argon2.verify(stored_hash, plain_password)
    except Exception:
     #    print("Verification error:", e)
        return False

def create_access_token(data:dict,       expires_delta:timedelta=None):
     to_encode=data.copy()
     expire=datetime.now(timezone.utc)+(expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_TIME_MIN))
     to_encode.update({"exp":expire})

     return jwt.encode(to_encode,JWT_SECRETE_KEY,JWT_ALGORITHM)

async def create_tokens(session:AsyncSession,user:User):
    access_token=create_access_token(data={"sub":str(user.id)})
    refresh_token_str=str(uuid.uuid4())
    expires_at=datetime.now(timezone.utc)+timedelta(days=JWT_REFRESH_TOKEN_TIME_DAY)
    refresh_token=RefreshToken(
        user_id=user.id,
        expires_at=expires_at,
        token=refresh_token_str
    )
    session.add(refresh_token)
    await session.commit()
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer"
    }

def decode_token(token:str):
    try:
        return jwt.decode(token,JWT_SECRETE_KEY,algorithms=JWT_ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
async def verify_refresh_token(session:AsyncSession,token:str): 
    stmt=select(RefreshToken).where(RefreshToken.token==token) 
    result = await session.scalars(stmt) 
    db_refresh_token=result.first()
    print("123456789 ",db_refresh_token,repr(token),db_refresh_token and not db_refresh_token.revoked)
    if db_refresh_token and not db_refresh_token.revoked :
        expires_at=db_refresh_token.expires_at
        if expires_at.tzinfo is None:
           expires_at=expires_at.replace(tzinfo=timezone.utc)
        if expires_at > datetime.now(timezone.utc):
            user_stmt=select(User).where(User.id==db_refresh_token.user_id)
            user_result=await session.scalars(user_stmt)
            return user_result.first()
    return None

def set_cookie(response,tokens):
    response.set_cookie(
        "access_token",
        value=tokens['access_token'],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60*60*24*1 # browser time
    )
    response.set_cookie(
        "refresh_token",
        value=tokens['refresh_token'].token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60*60*24*7 # browser time
    )
    
def create_email_verification_token(user_id:int):
    expire= datetime.now(timezone.utc)+timedelta(hours=EMAIL_VERIFICATION_TOKEN_TIME_HR)
    to_encode={"sub":str(user_id),"type":"verify_email","exp":expire} 
    return jwt.encode(to_encode,JWT_SECRETE_KEY,algorithm=JWT_ALGORITHM)   