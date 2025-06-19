from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app: FastAPI):
    """
    CORSミドルウェアをアプリケーションに追加します。
    """
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://yourdomain.com"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 許可するオリジン
        allow_credentials=True,
        allow_methods=["*"],  # 許可するHTTPメソッド
        allow_headers=["*"],  # 許可するHTTPヘッダー
    )
