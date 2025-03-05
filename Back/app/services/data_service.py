import pandas as pd
import os
import re
import uuid
import numpy as np
from typing import Dict, List, Any

from config import settings

async def process_file(file_id: str) -> Dict[str, Any]:
    """
    アップロードされたファイルを処理する
    """
    print(f"ファイル処理開始: {file_id}")
    try:
        # ファイルの検索
        upload_dir = settings.UPLOAD_DIR
        for filename in os.listdir(upload_dir):
            if filename.startswith(file_id):
                file_path = os.path.join(upload_dir, filename)
                print(f"ファイルを見つけました: {file_path}")
                break
        else:
            print(f"ファイルが見つかりません: {file_id}")
            raise FileNotFoundError(f"File with ID {file_id} not found")
        
        # ファイル形式に基づいて読み込み
        ext = filename.split(".")[-1].lower()
        if ext == "csv":
            # エンコーディングを指定して読み込み（日本語対応）
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                # UTF-8で読めない場合はShift-JISを試す
                df = pd.read_csv(file_path, encoding='shift_jis')
        elif ext in ["xlsx", "xls"]:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # 読み込んだデータの内容を詳細に確認
        print(f"読み込んだファイルの内容:")
        print(f"カラム: {list(df.columns)}")
        print(f"データタイプ: {df.dtypes}")
        print(f"先頭5行:\n{df.head()}")
        print(f"null値の数: {df.isnull().sum()}")
        
        # 必須カラムの確認（より柔軟な方法）
        required_found = False
        for required_col in settings.REQUIRED_COLUMNS:
            # 元のカラム名または変換後のスネークケース名をチェック
            column_matches = [col for col in df.columns if 
                              col.lower() == required_col.lower() or
                              to_snake_case(col) == required_col]
            
            if column_matches:
                required_found = True
                break

        if not required_found:
            print(f"必須カラムが見つかりません。カラム: {list(df.columns)}")
            raise ValueError(f"必須カラムが見つかりません。最低でも企業名/会社名が必要です。")
        
        # カラム名のマッピングを作成
        column_mapping = {}
        for col in df.columns:
            snake_case = to_snake_case(col)
            column_mapping[snake_case] = col
            print(f"カラム変換: '{col}' -> '{snake_case}'")
        
        # カラム名を変換
        df.columns = [to_snake_case(col) for col in df.columns]
        print(f"変換後のカラム: {list(df.columns)}")
        
        # データの正規化
        df = normalize_data(df)
        
        # データをJSON形式に変換
        def convert_to_json(df):
            """
            DataFrameをJSON形式に変換
            """
            # 各行にIDを追加
            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
            # DataFrameをJSON形式に変換（NaN値をNoneに変換）
            records = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        record[col] = None
                    else:
                        # 数値型の場合はそのまま、それ以外は文字列に変換
                        if isinstance(value, (int, float)):
                            record[col] = value
                        else:
                            record[col] = str(value)
                records.append(record)
            
            print(f"結果データ構造:")
            print(f"データ件数: {len(records)}")
            if records:
                print(f"最初の行のキー: {list(records[0].keys())}")
                print(f"最初の行の値: {list(records[0].values())}")
            
            return records

        # 変換を適用
        result_data = convert_to_json(df)
        
        return {
            "data": result_data,
            "mapping": column_mapping
        }
    except Exception as e:
        print(f"データ処理エラー: {str(e)}")
        raise

def to_snake_case(text: str) -> str:
    """
    テキストをスネークケースに変換する
    """
    # 日本語を英語に変換（実際のアプリケーションでは辞書を使用）
    translation = {
        "会社名": "company_name",
        "企業名": "company_name",
        "社名": "company_name",
        "業種": "industry",
        "業界": "industry",
        "担当者": "contact_person",
        "担当者名": "contact_person",
        "メールアドレス": "email",
        "メール": "email",
        "電話番号": "phone",
        "電話": "phone",
        "TEL": "phone",
        "住所": "address",
        "所在地": "address",
        "URL": "url",
        "ウェブサイト": "url",
        "HP": "url",
        "従業員数": "employee_count",
        "社員数": "employee_count",
        "売上": "revenue",
        "売上高": "revenue",
        "年商": "revenue",
        "設立年": "established_year",
        "設立": "established_year",
        "創業年": "established_year"
    }
    
    # 大文字小文字を区別せずに変換
    for key, value in translation.items():
        if text.lower() == key.lower():
            return value
    
    # 一般的な変換ロジック
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    # 空白やその他の文字を_に置換
    s3 = re.sub(r'[^\w]', '_', s2)
    # 連続する_を単一の_に置換
    s4 = re.sub(r'_+', '_', s3)
    # 先頭と末尾の_を削除
    return s4.strip('_')

def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    データを正規化する
    """
    # 欠損値の処理
    df = df.dropna(how='all')
    
    # データ型の変換
    for col in df.columns:
        # 数値型への変換を試みる
        if df[col].dtype == 'object':
            try:
                # errors='coerce'を使用して無効な値をNaNに変換
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass
        
        # 日付型への変換を試みる
        if df[col].dtype == 'object':
            try:
                # errors='coerce'を使用して無効な日付をNaTに変換
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # NaT値をNoneに変換
                mask = df[col].notna()
                df.loc[mask, col] = df.loc[mask, col].dt.strftime('%Y-%m-%d')
                df.loc[~mask, col] = None
            except:
                pass
    
    return df

async def get_company_data(list_id: str = None) -> List[Dict[str, Any]]:
    """
    会社データを取得する
    実際のアプリケーションではデータベースから取得
    """
    # テスト用のダミーデータ
    if list_id == "current":
        # 現在のセッションデータを返す（実際の実装ではセッションまたはDBから取得）
        # ここではテストデータを返す
        return [
            {
                "id": "test-1",
                "company_name": "テスト株式会社",
                "industry": "IT",
                "contact_person": "山田太郎",
                "email": "test@example.com",
                "phone": "03-1234-5678",
                "address": "東京都渋谷区",
                "url": "https://example.com",
                "employee_count": 100,
                "revenue": 500,
                "established_year": 2010,
                "status": "処理中"
            },
            {
                "id": "test-2",
                "company_name": "サンプル商事",
                "industry": "製造業",
                "contact_person": "佐藤次郎",
                "email": "sample@example.com",
                "phone": "03-8765-4321",
                "address": "大阪府大阪市",
                "url": "https://sample.com",
                "employee_count": 50,
                "revenue": 300,
                "established_year": 2005,
                "status": "処理中"
            }
        ]
    else:
        # テスト用のダミーデータを返す
        return [
            {
                "id": "test-1",
                "company_name": "テスト株式会社",
                "industry": "IT",
                "contact_person": "山田太郎",
                "email": "test@example.com",
                "phone": "03-1234-5678",
                "address": "東京都渋谷区",
                "url": "https://example.com",
                "employee_count": 100,
                "revenue": 500,
                "established_year": 2010,
                "status": "処理中"
            }
        ]