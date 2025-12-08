"""Refresh LLM model configurations with all available models

Revision ID: a1b2c3d4e5f6
Revises: f9b8c7d6e5a4
Create Date: 2025-12-08 12:00:00.000000

This migration updates existing LLM providers to include all available models
from litellm, ensuring users have access to the full model list after an upgrade.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f9b8c7d6e5a4"
branch_labels = None
depends_on = None


# Models that should be marked as visible by default for Anthropic
ANTHROPIC_VISIBLE_MODEL_NAMES = [
    "claude-opus-4-5-20251101",
    "claude-opus-4-1",
    "claude-opus-4-20250514",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-5",
    "claude-sonnet-4-20250514",
    "claude-haiku-4-5",
    "claude-3-7-sonnet-latest",
    # Also keep older popular models visible
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

OPENAI_VISIBLE_MODEL_NAMES = [
    "gpt-5",
    "gpt-5-mini",
    "o1",
    "o3-mini",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]

# Models to ignore (deprecated/obsolete)
IGNORABLE_ANTHROPIC_MODELS = [
    "claude-2",
    "claude-instant-1",
    "anthropic/claude-3-5-sonnet-20241022",
]


def get_anthropic_models() -> list[str]:
    """Get all Anthropic models from litellm."""
    try:
        import litellm
        return [
            model
            for model in litellm.anthropic_models
            if model not in IGNORABLE_ANTHROPIC_MODELS
        ]
    except ImportError:
        # Fallback list if litellm is not available during migration
        return [
            "claude-opus-4-5-20251101",
            "claude-opus-4-1",
            "claude-opus-4-20250514",
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-5",
            "claude-sonnet-4-20250514",
            "claude-haiku-4-5",
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-haiku-20241022",
        ]


def get_openai_models() -> list[str]:
    """Get OpenAI models."""
    return [
        "gpt-5",
        "gpt-5-mini",
        "gpt-5-nano",
        "o4-mini",
        "o3-mini",
        "o1-mini",
        "o3",
        "o1",
        "gpt-4",
        "gpt-4.1",
        "gpt-4o",
        "gpt-4o-mini",
        "o1-preview",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4-0613",
        "gpt-4o-2024-08-06",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-0301",
    ]


def model_supports_image_input(model_name: str, provider: str) -> bool:
    """Check if a model supports image input."""
    # Vision-capable models
    vision_models = {
        "gpt-4-vision-preview",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4.1",
        "gpt-5",
        "gpt-5-mini",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022",
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-5",
        "claude-sonnet-4-20250514",
        "claude-opus-4-5-20251101",
        "claude-opus-4-1",
        "claude-opus-4-20250514",
        "claude-haiku-4-5",
        "claude-3-7-sonnet-latest",
    }
    return model_name in vision_models


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
            # Get existing model configurations for this provider
            existing_models_result = session.execute(
                sa.text(
                    "SELECT name FROM model_configuration WHERE llm_provider_id = :provider_id"
                ),
                {"provider_id": provider_id}
            )
            existing_model_names = {row[0] for row in existing_models_result.fetchall()}

            # Determine which models to add based on provider type
            if provider_type == "anthropic":
                all_models = get_anthropic_models()
                visible_models = set(ANTHROPIC_VISIBLE_MODEL_NAMES)
            elif provider_type == "openai":
                all_models = get_openai_models()
                visible_models = set(OPENAI_VISIBLE_MODEL_NAMES)
            else:
                # Skip other providers (bedrock, ollama, etc. are dynamically fetched)
                continue

            # Add missing models
            for model_name in all_models:
                if model_name not in existing_model_names:
                    is_visible = model_name in visible_models
                    supports_image = model_supports_image_input(model_name, provider_type)

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
