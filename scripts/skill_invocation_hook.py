#!/usr/bin/env python3
"""
skill_invocation_hook.py - Claude Code PostToolUse hook for skill invocation tracking

This hook is triggered after the Skill tool is used and automatically records
the skill invocation in skill-usage.json.

Usage: Called automatically by Claude Code's hook system.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
SKILL_HUB_DIR = Path.home() / ".claude" / "skills" / "skill-hub"
RECORD_SCRIPT = SKILL_HUB_DIR / "scripts" / "record_invocation.py"
LOG_FILE = Path.home() / ".claude" / "skill-hooks.log"


def log(message: str) -> None:
    """Log to hook log file"""
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def main():
    """Main hook function"""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_result = input_data.get("tool_result", "")
        success = input_data.get("success", True)

        # Only process Skill tool
        if tool_name != "Skill":
            sys.exit(0)

        # Extract skill name
        skill_name = tool_input.get("skill", "")
        if not skill_name:
            log("⚠️ No skill name in input")
            sys.exit(0)

        # Only record successful invocations
        if not success:
            log(f"❌ Skill '{skill_name}' invocation failed, not recording")
            sys.exit(0)

        log(f"🎯 Recording skill invocation: {skill_name}")

        # Call record_invocation.py
        if RECORD_SCRIPT.exists():
            result = subprocess.run(
                [sys.executable, str(RECORD_SCRIPT), skill_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                log(f"✅ Recorded: {result.stdout.strip()}")
            else:
                log(f"❌ Record failed: {result.stderr}")
        else:
            log(f"❌ Record script not found: {RECORD_SCRIPT}")

    except json.JSONDecodeError as e:
        log(f"❌ JSON decode error: {e}")
    except Exception as e:
        log(f"❌ Hook error: {e}")

    # Always exit 0 to not block Claude Code
    sys.exit(0)


if __name__ == "__main__":
    main()
