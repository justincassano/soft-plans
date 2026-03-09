from app import db
from flask_login import UserMixin
from datetime import datetime
from uuid import uuid4

def uid():
    return uuid4().hex


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to activity suggestions
    activity_suggestions = db.relationship('ActivitySuggestion', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class ActivitySuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional user tracking
    
    # User input data
    time_available = db.Column(db.String(50), nullable=False)
    energy_level = db.Column(db.String(50), nullable=False)
    emotional_state = db.Column(db.String(50), nullable=False)
    desired_focus = db.Column(db.String(50), nullable=False)
    wants_affirmation = db.Column(db.Boolean, default=False)
    
    # Generated suggestion
    suggestion_text = db.Column(db.Text, nullable=False)
    completed_tasks = db.Column(db.Text)  # JSON string of completed task indices
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(128))  # Track anonymous sessions
    
    def __repr__(self):
        return f'<ActivitySuggestion {self.id}>'


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.String, primary_key=True, default=uid)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    time = db.Column(db.String)
    energy = db.Column(db.String)
    mood = db.Column(db.String)
    focus = db.Column(db.String)
    quote_text = db.Column(db.Text, nullable=True)
    quote_author = db.Column(db.String, nullable=True)
    session_id = db.Column(db.String(128))  # Track anonymous sessions

    tasks = db.relationship("Task", back_populates="entry", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Entry {self.id}>'


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.String, primary_key=True, default=uid)
    entry_id = db.Column(db.String, db.ForeignKey("entries.id"), index=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    done_at = db.Column(db.DateTime, nullable=True)
    order = db.Column(db.Integer, nullable=False, default=0)  # Maintain original order

    entry = db.relationship("Entry", back_populates="tasks")

    def __repr__(self):
        return f'<Task {self.id}: {self.text[:30]}>'


# Association table for many-to-many relationship between illustrations and tags
illustration_tags = db.Table('illustration_tags',
    db.Column('illustration_id', db.Integer, db.ForeignKey('illustration.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Illustration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.String(50), nullable=False)  # 'header', 'result_header', etc.
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with tags
    tags = db.relationship('Tag', secondary=illustration_tags, lazy='subquery',
                          backref=db.backref('illustrations', lazy=True))
    
    def __repr__(self):
        return f'<Illustration {self.filename}>'
    
    def get_score(self, user_inputs):
        """Calculate matching score based on user inputs"""
        score = 0
        
        # Default images get base score
        if self.is_default:
            score += 0.5
            
        # Score based on tag matches  
        try:
            for tag in self.tags:
                if tag.category == 'emotion' and tag.value.lower() == user_inputs.get('emotion', '').lower():
                    score += 3
                elif tag.category == 'energy' and tag.value.lower() == user_inputs.get('energy', '').lower():
                    score += 3
                elif tag.category == 'focus' and tag.value.lower() == user_inputs.get('focus', '').lower():
                    score += 2
                elif tag.category == 'time' and tag.value.lower() in user_inputs.get('time', '').lower():
                    score += 1
        except Exception:
            # Handle case where tags relationship isn't loaded
            pass
                
        return score


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # 'emotion', 'energy', 'focus', 'time'
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('category', 'value', name='_category_value_uc'),)
    
    def __repr__(self):
        return f'<Tag {self.category}:{self.value}>'