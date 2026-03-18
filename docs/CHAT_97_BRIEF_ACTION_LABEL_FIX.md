# CHAT 97: Fix Action Label + Rule Type for Max CPC Rules

**Date:** 2026-03-17
**Priority:** HIGH
**Estimated Time:** 15 minutes
**Dependencies:** None

---

## CONTEXT

Rules with `action_type = "decrease_max_cpc"` or `"increase_max_cpc"` display incorrectly:
- Rule type badge shows "Status" instead of "Bid"
- Action label shows "Decrease tROAS target by 10%" instead of "Lower Max CPC cap 10%"

---

## OBJECTIVE

Fix two things in `act_dashboard/routes/recommendations.py`. Read the file before editing.

---

## FIX 1: `_ACTION_TYPE_TO_RULE_TYPE` dict

Add missing entries (the map has `decrease_max_cpc_cap` but DB stores `decrease_max_cpc`):

```python
"decrease_max_cpc": "bid",
"increase_max_cpc": "bid",
```

---

## FIX 2: `get_action_label()` function

In the campaign section, the `bid` branch currently returns "tROAS target" for ALL bid rules. It needs to check `action_type` and return the correct label:

```python
action_type = rec.get('action_type', '')

if action_direction == 'increase':
    if rule_type == 'budget':
        return f"Increase daily budget by {action_magnitude}%"
    elif rule_type == 'bid':
        if 'max_cpc' in action_type:
            return f"Increase Max CPC cap by {action_magnitude}%"
        elif 'tcpa' in action_type or 'target_cpa' in action_type:
            return f"Increase tCPA target by {action_magnitude}%"
        else:
            return f"Increase tROAS target by {action_magnitude}%"
elif action_direction == 'decrease':
    if rule_type == 'budget':
        return f"Decrease daily budget by {action_magnitude}%"
    elif rule_type == 'bid':
        if 'max_cpc' in action_type:
            return f"Lower Max CPC cap by {action_magnitude}%"
        elif 'tcpa' in action_type or 'target_cpa' in action_type:
            return f"Decrease tCPA target by {action_magnitude}%"
        else:
            return f"Decrease tROAS target by {action_magnitude}%"
```

Apply the same action_type check pattern for the shopping entity section too.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — MODIFY

---

## REQUIREMENTS

- Read the file before editing
- Only modify `_ACTION_TYPE_TO_RULE_TYPE` and `get_action_label()`
- Do not touch any other function
- Verify by reading back both modified sections

---

## SUCCESS CRITERIA

- [ ] `_ACTION_TYPE_TO_RULE_TYPE` has entries for `decrease_max_cpc` and `increase_max_cpc`
- [ ] `get_action_label()` returns "Lower Max CPC cap by X%" for max_cpc rules
- [ ] `get_action_label()` still returns "Decrease tROAS target" for tROAS rules
- [ ] Flask starts cleanly
