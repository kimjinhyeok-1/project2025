"""Create initial tables (drop & recreate quiz.options with default [])

Revision ID: e5d7f165c226
Revises: 76c53498e4a7
Create Date: 2025-05-01 11:46:00.342116
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e5d7f165c226"
down_revision: Union[str, None] = "76c53498e4a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ──────────────────────────────────────────────────────────────
# UPGRADE
# ──────────────────────────────────────────────────────────────
def upgrade() -> None:
    """Upgrade schema (quiz.options 초기값을 [] 로 채우고 NOT NULL 유지)."""
    # 1. generated_questions 테이블
    op.create_table(
        "generated_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("paragraph", sa.Text(), nullable=False),
        sa.Column("questions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        op.f("ix_generated_questions_id"),
        "generated_questions",
        ["id"],
        unique=False,
    )

    # 2. quiz.options 드롭 → JSONB NOT NULL + 기본값 []
    with op.batch_alter_table("quiz") as batch_op:
        batch_op.drop_column("options")
        batch_op.add_column(
            sa.Column(
                "options",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default="[]",   # 모든 기존 행에 [] 삽입
            )
        )

    # (선택) 기본값 제거해 컬럼만 NOT NULL 상태로 유지하고 싶다면 주석 해제
    # op.execute("ALTER TABLE quiz ALTER COLUMN options DROP DEFAULT;")


# ──────────────────────────────────────────────────────────────
# DOWNGRADE
# ──────────────────────────────────────────────────────────────
def downgrade() -> None:
    """Downgrade schema (quiz.options TEXT nullable, drop generated_questions)."""
    with op.batch_alter_table("quiz") as batch_op:
        batch_op.drop_column("options")
        batch_op.add_column(sa.Column("options", sa.TEXT(), nullable=True))

    op.drop_index(op.f("ix_generated_questions_id"), table_name="generated_questions")
    op.drop_table("generated_questions")
