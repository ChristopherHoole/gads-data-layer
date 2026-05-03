"""Prompt version constants for the ACT AI classification system.

Bumping a version here = next classify run will re-classify all rows under
the new version (cache miss intentional). Old classifications remain
attributed to the previous version in act_v2_ai_classifications.prompt_version.

To bump a prompt:
  1. Copy <name>_vN.txt -> <name>_v(N+1).txt
  2. Edit the new file
  3. Update the corresponding constant + filename below
  4. Old rows in act_v2_ai_classifications keep their prompt_version='vN'
     (no retroactive re-classification, no data loss)
"""

# --- Version constants (used as act_v2_ai_classifications.prompt_version) ---
PROMPT_VERSION_CLASSIFY  = "v1"   # search_terms_v1.txt — block/review batch
PROMPT_VERSION_PASS3     = "v1"   # search_terms_pass3_v1.txt — Stage 11 router
PROMPT_VERSION_PASS3_AI  = "v4"   # search_terms_pass3_v2.txt — Brief G: drop 30d list from prompt; code-side dedup load-bearing (4 May 2026)
PROMPT_VERSION_EXPLAIN   = "v1"   # explain_row_v1.txt — Opus deep reasoning
PROMPT_VERSION_CHAT      = "v1"   # chat_v1.txt — free-text panel chat

# --- File names (resolved relative to this directory at request time) ---
PROMPT_FILE_CLASSIFY   = "search_terms_v1.txt"
PROMPT_FILE_PASS3      = "search_terms_pass3_v1.txt"
PROMPT_FILE_PASS3_AI   = "search_terms_pass3_v2.txt"
PROMPT_FILE_USER       = "search_terms_user_v1.txt"
PROMPT_FILE_PASS3_USER = "search_terms_pass3_user_v1.txt"
PROMPT_FILE_EXPLAIN    = "explain_row_v1.txt"
PROMPT_FILE_CHAT       = "chat_v1.txt"
