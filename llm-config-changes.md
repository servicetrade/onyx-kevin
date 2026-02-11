# LLM Configuration Changes Log

## Goal
Simplify LLM selection to only:
- 3 Claude 4.5 models (Haiku, Sonnet, Opus)
- 2 Llama 4 models (Maverick, Scout)
- 2 Mistral models (Large, Small)

Default: Claude Haiku 4.5

## Correct Model IDs (verified via AWS Bedrock API)
```
us.anthropic.claude-haiku-4-5-20251001-v1:0   # Note: date is 20251001, NOT 20251022
us.anthropic.claude-sonnet-4-5-20250929-v1:0
us.anthropic.claude-opus-4-5-20251101-v1:0
us.meta.llama4-maverick-17b-instruct-v1:0
us.meta.llama4-scout-17b-instruct-v1:0
mistral.mistral-large-2407-v1:0
mistral.mistral-small-2402-v1:0
```

## Key Findings
1. Claude 4.5 models REQUIRE inference profile IDs (us. prefix) - cannot use base model IDs directly
2. Original Haiku date was wrong: `20251022` should be `20251001`
3. IAM role `danswer-server-role` needs marketplace permissions for first-time model access

## Changes Made

### 1. Created migration file
**File**: `backend/alembic/versions/a1b2c3d4e5f6_simplify_llm_selection.py`
- Disables all models, enables only the 7 selected models
- Fixed Haiku date from 20251022 to 20251001

### 2. SQL changes run on staging

**Disable all, enable selected models:**
```sql
UPDATE model_configuration SET is_visible = false;
UPDATE model_configuration SET is_visible = true
WHERE name IN (
  'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
  'us.anthropic.claude-opus-4-5-20251101-v1:0',
  'us.anthropic.claude-haiku-4-5-20251001-v1:0',
  'us.meta.llama4-maverick-17b-instruct-v1:0',
  'us.meta.llama4-scout-17b-instruct-v1:0',
  'mistral.mistral-large-2407-v1:0',
  'mistral.mistral-small-2402-v1:0'
);
```

**Set Haiku 4.5 as default:**
```sql
UPDATE llm_provider
SET default_model_name = 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
    fast_default_model_name = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
WHERE id = (
  SELECT llm_provider_id FROM model_configuration
  WHERE name = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
  LIMIT 1
);
```

**Insert correct Haiku model (with correct date):**
```sql
INSERT INTO model_configuration (llm_provider_id, name, is_visible)
SELECT llm_provider_id, 'us.anthropic.claude-haiku-4-5-20251001-v1:0', true
FROM model_configuration
WHERE name = 'us.anthropic.claude-opus-4-5-20251101-v1:0'
LIMIT 1
ON CONFLICT DO NOTHING;
```

**Disable wrong models (non-us. prefix and wrong dates):**
```sql
UPDATE model_configuration SET is_visible = false
WHERE name IN (
  'us.anthropic.claude-haiku-4-5-20251022-v1:0',
  'anthropic.claude-haiku-4-5-20251001-v1:0',
  'anthropic.claude-sonnet-4-5-20250929-v1:0'
);
```

**Add Sonnet back (us. prefix):**
```sql
UPDATE model_configuration SET is_visible = true
WHERE name = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0';

INSERT INTO model_configuration (llm_provider_id, name, is_visible)
SELECT llm_provider_id, 'us.anthropic.claude-sonnet-4-5-20250929-v1:0', true
FROM model_configuration
WHERE name = 'us.anthropic.claude-opus-4-5-20251101-v1:0'
LIMIT 1
ON CONFLICT DO NOTHING;
```

### 3. Services restarted
```bash
cd /root/danswer/deployment/docker_compose && ./restart-onyx.sh
```

## Outstanding Issues

### IAM/Model Access (BLOCKING - waiting on Brian)
Error: "Model access is denied due to IAM user or service role is not authorized to perform the required AWS Marketplace actions"

**Root cause discovered by Brian (Dec 10, 6:10 PM)**:
- Kevin uses its own AWS API key/secret to call Bedrock (NOT the EC2 instance's `danswer-server-role`)
- That AWS account needs:
  1. IAM permissions for marketplace actions (Brian added this)
  2. Model access enabled for new Claude 4.5 models (NOT YET DONE)

**Status**: Brian will enable model access tonight or tomorrow morning.

## Current Database State
```
default_model_name: us.anthropic.claude-haiku-4-5-20251001-v1:0
fast_default_model_name: us.anthropic.claude-haiku-4-5-20251001-v1:0

Visible models:
- us.anthropic.claude-opus-4-5-20251101-v1:0 (WORKS)
- us.anthropic.claude-haiku-4-5-20251001-v1:0 (blocked by IAM)
- us.anthropic.claude-sonnet-4-5-20250929-v1:0 (needs to be added/verified)
- us.meta.llama4-scout-17b-instruct-v1:0
- us.meta.llama4-maverick-17b-instruct-v1:0
- mistral.mistral-large-2407-v1:0
- mistral.mistral-small-2402-v1:0
- anthropic.claude-haiku-4-5-20251001-v1:0 (should be disabled - no us. prefix)
- anthropic.claude-sonnet-4-5-20250929-v1:0 (should be disabled - no us. prefix)
```

## Cleanup Needed
After IAM is fixed, run:
```sql
UPDATE model_configuration SET is_visible = false
WHERE name IN (
  'anthropic.claude-haiku-4-5-20251001-v1:0',
  'anthropic.claude-sonnet-4-5-20250929-v1:0'
);
```
