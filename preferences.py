import json
import os


class Preferences:
    """Handles application preferences and configuration"""

    def __init__(self):
        self.config_file = os.path.expanduser("~") + "/.gpg_gui_config.json"
        self.defaults = {
            "last_directory": None,
            "use_key_encryption": False,
            "selected_key": None
        }
        self._preferences = self._load_preferences()

    def _load_preferences(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    prefs = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = self.defaults.copy()
                merged.update(prefs)
                return merged
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, return defaults
                return self.defaults.copy()
        return self.defaults.copy()

    def _save_preferences(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._preferences, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def load_last_directory(self):
        return self._preferences.get("last_directory")

    def save_last_directory(self, directory):
        self._preferences["last_directory"] = directory
        self._save_preferences()

    def get_use_key_encryption(self):
        return self._preferences.get("use_key_encryption", False)

    def set_use_key_encryption(self, use_key):
        self._preferences["use_key_encryption"] = bool(use_key)
        self._save_preferences()

    def get_selected_key(self):
        """Get the saved selected key (fingerprint, email) tuple"""
        key_data = self._preferences.get("selected_key")
        if key_data and isinstance(key_data, list) and len(key_data) == 2:
            return tuple(key_data)
        return None

    def set_selected_key(self, key_tuple):
        """Save the selected key (fingerprint, email) tuple"""
        if key_tuple is None:
            self._preferences["selected_key"] = None
        else:
            # Convert tuple to list for JSON serialization
            self._preferences["selected_key"] = list(key_tuple)
        self._save_preferences()
