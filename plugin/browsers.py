import os
import shutil
import sqlite3
from tempfile import gettempdir
from pathlib import Path
from datetime import datetime
import logging

log = logging.getLogger(__name__)

LOCAL_DATA = os.getenv('LOCALAPPDATA')
ROAMING = os.getenv('APPDATA')

# Paths to known browser history locations
BROWSER_PATHS = {
    'chrome': Path(LOCAL_DATA, 'Google', 'Chrome', 'User Data', 'Default', 'History'),
    'edge': Path(LOCAL_DATA, 'Microsoft', 'Edge', 'User Data', 'Default', 'History'),
    'brave': Path(LOCAL_DATA, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'History'),
    'brave nightly': Path(LOCAL_DATA, 'BraveSoftware', 'Brave-Browser-Nightly', 'User Data', 'Default', 'History'),
    'opera': Path(ROAMING, 'Opera Software', 'Opera Stable', 'Default', 'History'),
    'vivaldi': Path(LOCAL_DATA, 'Vivaldi', 'User Data', 'Default', 'History'),
    'arc': Path(LOCAL_DATA, 'Packages', 'TheBrowserCompany.Arc_ttt1ap7aakyb4', 'LocalCache', 'Local', 'Arc', 'User Data', 'Default', 'History'),
    'thorium': Path(LOCAL_DATA, 'Thorium', 'User Data', 'Default', 'History'),
    'firefox': Path(ROAMING, 'Mozilla', 'Firefox', 'Profiles'),
    'firefox nightly': Path(ROAMING, 'Mozilla', 'Firefox', 'Profiles'),
    'zen': Path(ROAMING, 'zen', 'Profiles'),
    'floorp': Path(ROAMING, 'Floorp', 'Profiles'),
}

# Constants for timestamp conversion
CHROMIUM_EPOCH_OFFSET = 11644473600  # seconds from 1601 to 1970


class Browser:
    def __init__(self, name, query, timestamp_type='chromium', custom_path=None, dynamic_profile=False, db_file='History'):
        self.name = name
        self.query = query
        self.timestamp_type = timestamp_type
        self.dynamic_profile = dynamic_profile
        self.db_file = db_file

        if custom_path:
            self.database_path = Path(custom_path)
        elif dynamic_profile:
            profile_base = BROWSER_PATHS.get(name)
            if not profile_base or not Path(profile_base).exists():
                raise FileNotFoundError(f"Profile base not found for {name}: {profile_base}")

            for profile_folder in Path(profile_base).iterdir():
                candidate_db = profile_folder / db_file
                if candidate_db.exists():
                    self.database_path = candidate_db
                    break
            else:
                raise FileNotFoundError(f"No valid profile found with {db_file} in {profile_base}")
        else:
            self.database_path = BROWSER_PATHS.get(name)

        if not self.database_path.exists():
            raise FileNotFoundError(f"Database not found for {name}: {self.database_path}")

    def _copy_database(self):
        temp_path = shutil.copy(self.database_path, gettempdir())
        self.temp_path = temp_path
        return temp_path

    def __del__(self):
        if hasattr(self, 'temp_path'):
            os.remove(self.temp_path)

    def history(self, limit=10):
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


# Queries
CHROMIUM_QUERY = 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC'
FIREFOX_QUERY = 'SELECT url, title, visit_date FROM moz_places INNER JOIN moz_historyvisits ON moz_historyvisits.place_id = moz_places.id ORDER BY visit_date DESC'

# Factory function
def get(browser_name, custom_profile_path=None):
    browser_name = browser_name.lower()
    if browser_name in ['chrome', 'edge', 'brave', 'brave nightly', 'opera', 'vivaldi', 'arc', 'thorium']:
        return Browser(browser_name, CHROMIUM_QUERY, 'chromium')
    elif browser_name in ['firefox', 'firefox nightly', 'zen', 'floorp']:
        return Browser(
            browser_name,
            FIREFOX_QUERY,
            'unix_us',
            dynamic_profile=True,
            db_file='places.sqlite'
        )
    elif browser_name == 'custom (chromium)':
        return Browser('custom', CHROMIUM_QUERY, 'chromium', custom_path=Path(custom_profile_path) / 'History')
    elif browser_name == 'custom (firefox)':
        return Browser('custom', FIREFOX_QUERY, 'unix_us', custom_path=Path(custom_profile_path) / 'places.sqlite')
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
