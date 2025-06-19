from celery import Celery
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
import time

# Celeryアプリケーションのインスタンスを作成
celery_app = Celery(
    'app',
    broker='redis://localhost:6379/0',  # ブローカーのURLを設定
    backend='redis://localhost:6379/0'  # 結果バックエンドのURLを設定
)

# タスクのロガーを取得
logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_data(self, data_id: int):
    """
    データの処理をバックグラウンドで実行するタスク。
    エラーが発生した場合は最大3回までリトライします。
    """
    try:
        logger.info(f"データID {data_id} の処理を開始します。")
        # データ処理のロジックをここに実装
        time.sleep(5)  # ダミーの処理時間
        logger.info(f"データID {data_id} の処理が完了しました。")
    except SoftTimeLimitExceeded:
        logger.error(f"データID {data_id} の処理がタイムアウトしました。")
    except Exception as exc:
        logger.error(f"データID {data_id} の処理中にエラーが発生しました: {exc}")
        raise self.retry(exc=exc)
