#!/home/manish/shared_space/manhwa_explainer/venv/bin/python3


import json
import time
import os
import subprocess
from datetime import datetime, timedelta
from llm_analysis import llm_main

# --- Configuration ---
HOSTS_FILE_PATH = '/etc/hosts'
REDIRECT_IP = '127.0.0.1'
CHECK_INTERVAL_SECONDS = 600  # 10 minutes

BLOCK_MARKER_START = "# --- FOCUSGUARD BLOCK START ---"
BLOCK_MARKER_END = "# --- FOCUSGUARD BLOCK END ---"

# --- MODIFIED STATE ---
# Now tracks the specific sites that are being blocked
BLOCK_STATE = {
    'active': False,
    'type': 'none',
    'expires_at': None,
    'sites': set()  # Using a set for efficient lookups
}

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


def load_json_data(filename):
    """Loads the analysis JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def apply_blocks(sites_to_block):
    """Creates the initial block in the hosts file."""
    print(f"Applying initial block for sites: {sites_to_block}")
    try:
        with open(HOSTS_FILE_PATH, 'a') as f:
            f.write(f"\n{BLOCK_MARKER_START}\n")
            for site in sites_to_block:
                f.write(f"{REDIRECT_IP}\t{site}\n")
                if not site.startswith('www.'):
                    f.write(f"{REDIRECT_IP}\twww.{site}\n")
            f.write(f"{BLOCK_MARKER_END}\n")
        
        print("✅ Blocks are now active.")
        # Update state with the list of blocked sites
        BLOCK_STATE['sites'] = set(sites_to_block)
        # Terminating brave
        terminate_browser()
        
    except Exception as e:
        print(f"❌ ERROR writing to hosts file: {e}")

# --- NEW FUNCTION ---
def add_sites_to_block(sites_to_add):
    """Adds new sites to an existing block in the hosts file."""
    if not sites_to_add:
        return
    print(f"Adding new sites to blocklist: {sites_to_add}")
    try:
        with open(HOSTS_FILE_PATH, 'r') as f:
            lines = f.readlines()

        # Find the end marker and insert new lines before it
        try:
            insert_index = lines.index(f"{BLOCK_MARKER_END}\n")
            for site in sites_to_add:
                lines.insert(insert_index, f"{REDIRECT_IP}\t{site}\n")
                if not site.startswith('www.'):
                    lines.insert(insert_index, f"{REDIRECT_IP}\twww.{site}\n")
        except ValueError:
            print("❌ ERROR: Could not find block markers in hosts file. Re-creating block.")
            remove_blocks()
            apply_blocks(BLOCK_STATE['sites'].union(sites_to_add))
            return

        with open(HOSTS_FILE_PATH, 'w') as f:
            f.writelines(lines)
        
        print("✅ Hosts file updated with new sites.")
        BLOCK_STATE['sites'].update(sites_to_add)
        # Terminating brave
        terminate_browser()


    except Exception as e:
        print(f"❌ ERROR updating hosts file: {e}")

def remove_blocks():
    """Removes all FocusGuard blocks from the hosts file."""
    print("Removing all active blocks...")
    try:
        with open(HOSTS_FILE_PATH, 'r') as f:
            lines = f.readlines()

        with open(HOSTS_FILE_PATH, 'w') as f:
            in_block_section = False
            for line in lines:
                if line.strip() == BLOCK_MARKER_START:
                    in_block_section = True
                    continue
                if line.strip() == BLOCK_MARKER_END:
                    in_block_section = False
                    continue
                if not in_block_section:
                    f.write(line)
        
        print("✅ Sites have been unblocked.")
        # Reset the sites in our state
        BLOCK_STATE['sites'] = set()
    
    except Exception as e:
        print(f"❌ ERROR modifying hosts file: {e}")


def main():
    """Main loop to check for analysis updates and manage blocks."""
    print("🛡️ FocusGuard Blocker started. Now with dynamic updates.")
    
    while True:
        # --- 1. Handle expired temporary blocks ---
        if BLOCK_STATE['active'] and BLOCK_STATE['type'] == 'temporary' and datetime.now() >= BLOCK_STATE['expires_at']:
            print("Temporary block has expired.")
            remove_blocks()
            BLOCK_STATE.update({'active': False, 'type': 'none', 'expires_at': None})

        # --- 2. Load the latest analysis ---
        today_str = datetime.now().strftime('%Y-%m-%d')
        analysis_filename = f"user_behaviour_{today_str}.json"

        # Generating report
        print("Generating report")
        llm_main()
        analysis = load_json_data(analysis_filename)

        if not analysis:
            if BLOCK_STATE['active']:
                print("New day detected, clearing previous day's block.")
                remove_blocks()
                BLOCK_STATE.update({'active': False, 'type': 'none', 'expires_at': None})
            
            print(f"Waiting for first analysis of the day ({analysis_filename})...")
            time.sleep(CHECK_INTERVAL_SECONDS)
            continue
        
        # --- 3. Process the analysis ---
        block_type = analysis.get('block_type', 'none')
        sites_from_llm = set(analysis.get('sites_to_block', []))

        if not BLOCK_STATE['active']:
            # If no block is active, check if we need to start one
            if block_type in ['temporary', 'permanent'] and sites_from_llm:
                apply_blocks(sites_from_llm)
                BLOCK_STATE['active'] = True
                BLOCK_STATE['type'] = block_type
                if block_type == 'temporary':
                    duration = analysis.get('temporary_block_duration_seconds', 300)
                    BLOCK_STATE['expires_at'] = datetime.now() + timedelta(seconds=duration)
                    print(f"Temporary block set for {duration} seconds.")
                else:
                    print("Permanent block set for the day.")
        else:
            # If a block IS active, check for NEW sites to add
            new_sites_to_add = sites_from_llm - BLOCK_STATE['sites']
            if new_sites_to_add:
                add_sites_to_block(new_sites_to_add)

        print(f"--- Status: Block Active ({BLOCK_STATE['type']}) on {len(BLOCK_STATE['sites'])} sites ---")
        print(f"Next check in {CHECK_INTERVAL_SECONDS // 60} minutes...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    remove_blocks()
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Script interrupted. Cleaning up...")
        remove_blocks()
        print("Cleanup complete. Exiting.")