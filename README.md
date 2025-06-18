# 🌟 Browser History Plugin for Flow Launcher

The **Browser History Plugin** for Flow Launcher allows you to quickly search and access your browsing history across multiple browsers. Whether you're looking for a specific webpage or want to revisit recent sites, this plugin makes it easy to find what you need with just a few keystrokes.

## 📋 Features

- **Multi-Browser Support**: Access history from Chrome, Firefox, Edge, Brave, Opera, Vivaldi, Arc, Zen, Floorp, Thorium, Waterfox, and more.
- **Custom Profiles**: Add custom Chromium-based or Firefox-based browser profiles for personalized history retrieval.
- **Combined History**: Combine and sort history entries from all supported browsers into a single list.
- **Profile Selection**: Automatically select the most recently updated profile or manually specify one.

## 🚀 Installation

### Step 1: Install Flow Launcher
Make sure you have [Flow Launcher](https://www.flowlauncher.com/)  installed on your system. If not, download and install it from the official website.

### Step 2: Install the Plugin
1. Open Flow Launcher and go to **Settings > Plugin Store**.
2. Search for "Browser History" in the store.
3. Click **Install** to add the plugin to your Flow Launcher setup.

Alternatively, you can manually install the plugin:
1. Clone this repository or download the latest release as a `.zip` file.
2. Extract the files and place the plugin folder in your Flow Launcher plugins directory: `%AppData%\FlowLauncher\Plugins`.
3. Restart Flow Launcher to load the new plugin.

### Step 3: Configure Settings
After installation, open the plugin settings in Flow Launcher:
- Set your **default browser** or profile.
- Enable **combined history** if you want to fetch results from all browsers.

## ⚙️ Configuration

The plugin provides several settings to customize its behavior:

| Setting Name                     | Description                                                                                   | Default Value       |
|:----------------------------------|:-----------------------------------------------------------------------------------------------|:---------------------:|
| **Default Browser or Profile**   | Select the browser or profile to use by default. Choose "Specific Chromium Profile" or "Specific Firefox Profile" for custom paths. | `Chrome`            |
| **Automatically Select Profile** | When enabled, the plugin selects the most recently updated profile for browsers that support multiple profiles. | `false`             |
| **Path to Profile Folder**       | Required if you select "Chromium Profile" or "Firefox Profile." Provide the full path to the folder containing the browser's profile data. | `N/A`                 |
| **Combine History**              | When enabled, the plugin fetches and combines history from all supported browsers, including custom profiles. | `false`             |
| **History Limit**                | Set the maximum number of history entries to fetch per browser. Decrease this value if you experience slowdowns. | `10000`             |

## 🔧 Troubleshooting

### 1. Plugin Not Working
- Ensure that Flow Launcher has permission to access your browser's history database.
- Verify that the browser's profile folder exists and contains the required files (`History` for Chromium-based browsers, `places.sqlite` for Firefox).

### 2. Missing or Incorrect Results
- Check the plugin settings to ensure the correct browser or profile is selected.
- If using a custom profile, confirm that the provided path is accurate.

### 3. Slow Performance
- Reduce the **History Limit** in the settings to fetch fewer entries.
- Disable **Combine History** if you only need results from a single browser.

### 4. Errors in Logs
- If you encounter errors, check the Flow Launcher logs for details: `%AppData%\FlowLauncher\Logs`

## ❓ Reporting Issues

If you encounter any issues while using the plugin or have suggestions for improvement, please feel free to open an issue on GitHub:

1. Navigate to the **Issues** page.
2. Click **New Issue** and provide the following information:
 - A clear description of the problem or feature request.
 - Steps to reproduce the issue (if applicable).
 - Any relevant error messages or logs from Flow Launcher.

> **Note**: Before opening a new issue, please check the existing issues to see if your problem has already been reported.
