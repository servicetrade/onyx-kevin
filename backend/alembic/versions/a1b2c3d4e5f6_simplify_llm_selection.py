"""Simplify LLM selection to Claude 4.5, Llama 4, and Mistral only

Revision ID: a1b2c3d4e5f6
Revises: f9b8c7d6e5a4
Create Date: 2025-12-10 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f9b8c7d6e5a4"
branch_labels = None
depends_on = None

# Models to keep visible
ENABLED_MODELS = [
    # Claude 4.5 (3 models)
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.anthropic.claude-opus-4-5-20251101-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    # Llama 4 (2 models)
    "us.meta.llama4-maverick-17b-instruct-v1:0",
    "us.meta.llama4-scout-17b-instruct-v1:0",
    # Mistral (2 models)
    "mistral.mistral-large-2407-v1:0",
    "mistral.mistral-small-2402-v1:0",
]


def upgrade() -> None:
    model_configuration = sa.table(
        "model_configuration",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("is_visible", sa.Boolean),
    )

    connection = op.get_bind()

    # Step 1: Disable ALL models
    connection.execute(
        model_configuration.update().values(is_visible=False)
    )

    # Step 2: Enable only our selected models
    connection.execute(
        model_configuration.update()
        .where(model_configuration.c.name.in_(ENABLED_MODELS))
        .values(is_visible=True)
    )


def downgrade() -> None:
    # No-op: we can't restore previous visibility state
    # Would need to track previous state to properly downgrade
    pass
