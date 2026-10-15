"""Initial migration — creates books and reservations tables.

Schema matches exactly the DDL specified in the challenge document.
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("author", sa.Text, nullable=False),
        sa.Column("total_copies", sa.Integer, nullable=False),
        sa.Column("available_copies", sa.Integer, nullable=False),
        sa.CheckConstraint("total_copies > 0", name="ck_books_total_positive"),
        sa.CheckConstraint("available_copies >= 0", name="ck_books_avail_nonneg"),
        sqlite_autoincrement=True,
    )
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("book_id", sa.Integer, nullable=False),
        sa.Column("user_name", sa.Text, nullable=False),
        sa.Column(
            "reservation_date",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.TIMESTAMP, nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
        ),
        sqlite_autoincrement=True,
    )


def downgrade() -> None:
    op.drop_table("reservations")
    op.drop_table("books")
