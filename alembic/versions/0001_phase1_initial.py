"""Initial Phase 1 schema: users, problems, sessions, session_events."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_phase1_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("google_sub", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("daily_minutes_used", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("quota_reset_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_google_sub", "users", ["google_sub"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "problems",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("difficulty", sa.String(32), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("constraints_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("optimal_complexity", sa.String(255), nullable=False),
        sa.Column("edge_cases_json", sa.Text(), nullable=False, server_default="[]"),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", sa.String(128), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("duration_sec", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("overall_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("correctness_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("complexity_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("edge_cases_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("communication_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("final_complexity", sa.String(255), nullable=False, server_default=""),
        sa.Column("is_optimal", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("missed_edge_cases_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("summary_feedback", sa.Text(), nullable=False, server_default=""),
        sa.Column("grading_source", sa.String(64), nullable=False, server_default="system2"),
        sa.Column("audio_path", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)
    op.create_index("ix_sessions_problem_id", "sessions", ["problem_id"], unique=False)

    op.create_table(
        "session_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(64), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_session_events_session_id", "session_events", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_table("session_events")
    op.drop_table("sessions")
    op.drop_table("problems")
    op.drop_table("users")
