from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# モデルのインポート
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import base  # noqa

# Alembic Config オブジェクトの取得
config = context.config

# ロギングの設定
fileConfig(config.config_file_name)

# ターゲットメタデータの設定
target_metadata = base.Base.metadata

# データベース URL の取得
def get_url():
    return os.getenv("DATABASE_URL")

# ランタイムでのマイグレーション実行
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
