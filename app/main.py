from fastapi import FastAPI

app=FastAPI(title="FastAPI E-Commerce Backend")

@app.get("/")
def root():
    return {'message':'welcome to the ecommerce api'}
