# app/utils/openai_client.py

import openai
import os

# OpenAIのAPIキー（環境変数から取得）
openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_ai_response(message: str) -> str:
    """
    指定されたメッセージに対してOpenAI GPTモデルで応答を生成する。
    """
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",  # または "gpt-4"（API制限による）
            messages=[
                {"role": "system", "content": "ペットの専門家として優しく親切に回答してください。"},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[OpenAIエラー]: {str(e)}"
