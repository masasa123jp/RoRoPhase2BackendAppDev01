# APIルーター：ダッシュボード統計エンドポイント

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import has_admin_role
from app.services.statistics import get_dashboard_stats

router = APIRouter()

@router.get("/admin/stats", summary="管理者向け統計KPI", response_model=dict)
async def admin_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    管理者専用のダッシュボード統計を返す。
    """
    try:
        stats = await get_dashboard_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"統計取得エラー: {str(e)}")
