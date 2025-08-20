from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.cloudinary_service import upload_cloudinary_image

router = APIRouter()

@router.post('/upload')
async def upload_image(file: UploadFile = File(...), key: str = None):
    try:
        result = upload_cloudinary_image(file=file, key=key)
        return {"message": "Upload successfull", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
