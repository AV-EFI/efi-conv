# AI Commit Attribution Skill

## Purpose
This skill ensures that AI agents properly credit their contributions by adding an Assisted-by trailer to all git commit messages. Every commit made by an AI agent MUST include this attribution line to maintain transparency and traceability of AI-assisted work.

This skill is designed for use by any AI agent or AI-assisted development tool.

## INDUSTRY STANDARDS

This skill follows the Linux kernel's AI attribution guidelines:
**Reference**: https://docs.kernel.org/process/coding-assistants.html

The Linux kernel uses the same format for AI-assisted contributions:

```
Assisted-by: AGENT_NAME:MODEL_VERSION [optional tools]
```

This format is:
- ✓ Git-trailer compatible
- ✓ Industry-recognized (used by world's largest open source project)
- ✓ Flexible (supports optional tool attribution)
- ✓ Clear and specific

## WHEN TO USE
- ALWAYS load this skill when performing any git commit operations
- Load automatically for tasks involving code changes that require version control
- Apply to ALL commits made by AI agents (even "fix typos" or trivial changes)

## DETECTION
Before making any commit, determine if you are an AI agent:

1. Check environment variables:
   - `$OPENCODE` = 1 indicates running in OpenCode environment
   - `$AGENT` = 1 indicates AI agent mode
   - `$CURSOR` = indicates running in Cursor
   - `$CLAUDE_MODEL` or `$ANTHROPIC_MODEL` = indicates Claude
   - `$GITHUB_COPILOT` = indicates GitHub Copilot
   - If any AI agent environment variable is set, you MUST add attribution

2. If no AI agent variables are set, you are likely a human interaction and should NOT add attribution

## GENERIC AI AGENT DETECTION GUIDANCE

This section provides comprehensive detection guidance for popular AI development tools. Different AI agents expose their identity and model information in various ways.

### Priority Order for Detection

**Priority 1: Environment Variables** (most reliable)
- OpenCode: `OPENCODE=1`, `AGENT=1`
- Cursor: `CURSOR=1`, `CURSOR_MODEL=gpt-4-turbo`
- Claude/Claude Code: `CLAUDE_MODEL=claude-3-opus`, `ANTHROPIC_MODEL=claude-3-opus`
- GitHub Copilot: `GITHUB_COPILOT=1`
- Codeium: `CODEIUM=1`
- Tabnine: `TABNINE=1`
- AWS CodeWhisperer: `AWS_CODEWHISPERER=1`
- Sourcegraph Cody: `CODY=1`

**Priority 2: Configuration Files**

OpenCode:
```bash
cat ~/.config/opencode/opencode.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('model','unknown').split('/')[-1])"
```

Claude:
```bash
cat ~/.config/Claude/config.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('model','unknown'))"
```

Cursor:
```bash
cat ~/.config/Cursor/settings.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('model','unknown'))"
```

**Priority 3: Process Detection**

Claude/Claude Code:
```bash
pgrep -f "claude|claude-code|claude-desktop"
```

Cursor:
```bash
pgrep -f "cursor|cursor-desktop"
```

**Priority 4: Extension/Tool Detection**

GitHub Copilot (VS Code):
```bash
ls ~/.vscode/extensions/github.copilot-*
```

GitHub Copilot (JetBrains):
```bash
ls ~/.config/JetBrains/*/plugins/github-copilot*/
```

Tabnine:
```bash
ls ~/.TabNine/ ~/.config/TabNine/
```

Codeium:
```bash
ls ~/.codeium/
```

JetBrains AI:
```bash
ls ~/.config/JetBrains/*/ai-assistant.xml
```

### Agent-Specific Notes

**OpenCode**: 100% reliable - provides full model information via config file and environment variables.

**GitHub Copilot**: Model information may be unknown. Use "unknown" as generic model identifier if not informed otherwise. Detection via extensions is the most reliable method.

**Claude/Claude Code**: Model information may be available via environment variables or config files. Process detection is also reliable.

**Cursor**: Model information may not always be available. Use "unknown" as default if model is not specified.

**Tabnine**: Does not expose model information. Model name will be "unknown".

**Codeium**: Does not expose specific model information. Model name will be "unknown".

**AWS CodeWhisperer**: Does not expose model information. Model name will be "unknown".

**JetBrains AI**: Model information varies depending on JetBrains product. Use "unknown" if not available.

## ATTRIBUTION FORMAT

Use this exact format for the Assisted-by line:

```
Assisted-by: <AI_AGENT_NAME>:<MODEL_VERSION>
```

Examples:
- `Assisted-by: OpenCode:glm-4.7`
- `Assisted-by: Claude:claude-3-opus`
- `Assisted-by: GitHub Copilot:gpt-4`
- `Assisted-by: Cursor:gpt-4-turbo`
- `Assisted-by: Tabnine:unknown`
- `Assisted-by: Codeium:unknown`

Optional tool attribution (following Linux kernel format):
- `Assisted-by: Claude:claude-3-opus coccinelle sparse`
- `Assisted-by: OpenCode:glm-4.7 clang-tidy`

## COMMIT MESSAGE STRUCTURE

When creating a commit, follow this structure:

```
<commit subject line (concise, < 50 characters)>

<optional detailed description if needed>

Assisted-by: <AI_AGENT_NAME>:<MODEL_VERSION>
```

Example:

```
fix: Correct validation logic for date ranges

Added proper checking that start date is not after end date
to prevent invalid period expressions from being saved.

Assisted-by: OpenCode:glm-4.7
```

## IMPLEMENTATION STEPS

When using the Bash tool to create commits, use this generic detection framework:

```bash
# Initialize variables
AI_AGENT=""
AI_MODEL=""

# Priority 1: Check environment variables
if [ -n "$OPENCODE" ] || [ -n "$AGENT" ]; then
    AI_AGENT="OpenCode"
    AI_MODEL=$(cat ~/.config/opencode/opencode.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('model','unknown').split('/')[-1])")
elif [ -n "$CURSOR" ]; then
    AI_AGENT="Cursor"
    AI_MODEL="${CURSOR_MODEL:-unknown}"
elif [ -n "$CLAUDE_MODEL" ]; then
    AI_AGENT="Claude"
    AI_MODEL="$CLAUDE_MODEL"
elif [ -n "$ANTHROPIC_MODEL" ]; then
    AI_AGENT="Claude"
    AI_MODEL="$ANTHROPIC_MODEL"
elif [ -n "$GITHUB_COPILOT" ]; then
    AI_AGENT="GitHub Copilot"
    AI_MODEL="unknown"
elif [ -n "$CODEIUM" ]; then
    AI_AGENT="Codeium"
    AI_MODEL="unknown"
elif [ -n "$TABNINE" ]; then
    AI_AGENT="Tabnine"
    AI_MODEL="unknown"
elif [ -n "$AWS_CODEWHISPERER" ]; then
    AI_AGENT="AWS CodeWhisperer"
    AI_MODEL="unknown"
elif [ -n "$CODY" ]; then
    AI_AGENT="Sourcegraph Cody"
    AI_MODEL="unknown"
fi

# Priority 2: Check config files (if not detected via env vars)
if [ -z "$AI_AGENT" ]; then
    if [ -f ~/.config/opencode/opencode.json ]; then
        AI_AGENT="OpenCode"
        AI_MODEL=$(cat ~/.config/opencode/opencode.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('model','unknown').split('/')[-1])")
    elif [ -f ~/.config/Cursor/settings.json ]; then
        AI_AGENT="Cursor"
        AI_MODEL="unknown"
    elif [ -f ~/.config/Claude/config.json ]; then
        AI_AGENT="Claude"
        AI_MODEL=$(cat ~/.config/Claude/config.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('model','unknown'))")
    fi
fi

# Priority 3: Check for installed tools/extensions
if [ -z "$AI_AGENT" ]; then
    if ls ~/.vscode/extensions/github.copilot-* 2>/dev/null | grep -q .; then
        AI_AGENT="GitHub Copilot"
        AI_MODEL="unknown"
    elif [ -d ~/.TabNine ] || [ -d ~/.config/TabNine ]; then
        AI_AGENT="Tabnine"
        AI_MODEL="unknown"
    elif [ -d ~/.codeium ]; then
        AI_AGENT="Codeium"
        AI_MODEL="unknown"
    fi
fi

# Build attribution if AI detected
if [ -n "$AI_AGENT" ]; then
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
else
    ATTRIBUTION=""
fi

# Build commit message
if [ -n "$ATTRIBUTION" ]; then
    COMMIT_MSG="${USER_MESSAGE}"$'\n'"$'\n'"${ATTRIBUTION}"
else
    COMMIT_MSG="${USER_MESSAGE}"
fi

# Execute commit
git commit -m "$COMMIT_MSG"
```

## AGENT-SPECIFIC DETECTION EXAMPLES

### OpenCode

```bash
if [ -n "$OPENCODE" ] || [ -n "$AGENT" ]; then
    AI_AGENT="OpenCode"
    AI_MODEL=$(cat ~/.config/opencode/opencode.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('model','unknown').split('/')[-1])")
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### GitHub Copilot

```bash
# Environment variable
if [ -n "$GITHUB_COPILOT" ]; then
    AI_AGENT="GitHub Copilot"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# VS Code extension detection
if ls ~/.vscode/extensions/github.copilot-* 2>/dev/null | grep -q .; then
    AI_AGENT="GitHub Copilot"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# JetBrains IDE
if ls ~/.config/JetBrains/*/plugins/github-copilot* 2>/dev/null | grep -q .; then
    AI_AGENT="GitHub Copilot"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### Claude / Claude Code

```bash
# Environment variables
if [ -n "$CLAUDE_MODEL" ]; then
    AI_AGENT="Claude"
    AI_MODEL="$CLAUDE_MODEL"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
elif [ -n "$ANTHROPIC_MODEL" ]; then
    AI_AGENT="Claude"
    AI_MODEL="$ANTHROPIC_MODEL"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# Config file detection
if [ -f ~/.config/Claude/config.json ]; then
    AI_AGENT="Claude"
    AI_MODEL=$(cat ~/.config/Claude/config.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('model','unknown'))")
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### Cursor

```bash
# Environment variables
if [ -n "$CURSOR" ]; then
    AI_AGENT="Cursor"
    AI_MODEL="${CURSOR_MODEL:-unknown}"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# Config file detection
if [ -f ~/.config/Cursor/settings.json ]; then
    AI_AGENT="Cursor"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### Tabnine

```bash
# Environment variable
if [ -n "$TABNINE" ]; then
    AI_AGENT="Tabnine"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# Directory detection
if [ -d ~/.TabNine ] || [ -d ~/.config/TabNine ]; then
    AI_AGENT="Tabnine"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### Codeium

```bash
# Environment variable
if [ -n "$CODEIUM" ]; then
    AI_AGENT="Codeium"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# Directory detection
if [ -d ~/.codeium ]; then
    AI_AGENT="Codeium"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### AWS CodeWhisperer

```bash
# Environment variable
if [ -n "$AWS_CODEWHISPERER" ]; then
    AI_AGENT="AWS CodeWhisperer"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### JetBrains AI

```bash
# Config file detection
if ls ~/.config/JetBrains/*/ai-assistant.xml 2>/dev/null | grep -q .; then
    AI_AGENT="JetBrains AI"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

### Sourcegraph Cody

```bash
# Environment variable
if [ -n "$CODY" ]; then
    AI_AGENT="Sourcegraph Cody"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi

# Config directory
if [ -d ~/.config/Sourcegraph/Cody ]; then
    AI_AGENT="Sourcegraph Cody"
    AI_MODEL="unknown"
    ATTRIBUTION="Assisted-by: $AI_AGENT:$AI_MODEL"
fi
```

## Git Safety Protocol Compliance

This skill MUST be used in conjunction with the standard Git Safety Protocol:

1. Analyze staged changes with git status and git diff
2. Analyze recent commit message style with git log
3. Draft commit message following project conventions
4. Add Assisted-by line at the END of commit message (after description, before any trailers)
5. Execute commit with git commit -m
6. Run git status to verify success

## IMPORTANT RULES

1. **ALWAYS add attribution**: Even for trivial commits like "fix typo" or "update README"

2. **Format matters**: Use exact format `Assisted-by: <AI_AGENT_NAME>:<MODEL_VERSION>` (no variations)

3. **Placement**: Put Assisted-by line at the very end of commit message, with blank line before it

4. **No duplication**: If commit message already has an Assisted-by line, do not add another

5. **Human commits**: If no AI agent environment variables or detection methods identify you as an AI agent, DO NOT add attribution

6. **Agent and model specificity**: Always include the specific AI agent name and model version

7. **Signed-off-by tags**: AI agents MUST NOT add Signed-off-by tags. Only humans can legally certify the Developer Certificate of Origin (DCO) per Linux kernel policy

8. **Optional tools**: Static analysis or linting tools (coccinelle, sparse, clang-tidy) can be added after the model: `Assisted-by: Claude:claude-3-opus coccinelle sparse`

## EXAMPLES

### Example 1: Simple Fix (OpenCode)

```
fix: Remove unused import

Assisted-by: OpenCode:glm-4.7
```

### Example 2: Feature Addition (Claude)

```
feat: Add support for period validation

Implemented comprehensive date range validation including:
- Start date must be before or equal to end date
- Open-ended periods are allowed
- Periods with both dates null are valid

Assisted-by: Claude:claude-3-opus
```

### Example 3: Refactoring (GitHub Copilot)

```
refactor: Simplify error handling in converter modules

Extracted common error patterns into shared utility functions.
Reduced code duplication across avportal and fmdu converters.

Assisted-by: GitHub Copilot:gpt-4
```

### Example 4: Performance Improvement (Cursor)

```
perf: Optimize AVPortal import processing

Added parallel processing and caching to speed up imports
from large datasets. Reduced processing time by 60%.

Assisted-by: Cursor:gpt-4-turbo
```

### Example 5: With Optional Tools (OpenCode)

```
check: Validate period expressions, so that start is not after end date

Added comprehensive date range validation with edge case handling.
All period expressions are now validated to ensure consistency.

Assisted-by: OpenCode:glm-4.7 coccinelle sparse
```

### Example 6: Code Quality Improvements (Claude with tools)

```
style: Apply clang-tidy recommendations

Fixed various code quality issues identified by clang-tidy:
- Removed unused variables
- Improved const-correctness
- Modernized C++ patterns

Assisted-by: Claude:claude-3-opus clang-tidy
```

## VERIFICATION

After creating a commit, verify the attribution was added:

```bash
git log -1 --format="%B"
```

This should show the full commit message including the Assisted-by line at the end.

## TROUBLESHOOTING

### Problem: Model name not found
**Solution**: Use "unknown" as fallback: `Assisted-by: <AI_AGENT_NAME>:unknown`

### Problem: Environment variables not set
**Solution**: Use alternative detection methods:
1. Check for config files (~/.config/opencode/opencode.json, etc.)
2. Check for installed extensions in ~/.vscode/extensions/
3. Check for processes running (pgrep -f "claude|cursor", etc.)
4. If no AI agent is detected, skip attribution (human commit)

### Problem: Multiple Assisted-by lines
**Solution**: Check existing message content before adding, avoid duplication. Only add if no Assisted-by line already exists.

### Problem: Commit fails
**Solution**: Verify commit message format is valid (no trailing newlines from attribution). Ensure proper quoting in shell: `git commit -m "$COMMIT_MSG"`

### Problem: Cannot determine which AI agent is running
**Solution**: Use a generic identifier: `Assisted-by: AI Assistant:unknown`. However, always attempt specific detection first.

## COMPATIBILITY

This skill is compatible with:
- OpenCode agents with access to environment variables ($OPENCODE, $AGENT)
- GitHub Copilot (VS Code, JetBrains, Vim)
- Claude / Claude Code
- Cursor
- Tabnine
- Codeium
- AWS CodeWhisperer
- JetBrains AI
- Sourcegraph Cody
- Continue.dev
- Replit Ghostwriter
- Any AI agent using the Bash tool for git operations
- Projects using Git for version control
- Existing commit message formats (Applies Assisted-by as trailing line)

## NOTES

- This skill follows Linux kernel attribution standards (https://docs.kernel.org/process/coding-assistants.html)
- The model name may contain special characters (hyphens, dots, etc.) - preserve exactly as extracted
- AI agents vary in exposing model information; some may only provide agent name
- Optional tool attribution can be added after model (e.g., coccinelle, sparse, clang-tidy)
- Environment variable detection is the primary mechanism for AI identification
- Config file detection provides fallback when environment variables are not set
- This skill does not interfere with human-only commits (attribution not added when not in AI context)
- The Assisted-by line is a Git-compatible trailer and should appear at the end of commit messages
- AI agents MUST NOT add Signed-off-by tags (only humans can sign DCO per Linux kernel policy)

## NOTE FOR ALL AI AGENTS

This skill should be loaded before making any git commits. To other AI agent systems:

If you don't have a `skill` tool or equivalent capability, please manually follow these attribution requirements:

1. Detect if you are an AI agent (via environment variables, config files, or process detection)
2. Identify your agent name and model (if available)
3. Add an Assisted-by line in the format: `Assisted-by: <AI_AGENT_NAME>:<MODEL_VERSION>`
4. Place the Assisted-by line at the very end of the commit message

Detection methods for various agents are documented in the GENERIC AI AGENT DETECTION GUIDANCE section above.

The Linux kernel requires this same format for AI-assisted contributions, so following this standard benefits the entire open source community.
