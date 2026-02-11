# Story: Fix Missing Sidebar Assistants After v2.5.9 Upgrade

## Problem Statement
After upgrading Kevin AI from v0.28.2 to v2.5.9, users see an empty "Agents" section in the sidebar instead of the expected list of assistants.

## Expected Behavior
Users should see these assistants in the sidebar by default:
- Default (id: 11)
- ServiceTrade Corp (id: 10)
- Sales Assistant (id: 13)
- General (id: -1)
- Paraphrase (id: -2)
- Search (id: -3, currently named "Art")

Additionally:
- "My Documents" link should be visible (was removed in v2.5.9)

## Current State
- Database has all personas with correct flags: `is_default_persona=true`, `is_visible=true`, `is_public=true`, `deleted=false`
- User has `pinned_assistants=NULL` which should trigger fallback to show default personas
- API endpoint `/api/persona` needs verification - may not be returning built-in personas (negative IDs)
- UI shows empty "Agents" section with only "Explore Agents" link

## Technical Context

### v2.5.9 Sidebar Changes
The sidebar structure changed significantly:
- Old (v0.28.2): Shows all visible assistants in "Assistants" section
- New (v2.5.9): Shows only "pinned agents" in "Agents" section

### Key Code Path
1. `AgentsContext.tsx` line 56-67 - `getPinnedAgents()` function:
   - If `pinnedAgentIds` is NULL → returns `agents.filter(agent => agent.is_default_persona && agent.id !== 0)`
   - If `pinnedAgentIds` is `[]` → returns empty array

2. `AppSidebar.tsx` line 131, 148-151, 458-459:
   - Gets `pinnedAgents` from context
   - Builds `visibleAgents` from `pinnedAgents` + `currentAgent`
   - Renders only `visibleAgents` in sidebar

### Suspected Issues
1. **API not returning built-in personas** - `/api/persona` may filter out negative IDs
2. **AgentsProvider not receiving correct initial data** - Server-side props may not include built-in personas
3. **Backend query filtering** - `persona.py` may have additional filters we haven't found

## Acceptance Criteria
1. [ ] All 6 default assistants appear in sidebar for users with no custom pins
2. [ ] Built-in personas (negative IDs) appear in `/api/persona` response
3. [ ] "My Documents" link restored (if feasible)
4. [ ] Existing users with custom `pinned_assistants` are not affected
5. [ ] Fix is in source control, not cowboy database changes

## Investigation Steps
1. Check `/api/persona` response - does it include negative ID personas?
2. Trace server-side data fetching for AgentsProvider initial props
3. Check backend `persona.py` for filters on builtin/negative IDs
4. Verify the fix works for a fresh user with no preferences
