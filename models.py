from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    coins = db.Column(db.Integer, default=0)
    referral_code = db.Column(db.String(100))
    referred_by = db.Column(db.String(100))
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

class AdWatchSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_date = db.Column(db.String(20))
    ads_watched_count = db.Column(db.Integer, default=0)
    direct_ads_watched_count = db.Column(db.Integer, default=0)
