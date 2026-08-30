"""add podcast and episode metadata

Revision ID: 002_add_podcast_and_episode_metadata
Revises: 001_initial_schema
Create Date: 2026-08-30 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_podcast_and_episode_metadata'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create podcasts table
    op.create_table(
        'podcasts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('publisher', sa.String(), nullable=True),
        sa.Column('artwork_url', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True, server_default='en'),
        sa.Column('feed_url', sa.String(), nullable=True, unique=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_podcasts_title', 'podcasts', ['title'])
    op.create_index('ix_podcasts_feed_url', 'podcasts', ['feed_url'])
    op.create_index('ix_podcasts_external_id', 'podcasts', ['external_id'])

    # 2. Add columns to episodes table
    with op.batch_alter_table('episodes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('podcast_id', sa.String(), sa.ForeignKey('podcasts.id', ondelete='CASCADE'), nullable=True))
        batch_op.add_column(sa.Column('guid', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('artwork_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('episode_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('season_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('publication_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index('ix_episodes_podcast_id', ['podcast_id'])
        batch_op.create_index('ix_episodes_guid', ['guid'])
        batch_op.create_index('ix_episodes_publication_date', ['publication_date'])

def downgrade() -> None:
    with op.batch_alter_table('episodes', schema=None) as batch_op:
        batch_op.drop_index('ix_episodes_publication_date')
        batch_op.drop_index('ix_episodes_guid')
        batch_op.drop_index('ix_episodes_podcast_id')
        batch_op.drop_column('publication_date')
        batch_op.drop_column('season_number')
        batch_op.drop_column('episode_number')
        batch_op.drop_column('artwork_url')
        batch_op.drop_column('guid')
        batch_op.drop_column('podcast_id')

    op.drop_table('podcasts')
