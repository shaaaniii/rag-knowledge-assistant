# backend/pipeline/memory.py

from collections import defaultdict

# Stores conversation history per session in memory
# Structure:
# {
#   "session_abc": [
#       {"role": "user",      "content": "How many leave days?"},
#       {"role": "assistant", "content": "You get 20 days..."},
#   ]
# }
_session_store: dict = defaultdict(list)

# Max messages to remember per session
# 10 messages = 5 back and forth exchanges
MAX_HISTORY = 10


def add_to_history(session_id: str, role: str, content: str):
    """
    Adds one message to the session history.
    role is either "user" or "assistant"
    """
    _session_store[session_id].append({
        "role": role,
        "content": content
    })

    # Trim if we exceed the limit
    # list[-10:] means keep only the last 10 items
    if len(_session_store[session_id]) > MAX_HISTORY:
        _session_store[session_id] = _session_store[session_id][-MAX_HISTORY:]


def get_history(session_id: str) -> list:
    """Returns all messages for a session. Empty list if none."""
    return _session_store.get(session_id, [])


def format_history_for_prompt(session_id: str) -> str:
    """
    Formats past conversation into a string to include in the prompt.
    This helps GPT-4o understand follow-up questions like
    "what about part-time staff?" (it knows what "what" refers to)

    Example output:
    Previous conversation:
    User: How many leave days?
    Assistant: You get 20 days per year...
    """
    history = get_history(session_id)

    if not history:
        return ""

    lines = ["Previous conversation:"]
    for message in history:
        speaker = message["role"].capitalize()
        lines.append(f"{speaker}: {message['content']}")

    return "\n".join(lines)


def clear_history(session_id: str):
    """Clears all history for a session. Called on 'New Chat'."""
    if session_id in _session_store:
        del _session_store[session_id]