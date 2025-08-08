from fastapi import FastAPI
from app.api.v1 import routers

app = FastAPI(title="Sociafy API")


for router, prefix, tag in routers:
    app.include_router(router, prefix=f"/api/v1{prefix}", tags=[tag])

@app.get('/api/v1')
def root():
    return {"message":"Hello"}