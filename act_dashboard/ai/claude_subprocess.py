"""Claude CLI subprocess wrapper. Single retry. Returns parsed result or raises.

Confirmed invocation (per Stage 4 Pause 1):
    claude -p --output-format json --model <model> \\
           --system-prompt <system> --no-session-persistence
    user_message piped via stdin

UTF-8 encoding is REQUIRED on stdin/stdout — prompts contain £ and –
characters; without encoding='utf-8' Windows defaults to CP1252 and
mangles the input.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

CLAUDE_CMD = 'claude'  # must be on PATH
DEFAULT_TIMEOUT_S = 60


def _resolve_claude_cmd() -> str | None:
    """Resolve CLAUDE_CMD to an absolute path on first call.

    Windows ships the CLI as `claude.CMD` (a batch wrapper). Python's
    subprocess.run(list, shell=False) calls CreateProcess directly, which
    doesn't auto-append .CMD/.BAT to bare names — so a literal 'claude'
    fails with FileNotFoundError. shutil.which() does the PATHEXT lookup
    we need, returning the full resolved path on every platform.
    Returns None if the CLI isn't installed.
    """
    return shutil.which(CLAUDE_CMD)


class ClaudeError(Exception):
    """Base class. Has .error_type for act_v2_ai_errors logging.

    error_type ∈ {
        'subprocess_failed', 'invalid_json', 'timeout', 'quota_exhausted'
    }
    """

    def __init__(self, error_type: str, message: str, raw_output: str = ''):
        super().__init__(message)
        self.error_type = error_type
        self.raw_output = (raw_output or '')[:4096]  # truncate for DB


def run_claude(model: str, system_prompt: str, user_message: str,
               timeout_s: int = DEFAULT_TIMEOUT_S
               ) -> tuple[str, dict, int]:
    """Invoke Claude CLI with system + user prompt.

    Returns: (result_text, usage_dict, wall_clock_ms)
    Raises ClaudeError on any failure. Caller (classifier) does retry-once.
    """
    resolved = _resolve_claude_cmd()
    if not resolved:
        raise ClaudeError(
            'subprocess_failed',
            f'`{CLAUDE_CMD}` CLI not found on PATH', '',
        )
    # NOTE: Pause 1 preferred passing system_prompt via --system-prompt flag.
    # Test 1 surfaced WinError 122 ("data area passed to a system call is
    # too small") — Windows CreateProcess caps the combined command line at
    # ~32KB and our system prompt (~9KB) plus argument escaping blows past
    # that. Falling back to the brief's documented stdin-combine path:
    # system + separator + user, all on stdin.  The model still treats the
    # combined message correctly because the OUTPUT FORMAT instructions sit
    # at the end of the system block (and immediately precede the user list)
    # which is where Claude looks for response-shape rules anyway.
    cmd = [
        resolved, '-p',
        '--output-format', 'json',
        '--model', model,
        '--no-session-persistence',
    ]
    stdin_payload = f"{system_prompt}\n\n---\n\n{user_message}"

    # Strip CLAUDECODE from the inherited env: if Flask was started inside
    # another Claude Code session (e.g. during dev when the operator is
    # using `claude` interactively), the spawned CLI refuses to launch
    # ("Nested sessions share runtime resources and will crash all active
    # sessions"). The server has no need to inherit that flag, so unset
    # unconditionally.
    env = {k: v for k, v in os.environ.items() if k != 'CLAUDECODE'}

    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            input=stdin_payload,
            capture_output=True,
            text=True,
            encoding='utf-8',          # CRITICAL — UTF-8 chars in prompts
            timeout=timeout_s,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as e:
        raise ClaudeError(
            'timeout', f'subprocess timed out after {timeout_s}s',
            (e.stdout or ''),
        ) from e
    except FileNotFoundError as e:
        raise ClaudeError(
            'subprocess_failed',
            f'`{CLAUDE_CMD}` CLI not found on PATH', '',
        ) from e

    elapsed_ms = int((time.monotonic() - start) * 1000)

    if proc.returncode != 0:
        stderr_lower = (proc.stderr or '').lower()
        if ('quota' in stderr_lower
                or 'rate limit' in stderr_lower
                or 'usage limit' in stderr_lower):
            raise ClaudeError(
                'quota_exhausted',
                proc.stderr.strip(),
                proc.stdout,
            )
        raise ClaudeError(
            'subprocess_failed',
            f'exit {proc.returncode}: {(proc.stderr or "").strip()[:500]}',
            proc.stdout,
        )

    # Parse outer envelope
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ClaudeError(
            'invalid_json', f'outer JSON parse failed: {e}', proc.stdout,
        ) from e

    if 'result' not in envelope:
        raise ClaudeError(
            'invalid_json',
            'envelope missing "result" field',
            proc.stdout,
        )

    result_text = envelope['result']
    usage = envelope.get('usage', {}) or {}
    return result_text, usage, elapsed_ms
