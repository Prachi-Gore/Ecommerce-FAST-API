from pydantic import BaseModel,Field

class CategoryCreate(BaseModel):
    name:str

class CategoryOut(CategoryCreate):
    id:int
    model_config={
        "from_attributes":True
    }