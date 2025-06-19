"""
アプリケーションエントリポイント (backend/app/main.py)
======================================================
* FastAPI インスタンスの生成
* 依存ミドルウェア（CORS / OpenTelemetry / レートリミット）の組み込み
* API ルーターの自動登録
* スタートアップ／シャットダウンハンドラで外部サービスをウォームアップ
--------------------------------------------------------------------
このファイル 1 本を `uvicorn app.main:app` で起動すれば
Azure App Service（Docker コンテナ）でもローカルでも同一挙動になる。
"""

from __future__ import annotations

import asyncio
import importlib
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# レート制御
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .core.config import get_settings
from .core.logging import configure_logging  # 独自 logging 設定ヘルパ
from .core import security  # ensure JWT utils are imported once

settings = get_settings()
logger = configure_logging()

# ------------------------------------------------------------------
# Limiter 準備: 1 IP 100 req/min（必要に応じ環境変数で調整可）
limiter = Limiter(key_func=lambda request: request.client.host, default_limits=["100/minute"])

# ------------------------------------------------------------------
# OpenTelemetry 初期化
resource = Resource.create({"service.name": settings.project_name})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())  # デフォルト: http://localhost:4318
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# ------------------------------------------------------------------
# FastAPI インスタンス作成
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan="on",
)

# --- CORS: Front Door の公開ドメインを許可 --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin or "https://api.roro.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- レートリミットミドルウェア -------------------------------------
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# --- OpenTelemetry 自動計測 ----------------------------------------
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider, excluded_urls=r"/(docs|openapi\.json)")

# ------------------------------------------------------------------
# ルーター自動登録
def include_routers() -> None:
    """
    api/routes/*.py を動的ロードし、router 変数を app に登録。
    """
    routes_dir = Path(__file__).parent / "api" / "routes"
    for file in routes_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = f"app.api.routes.{file.stem}"
        module = importlib.import_module(module_name)
        router = getattr(module, "router", None)
        if router:
            app.include_router(router)
            logger.debug("📌 Router [%s] registered", module_name)


include_routers()

# ------------------------------------------------------------------
# 起動＆終了イベントハンドラ
@app.on_event("startup")
async def on_startup() -> None:
    """
    * DB 接続ウォームアップ
    * OpenAI モデルウォームアップ（非同期）
    * その他外部サービスの疎通チェック
    """
    from ..shared_lib.db import engine  # 遅延 import で循環回避

    logger.info("🟢 FastAPI starting up…")
    try:
        # 接続確認 (0.5 秒タイムアウト)
        async with engine.connect() as conn:
            await asyncio.wait_for(conn.execute("SELECT 1"), timeout=0.5)
        logger.info("✅ PostgreSQL 接続 OK")
    except Exception as exc:  # pragma: no cover
        logger.warning("⚠️  PostgreSQL 接続チェック失敗: %s", exc)

    # OpenAI モデルプリロード（並列で実施）
    async def preload_openai() -> None:
        try:
            from .utils.openai_client import get_client
            await get_client().chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": "ping"}], max_tokens=1
            )
            logger.info("✅ OpenAI 通信ウォームアップ完了")
        except Exception as exc:
            logger.error("❌ OpenAI 通信失敗: %s", exc)

    asyncio.create_task(preload_openai())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    BatchSpanProcessor Flush / DB Engine Dispose など。
    """
    logger.info("🛑 FastAPI shutting down…")
    await trace.get_tracer_provider().shutdown()

    from ..shared_lib.db import engine

    await engine.dispose()
