"""Asana enum display names for org-os (match project CF labels, not snake_case)."""

# OS Suspend Reason CF enum values (Asana UI labels)
SUSPEND_REASON_APPROVAL = "Approval"
SUSPEND_REASON_HUMAN_REVIEW = "Human Review"
SUSPEND_REASON_EXTERNAL_BLOCK = "External Block"

SUSPEND_REASONS = (
    SUSPEND_REASON_APPROVAL,
    SUSPEND_REASON_HUMAN_REVIEW,
    SUSPEND_REASON_EXTERNAL_BLOCK,
)
