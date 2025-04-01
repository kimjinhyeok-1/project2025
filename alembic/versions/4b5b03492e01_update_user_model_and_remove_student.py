from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '4b5b03492e01'
down_revision = 'fa2867e99fce'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. chat_history 외래키 제거 및 student_name 컬럼 제거
    op.drop_constraint('chat_history_student_name_fkey', 'chat_history', type_='foreignkey')
    op.drop_column('chat_history', 'student_name')

    # 2. students 테이블 제거
    op.drop_index('ix_students_name', table_name='students')
    op.drop_table('students')

    # 3. snapshots 테이블 제거
    op.drop_index('ix_snapshots_id', table_name='snapshots')
    op.drop_table('snapshots')

    # 4. user_id 컬럼을 nullable=True로 먼저 추가
    op.add_column('chat_history', sa.Column('user_id', sa.Integer(), nullable=True))

    # 5. user_id = 1 임시 값 채우기
    op.execute("UPDATE chat_history SET user_id = 1")

    # 6. 외래키 추가
    op.create_foreign_key(None, 'chat_history', 'users', ['user_id'], ['id'])

    # 7. user_id NOT NULL로 변경
    op.alter_column('chat_history', 'user_id', nullable=False)

    # 8. lecture_snapshots.lecture_id 타입 변경
    op.alter_column(
        'lecture_snapshots',
        'lecture_id',
        existing_type=sa.VARCHAR(),
        type_=sa.Integer(),
        nullable=False,
        postgresql_using="lecture_id::integer"
    )
    op.drop_index('ix_lecture_snapshots_lecture_id', table_name='lecture_snapshots')
    op.create_foreign_key(None, 'lecture_snapshots', 'lectures', ['lecture_id'], ['id'])

    # 9. recordings.lecture_id NOT NULL
    op.alter_column('recordings', 'lecture_id', existing_type=sa.INTEGER(), nullable=False)

    # 10. users 테이블 변경
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('password', existing_type=sa.VARCHAR(), nullable=False)

        # 인덱스 존재 시 삭제
        conn = op.get_bind()
        index_exists = lambda name: conn.execute(text(f"""
            SELECT to_regclass('{name}') IS NOT NULL;
        """)).scalar()

        if index_exists('ix_users_email'):
            op.execute("DROP INDEX ix_users_email")
        if index_exists('ix_users_username'):
            op.execute("DROP INDEX ix_users_username")

        # 인덱스 중복 방지
        try:
            batch_op.create_index(op.f('ix_users_name'), ['name'], unique=True)
        except Exception:
            pass

        # 컬럼 존재 시 삭제
        inspector = sa.inspect(conn)
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'username' in columns:
            batch_op.drop_column('username')
        if 'email' in columns:
            batch_op.drop_column('email')

def downgrade() -> None:
    # 그대로 유지 (기존과 동일)
    ...
