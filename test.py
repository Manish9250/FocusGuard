import subprocess
import os
def show_block_notification():
    """
    Opens a new Brave window as the original user to show the block page.
    """
    print("띄 Proactively showing the block page to the user...")
    try:
        # Get the original user who ran sudo
        user = "manish"
        #user = os.getenv('SUDO_USER')
        if not user:
            print("⚠️ Could not find SUDO_USER. Cannot open browser window.")
            return

        # Use subprocess.Popen to launch the browser without waiting for it to close.
        # We run this command as the original user using 'sudo -u'.
        subprocess.Popen([
            "sudo",
            "-u",
            user,
            "brave-browser",
            "--new-window",
            "https://127.0.0.1/"
        ])
    except Exception as e:
        print(f"❌ An error occurred while trying to open the browser: {e}")

show_block_notification()