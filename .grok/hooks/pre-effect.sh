# Grok hooks for agent supervision (borrowed/extended from .claude/.codex patterns in gemOptq)

# Example pre-approval hook
# Called before risky actions
if [ "$EFFECT" = "write:production" ]; then
  echo "Grok review required for production write"
  exit 1  # block or let Grok decide
fi
