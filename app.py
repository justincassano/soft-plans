import os
import logging
import uuid
import json
import re
import hashlib
import pytz
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Setup logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# OpenAI no longer used - using curated JSON suggestions only

# Load quotes
quotes = []
try:
    with open('quotes.json', 'r') as f:
        quotes = json.load(f)
    logging.info(f"Loaded {len(quotes)} quotes")
except Exception as e:
    logging.error(f"Failed to load quotes.json: {str(e)}")

# Load activity suggestions
activity_suggestions = {}
try:
    with open('Soft_Plans_Activity_Suggestions.json', 'r') as f:
        activity_suggestions = json.load(f)
    logging.info(f"Loaded activity suggestions for {len(activity_suggestions.get('suggestions', {}))} time categories")
except Exception as e:
    logging.error(f"Failed to load Soft_Plans_Activity_Suggestions.json: {str(e)}")

# Import models after db is configured
with app.app_context():
    import models
    db.create_all()



def get_curated_quote(time_available, energy_level, emotional_state, desired_focus, session_id):
    """Get a curated quote that changes with each regeneration"""
    if not quotes:
        return None
    
    # Get generation count for this session to ensure quotes change each time
    from models import Entry
    generation_count = Entry.query.filter_by(session_id=session_id).count()
    
    # Create hash input from user parameters, date, and generation count
    today = datetime.now().strftime('%Y-%m-%d')
    hash_input = f"{time_available}|{energy_level}|{emotional_state}|{desired_focus}|{today}|{generation_count}"
    
    # Generate deterministic index
    hash_object = hashlib.md5(hash_input.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    index = hash_int % len(quotes)
    
    return quotes[index]

def normalize_form_values(time_available, energy_level, emotional_state, desired_focus):
    """Normalize values to lowercase internally but keep display in title case"""
    return {
        'time': time_available,  # Keep as-is for display
        'energy': energy_level,  # Keep as-is for display
        'mood': emotional_state,  # Keep as-is for display
        'focus': desired_focus,  # Keep as-is for display
        'time_lower': time_available.lower(),
        'energy_lower': energy_level.lower(),
        'mood_lower': emotional_state.lower(), 
        'focus_lower': desired_focus.lower()
    }

def get_suggestions_from_json(time_available, energy_level, emotional_state, desired_focus):
    """Get curated activity suggestions from JSON file based on user input"""
    
    if not activity_suggestions or 'suggestions' not in activity_suggestions:
        logging.error("Activity suggestions not loaded")
        return ["No suggestions available"]
    
    # Get suggestions for the specific time category
    time_suggestions = activity_suggestions['suggestions'].get(time_available, [])
    
    if not time_suggestions:
        logging.warning(f"No suggestions found for time: {time_available}")
        return ["No suggestions available"]
    
    # Debug log what we're looking for
    logging.info(f"Looking for suggestions: time={time_available}, energy={energy_level}, mood={emotional_state}, focus={desired_focus}")
    logging.info(f"Found {len(time_suggestions)} suggestions for {time_available}")
    
    # Filter suggestions to ONLY show activities that match the selected focus
    matching_suggestions = []
    
    for suggestion in time_suggestions:
        tags = suggestion.get('tags', {})
        
        # Check if suggestion matches user's criteria
        energy_match = energy_level in tags.get('energy_level', [])
        mood_match = emotional_state in tags.get('emotional_state', [])  
        focus_match = desired_focus in tags.get('desired_focus', [])
        
        # Debug log each suggestion
        logging.info(f"Checking '{suggestion['text']}': energy={energy_match}, mood={mood_match}, focus={focus_match}")
        
        # ONLY include activities that match the selected focus
        if focus_match:
            matching_suggestions.append(suggestion['text'])
            logging.info(f"✓ Added '{suggestion['text']}' (matches focus: {desired_focus})")
        else:
            logging.info(f"✗ Skipped '{suggestion['text']}' (doesn't match focus: {desired_focus})")
    
    # If we don't have enough matching suggestions, include less strict matches
    if len(matching_suggestions) < 4:
        for suggestion in time_suggestions:
            if suggestion['text'] not in matching_suggestions:
                tags = suggestion.get('tags', {})
                # Include if any single criterion matches
                if (energy_level in tags.get('energy_level', []) or
                    emotional_state in tags.get('emotional_state', []) or
                    desired_focus in tags.get('desired_focus', [])):
                    matching_suggestions.append(suggestion['text'])
                    if len(matching_suggestions) >= 10:  # Get a good pool
                        break
    
    # If still not enough, include all suggestions for the time slot
    if len(matching_suggestions) < 4:
        matching_suggestions = [s['text'] for s in time_suggestions]
    
    # Simple selection - use all matching suggestions for now
    available_suggestions = matching_suggestions
    
    # Randomly select 4 suggestions
    import random
    selected = random.sample(available_suggestions, min(4, len(available_suggestions)))
    
    # Ensure we have exactly 4, pad with random ones if needed
    while len(selected) < 4 and len(matching_suggestions) > len(selected):
        remaining = [s for s in matching_suggestions if s not in selected]
        if remaining:
            selected.append(random.choice(remaining))
        else:
            break
    
    logging.info(f"Selected {len(selected)} suggestions from {len(matching_suggestions)} matches for {energy_level}/{emotional_state}/{desired_focus}")
    return selected

def generate_suggestion_entry(time_available, energy_level, emotional_state, desired_focus, wants_affirmation, quiet_mode):
    """Generate a suggestion and return as entry dict"""
    
    # Generate session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Get suggestions from JSON instead of OpenAI
    suggestions = get_suggestions_from_json(time_available, energy_level, emotional_state, desired_focus)
    
    # Normalize values for display
    normalized = normalize_form_values(time_available, energy_level, emotional_state, desired_focus)
    
    # Get curated quote if not in quiet mode
    quote = None if quiet_mode else get_curated_quote(time_available, energy_level, emotional_state, desired_focus, session['session_id'])
    
    # Store in new Entry/Task database structure
    from models import Entry, Task
    
    entry = Entry(
        time=time_available,
        energy=energy_level,
        mood=emotional_state,
        focus=desired_focus,
        quote_text=quote.get("text") if quote else None,
        quote_author=quote.get("author") if quote else None,
        session_id=session['session_id']
    )
    
    try:
        db.session.add(entry)
        db.session.flush()  # Get the entry ID
        
        # Add each task as a separate Task record with order preserved
        for i, task_text in enumerate(suggestions):
            task = Task(entry_id=entry.id, text=task_text, order=i)
            db.session.add(task)
        
        db.session.commit()
        logging.info(f"Stored entry with ID: {entry.id} and {len(suggestions)} tasks from JSON")
    except Exception as e:
        logging.error(f"Failed to store entry: {str(e)}")
        db.session.rollback()
        return None
    
    # Create response dict
    entry_dict = {
        "id": entry.id,
        "time": time_available,
        "energy": energy_level,
        "mood": emotional_state,
        "focus": desired_focus,
        "tasks": [{"id": task.id, "text": task.text, "done": task.done} for task in sorted(entry.tasks, key=lambda t: t.order)],
        "quote": quote,
        "quiet": quiet_mode,
        "show_illustration": energy_level.lower() in ["very low", "low"] and not quiet_mode,
        "created_at": entry.created_at
    }
    
    return entry_dict

@app.route('/', methods=['GET', 'POST'])
def index():
    entry = None
    
    if request.method == 'POST':
        # Get form data
        time_available = request.form.get('time_available')
        energy_level = request.form.get('energy_level')
        emotional_state = request.form.get('emotional_state')
        desired_focus = request.form.get('desired_focus')
        quiet_mode = request.form.get('quiet_mode') == 'yes'
        
        # Validate required fields
        if not all([time_available, energy_level, emotional_state, desired_focus]):
            flash('Please fill in all fields')
            return render_template('index.html', entry=entry)
        
        # Log regeneration attempt for debugging
        session_id = session.get('session_id')
        if session_id:
            from models import Entry
            recent_count = Entry.query.filter_by(session_id=session_id).count()
            logging.info(f"Generating suggestion #{recent_count + 1} for session {session_id[:8]}")
        
        # Generate suggestion
        entry = generate_suggestion_entry(
            time_available, energy_level, emotional_state, 
            desired_focus, False, quiet_mode  # Remove wants_affirmation parameter
        )
    
    return render_template('index.html', entry=entry)

@app.route('/history')
def history():
    from models import Entry
    from sqlalchemy.orm import joinedload
    
    # Get session entries
    session_id = session.get('session_id')
    if not session_id:
        return render_template('history.html', entries=[])
    
    # Optimized query with eager loading of tasks to avoid N+1 queries
    entries = Entry.query.options(joinedload(Entry.tasks)).filter_by(session_id=session_id).order_by(Entry.created_at.desc()).all()
    
    # Convert to entry dicts with optimized task processing
    entry_dicts = []
    for entry in entries:
        quote = None
        if entry.quote_text and entry.quote_author:
            quote = {"text": entry.quote_text, "author": entry.quote_author}
        
        # Sort tasks once and create dict in single pass
        sorted_tasks = sorted(entry.tasks, key=lambda t: t.order)
        tasks = [{"id": task.id, "text": task.text, "done": task.done} for task in sorted_tasks]
        
        # Convert UTC to Eastern Time
        est = pytz.timezone('US/Eastern')
        utc = pytz.UTC
        utc_time = utc.localize(entry.created_at) if entry.created_at.tzinfo is None else entry.created_at
        est_time = utc_time.astimezone(est)
        
        entry_dict = {
            "id": entry.id,
            "time": entry.time,
            "energy": entry.energy,
            "mood": entry.mood,
            "focus": entry.focus,
            "tasks": tasks,
            "quote": quote,
            "quiet": quote is None,  # If no quote, it was quiet mode
            "show_illustration": entry.energy.lower() in ["very low", "low"] and quote is not None,
            "created_at": est_time
        }
        entry_dicts.append(entry_dict)
    
    return render_template('history.html', entries=entry_dicts)

@app.route('/api/tasks/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """API endpoint to toggle task completion status"""
    from models import Task
    
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"ok": False, "error": "not_found"}), 404
    
    data = request.get_json()
    new_state = data.get("done") if data else None
    if not isinstance(new_state, bool):
        return jsonify({"ok": False, "error": "bad_request"}), 400
    
    task.done = new_state
    task.done_at = datetime.utcnow() if new_state else None
    
    try:
        db.session.commit()
        return jsonify({
            "ok": True, 
            "done": task.done, 
            "done_at": task.done_at.isoformat() if task.done_at else None
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to toggle task {task_id}: {str(e)}")
        return jsonify({"ok": False, "error": "database_error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)