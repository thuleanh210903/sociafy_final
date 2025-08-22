#store endpoint / route of API version 1
# python package to import easily

from .role_router import router as role_router
from .auth_router import router as auth_router
from .post_router import router as post_router
from .upload_router import router as upload_router
from .user_router import router as user_router
from .friend_router import router as friend_router
from .reaction_router import router as reaction_router

routers = [
    (role_router, '/role', "Role"),
    (auth_router, '/auth', "Auth"),
    (post_router, '/post', "Post"),
    (upload_router, '/upload', "Image"),
    (user_router, '/user', "User"),
    (friend_router, '/friend', "Friend"),
    (reaction_router, '/react', "Reaction")
]
