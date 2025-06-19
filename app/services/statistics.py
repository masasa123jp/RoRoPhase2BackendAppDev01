# サマリ統計データ取得ロジック

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.report import Report  # 仮に report モデルがあると仮定

async def get_dashboard_stats(db: AsyncSession) -> dict:
    """
    ダッシュボード用の集計統計を返す。
    - アクティブユーザー数
    - 非アクティブユーザー数
    - レポート提出数（例）
    """
    result = {}

    # アクティブ/非アクティブユーザー数
    total_users = await db.scalar(select(func.count()).select_from(User))
    active_users = await db.scalar(select(func.count()).select_from(User).where(User.is_active == True))
    inactive_users = total_users - active_users

    # レポート数（仮に存在する場合）
    total_reports = await db.scalar(select(func.count()).select_from(Report))

    result["total_users"] = total_users
    result["active_users"] = active_users
    result["inactive_users"] = inactive_users
    result["total_reports"] = total_reports

    return result
