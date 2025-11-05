import re
from src.user.service import user_service

# -------- Replace with Mentions --------
def replace_with_mentions(text):
    """Replace username mentions with Discord mentions using word boundaries to avoid partial matches"""

    # Get all users from the UserService
    users = user_service.user_data.values()

    # Apply each replacement using regex with case-insensitive flag where appropriate
    for user in users:
        # Replace username
        pattern = r'\b' + re.escape(user['username']) + r'\b'
        mention = f"<@{user['discord_id']}>"
        text = re.sub(pattern, mention, text, flags=re.IGNORECASE)

        # Replace aliases
        for alias in user.get('aliases', []):
            pattern = r'\b' + re.escape(alias) + r'\b'
            text = re.sub(pattern, mention, text, flags=re.IGNORECASE)

    return text
