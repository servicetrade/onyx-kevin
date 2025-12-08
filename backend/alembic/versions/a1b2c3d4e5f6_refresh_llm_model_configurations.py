"""Refresh LLM model configurations with latest models

Revision ID: a1b2c3d4e5f6
Revises: f9b8c7d6e5a4
Create Date: 2025-12-08 12:00:00.000000

This migration updates existing LLM providers to include all available models,
ensuring users have access to the latest models after an upgrade.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "b329d00a9ea6"
branch_labels = None
depends_on = None


# Anthropic models - only 3.5+ (dropped older Claude 3 base models)
ANTHROPIC_MODELS = [
    # Claude 4.5 (latest)
    ("claude-sonnet-4-5-20250929", True, True),
    ("claude-sonnet-4-5", True, True),
    ("claude-opus-4-5-20251101", True, True),
    ("claude-haiku-4-5", True, True),
    # Claude 4
    ("claude-opus-4-1", True, True),
    ("claude-opus-4-20250514", True, True),
    ("claude-sonnet-4-20250514", True, True),
    # Claude 3.7
    ("claude-3-7-sonnet-latest", True, True),
    # Claude 3.5
    ("claude-3-5-sonnet-20241022", True, True),
    ("claude-3-5-sonnet-20240620", True, True),
    ("claude-3-5-haiku-20241022", True, True),
]

# Bedrock models - includes Meta Llama 4 and Anthropic via Bedrock
BEDROCK_MODELS = [
    # Meta Llama 4 (latest)
    ("meta.llama4-scout-17b-instruct-v1:0", True, False),
    ("meta.llama4-maverick-17b-instruct-v1:0", True, False),
    ("us.meta.llama4-scout-17b-instruct-v1:0", True, False),
    ("us.meta.llama4-maverick-17b-instruct-v1:0", True, False),
    # Meta Llama 3.3
    ("meta.llama3-3-70b-instruct-v1:0", True, False),
    ("us.meta.llama3-3-70b-instruct-v1:0", True, False),
    # Meta Llama 3.2
    ("meta.llama3-2-90b-instruct-v1:0", True, True),
    ("meta.llama3-2-11b-instruct-v1:0", True, True),
    ("meta.llama3-2-3b-instruct-v1:0", True, False),
    ("meta.llama3-2-1b-instruct-v1:0", True, False),
    ("us.meta.llama3-2-90b-instruct-v1:0", True, True),
    ("us.meta.llama3-2-11b-instruct-v1:0", True, True),
    # Meta Llama 3.1
    ("meta.llama3-1-405b-instruct-v1:0", True, False),
    ("meta.llama3-1-70b-instruct-v1:0", True, False),
    ("meta.llama3-1-8b-instruct-v1:0", True, False),
    ("us.meta.llama3-1-405b-instruct-v1:0", True, False),
    ("us.meta.llama3-1-70b-instruct-v1:0", True, False),
    # Anthropic Claude via Bedrock
    ("anthropic.claude-3-5-sonnet-20241022-v2:0", True, True),
    ("anthropic.claude-3-5-haiku-20241022-v1:0", True, True),
    ("anthropic.claude-3-sonnet-20240229-v1:0", True, True),
    ("anthropic.claude-3-haiku-20240307-v1:0", True, True),
    ("us.anthropic.claude-3-5-sonnet-20241022-v2:0", True, True),
    ("us.anthropic.claude-3-5-haiku-20241022-v1:0", True, True),
]

# OpenAI models
OPENAI_MODELS = [
    ("gpt-4o", True, True),
    ("gpt-4o-mini", True, True),
    ("gpt-4-turbo", True, True),
    ("o1", True, False),
    ("o1-mini", True, False),
    ("o3-mini", True, False),
    ("gpt-4", True, False),
    ("gpt-3.5-turbo", True, False),
]


def upgrade() -> None:
    """Add missing model configurations to existing LLM providers."""
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Get existing LLM providers
        result = session.execute(
            sa.text("SELECT id, provider, name FROM llm_provider")
        )
        providers = result.fetchall()

        for provider_id, provider_type, provider_name in providers:
            # Determine which models to add based on provider type
            if provider_type == "anthropic":
                models_to_add = ANTHROPIC_MODELS
            elif provider_type == "bedrock":
                models_to_add = BEDROCK_MODELS
            elif provider_type == "openai":
                models_to_add = OPENAI_MODELS
            else:
                # Skip other providers (ollama, openrouter, etc. are dynamically fetched)
                continue

            # Add models (ON CONFLICT DO NOTHING prevents duplicates)
            for model_name, is_visible, supports_image in models_to_add:
                session.execute(
                    sa.text(
                        """
                        INSERT INTO model_configuration
                        (llm_provider_id, name, is_visible, max_input_tokens, supports_image_input)
                        VALUES (:provider_id, :name, :is_visible, NULL, :supports_image)
                        ON CONFLICT (llm_provider_id, name) DO NOTHING
                        """
                    ),
                    {
                        "provider_id": provider_id,
                        "name": model_name,
                        "is_visible": is_visible,
                        "supports_image": supports_image,
                    }
                )

            print(f"Updated model configurations for {provider_name} ({provider_type})")

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        session.close()


def downgrade() -> None:
    """
    Downgrade is a no-op since we only added models.
    Removing them could break existing configurations.
    """
    pass
