import os
import shutil
import sqlite3
from tempfile import gettempdir
from pathlib import Path
from datetime import datetime

# Environment variables
LOCAL_DATA = os.getenv('LOCALAPPDATA')
ROAMING = os.getenv('APPDATA')

# Chromium profile base folders (User Data only, profile selected later)
CHROMIUM_PROFILE_BASES = {
    'chrome': Path(LOCAL_DATA, 'Google', 'Chrome', 'User Data'),
    'edge': Path(LOCAL_DATA, 'Microsoft', 'Edge', 'User Data'),
    'brave': Path(LOCAL_DATA, 'BraveSoftware', 'Brave-Browser', 'User Data'),
    'brave nightly': Path(LOCAL_DATA, 'BraveSoftware', 'Brave-Browser-Nightly', 'User Data'),
    'vivaldi': Path(LOCAL_DATA, 'Vivaldi', 'User Data'),
    'arc': Path(LOCAL_DATA, 'Packages', 'TheBrowserCompany.Arc_ttt1ap7aakyb4', 'LocalCache', 'Local', 'Arc', 'User Data'),
    'thorium': Path(LOCAL_DATA, 'Thorium', 'User Data'),
}

# Single fixed path browsers
FIXED_PATHS = {
    'opera': Path(ROAMING, 'Opera Software', 'Opera Stable', 'Default', 'History'),
}

FIREFOX_BASES = {
    'firefox': Path(ROAMING, 'Mozilla', 'Firefox', 'Profiles'),
    'firefox nightly': Path(ROAMING, 'Mozilla', 'Firefox', 'Profiles'),
    'zen': Path(ROAMING, 'zen', 'Profiles'),
    'floorp': Path(ROAMING, 'Floorp', 'Profiles'),
    'waterfox': Path(ROAMING, 'Waterfox', 'Waterfox', 'Profiles')
}

CHROMIUM_QUERY = 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC'
FIREFOX_QUERY = 'SELECT url, title, visit_date FROM moz_places INNER JOIN moz_historyvisits ON moz_historyvisits.place_id = moz_places.id ORDER BY visit_date DESC'

CHROMIUM_EPOCH_OFFSET = 11644473600


class Browser:
    def __init__(
        self, name, query, timestamp_type='chromium', custom_path=None,
        dynamic_profile=False, db_file='History', profile_last_updated=False
    ):
        self.name = name
        self.query = query
        self.timestamp_type = timestamp_type
        self.db_file = db_file

        if custom_path:
            self.database_path = Path(custom_path)

        elif name in CHROMIUM_PROFILE_BASES:
            self.database_path = self._select_chromium_profile(
                CHROMIUM_PROFILE_BASES[name], db_file, profile_last_updated
            )

        elif name in FIREFOX_BASES:
            self.database_path = self._select_firefox_profile(
                FIREFOX_BASES[name], db_file, profile_last_updated
            )

        elif name in FIXED_PATHS:
            self.database_path = FIXED_PATHS[name]

        else:
            raise ValueError(f"Unsupported browser name: {name}")

        if not self.database_path or not self.database_path.exists():
            raise FileNotFoundError(f"Database not found for {name}: {self.database_path}")

    def _select_chromium_profile(self, base: Path, db_file: str, last_updated: bool) -> Path:
        if not base.exists():
            return None

        candidates = [
            p / db_file
            for p in base.iterdir()
            if p.is_dir() and (p / db_file).exists() and (p.name == 'Default' or p.name.startswith('Profile '))
        ]

        if not candidates:
            return None

        return max(candidates, key=lambda p: p.stat().st_mtime) if last_updated else candidates[0]

    def _select_firefox_profile(self, base: Path, db_file: str, last_updated: bool) -> Path:
        if not base.exists():
            return None

        candidates = [
            p / db_file
            for p in base.iterdir()
            if p.is_dir() and (p / db_file).exists()
        ]

        if not candidates:
            return None

        return max(candidates, key=lambda p: p.stat().st_mtime) if last_updated else candidates[0]

    def _copy_database(self) -> str:
        temp_path = shutil.copy(self.database_path, gettempdir())
        self.temp_path = temp_path
        return temp_path

    def __del__(self):
        if hasattr(self, 'temp_path') and os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def history(self, limit=100):
        db_path = self._copy_database()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(f"{self.query} LIMIT {limit}")
        rows = cursor.fetchall()
        connection.close()
        return [HistoryItem(self, *row) for row in rows]

    def convert_timestamp(self, raw_time):
        if self.timestamp_type == 'chromium':
            return datetime.fromtimestamp(raw_time / 1_000_000 - CHROMIUM_EPOCH_OFFSET)
        elif self.timestamp_type == 'unix_us':
            return datetime.fromtimestamp(raw_time / 1_000_000)


class HistoryItem:
    def __init__(self, browser, url, title, last_visit_time):
        self.browser = browser
        self.url = url
        self.title = title.strip() if title else url
        self.last_visit_time = last_visit_time

    def timestamp(self):
        return self.browser.convert_timestamp(self.last_visit_time)


def get(browser_name, custom_profile_path=None, profile_last_updated=False):
    browser_name = browser_name.lower()
    profile_last_updated = bool(profile_last_updated)

    try:
        if browser_name in CHROMIUM_PROFILE_BASES or browser_name in FIXED_PATHS:
            return Browser(browser_name, CHROMIUM_QUERY, 'chromium', profile_last_updated=profile_last_updated)

        elif browser_name in FIREFOX_BASES:
            return Browser(
                browser_name,
                FIREFOX_QUERY,
                'unix_us',
                dynamic_profile=True,
                db_file='places.sqlite',
                profile_last_updated=profile_last_updated
            )

        elif browser_name == 'custom (chromium)':
            return Browser(
                'custom',
                CHROMIUM_QUERY,
                'chromium',
                custom_path=Path(custom_profile_path) / 'History'
            )

        elif browser_name == 'custom (firefox)':
            return Browser(
                'custom',
                FIREFOX_QUERY,
                'unix_us',
                custom_path=Path(custom_profile_path) / 'places.sqlite'
            )

        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

    except FileNotFoundError:
        return None  # Skip browsers with missing profiles