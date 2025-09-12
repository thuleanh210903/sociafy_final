#store endpoint / route of API version 1
# python package to import easily

from .role_router import router as role_router
from .auth_router import router as auth_router
from .post_router import router as post_router
from .upload_router import router as upload_router
from .user_router import router as user_router
from .friend_router import router as friend_router
from .reaction_router import router as reaction_router
from .comment_router import router as comment_router
from .share_router import router as share_router
from .notify_router import router as notify_router
from .report_router import router as report_router
from .violation_router import router as violation_router
from .ai_flag_router import router as ai_flag_router
from .ai_flag_disputes import router as ai_flag_disputes

routers = [
    (role_router, '/role', "Role"),
    (auth_router, '/auth', "Auth"),
    (post_router, '/post', "Post"),
    (upload_router, '/upload', "Image"),
    (user_router, '/user', "User"),
    (friend_router, '/friend', "Friend"),
    (reaction_router, '/react', "Reaction"),
    (comment_router, '/comment', "Comment"),
    (share_router, '/share', "Share"),
    (notify_router, '/notify', "Notify"),
    (report_router, '/report', "Report"),
    (violation_router, 'violation', "Violation"),
    (ai_flag_router, 'ai-flag', "AI_Flag"),
    (ai_flag_disputes, 'disputes', "AI_Flag_Disputes")
]
