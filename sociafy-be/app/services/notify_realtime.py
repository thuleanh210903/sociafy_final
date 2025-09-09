from datetime import datetime
from app.share.enum.notification import NotificationType
from app.db.supabase_client import supabase

def create_notification(target_user_id: str, type: NotificationType, message: str, post_id: str = None, comment_id: str = None):
    if not target_user_id:
        return 
    
    supabase.table('notification').insert({
        "user_id": target_user_id,
        "type": type.value,
        "post_id": post_id,
        "comment_id": comment_id,
        "is_read": False,
        "created_at": datetime.utcnow().isoformat()
    }).execute()