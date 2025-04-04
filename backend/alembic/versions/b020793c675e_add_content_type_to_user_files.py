"""Add content type to user files

Revision ID: b020793c675e
Revises: 4794bc13e484
Create Date: 2025-04-04 10:22:32.744461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b020793c675e"
down_revision = "4794bc13e484"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add content_type column to user_file table
    op.add_column(
        "user_file",
        sa.Column("content_type", sa.String(), nullable=True),
    )


def downgrade() -> None:
    # Drop content_type column from user_file table
    op.drop_column("user_file", "content_type")
