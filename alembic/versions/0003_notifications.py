"""In-app notifications table migration.

Supports patron notification alerts when an administrator cancels their reservation,
or other account-related notifications.
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "in_app_notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_email", sa.Text, nullable=False),
        sa.Column("user_name", sa.Text, nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_notifications_user_email", "in_app_notifications", ["user_email"])
    op.create_index("idx_notifications_is_read", "in_app_notifications", ["is_read"])


def downgrade() -> None:
    op.drop_index("idx_notifications_is_read", table_name="in_app_notifications")
    op.drop_index("idx_notifications_user_email", table_name="in_app_notifications")
    op.drop_table("in_app_notifications")
