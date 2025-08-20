import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from fastapi import UploadFile
import cloudinary
import cloudinary.uploader

load_dotenv()

# cloudinary config account 
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# type file
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/avif"
}

# structure upload file on Cloudinary
def build_folder(key: str, user_id: Optional[str] = None, post_id: Optional[str] = None) -> str:
    uid = user_id or "anon"
    # key = 'post' or avatar -> save
    if key == "post":
        pid = post_id or "no-post"
        return f"posts/{uid}/{pid}"
    if key == "avatar":
        return f"avatars/{uid}"
    if key == 'comment':
        return f"comment/{uid}"
    return f"general/{uid}"

def upload_cloudinary_image(
    file: UploadFile,
    key: str,
    *,
    user_id: Optional[str] = None,
    post_id: Optional[str] = None,
    #preset of Cloudinary
    upload_preset: Optional[str] = None,
) -> Dict[str, Any]:
    # Validate MIME type, prevent some file pdf, exe,...
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Unsupported content type: {file.content_type}")

    folder = build_folder(key, user_id=user_id, post_id=post_id)

    options = {
        "folder": folder,
        "resource_type": "auto",
        "use_filename": True,
        "unique_filename": True,
        "overwrite": False,
    }
    if upload_preset:
        options["upload_preset"] = upload_preset

    result = cloudinary.uploader.upload(file.file, **options)

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
        "bytes": result.get("bytes"),
        "format": result.get("format"),
        "width": result.get("width"),
        "height": result.get("height"),
        "resource_type": result.get("resource_type"),
        "folder": folder,
    }

# user delete post or change avatar
def delete_cloudinary_asset(public_id: str) -> Dict[str, Any]:
    return cloudinary.uploader.destroy(public_id, invalidate=True)