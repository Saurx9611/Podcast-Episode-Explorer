"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-29 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Enable pgvector extension (if postgres)
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True, server_default='Engineer'),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # 3. Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # 4. Create episodes table
    op.create_table(
        'episodes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('audio_url', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('language', sa.String(), nullable=True, server_default='en'),
        sa.Column('status', sa.String(), nullable=True, server_default='uploaded'),
        sa.Column('processing_model', sa.String(), nullable=True, server_default='whisper-large-v3'),
        sa.Column('index_time', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_episodes_title', 'episodes', ['title'])
    op.create_index('ix_episodes_status', 'episodes', ['status'])
    op.create_index('ix_episodes_project_id', 'episodes', ['project_id'])

    # 5. Create speakers table
    op.create_table(
        'speakers',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('episode_id', sa.String(), sa.ForeignKey('episodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('speaking_duration', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('segment_count', sa.Integer(), nullable=True, server_default='0'),
    )
    op.create_index('ix_speakers_episode_id', 'speakers', ['episode_id'])

    # 6. Create transcript_segments table
    op.create_table(
        'transcript_segments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('episode_id', sa.String(), sa.ForeignKey('episodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker_id', sa.String(), sa.ForeignKey('speakers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_transcript_segments_episode_id', 'transcript_segments', ['episode_id'])
    op.create_index('ix_transcript_segments_speaker_id', 'transcript_segments', ['speaker_id'])
    op.create_index('ix_transcript_segments_start_time', 'transcript_segments', ['start_time'])
    op.create_index('ix_transcript_segments_sequence_number', 'transcript_segments', ['sequence_number'])

    # 7. Create embeddings table
    embedding_col = Vector(1536) if conn.dialect.name == "postgresql" else sa.JSON()
    op.create_table(
        'embeddings',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('segment_id', sa.String(), sa.ForeignKey('transcript_segments.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('embedding', embedding_col, nullable=False),
    )
    op.create_index('ix_embeddings_segment_id', 'embeddings', ['segment_id'])

    # 8. Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('episode_id', sa.String(), sa.ForeignKey('episodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(), nullable=True, server_default='queued'),
        sa.Column('current_stage', sa.String(), nullable=True, server_default='upload'),
        sa.Column('progress', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_processing_jobs_episode_id', 'processing_jobs', ['episode_id'])
    op.create_index('ix_processing_jobs_status', 'processing_jobs', ['status'])

    # 9. Create saved_searches table
    op.create_table(
        'saved_searches',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('filters', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('run_count', sa.Integer(), nullable=True, server_default='0'),
    )
    op.create_index('ix_saved_searches_user_id', 'saved_searches', ['user_id'])

    # 10. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('read', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_read', 'notifications', ['read'])

    # 11. Create episode_insights table
    op.create_table(
        'episode_insights',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('episode_id', sa.String(), sa.ForeignKey('episodes.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('overview', sa.Text(), nullable=True),
        sa.Column('competencies', sa.JSON(), nullable=True),
        sa.Column('technologies', sa.JSON(), nullable=True),
        sa.Column('architecture', sa.JSON(), nullable=True),
        sa.Column('resume_bullet', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_episode_insights_episode_id', 'episode_insights', ['episode_id'])

def downgrade() -> None:
    op.drop_table('episode_insights')
    op.drop_table('notifications')
    op.drop_table('saved_searches')
    op.drop_table('processing_jobs')
    op.drop_table('embeddings')
    op.drop_table('transcript_segments')
    op.drop_table('speakers')
    op.drop_table('episodes')
    op.drop_table('projects')
    op.drop_table('users')
