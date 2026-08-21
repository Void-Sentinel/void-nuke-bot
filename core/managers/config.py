import json
import re

from core.config.config import LINKSERV

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?\S+"
    r"|www\.\S+"
    r"|discord\.(?:gg|com|io|me|invite)/\S+"
    r"|(?:discordapp|discord)\.com/invite/\S+",
    re.IGNORECASE,
)


class NukeConfig:
    def __init__(self, user_id, filename="data/nukeconfig.json"):
        self.user_id = str(user_id)
        self.filename = filename
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"users": {}}
        else:
            if "users" not in self.data or not isinstance(self.data["users"], dict):
                self.data["users"] = {}
        return self.data

    def _ensure_user(self):
        user = self.data["users"].get(self.user_id)
        if not isinstance(user, dict):
            user = {
                "spam_message": "",
                "channel_names": [],
                "guild_settings": {"name": "", "description": ""},
            }
            self.data["users"][self.user_id] = user
        for key in ("name", "description"):
            if key not in user["guild_settings"]:
                user["guild_settings"][key] = ""
        return user

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    @staticmethod
    def sanitize(text):
        if not text:
            return ""
        return URL_PATTERN.sub(LINKSERV, text)

    def get_spam_message(self):
        return self._ensure_user()["spam_message"]

    def set_spam_message(self, message):
        self._ensure_user()["spam_message"] = self.sanitize(message)
        self.save()
        return self.get_spam_message()

    def get_channel_names(self):
        return self._ensure_user()["channel_names"]

    def set_channel_names(self, names):
        cleaned = [self.sanitize(name) for name in names if name and name.strip()]
        self._ensure_user()["channel_names"] = cleaned[:5]
        self.save()
        return self.get_channel_names()

    def get_guild_settings(self):
        return self._ensure_user()["guild_settings"]

    def set_guild_settings(self, name, description):
        user = self._ensure_user()
        user["guild_settings"]["name"] = self.sanitize(name)
        user["guild_settings"]["description"] = self.sanitize(description)
        self.save()
        return user["guild_settings"]
