import json
from src.utils.logger import log
from colorama import Fore

class UserService:
    def __init__(self, filepath='users.json'):
        self.filepath = filepath
        self.user_data = self._load_user_data()

    def _load_user_data(self):
        # SECURITY NOTE: This file contains PII and is stored in plain text.
        # In a production environment, this data should be encrypted or stored in a secure database.
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            log(f"[WARNING] User data file not found at {self.filepath}", Fore.YELLOW)
            return {}

    def get_user_info(self, user_id):
        return self.user_data.get(str(user_id))

    def replace_aliases_with_usernames(self, text):
        for user_id, user_info in self.user_data.items():
            for alias in user_info.get('aliases', []):
                text = text.replace(alias, user_info['username'])
        return text

user_service = UserService()

def replace_aliases_with_usernames(text):
    return user_service.replace_aliases_with_usernames(text)
