from flox import Flox, ICON_HISTORY, ICON_BROWSER, ICON_FILE
import pyperclip
import browsers

HISTORY_GLYPH = ''
DEFAULT_BROWSER = 'chrome'


class BrowserHistory(Flox):

    def __init__(self):
        super().__init__()
        self.default_browser = self.settings.get('default_browser', DEFAULT_BROWSER).lower()
        self.custom_profile_path = self.settings.get('custom_profile_path', '')
        self.profile_last_updated = self.settings.get('profile_last_updated', False)
        self.all_browsers_history = self.settings.get('all_browsers_history', False)
        self.history_limit = int(self.settings.get('history_limit', 10000))  # Default limit is 10000

        # Initialize browser(s)
        if self.all_browsers_history:
            self.browsers = [
                browsers.get(browser_name, profile_last_updated=self.profile_last_updated)
                for browser_name in browsers.CHROMIUM_PROFILE_BASES.keys() | browsers.FIREFOX_BASES.keys()
            ]

            # Include custom browsers if a custom profile path is provided
            if self.custom_profile_path:
                custom_chromium = browsers.get(
                    'custom (chromium)',
                    custom_profile_path=self.custom_profile_path,
                    profile_last_updated=self.profile_last_updated
                )
                custom_firefox = browsers.get(
                    'custom (firefox)',
                    custom_profile_path=self.custom_profile_path,
                    profile_last_updated=self.profile_last_updated
                )

                if custom_chromium:
                    self.browsers.append(custom_chromium)
                if custom_firefox:
                    self.browsers.append(custom_firefox)

            # Filter out None values (browsers with missing profiles)
            self.browsers = [browser for browser in self.browsers if browser is not None]
        else:
            self.browser = browsers.get(
                self.default_browser,
                self.custom_profile_path,
                profile_last_updated=self.profile_last_updated
            )
            if self.browser is None:
                self.add_item(
                    title='Error',
                    subtitle=f"Default browser '{self.default_browser}' not found or profile missing."
                )

    def query(self, query):
        try:
            if self.all_browsers_history:
                combined_history = self._get_combined_history(query)
                for idx, item in enumerate(combined_history):
                    self.add_item(
                        title=item.title,
                        subtitle=f"{idx + 1}. {item.url}",
                        icon=ICON_HISTORY,
                        glyph=HISTORY_GLYPH,
                        method=self.browser_open,
                        parameters=[item.url],
                        context=[item.title, item.url]
                    )
            else:
                history = self.browser.history(limit=self.history_limit)
                for idx, item in enumerate(history):
                    if query.lower() in item.title.lower() or query.lower() in item.url.lower():
                        self.add_item(
                            title=item.title,
                            subtitle=f"{idx + 1}. {item.url}",
                            icon=ICON_HISTORY,
                            glyph=HISTORY_GLYPH,
                            method=self.browser_open,
                            parameters=[item.url],
                            context=[item.title, item.url]
                        )
        except Exception as e:
            self.add_item(
                title='An error occurred',
                subtitle=str(e),
            )

    def _get_combined_history(self, query):
        """Combine histories from all browsers, deduplicate, and sort."""
        combined_history = []
        for browser in self.browsers:
            try:
                combined_history.extend(browser.history(limit=self.history_limit))
            except FileNotFoundError:
                continue  # Skip browsers with missing databases

        # Deduplicate by URL
        seen_urls = set()
        unique_history = []
        for item in combined_history:
            if item.url not in seen_urls:
                unique_history.append(item)
                seen_urls.add(item.url)

        # Sort by normalized timestamp (most recent first)
        unique_history.sort(key=lambda x: x.timestamp(), reverse=True)

        # Filter by query
        return [
            item for item in unique_history
            if query.lower() in item.title.lower() or query.lower() in item.url.lower()
        ]

    def context_menu(self, data):
        self.add_item(
            title='Open in browser',
            subtitle=data[0],
            icon=ICON_BROWSER,
            method=self.browser_open,
            parameters=[data[1]],
        )
        self.add_item(
            title='Copy to clipboard',
            subtitle=data[1],
            icon=ICON_FILE,
            method=self.copy_to_clipboard,
            parameters=[data[1]],
        )

    def copy_to_clipboard(self, data):
        pyperclip.copy(data)
        self.show_msg("Copied!", f"{data}")

    def run(self):
        """
        Entry point for Flow Launcher.
        This method is required to start the plugin.
        """
        pass  # Ensure this method exists


if __name__ == "__main__":
    BrowserHistory().run()