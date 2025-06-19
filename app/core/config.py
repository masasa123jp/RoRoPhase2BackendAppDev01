# app/core/config.py

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, List, Optional

from pydantic import AnyUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラス。
    環境変数や .env ファイルから設定を読み込みます。
    """

    # プロジェクト情報
    project_name: str = "Project RORO API"
    environment: str = Field("development", description="環境名 dev/stage/prod")
    version: str = "0.2.0"

    # 認証設定
    jwt_audience: str = "api://roro"
    jwt_issuers: List[AnyUrl] = [
        "https://accounts.google.com",
        "https://login.microsoftonline.com/consumers/v2.0",
        "https://appleid.apple.com",
        "https://github.com/login/oauth",
    ]
    secret_key: SecretStr = Field(..., env="SECRET_KEY")  # JWTシークレットキーをSecretStr型で安全に管理

    # 接続文字列（環境変数から読み込む）
    postgres_uri: Annotated[AnyUrl, Field(..., env="POSTGRES_URI")]
    cosmos_uri: Annotated[AnyUrl, Field(..., env="COSMOS_URI")]
    storage_conn: Annotated[str, Field(..., env="STORAGE_CONNECTION")]
    sb_conn: Annotated[str, Field(..., env="SERVICEBUS_CONNECTION")]

    # OpenAI 設定
    openai_endpoint: Optional[AnyUrl] = None
    openai_api_key: Optional[SecretStr] = None  # OpenAIキーもSecretStrで隠蔽

    # CORS 許可ドメイン
    allowed_hosts: List[str] = ["https://api.roro.com"]

    # モデル設定
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    設定のインスタンスを取得します。
    lru_cache を使用して、設定の読み込みを一度だけ行います。
    """
    return Settings()
