# Actions Log - Onyx v2.5.9 Upgrade (Dec 8, 2025)

## Context
Upgrading Kevin AI (forked Onyx) from servicetrade branch to upstream v2.5.9

## Actions Taken

### 1. Merge & Initial Fixes (Local)
- Merged upstream v2.5.9 into servicetrade branch - **OK**
- Fixed Dockerfile ONYX_VERSION to v2.5.9 (was incorrectly 0.28.2) - **OK**
- Created missing shadcn/ui components (button.tsx, separator.tsx) for build - **OK**
- Fixed import in reports.py (`onyx.db.engine` → `onyx.db.engine.sql_engine`) - **OK**
- Fixed Kevin AI branding in 4 files (Logo.tsx, ChatPopup.tsx, OnyxInitializingLoader.tsx, FederatedOAuthModal.tsx) - **OK**

### 2. LLM Models Issue
- User reported missing Claude 4.5 and Meta models
- Created migration `a1b2c3d4e5f6_refresh_llm_model_configurations.py` to add models - **CAUSED PROBLEMS**
- Migration had wrong `down_revision`, causing "multiple heads" error
- Attempted to fix by changing down_revision - **STILL FAILED**
- Deleted migration file entirely - **OK locally**

### 3. Staging Deployment Attempts
- Server at `/root/danswer/deployment/docker_compose`
- `git pull` on server - **OK**
- Discovered containers use pre-built images, not local code
- Attempted `docker-compose build` - used wrong docker command
- Used `docker build -t onyxdotapp/onyx-backend:latest -f backend/Dockerfile backend/` - **OK**
- `./restart-onyx.sh` - **FAILED: multiple heads error persists**

### 4. Debugging Multiple Heads
- Checked `alembic heads` inside container - shows single head `6436661d5b65` - **OK**
- Checked for duplicate down_revisions - none found - **OK**
- Discovered TWO sets of containers running: `danswer-stack-*` (newer) and `onyx-*` (older, broken)
- Old `onyx-api_server-1` using stale image `932cc4d19c2f` was the one failing

### 5. Database State
- Connected to postgres: `docker exec -it onyx-relational_db-1 psql -U postgres -d postgres`
- Database only has `alembic_version` table with 0 rows - migrations never ran
- All app tables missing because migrations keep failing

### 6. Deployment Fix (Dec 8, 2025 evening)
- Stopped all containers: `docker stop $(docker ps -aq) && docker rm $(docker ps -aq)`
- Ran `./restart-onyx.sh` - containers didn't start (empty compose output)
- Ran `docker-compose up -d` manually - **11/12 containers started**
- nginx failed: port 80 already allocated by stale docker-proxy
- Killed stale processes and retried - still failed (docker respawned proxy)
- Full clean restart: `docker stop $(docker ps -aq) && sleep 2 && docker-compose up -d` - **ALL 12 CONTAINERS UP**
- API server logs show:
  - Migrations ran successfully (no multiple heads error!)
  - Vespa setup complete
  - S3 bucket initialized
  - Health checks passing
- **DEPLOYMENT WORKING** ✅

### 7. Nginx Module Fix
- nginx was crash-looping: missing `ngx_http_headers_more_filter_module.so`
- The `run-nginx.sh` script was trying to load a module not in `nginx:1.25.5-alpine` image
- Fixed in source control: removed `load_module` line from `deployment/data/nginx/run-nginx.sh`
- Committed and pushed, pulled on server, restarted nginx - **WORKING** ✅

### 8. Database State Discovery
- App loads but prompts users for individual LLM API keys
- This indicates LLM provider admin configuration is missing
- **IMPORTANT**: The database was already empty/broken before this session
  - Section 5 above documents: "Database only has `alembic_version` table with 0 rows"
  - The migration failures had prevented tables from ever being created
  - When migrations finally ran successfully, they created fresh empty tables
- User needs to reconfigure LLM providers in admin settings

## Next Steps
1. Reconfigure LLM providers in Admin → LLM settings (add API keys)
2. Run SQL to add additional LLM models (script below)

## SQL Script - Add LLM Models
Run this after confirming app works:

```sql
INSERT INTO model_configuration (llm_provider_id, name, is_visible, max_input_tokens, supports_image_input)
SELECT lp.id, m.name, m.is_visible, NULL, m.supports_image
FROM llm_provider lp
CROSS JOIN (VALUES
    ('claude-sonnet-4-5-20250929', true, true),
    ('claude-sonnet-4-5', true, true),
    ('claude-opus-4-5-20251101', true, true),
    ('claude-haiku-4-5', true, true),
    ('claude-opus-4-1', true, true),
    ('claude-sonnet-4-20250514', true, true),
    ('claude-3-7-sonnet-latest', true, true),
    ('claude-3-5-sonnet-20241022', true, true),
    ('claude-3-5-haiku-20241022', true, true)
) AS m(name, is_visible, supports_image)
WHERE lp.provider = 'anthropic'
ON CONFLICT (llm_provider_id, name) DO NOTHING;
```
