# app/events/event_handler.py

import logging
from datetime import datetime
from typing import Any, Dict

# アプリ全体で使用される共通のイベントロガー
logger = logging.getLogger(__name__)

def log_event(event_type: str, user_id: int, details: Dict[str, Any]):
    """
    イベントログをINFOレベルで出力。
    例：ユーザー削除、設定変更、管理操作など
    """
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "details": details
    }
    logger.info(f"イベントログ: {event}")
