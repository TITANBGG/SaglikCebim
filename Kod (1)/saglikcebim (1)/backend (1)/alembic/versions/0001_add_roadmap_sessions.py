"""create roadmap_sessions table

Revision ID: 0001_add_roadmap_sessions
Revises: 
Create Date: 2026-05-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '0001_add_roadmap_sessions'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'roadmap_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('roadmap_json', sqlite.JSON(), nullable=True),
        sa.Column('safety_validated', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('roadmap_sessions')
