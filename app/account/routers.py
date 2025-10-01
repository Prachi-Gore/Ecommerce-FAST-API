from fastapi import APIRouter, Depends,Request,HTTPException,status
from fastapi.responses import JSONResponse
from app.account.schemas import UserCreate,UserOut,UserLogin
from app.account.services import create_user,authenticate_user,email_verification_send
from app.db.config import SessionDep
from app.account.utils import create_tokens,verify_refresh_token,set_cookie,revoke_refresh_token
from app.account.models import User
from app.account.deps import get_current_user,require_admin

router=APIRouter()

@router.post("/register",response_model=UserOut)
async def register(session:SessionDep,user:UserCreate):
    return await create_user(session,user)

@router.post("/login")
async def login(session:SessionDep,user_login:UserLogin):
    user= await authenticate_user(session,user_login)
    if not user:
        return{"message":"Invalid"}
    tokens=await create_tokens(session,user)
    response=JSONResponse(content={"message":"Login Successful"})
    set_cookie(response,tokens)
    return response

@router.get("/me",response_model=UserOut)
async def me(user:User=Depends(get_current_user)):
    return user

@router.post("/refresh")
async def refresh_token(session:SessionDep,request:Request):
    token=request.cookies.get('refresh_token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    user=await verify_refresh_token(session,token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired refresh token"
        )
    tokens=await create_tokens(session,user)
    response=JSONResponse(content={"message":"Token refresh Successful"})
    set_cookie(response,tokens)
    return response

@router.post("/send-verificaton-email")
async def send_verification_email(user:User=Depends(get_current_user)):
    return await email_verification_send(user)

@router.get('/admin')
async def admin(user:User=Depends(require_admin)):
    return {
        "message":f"welcome Admin {user.email}"
    }

@router.post("/logout")
async def logout(session:SessionDep,request:Request,user:User=Depends(get_current_user)):
    refresh_token=request.cookies.get("refresh_token")
    if refresh_token:
       await revoke_refresh_token(session,refresh_token)
    response=JSONResponse(content={"detail":"Logged out"})
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    return response
