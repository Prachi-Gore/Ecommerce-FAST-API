from pydantic import BaseModel,EmailStr

class UserBase(BaseModel):
    email:EmailStr
    is_active:bool=True
    is_admin: bool=False
    is_verified:bool=False

class UserCreate(UserBase):
    password:str    

class UserOut(UserBase):
    id:int
    model_config={"from_attributes":True}

# class UserOutMe(UserBase):
#     id:int
#     class Config:
#         orm_mode = True   # <-- important to allow ORM objects in response

class UserLogin(BaseModel):
    email:EmailStr
    password:str