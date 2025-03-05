from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from services.data_service import process_file

class ProcessRequest(BaseModel):
    file_id: str

router = APIRouter()

@router.post("/process")
async def process_data(request: ProcessRequest) -> Dict[str, Any]:
    """
    アップロードされたファイルを処理するエンドポイント
    """
    try:
        result = await process_file(request.file_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ処理中にエラーが発生しました: {str(e)}")