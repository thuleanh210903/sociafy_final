from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.api.v1 import routers

app = FastAPI(title="Sociafy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router, prefix, tag in routers:
    app.include_router(router, prefix=f"/api/v1{prefix}", tags=[tag])

@app.get('/api/v1')
def root():
    return {"message":"Hello"}