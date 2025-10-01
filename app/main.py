from fastapi import FastAPI

from app.account.routers import router as account_router
from app.product.routers.categoryRouter import router as category_router


app=FastAPI(title="FastAPI E-Commerce Backend")

@app.get("/")
def root():
    return {'message':'welcome to the ecommerce api'}

app.include_router(account_router,prefix="/api/account",tags=["Account"])
app.include_router(category_router,prefix="/api/products/category",tags=["Category"])