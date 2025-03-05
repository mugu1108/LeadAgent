from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from typing import List, Dict

router = APIRouter()

@router.get("/export")
async def export_data(request: Request, format: str = "csv"):
    """
    データをCSVまたはExcelとしてエクスポートする
    """
    try:
        # クエリパラメータからリストIDを取得
        list_id = request.query_params.get("list_id")
        
        # データの取得（実際の実装ではDBなどから取得）
        data = await get_company_data(list_id)
        
        # DataFrameに変換
        df = pd.DataFrame(data)
        
        # 必要なカラムのみ選択
        columns = ["company_name", "industry", "contact_person", "email", 
                   "phone", "address", "url", "salesText"]
        df = df[columns]
        
        # 日本語カラム名に変換
        column_mapping = {
            "company_name": "会社名",
            "industry": "業種",
            "contact_person": "担当者",
            "email": "メールアドレス",
            "phone": "電話番号",
            "address": "住所",
            "url": "URL",
            "salesText": "営業文面"
        }
        df = df.rename(columns=column_mapping)
        
        # 指定された形式でエクスポート
        if format.lower() == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False, encoding="utf-8")
            response = StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv"
            )
            response.headers["Content-Disposition"] = f"attachment; filename=sales_list_{list_id}.csv"
            return response
        
        elif format.lower() == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            output.seek(0)
            response = StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response.headers["Content-Disposition"] = f"attachment; filename=sales_list_{list_id}.xlsx"
            return response
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 