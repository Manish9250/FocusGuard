import os
import json
from datetime import datetime, timezone, timedelta
import google.generativeai as genai
from brave_history import get_history_for_range

# --- Configuration ---
# It's highly recommended to set this as an environment variable
# export GOOGLE_API_KEY='YOUR_API_KEY'
API_KEY = os.getenv("GENAI_API_KEY_1")
MODEL_NAME = 'gemini-2.5-flash'


def save_json_data(data, filename):
    """Saves a dictionary to a JSON file with pretty printing."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✅ Successfully saved analysis to {filename}")
    except IOError as e:
        print(f"❌ Error saving data to {filename}: {e}")

def load_chat_history(filename):
    """Loads chat history from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty list if the file doesn't exist or is empty/corrupt
        return []

def analyze_productivity(history_data, chat_history, previous_analysis):
    """
    Analyzes browsing history using the Gemini API, maintains a chat session,
    and returns a structured JSON analysis.
    
    Args:
        history_data (list): A list of tuples containing browsing history.
        chat_history (list): The existing chat history for the session.

    Returns:
        tuple: A tuple containing (analysis_dict, updated_history_list).
               Returns (None, chat_history) on failure.
    """
    if not API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set.")
        return None, chat_history
    
    genai.configure(api_key=API_KEY)

    # If no previous analysis exists (first run of the day), create a default structure.
    if previous_analysis is None:
        previous_analysis = {
            "datetime_utc": "N/A", "total_active_time_minutes": 0,
            "productivity_score_percent": 100,
            "time_by_category": {"Productive": 0, "Neutral": 0, "Distracting": 0},
            "sites_by_duration": [], "sites_to_block": [], "block_type": "none",
            "temporary_block_duration_seconds": 0
        }

    # Format the history data for the prompt
    formatted_history = "\n".join(
        [f"- Visited '{t}' ({u}) for {d} seconds at {ts.strftime('%H:%M:%S')}" for u, t, d, ts in history_data]
    )
    previous_analysis_str = json.dumps(previous_analysis, indent=2)

    # The detailed prompt instructing the LLM on its task, logic, and output format
    prompt = f"""
    You are a sophisticated productivity analyst. Your task is to analyze the user's recent web browsing activity and provide a detailed report in a specific JSON format. Maintain the context from our previous interactions.

    **Current Date:** {datetime.now()}
    **Permitted Daily Distraction Time:** 1 hour (3600 seconds)

    **Analysis Rules & Blocking Logic:**
    1.  **Analyze Activity:** Categorize each entry as 'Productive' (e.g., work, learning), 'Neutral' (e.g., search engines, news), or 'Distracting' (e.g., social media, entertainment, videos).
    2.  **Temporary Block:** If you detect a 'Distracting' activity lasting for approximately 10 minutes (600 seconds) or more, trigger a temporary block. The goal is a short "cool-down" period.
    3.  **Permanent Block:** If the CUMULATIVE 'Distracting' time for the entire day (based on our full conversation history) exceeds the 1-hour limit, trigger a permanent block for the rest of the day.
    4.  **No Block:** If neither of the above conditions is met, no block is necessary.

    **JSON Output Specification:**
    Based on your analysis, provide a response ONLY in the following JSON format. Do not include any text, explanations, or markdown formatting outside of the JSON object itself.

    {{
        "datetime_utc": "<string_iso_format>",
        "total_active_time_minutes": <integer>,
        "productivity_score_percent": <integer>,
        "time_by_category": {{
            "Productive": <integer_minutes>,
            "Neutral": <integer_minutes>,
            "Distracting": <integer_minutes>
        }},
        "sites_by_duration": [
            {{ "site": "www.basedomain.com", "duration_minutes": <integer> }}
        ],
        "sites_to_block": [
            "www.youtube.com",
            "www.instagram.com"
        ],
        "block_type": "<'none', 'temporary', or 'permanent'>",
        "temporary_block_duration_seconds": <integer>
    }}

    **Field Instructions:**
    - `sites_to_block`: List the base domains (e.g., www.youtube.com) of distracting sites. This list should be populated if `block_type` is 'temporary' or 'permanent'.
    - `block_type`: Set to 'temporary' for a short block, 'permanent' for the rest of the day, or 'none'.
    - `temporary_block_duration_seconds`: If `block_type` is 'temporary', suggest a duration in seconds (e.g., 300 or 600). If `block_type` is 'permanent' or 'none', set this to 0.

    Note: Don't block  permanently if distraction time is less than 1 hour 
    
    <previous analysis>
    {previous_analysis_str}
    </previous analysis>

    Note: Compare the distraction time from previous analysis and this updated history, And if you see the user is continuously distracted like distration time increased from 10 mintues to 20 mintues then block temporaryly and block the site for every 10 mintues distraction.

    <updated_complete_history>
    {formatted_history}
    </updated_complete_history?


    Mistakes that you make:
    1. you add the previous analysis time duration along with the updated history, which is wrong, as i provide you full history of the day everytime.
    2. store all the duration in mintues.
   """

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Start a chat session with the loaded history
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt)

        # Clean the response to extract only the JSON
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        analysis_result = json.loads(json_text)
        
        # Return the parsed dictionary and the updated chat history
        return analysis_result, chat.history

    except Exception as e:
        print(f"❌ An error occurred with the Gemini API or JSON parsing: {e}")
        return None, chat_history


def llm_main():
    # --- This is an example of how to use the script ---
    
    # 1. Define filenames for today
    today_str = datetime.now().strftime('%Y-%m-%d')
    analysis_filename = f"user_behaviour_{today_str}.json"
    chat_history_filename = f"chat_history_{today_str}.json"
    
    previous_analysis = load_chat_history(analysis_filename)
    print("--- Previous Analysis State ---")
    print(json.dumps(previous_analysis, indent=2) if previous_analysis else "No previous analysis found for today.")
    print("\n")

    # 2. Load the chat history from the last run (if any)
    # The 'history' object is a list of structured content dictionaries
    history = load_chat_history(chat_history_filename)
    print(f"Loaded {len(history)} previous messages from the chat session.")

    # Getting brave history 
    # 1. Get the current time in your LOCAL timezone (IST)
    now_local = datetime.now().astimezone()

    # 2. Determine the start of today (midnight) in your LOCAL timezone
    start_of_today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    print("Start time: ", start_of_today_local)
    
    # 3. NOW, convert that correct local start time to UTC for the database
    start_time_utc = start_of_today_local.astimezone(timezone.utc)

    # 4. The end time is simply the current moment in UTC
    end_time_utc = datetime.now(timezone.utc)
    
    print(f"✅ Correctly fetching history for today ({now_local.strftime('%Y-%m-%d')}).")
    print(f"Querying data from {start_time_utc.isoformat()} to {end_time_utc.isoformat()}...")

    # The rest of your script follows...
    brave_history = get_history_for_range(start_time_utc, end_time_utc)

    # 4. Call the analysis function
    analysis, updated_history = analyze_productivity(brave_history, history, previous_analysis)

    # 5. Process and save the results
    if analysis:
        print("\n--- Gemini Analysis Result ---")
        #print(json.dumps(analysis, indent=2))
        
        # Save the detailed analysis and the updated chat session
        save_json_data(analysis, analysis_filename)
        
        # Convert the proprietary 'Content' objects to a serializable list of dicts
        #serializable_history = [
        #    {'role': msg.role, 'parts': [part.text for part in msg.parts]}
        #    for msg in updated_history if msg.role == "model"
        #]
        #save_json_data(serializable_history, chat_history_filename) 