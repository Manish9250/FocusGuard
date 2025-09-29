import subprocess
def terminate_browser():
    """Forcefully terminates all Brave browser processes."""
    print("🔴 Terminating Brave browser to apply new blocking rules...")
    try:
        # Use 'pkill -f' to find and kill all processes matching 'brave'.
        # This is effective as browsers often have many related helper processes.
        # 'check=True' will raise an exception if the command fails.
        # 'capture_output=True' hides the command's output from our script's log.
        subprocess.run(["pkill", "-f", "brave"], check=True, capture_output=True)
        print("✅ Brave browser has been terminated.")
    except subprocess.CalledProcessError:
        # This error typically occurs if pkill doesn't find any processes,
        # which means the browser wasn't running.
        print("👍 Brave browser was not running.")
    except Exception as e:
        print(f"❌ An error occurred while trying to terminate the browser: {e}")


terminate_browser()