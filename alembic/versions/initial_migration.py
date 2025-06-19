"""Initial migration

Revision ID: 123456789abc
Revises: 
Create Date: 2025-05-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# リビジョン識別子
revision = '123456789abc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ユーザーテーブルの作成
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
    )

def downgrade():
    # ユーザーテーブルの削除
    op.drop_table('users')
