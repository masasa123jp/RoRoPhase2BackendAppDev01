import logging
import sys
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from app.core.config import settings

# Sentryのロギング統合を設定
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # INFO以上のログをSentryのブレッドクラムとして記録
    event_level=logging.ERROR  # ERROR以上のログをSentryのイベントとして送信
)

# Sentry SDKの初期化
sentry_sdk.init(
    dsn=settings.sentry_dsn,  # SentryのDSNを設定
    integrations=[sentry_logging],
    traces_sample_rate=1.0,   # トレースのサンプリングレートを設定（必要に応じて調整）
    send_default_pii=True     # ユーザー情報などのPIIを送信（必要に応じて設定）
)

# ルートロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# コンソール出力のハンドラーを追加
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# ログのフォーマットを設定
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
console_handler.setFormatter(formatter)

# ハンドラーをロガーに追加
logger.addHandler(console_handler)
