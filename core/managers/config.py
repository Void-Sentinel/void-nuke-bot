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
    def __init__(self, filename="data/nukeconfig.json"):
        self.filename = filename
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {
                "spam_message": "",
                "channel_names": [],
                "guild_settings": {"name": "", "description": ""},
            }
        else:
            self._ensure_keys()
        return self.data

    def _ensure_keys(self):
        if "spam_message" not in self.data:
            self.data["spam_message"] = ""
        if "channel_names" not in self.data or not isinstance(self.data["channel_names"], list):
            self.data["channel_names"] = []
        if "guild_settings" not in self.data or not isinstance(self.data["guild_settings"], dict):
            self.data["guild_settings"] = {"name": "", "description": ""}
        for key in ("name", "description"):
            if key not in self.data["guild_settings"]:
                self.data["guild_settings"][key] = ""

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    @staticmethod
    def sanitize(text):
        if not text:
            return ""
        return URL_PATTERN.sub(LINKSERV, text)

    def get_spam_message(self):
        return self.data["spam_message"]

    def set_spam_message(self, message):
        self.data["spam_message"] = self.sanitize(message)
        self.save()
        return self.data["spam_message"]

    def get_channel_names(self):
        return self.data["channel_names"]

    def set_channel_names(self, names):
        cleaned = [self.sanitize(name) for name in names if name and name.strip()]
        self.data["channel_names"] = cleaned[:5]
        self.save()
        return self.data["channel_names"]

    def get_guild_settings(self):
        return self.data["guild_settings"]

    def set_guild_settings(self, name, description):
        self.data["guild_settings"]["name"] = self.sanitize(name)
        self.data["guild_settings"]["description"] = self.sanitize(description)
        self.save()
        return self.data["guild_settings"]
