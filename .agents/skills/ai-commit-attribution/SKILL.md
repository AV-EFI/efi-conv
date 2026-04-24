---
name: ai-commit-attribution
description: Ensure that AI agents add Assisted-by trailers to commit messages
license: MIT
metadata:
  audience:
  - developers
  - AI agents
  workflow: git commit
---
# AI Commit Attribution Skill

## Purpose

Ensures AI agents properly credit their contributions by adding Assisted-by trailers to all git commit messages. Every commit made by an AI agent MUST include this attribution line to maintain transparency and traceability of AI-assisted work.

## Linux Kernel Standards

Follows the Linux kernel's AI attribution guidelines: https://docs.kernel.org/process/coding-assistants.html

Format:
```
Assisted-by: AGENT_NAME:MODEL_VERSION [optional tools]
```

This format is Git-trailer compatible, industry-recognized, flexible, and clear.

## Detection Method

Universal detection script with fallback chain (environment variables → config files → installation):

```bash
# Priority 1: Environment variables
AI_AGENT=""
AI_MODEL=""

if [ -n "$OPENCODE" ]; then
    AI_AGENT="OpenCode"
elif [ -n "$CURSOR" ]; then
    AI_AGENT="Cursor"
elif [ -n "$CLAUDE_MODEL" ] || [ -n "$ANTHROPIC_MODEL" ]; then
    AI_AGENT="Claude"
elif [ -n "$CODEX" ]; then
    AI_AGENT="Codex"
elif [ -n "$GITHUB_COPILOT" ]; then
    AI_AGENT="GitHub Copilot"
elif [ -n "$ANTIGRAVITY" ]; then
    AI_AGENT="Antigravity"
elif [ -n "$GEMINI_API_KEY" ]; then
    AI_AGENT="Gemini CLI"
fi

# Priority 2: Config files (separate agent detection from model detection)
if [ -z "$AI_AGENT" ]; then
    if [ -f ~/.config/opencode/opencode.json ]; then
        AI_AGENT="OpenCode"
    elif [ -f ~/.config/Cursor/settings.json ]; then
        AI_AGENT="Cursor"
    elif [ -f ~/.config/Claude/config.json ]; then
        AI_AGENT="Claude"
    elif [ -f ~/.codex/config.toml ]; then
        AI_AGENT="Codex"
    elif [ -d ~/.gemini/antigravity ]; then
        AI_AGENT="Antigravity"
    elif [ -f ~/.gemini/settings.json ]; then
        AI_AGENT="Gemini CLI"
    fi
fi

# Priority 3: Installation checks
if [ -z "$AI_AGENT" ]; then
    ls ~/.vscode/extensions/github.copilot-* 2>/dev/null | grep -q . && AI_AGENT="GitHub Copilot"
    npm list -g @openai/codex >/dev/null 2>&1 && AI_AGENT="Codex"
    command -v gemini >/dev/null 2>&1 && AI_AGENT="Gemini CLI"
fi

# Model extraction (Priority: env vars → config files → fallback)
if [ -n "$AI_AGENT" ]; then
    case "$AI_AGENT" in
        OpenCode)
            AI_MODEL=$(cat ~/.config/opencode/opencode.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('model','unknown').split('/')[-1])")
            ;;
        Claude)
            AI_MODEL="${CLAUDE_MODEL:-${ANTHROPIC_MODEL:-}}"
            [ -z "$AI_MODEL" ] && AI_MODEL=$(cat ~/.config/Claude/config.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('model','unknown'))")
            ;;
        Cursor)
            AI_MODEL="${CURSOR_MODEL:-unknown}"
            ;;
        Codex)
            AI_MODEL=$(cat ~/.codex/config.toml 2>/dev/null | python3 -c "
import tomllib, sys
try:
    with open('~/.codex/config.toml', 'rb') as f:
        cfg = tomllib.load(f)
        print(cfg.get('model', 'unknown'))
except:
    print('unknown')" 2>/dev/null || echo "unknown")
            ;;
        Gemini\ CLI)
            AI_MODEL=$(cat ~/.gemini/settings.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('model',{}).get('name','unknown'))")
            ;;
        *)
            AI_MODEL="unknown"
            ;;
    esac
fi

# Build attribution
if [ -n "$AI_AGENT" ]; then
    ATTRIBUTION="Assisted-by: $AI_AGENT:${AI_MODEL:-unknown}"
else
    ATTRIBUTION=""
fi
```

## Agent-Specific Detection Examples

**OpenCode**: Env var `$OPENCODE`, config at `~/.config/opencode/opencode.json`

**Claude**: Env vars `$CLAUDE_MODEL` or `$ANTHROPIC_MODEL`, config at `~/.config/Claude/config.json`

**Codex**: Env var `$CODEX`, config at `~/.codex/config.toml` (TOML format), or npm install `@openai/codex`

**Cursor**: Env var `$CURSOR`, config at `~/.config/Cursor/settings.json`

**GitHub Copilot**: VS Code extension `github.copilot`, or JetBrains plugin

**Gemini CLI**: Env var `$GEMINI_API_KEY`, config at `~/.gemini/settings.json`, or command `gemini`

**Antigravity**: Env var `$ANTIGRAVITY`, config directory at `~/.gemini/antigravity/`

## Attribution Format

Exact format:
```
Assisted-by: <AGENT_NAME>:<MODEL_VERSION>
```

Examples:
- `Assisted-by: OpenCode:glm-4.7`
- `Assisted-by: Claude:claude-3-opus`
- `Assisted-by: Codex:gpt-5.5`
- `Assisted-by: GitHub Copilot:unknown`
- `Assisted-by: Cursor:gpt-4-turbo`
- `Assisted-by: Gemini CLI:gemini-3-flash`
- `Assisted-by: Antigravity:unknown`

Optional tools (following Linux kernel format):
- `Assisted-by: Claude:claude-3-opus coccinelle sparse`

## Important Rules

1. **ALWAYS add attribution**: Even for trivial commits like "fix typo"
2. **Format matters**: Use exact `Assisted-by: <AI_AGENT_NAME>:<MODEL_VERSION>` (no variations)
3. **Placement**: Put Assisted-by line at the very end, with blank line before it
4. **No duplication**: Skip if message already has an Assisted-by line
5. **Human commits**: If no AI agent detected, DO NOT add attribution
6. **Agent specificity**: Always include specific AI agent name and model version
7. **Signed-off-by tags**: AI agents MUST NOT add Signed-off-by tags (DCO requires human certification)
8. **Optional tools**: Static analysis tools can be added after model: `Assisted-by: Claude:claude-3-opus clang-tidy`

## Target Agents

| Agent | Config Detection | Model Extraction | Fallback |
|-------|-----------------|------------------|----------|
| OpenCode | `~/.config/opencode/opencode.json` | `model` field | env vars |
| Claude | `~/.config/Claude/config.json` | `model` field | `$CLAUDE_MODEL` |
| Codex | `~/.codex/config.toml` | `model` field | npm install |
| GitHub Copilot | Extension detection | Not exposed | "unknown" |
| Cursor | `~/.config/Cursor/settings.json` | `$CURSOR_MODEL` | "unknown" |
| Gemini CLI | `~/.gemini/settings.json` | `model.name` field | command availability |
| Antigravity | `~/.gemini/antigravity/` | Not exposed | "unknown" |

## Example Commit Message

```
fix: Correct validation logic for date ranges

Added proper checking that start date is not after end date
to prevent invalid period expressions from being saved.

Assisted-by: OpenCode:glm-4.7
```

## Verification

After creating a commit, verify the attribution was added:

```bash
git log -1 --format="%B"
```

This should show the full commit message including the Assisted-by line at the end.
