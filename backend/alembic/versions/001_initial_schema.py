"""Initial schema for users and prediction_history

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-04 23:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create prediction_history table
    op.create_table(
        'prediction_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('prediction_type', sa.String(length=50), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('prediction_result', sa.JSON(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prediction_history_id'), 'prediction_history', ['id'], unique=False)
    op.create_index(op.f('ix_prediction_history_user_id'), 'prediction_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_prediction_history_prediction_type'), 'prediction_history', ['prediction_type'], unique=False)
    op.create_index(op.f('ix_prediction_history_created_at'), 'prediction_history', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_prediction_history_created_at'), table_name='prediction_history')
    op.drop_index(op.f('ix_prediction_history_prediction_type'), table_name='prediction_history')
    op.drop_index(op.f('ix_prediction_history_user_id'), table_name='prediction_history')
    op.drop_index(op.f('ix_prediction_history_id'), table_name='prediction_history')
    op.drop_table('prediction_history')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
