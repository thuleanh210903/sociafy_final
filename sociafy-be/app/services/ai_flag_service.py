from datetime import datetime, timedelta
from app.db.supabase_client import supabase

def process_ai_flag():
    now = datetime.utcnow()
    threshold_date = now - timedelta(days=5)

    res = supabase.table("ai_flag").select("*").eq("confirmed_status", "pending").execute()

    for flag in res.data:
        flagged_at = datetime.fromisoformat(flag["flagged_at"])
        if flagged_at < threshold_date:
            dispute_res = supabase.table("ai_flag_disputes").select("*").eq("ai_flag_id", flag["id"]).execute()
            if not dispute_res.data:
                # add violation
                supabase.table("violation").insert({
                    "id": flag["id"],
                    "post_id": flag.get("post_id"),
                    "comment_id": flag.get("comment_id"),
                    "reason": flag.get("detected_label"),
                    "strike_count": 1,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()

                # update reviewed
                supabase.table("ai_flag").update({
                    "reviewed": True,
                    "confirmed_status": "confirmed"
                }).eq("id", flag["id"]).execute()
            
