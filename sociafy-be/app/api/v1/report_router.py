from datetime import datetime
import uuid
from app.db.supabase_client import supabase
from fastapi import APIRouter, HTTPException, Request
from app.schemas.report import ReportCreate, ReportMessageResponse, ReportUpdateStatus
from app.share.enum.report_status import ReportStatusEnum

router = APIRouter()
@router.get('/')
def get_all():
    res = supabase.table("report").select("*").execute()
    return {"message": "All reports", "reports": res.data}

@router.post("/add", response_model=ReportMessageResponse)
def add_report(request: Request, payload: ReportCreate):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    reporterId = user["id"]
    if not payload.post_id and not payload.comment_id:
        raise HTTPException(status_code=400, detail="Must provide post_id or comment_id")

    new_report = {
        "id": str(uuid.uuid4()),
        "reporter_id": reporterId,
        "post_id": payload.post_id,
        "comment_id": payload.comment_id,
        "reason": payload.reason,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    supabase.table("report").insert(new_report).execute()
    return {"message": "Report submitted", "report": new_report}

@router.get('/pending')
def get_pending_reports():
     res = supabase.table('report').select("*").eq("status", "pending").execute()
     return {
          "message": "Get all pending reports",
          "reports": res.data
     }


@router.put('/check/{report_id}')
def confirmReport(report_id: str, payload: ReportUpdateStatus):

    status = payload.status

    # check report exist
    res = supabase.table("report").select("*").eq("id", report_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Report not found")

    report = res.data[0]

    # update status
    supabase.table("report").update({"status": status.value}).eq("id", report_id).execute()

    # status = verified => resolve violation
    if status == ReportStatusEnum.verified:
        user_id = None

        if report.get("post_id"):
            post = supabase.table("post").select("user_id").eq("id", report["post_id"]).execute()
            if post.data:
                user_id = post.data[0]["user_id"]
        elif report.get("comment_id"):
            comment = supabase.table("comment").select("user_id").eq("id", report["comment_id"]).execute()
            if comment.data:
                user_id = comment.data[0]["user_id"]

        if not user_id:
            raise HTTPException(status_code=400, detail="Reported content not found")

        # add violation
        supabase.table("violation").insert({
            "user_id": user_id,
            "post_id": report.get("post_id"),
            "comment_id": report.get("comment_id"),
            "reason": report["reason"],
            "strike_count": 1,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        check_strike(user_id, report.get("post_id"), report.get("comment_id"))
        return {"message": f"Report updated to {status.value}, violation added"}

    return {"message": f"Report updated to {status.value}"}


    
def check_strike(user_id: str, post_id: str | None, comment_id: str | None):
    # if post/ comment >= 5 violation => hidden post
    if post_id:
        res = supabase.table("violation").select("*").eq("post_id", post_id).execute()
        if len(res.data) >= 5:
            supabase.table("post").update({"is_hided": True}).eq("id", post_id).execute()
    
    if comment_id:
        res = supabase.table("violation").select("*").eq("comment_id", comment_id).execute()
        if len(res.data) >= 5:
            supabase.table("comment").update({"is_hided": True}).eq("id", comment_id).execute()


    # if user > = 5 has hided different content => banned user
    res = supabase.table("violation").select("post_id, comment_id").eq("user_id", user_id).execute()
    unique_contents = set()
    for v in res.data:
        if v.get("post_id"):
            unique_contents.add(v["post_id"])
        if v.get("comment_id"):
            unique_contents.add(v["comment_id"])
    
    if len(unique_contents) >= 5:
        supabase.table("user").update({"is_banned": True}).eq("id", user_id).execute()
