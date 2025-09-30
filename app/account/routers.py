from fastapi import APIRouter, Depends,Request,HTTPException,status
from fastapi.responses import JSONResponse
from app.account.schemas import UserCreate,UserOut,UserLogin
from app.account.services import create_user,authenticate_user,email_verification_send
from app.db.config import SessionDep
from app.account.utils import create_tokens,verify_refresh_token,set_cookie
from app.account.models import User
from app.account.deps import get_current_user

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

