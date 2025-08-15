#store endpoint / route of API version 1
# python package to import easily

from .role_router import router as role_router
from .auth_router import router as auth_router

routers = [
    (role_router, '/role', "Role"),
    (auth_router, '/auth', "Auth")
]
