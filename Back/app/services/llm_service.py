import os
import asyncio
from typing import Dict, Any, List
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import random

# Gemini APIキーの設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# テスト用のダミー営業文面
SAMPLE_TEXTS = [
    "株式会社{company_name}様\n\n平素より格別のご高配を賜り、誠にありがとうございます。\n\n弊社の業務効率化ソリューションは、{industry}業界での実績が豊富であり、御社の課題解決に最適なツールとなります。特に、従業員数{employee_count}名規模の企業様では、導入後3ヶ月で平均30%の業務効率化を実現しております。\n\n是非一度、オンラインデモをご覧いただければ幸いです。ご連絡お待ちしております。",
    
    "{company_name}様\n\n貴社のますますのご発展を心よりお喜び申し上げます。\n\n弊社は{industry}業界に特化したコンサルティングサービスを提供しており、売上{revenue}百万円規模の企業様に対して、売上向上のための戦略立案をサポートしております。\n\n{contact_person}様のお時間を頂戴できれば、貴社の課題に合わせたご提案をさせていただきます。",
    
    "{company_name}様\n\n拝啓 時下ますますご清栄のこととお慶び申し上げます。\n\n弊社では、{established_year}年創業の老舗企業様向けに、伝統と革新を両立させるデジタル変革支援を行っております。{industry}業界での豊富な実績を基に、貴社の価値を最大化するソリューションをご提案いたします。\n\n詳細資料をお送りいたしますので、ご検討いただければ幸いです。敬具"
]

# ダミー営業文面を生成する関数
def generate_dummy_sales_text(company_data):
    template = random.choice(SAMPLE_TEXTS)
    
    # 会社データを使用してテンプレートを埋める
    for key, value in company_data.items():
        if value and isinstance(value, (str, int, float)):
            placeholder = "{" + key + "}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
    
    return template

# 本番環境ではGemini API、開発環境ではダミーテキストを使用
async def generate_sales_text(company_data: Dict[str, Any]) -> str:
    """
    企業データに基づいて営業文面を生成する
    """
    # 会社情報のフォーマット
    company_info = ""
    for key, value in company_data.items():
        if value and key not in ["id", "status", "salesText"]:
            company_info += f"{key}: {value}\n"
    
    # プロンプトの作成
    prompt = f"""
    以下の企業情報に基づいて、効果的な営業文面を日本語で作成してください。
    
    ## 企業情報
    {company_info}
    
    ## 指示
    - 丁寧な敬語を使用すること
    - 企業の業種や規模に合わせた提案をすること
    - 具体的な価値提案を含めること
    - 営業文面は300文字程度にすること
    """
    
    try:
        # 本番環境ではGemini APIを使用
        if os.getenv("ENVIRONMENT") == "production":
            # 既存のGemini API呼び出しコード
            # 非同期処理をシミュレート（Gemini APIは現在直接の非同期サポートがないため）
            loop = asyncio.get_event_loop()
            
            # Gemini APIを使用して文面を生成（同期処理を非同期的に実行）
            def call_gemini_api():
                # 利用可能なモデルを確認
                models = genai.list_models()
                available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
                print(f"利用可能なモデル: {available_models}")
                
                # 利用可能なモデルから選択
                model_name = 'gemini-1.5-flash'  # 基本的なモデル名
                if 'models/gemini-1.5-flash' in available_models:
                    model_name = 'models/gemini-1.5-flash'
                elif 'gemini-1.5-flash' in available_models:
                    model_name = 'gemini-1.5-flash'
                
                print(f"使用するモデル: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    [
                        {"role": "user", "parts": [{"text": "あなたはプロの営業文面作成者です。"}]},
                        {"role": "user", "parts": [{"text": prompt}]}
                    ]
                )
                return response.text
            
            sales_text = await loop.run_in_executor(None, call_gemini_api)
            return sales_text
        else:
            # 開発環境ではダミーテキストを使用
            return generate_dummy_sales_text(company_data)
    except GoogleAPIError as e:
        print(f"Gemini API呼び出しエラー: {str(e)}")
        return f"営業文面の生成に失敗しました: {str(e)}"
    except Exception as e:
        print(f"LLM呼び出しエラー: {str(e)}")
        # エラー時はダミーテキストを返す
        return generate_dummy_sales_text(company_data)