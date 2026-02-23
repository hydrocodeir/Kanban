"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-01
"""

from alembic import op
import sqlalchemy as sa


revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False),
        sa.Column('telegram_chat_id', sa.String(length=64), nullable=True),
        sa.Column('notify_enabled', sa.Boolean(), nullable=False),
        sa.Column('dark_mode', sa.Boolean(), nullable=False),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    op.create_table(
        'boards',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=180), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_index('ix_boards_owner_id', 'boards', ['owner_id'])

    op.create_table(
        'columns',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('board_id', sa.Integer(), sa.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_index('ix_columns_board_id', 'columns', ['board_id'])

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=180), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'done', name='taskstatus'), nullable=False),
        sa.Column('column_id', sa.Integer(), sa.ForeignKey('columns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_tasks_column_id', 'tasks', ['column_id'])
    op.create_index('ix_tasks_owner_id', 'tasks', ['owner_id'])

    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(length=120), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_activity_logs_user_id', 'activity_logs', ['user_id'])
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('activity_logs')
    op.drop_table('tasks')
    op.drop_table('columns')
    op.drop_table('boards')
    op.drop_table('users')
