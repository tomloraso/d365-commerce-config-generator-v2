"""
Save and load ProjectProfile to/from JSON.
Also manages the recent profiles list stored in the user's home directory.
"""

import json
import copy
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from .profile import ProjectProfile
from .defaults import get_default_settings, SETTINGS_SCHEMA

RECENT_FILE = Path.home() / ".d365gen" / "recent.json"
MAX_RECENT = 10


def save_profile(profile: ProjectProfile, path: Path) -> None:
    data = {
        "profile_name": profile.profile_name,
        "notes": profile.notes,
        "output_directory": profile.output_directory,
        "modified": datetime.now().isoformat(),
        "settings": profile.settings,
        "accepted_cards": profile.accepted_cards,
        "selected_files": profile.selected_files,
        "stores": profile.stores,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _add_recent(str(path))


def load_profile(path: Path) -> ProjectProfile:
    data = json.loads(path.read_text(encoding="utf-8"))

    # Merge saved settings over defaults so new keys added in future versions
    # always have a value even when loading an older profile file.
    settings = get_default_settings()
    for category, values in data.get("settings", {}).items():
        if category in settings:
            settings[category].update(values)
        else:
            settings[category] = values

    profile = ProjectProfile(
        profile_name=data.get("profile_name", "Untitled Project"),
        notes=data.get("notes", ""),
        output_directory=data.get("output_directory", ""),
        settings=settings,
        accepted_cards=data.get("accepted_cards", []),
        selected_files=data.get("selected_files", []),
        stores=data.get("stores", []),
    )
    _add_recent(str(path))
    return profile


def get_recent_profiles() -> List[str]:
    if not RECENT_FILE.exists():
        return []
    try:
        return json.loads(RECENT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _add_recent(path_str: str) -> None:
    recent = get_recent_profiles()
    if path_str in recent:
        recent.remove(path_str)
    recent.insert(0, path_str)
    recent = recent[:MAX_RECENT]
    RECENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    RECENT_FILE.write_text(json.dumps(recent, indent=2), encoding="utf-8")
