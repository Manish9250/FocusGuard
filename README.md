# FocusGuard: The LLM-Powered Website Blocker 🛡️🧠

FocusGuard is a Python-based smart website blocker for Ubuntu that helps you stay productive. It analyzes your **Brave browser history** for the day, uses a **Large Language Model (LLM)** to identify distracting websites, and automatically blocks them if you exceed a preset distraction limit.


## ✨ Core Features

* **Intelligent Analysis**: Leverages the power of Google's Gemini (or another LLM) to understand which sites are productive versus distracting, rather than relying on a static blocklist.
* **Dynamic Blocking**: Only blocks sites *after* you've spent too much time on distracting content for the day.
* **Time-Aware**: Tracks the duration of your visits to calculate total distraction time.
* **System-Level Blocking**: Modifies the `/etc/hosts` file for robust, browser-agnostic blocking.
* **Immediate Effect**: Automatically terminates the browser process to ensure blocking rules are applied instantly.
* **Automated**: Designed to be run automatically in the background using a cron job.

---

## ⚙️ How It Works

The script follows a simple yet powerful workflow:

1.  **🔍 Extract Data**: The script safely copies your Brave browser's `History` SQLite database to avoid file-locking issues.
2.  **📊 Process History**: It queries the database to get a list of all websites you've visited today, including the title and visit duration for each.
3.  **🤖 Send to LLM**: This data is formatted and sent to an LLM with a specific prompt asking it to:
    * Calculate the total time spent on distracting sites (social media, news, entertainment, etc.).
    * Compare this total against a defined limit (e.g., 1 hour).
    * Return a list of distracting domains *only if* the limit is breached.
4.  **📝 Update Hosts File**: If the LLM returns a list of sites, the script adds them to your `/etc/hosts` file, redirecting them to `127.0.0.1`.
5.  **💥 Enforce Rules**: Finally, it kills the Brave browser process, forcing it to recognize the new `hosts` file rules upon restart.

---

## 🚀 Getting Started

Follow these steps to get FocusGuard up and running on your system.

### Prerequisites

* **OS**: An Ubuntu-based Linux distribution.
* **Python**: Python 3.8 or newer.
* **Browser**: Brave Browser.
* **API Key**: A Google AI API key for the Gemini model. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Manish9250/FocusGuard.git](https://github.com/your-username/FocusGuard.git)
    cd FocusGuard
    ```

2.  **Install Python dependencies:**
    *(Create a `requirements.txt` file with the following content:)*
    ```
    google-generativeai
    pandas
    ```
    *Then run:*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API Key:**
    It's crucial to set your API key as an environment variable rather than hardcoding it.
    ```bash
    export GOOGLE_API_KEY='YOUR_API_KEY_HERE'
    ```
    To make this permanent, add the line above to your shell's configuration file (`~/.bashrc` or `~/.zshrc`) and then run `source ~/.bashrc` or `source ~/.zshrc`.

---

## 💻 Usage

### Manual Execution

Because the script modifies the system-level `/etc/hosts` file, you **must** run it with `sudo`.

```bash
sudo python3 main_blocker.py
