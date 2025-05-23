from flox import Flox, ICON_HISTORY, ICON_BROWSER, ICON_FILE

import pyperclip
import browsers

HISTORY_GLYPH = ''
DEFAULT_BROWSER = 'chrome'

def remove_duplicates(results):
    seen = set()
    unique_results = []
    for item in results:
        if item not in seen:
            unique_results.append(item)
            seen.add(item)
    return unique_results

class BrowserHistory(Flox):

    def __init__(self):
        super().__init__()
        self.default_browser = self.settings.get('default_browser', DEFAULT_BROWSER)
        self.custom_profile_path = self.settings.get('custom_profile_path', '')
        self.browser = browsers.get(self.default_browser.lower(), self.custom_profile_path)

    def _query(self, query):
        try:
            self.query(query)
        except FileNotFoundError:
            self.add_item(
                title='History not found!',
                subtitle='Check your logs for more information.',
            )
        finally:
            return self._results

    def query(self, query):
        history = self.browser.history(limit=10000)
        for idx, item in enumerate(history):
            if query.lower() in item.title.lower() or query.lower() in item.url.lower():
                subtitle = f"{idx}. {item.url}"
                self.add_item(
                    title=item.title,
                    subtitle=subtitle,
                    icon=ICON_HISTORY,
                    glyph=HISTORY_GLYPH,
                    method=self.browser_open,
                    parameters=[item.url],
                    context=[item.title, item.url]
                )

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

if __name__ == "__main__":
    BrowserHistory().run()
