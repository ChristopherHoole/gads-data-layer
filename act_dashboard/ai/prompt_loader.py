"""Read prompt files at request time (hot-reload during MVP).

Simple {{var}} placeholder substitution. Missing keys raise KeyError so
that missing-context bugs surface here, not in Claude's confused output.
"""
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROMPTS_DIR = os.path.join(_HERE, 'prompts')

_PLACEHOLDER_RE = re.compile(r'\{\{(\w+)\}\}')


def load_prompt(filename: str) -> str:
    """Read a prompt file from act_dashboard/ai/prompts/. No cache — every
    call hits disk so prompt edits during MVP take effect on the next
    request without a Flask restart."""
    path = os.path.join(_PROMPTS_DIR, filename)
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def render(template: str, **kwargs) -> str:
    """Substitute {{var}} placeholders in `template` with values from
    kwargs. Missing keys raise KeyError so we catch missing-context bugs
    early instead of silently sending {{var}} to Claude.
    """
    def _sub(m):
        key = m.group(1)
        if key not in kwargs:
            raise KeyError(f"prompt placeholder {{{{{key}}}}} has no value")
        return str(kwargs[key])
    return _PLACEHOLDER_RE.sub(_sub, template)
