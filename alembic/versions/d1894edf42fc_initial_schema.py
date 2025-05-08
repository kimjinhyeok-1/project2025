"""initial schema

Revision ID: d1894edf42fc
Revises: 418d9c2891b7
Create Date: 2025-05-08 10:40:54.850136
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd1894edf42fc'
down_revision: Union[str, None] = '418d9c2891b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: safely drop dependent tables first, then parent."""
    # Drop child tables first (those that have foreign keys referencing pdf_summary)
    op.drop_index('ix_embedding_id', table_name='embedding')
    op.drop_table('embedding')

    op.drop_index('ix_quiz_id', table_name='quiz')
    op.drop_table('quiz')

    # Then drop parent table
    op.drop_index('ix_pdf_summary_filename', table_name='pdf_summary')
    op.drop_index('ix_pdf_summary_id', table_name='pdf_summary')
    op.drop_table('pdf_summary')


def downgrade() -> None:
    """Downgrade schema: restore tables in order."""
    op.create_table('pdf_summary',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('file_path', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('embedding', sa.TEXT(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='pdf_summary_pkey')
    )
    op.create_index('ix_pdf_summary_id', 'pdf_summary', ['id'], unique=False)
    op.create_index('ix_pdf_summary_filename', 'pdf_summary', ['filename'], unique=True)

    op.create_table('quiz',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('question', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
        sa.Column('answer', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('material_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['material_id'], ['pdf_summary.id'], name='quiz_material_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='quiz_pkey')
    )
    op.create_index('ix_quiz_id', 'quiz', ['id'], unique=False)

    op.create_table('embedding',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('chunk_index', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('embedding', sa.TEXT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['material_id'], ['pdf_summary.id'], name='embedding_material_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='embedding_pkey')
    )
    op.create_index('ix_embedding_id', 'embedding', ['id'], unique=False)
