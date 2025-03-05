from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid

from services.file_service import validate_file, save_file
from config import settings

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    ファイルをアップロードするエンドポイント
    """
    try:
        # ファイル形式の検証
        await validate_file(file)
        
        # ファイルの保存
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}-{file.filename}"
        file_path = await save_file(file, file_name)
        
        return {
            "success": True,
            "file_id": file_id,
            "file_name": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))