"""Enhanced features migration — adds genre to books, users, waitlist_notifications, and audit_logs tables.

Supports:
- Book genre categorization and indexing
- User authentication (Gmail registration with random 8-char password, login, forgot password)
- Out-of-stock waitlist restock notifications
- Comprehensive administrative audit trail
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add genre column to books table
    op.add_column(
        "books",
        sa.Column("genre", sa.Text(), nullable=False, server_default="General"),
    )
    op.create_index("idx_books_genre", "books", ["genre"])

    # 2. Create users table for authentication
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("passcode_hash", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False, server_default="user"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_login_at", sa.TIMESTAMP, nullable=True),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_users_email", "users", ["email"])

    # 3. Create waitlist_notifications table
    op.create_table(
        "waitlist_notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("book_id", sa.Integer, nullable=False),
        sa.Column("user_email", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("notified_at", sa.TIMESTAMP, nullable=True),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
        ),
        sqlite_autoincrement=True,
    )
    op.create_index(
        "idx_waitlist_book_status",
        "waitlist_notifications",
        ["book_id", "status"],
    )

    # 4. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("user_email", sa.Text, nullable=True),
        sa.Column("details", sa.Text, nullable=False),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_audit_logs_event_type", "audit_logs", ["event_type"])
    op.create_index("idx_audit_logs_timestamp", "audit_logs", ["timestamp"])


def downgrade() -> None:
    op.drop_index("idx_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("idx_audit_logs_event_type", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(
        "idx_waitlist_book_status", table_name="waitlist_notifications"
    )
    op.drop_table("waitlist_notifications")

    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("idx_books_genre", table_name="books")
    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_column("genre")
