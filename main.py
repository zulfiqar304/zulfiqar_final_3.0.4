from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from register import register_bp
from models import db
import requests
import uuid  # Import the UUID module
from supabase_config import supabase, test_supabase_connection  # Import Supabase configuration
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'  # Change to something strong
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(register_bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:[EnergySystem7130@]@db.qwpghbpprmmhhlxjsllc.supabase.co:5432/postgres'  # Ya jo bhi URI hai
db.init_app(app)

db = SQLAlchemy(app)

# ---------------------- DATABASE MODELS ---------------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    coins = db.Column(db.Integer, default=10)
    last_login_date = db.Column(db.String(20))  # YYYY-MM-DD format
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)  # Track when user was last active
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    referral_code = db.Column(db.String(20), unique=True)  # User's unique referral code
    referred_by = db.Column(db.String(20))  # Referral code used to sign up

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer)
    service_name = db.Column(db.String(100))
    link = db.Column(db.String(300))
    quantity = db.Column(db.Integer)
    coins_required = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending')
    jap_order_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_count = db.Column(db.Integer, default=0)
    remains = db.Column(db.Integer, default=0)
    completion_time = db.Column(db.String(50))  # JAP completion time
    last_status_update = db.Column(db.DateTime, default=datetime.utcnow)

class SelectedService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, unique=True)
    service_name = db.Column(db.String(200))
    category = db.Column(db.String(100))
    rate = db.Column(db.Float)
    min_quantity = db.Column(db.Integer)
    max_quantity = db.Column(db.Integer)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CoinConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String(100), unique=True, nullable=False)
    coin_value = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class CoinTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_type = db.Column(db.String(50))  # 'login_bonus', 'ad_reward', 'order_payment', 'admin_adjustment'
    amount = db.Column(db.Integer)  # positive for credit, negative for debit
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdWatchSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_date = db.Column(db.String(20))  # YYYY-MM-DD format
    ads_watched_count = db.Column(db.Integer, default=0)
    direct_ads_watched_count = db.Column(db.Integer, default=0)  # Separate counter for direct ads
    last_ad_time = db.Column(db.DateTime)
    last_direct_ad_time = db.Column(db.DateTime)
    cooldown_until = db.Column(db.DateTime)
    direct_cooldown_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    highlight_text = db.Column(db.String(200), default='')
    show_on_home = db.Column(db.Boolean, default=False)
    show_on_dashboard = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    background_color = db.Column(db.String(50), default='gradient-bg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))  # Store IP Address
    user_agent = db.Column(db.String(500))  # Store User Agent

class SpinWheel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    spin_date = db.Column(db.String(20))  # YYYY-MM-DD format
    reward_type = db.Column(db.String(50))  # 'coins', 'extra_spin', 'no_reward'
    reward_amount = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserReferral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # User who referred
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # User who was referred
    referral_code = db.Column(db.String(20), nullable=False)  # Unique referral code
    domain_used = db.Column(db.String(100))  # Domain used for referral
    is_qualified = db.Column(db.Boolean, default=False)  # Has referred user earned at least 1 coin?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    qualified_at = db.Column(db.DateTime)  # When they became qualified

class ReferralReward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reward_date = db.Column(db.String(20))  # YYYY-MM-DD format
    referral_count = db.Column(db.Integer)  # Number of referrals when reward was given
    spins_awarded = db.Column(db.Integer, default=3)
    spins_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DeviceRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    device_id = db.Column(db.String(100), nullable=False)  # IMEI or device fingerprint
    browser_fingerprint = db.Column(db.String(200))  # Browser fingerprint
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    is_primary = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdminSpinGrant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    spins_granted = db.Column(db.Integer, default=1)
    reason = db.Column(db.String(200))  # e.g., 'Loyal User Reward'
    grant_date = db.Column(db.String(20))  # YYYY-MM-DD format
    spins_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PageVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    device_id = db.Column(db.String(100), nullable=False)  # IMEI or device fingerprint
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    visit_start = db.Column(db.DateTime, default=datetime.utcnow)
    visit_end = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)
    is_qualified = db.Column(db.Boolean, default=False)
    referral_code = db.Column(db.String(20)) # Track referral code used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HomePageContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_type = db.Column(db.String(50), nullable=False)  # 'hero', 'feature', 'offer'
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(300))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    button_text = db.Column(db.String(100))
    button_link = db.Column(db.String(300))
    background_color = db.Column(db.String(50), default='bg-white')
    text_color = db.Column(db.String(50), default='text-gray-900')
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class CoinPurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_id = db.Column(db.String(100), nullable=False, unique=True)
    amount_pkr = db.Column(db.Float, nullable=False)
    coins_requested = db.Column(db.Integer, nullable=False)
    coins_awarded = db.Column(db.Integer, default=0)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ApkFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    download_count = db.Column(db.Integer, default=0)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'technical', 'billing', 'account', 'general'
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'resolved', 'closed'
    admin_notes = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who handled the ticket
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------- JAP API CONFIGURATION ---------------------- #
JAP_API_URL = "https://justanotherpanel.com/api/v2"
JAP_API_KEY = "c88871268f8d5276927ff8c09fceb422"

def get_jap_api_key():
    """Get JAP API key from configuration"""
    config = CoinConfiguration.query.filter_by(config_name='jap_api_key', is_active=True).first()
    return config.description if config else JAP_API_KEY

def get_jap_api_url():
    """Get JAP API URL from configuration"""
    config = CoinConfiguration.query.filter_by(config_name='jap_api_url', is_active=True).first()
    return config.description if config else JAP_API_URL

def get_jap_services():
    """Fetch services from JAP API"""
    try:
        api_url = get_jap_api_url()
        api_key = get_jap_api_key()
        response = requests.post(api_url, data={
            'key': api_key,
            'action': 'services'
        })
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching services: {e}")
        return []

def place_jap_order(service_id, link, quantity):
    """Place order through JAP API"""
    try:
        api_url = get_jap_api_url()
        api_key = get_jap_api_key()
        response = requests.post(api_url, data={
            'key': api_key,
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        })
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error placing order: {e}")
        return None

def get_jap_order_status(order_id):
    """Get order status from JAP API"""
    try:
        api_url = get_jap_api_url()
        api_key = get_jap_api_key()
        response = requests.post(api_url, data={
            'key': api_key,
            'action': 'status',
            'order': order_id
        })
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting order status: {e}")
        return None

def update_order_from_jap(order):
    """Update order details from JAP API"""
    if not order.jap_order_id:
        return False

    jap_status = get_jap_order_status(order.jap_order_id)
    if not jap_status:
        return False

    # Map JAP status to our status
    status_mapping = {
        'Pending': 'Pending',
        'In progress': 'Processing', 
        'Processing': 'Processing',
        'Partial': 'Partial',
        'Completed': 'Completed',
        'Canceled': 'Cancelled'
    }

    jap_order_status = jap_status.get('status', 'Unknown')
    new_status = status_mapping.get(jap_order_status, jap_order_status)

    # Update order details
    order.status = new_status
    order.start_count = jap_status.get('start_count', order.start_count)
    order.remains = jap_status.get('remains', order.remains)

    # Set completion time if completed
    if new_status == 'Completed' and not order.completion_time:
        order.completion_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    order.last_status_update = datetime.utcnow()

    try:
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating order: {e}")
        db.session.rollback()
        return False

# ---------------------- HELPER FUNCTIONS ---------------------- #
def update_user_activity(user_id):
    """Update user's last activity timestamp"""
    try:
        user = User.query.get(user_id)
        if user:
            user.last_activity = datetime.utcnow()
            db.session.commit()
    except:
        pass

def get_online_users_count():
    """Get count of users who were active in the last 5 minutes"""
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    return User.query.filter(User.last_activity >= five_minutes_ago, User.is_banned == False).count()

def get_user_level(user_id):
    """Calculate user level based on completed orders"""
    completed_orders = Order.query.filter_by(user_id=user_id, status='Completed').count()

    if completed_orders >= 50:
        return {"level": "Expert", "name": "Expert", "orders": completed_orders, "next_level": None, "orders_needed": 0}
    elif completed_orders >= 10:
        return {"level": "Professional", "name": "Professional", "orders": completed_orders, "next_level": "Expert", "orders_needed": 50 - completed_orders}
    else:
        return {"level": "Beginner", "name": "Beginner", "orders": completed_orders, "next_level": "Professional", "orders_needed": 10 - completed_orders}

def generate_referral_code(username):
    """Generate a unique referral code for user"""
    import string
    import random

    # Use first 3 letters of username + 5 random characters
    prefix = username[:3].upper()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return prefix + suffix

def get_current_domain(request):
    """Get current domain from request"""
    return request.host

def check_and_award_referral_bonus(user_id):
    """Check if user qualifies for referral bonus and award spins"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if user already got bonus today
    existing_reward = ReferralReward.query.filter_by(user_id=user_id, reward_date=today).first()
    if existing_reward:
        return False

    # Count qualified referrals (based on page visit duration, not coin earning)
    qualified_referrals = UserReferral.query.filter_by(referrer_id=user_id, is_qualified=True).count()

    # Check if user has 10 or more qualified referrals and hasn't received reward for this count
    if qualified_referrals >= 10:
        # Check if they already got reward for this referral count
        existing_for_count = ReferralReward.query.filter_by(user_id=user_id, referral_count=qualified_referrals).first()
        if not existing_for_count:
            # Award 3 free spins
            reward = ReferralReward(
                user_id=user_id,
                reward_date=today,
                referral_count=qualified_referrals,
                spins_awarded=3,
                spins_used=0
            )
            db.session.add(reward)
            db.session.commit()
            return True

    return False

class AdConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_type = db.Column(db.String(50), nullable=False)  # 'advanced_ad', 'direct_ad'
    ad_code = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Ad network name
    ad_url = db.Column(db.String(500), nullable=False)  # Direct ad URL
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class MultipleAdConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_type = db.Column(db.String(50), nullable=False)  # 'watch_ad_1', 'watch_ad_2'
    ad_name = db.Column(db.String(100), nullable=False)  # Display name like "Propeller Ads"
    ad_code = db.Column(db.Text, nullable=False)  # HTML/JS code
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

def check_page_visit_qualification(user_id, device_id):
    """Check if page visit qualifies for referral (2+ minutes)"""
    visit = PageVisit.query.filter_by(user_id=user_id, device_id=device_id, is_qualified=False).first()
    if visit and visit.duration_seconds >= 120:  # 2 minutes = 120 seconds
        visit.is_qualified = True

        # Qualify the referral if exists
        referral = UserReferral.query.filter_by(referred_id=user_id, is_qualified=False).first()
        if referral:
            referral.is_qualified = True
            referral.qualified_at = datetime.utcnow()

            # Check if referrer should get bonus
            check_and_award_referral_bonus(referral.referrer_id)

        db.session.commit()
        return True
    return False

def get_available_referral_spins(user_id):
    """Get number of available referral spins for user"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Get today's referral reward
    today_reward = ReferralReward.query.filter_by(user_id=user_id, reward_date=today).first()
    if today_reward:
        return today_reward.spins_awarded - today_reward.spins_used

    return 0

def use_referral_spin(user_id):
    """Use one referral spin"""
    today = datetime.now().strftime('%Y-%m-%d')

    today_reward = ReferralReward.query.filter_by(user_id=user_id, reward_date=today).first()
    if today_reward and today_reward.spins_used < today_reward.spins_awarded:
        today_reward.spins_used += 1
        db.session.commit()
        return True

    return False

def get_available_admin_spins(user_id):
    """Get number of available admin-granted spins for user"""
    today = datetime.now().strftime('%Y-%m-%d')

    today_grants = AdminSpinGrant.query.filter_by(user_id=user_id, grant_date=today).all()
    total_granted = sum(grant.spins_granted for grant in today_grants)
    total_used = sum(grant.spins_used for grant in today_grants)

    return total_granted - total_used

def sync_user_data_to_supabase(user_id):
    """Sync user activity data to Supabase for analytics"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False
            
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            ad_session = AdWatchSession.query.filter_by(user_id=user_id, session_date=today).first()
            ads_watched_today = ad_session.ads_watched_count if ad_session else 0
            # Handle potential missing column
            try:
                direct_ads_watched_today = ad_session.direct_ads_watched_count if ad_session else 0
            except AttributeError:
                direct_ads_watched_today = 0
        except Exception:
            ads_watched_today = 0
            direct_ads_watched_today = 0
        
        # Prepare data for Supabase
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'coins': user.coins,
            'last_activity': user.last_activity.isoformat() if user.last_activity else None,
            'ads_watched_today': ads_watched_today,
            'direct_ads_watched_today': direct_ads_watched_today,
            'is_online': (datetime.utcnow() - user.last_activity).total_seconds() <= 300 if user.last_activity else False,
            'sync_timestamp': datetime.utcnow().isoformat()
        }
        
        # Upsert to Supabase
        result = supabase.table('user_activity').upsert(user_data, on_conflict='user_id').execute()
        return True
        
    except Exception as e:
        print(f"Error syncing to Supabase: {e}")
        return False

def get_coin_purchase_rate():
    """Get PKR to coins conversion rate"""
    config = CoinConfiguration.query.filter_by(config_name='pkr_to_coins_rate', is_active=True).first()
    return config.coin_value if config else 2  # Default 2 PKR = 1 Coin

def get_easypaisa_account_name():
    """Get EasyPaisa account name"""
    config = CoinConfiguration.query.filter_by(config_name='easypaisa_account_name', is_active=True).first()
    return config.description if config else 'Zulfiqar Ali'  # Default name

def get_easypaisa_account_number():
    """Get EasyPaisa account number"""
    config = CoinConfiguration.query.filter_by(config_name='easypaisa_account_number', is_active=True).first()
    return config.description if config else '+92-343-3662304'  # Default number

def use_admin_spin(user_id):
    """Use one admin-granted spin"""
    today = datetime.now().strftime('%Y-%m-%d')

    grants = AdminSpinGrant.query.filter_by(user_id=user_id, grant_date=today).all()
    for grant in grants:
        if grant.spins_used < grant.spins_granted:
            grant.spins_used += 1
            db.session.commit()
            return True

    return False

def grant_admin_spin(user_id, admin_id, spins=1, reason="Admin Grant"):
    """Grant spins to user by admin"""
    today = datetime.now().strftime('%Y-%m-%d')

    grant = AdminSpinGrant(
        user_id=user_id,
        admin_id=admin_id,
        spins_granted=spins,
        reason=reason,
        grant_date=today
    )
    db.session.add(grant)
    db.session.commit()
    return True

# ---------------------- ACTIVITY TRACKING ---------------------- #
@app.before_request
def track_user_activity():
    """Track user activity on every request"""
    if 'user_id' in session:
        update_user_activity(session['user_id'])

# ---------------------- CONTEXT PROCESSORS ---------------------- #
@app.context_processor
def inject_global_announcements():
    """Make announcements available globally in templates"""
    try:
        global_announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).all()
        return dict(global_announcements=global_announcements)
    except:
        return dict(global_announcements=[])

# ---------------------- ROUTES ---------------------- #
@app.route('/')
def home():
    # Get active announcements for home page
    announcements = Announcement.query.filter_by(is_active=True, show_on_home=True).order_by(Announcement.created_at.desc()).all()

    # Get dynamic home page content
    hero_content = HomePageContent.query.filter_by(section_type='hero', is_active=True).order_by(HomePageContent.display_order).all()
    feature_content = HomePageContent.query.filter_by(section_type='feature', is_active=True).order_by(HomePageContent.display_order).all()
    offer_content = HomePageContent.query.filter_by(section_type='offer', is_active=True).order_by(HomePageContent.display_order).all()

    return render_template('home.html', 
                         announcements=announcements,


hero_content=hero_content,
                         feature_content=feature_content,
                         offer_content=offer_content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    referral_code = request.args.get('ref', '').strip()

    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        referral_input = request.form.get('referral', '').strip()

        if not username or not email or not password:
            flash('Please fill in all fields.')
            return redirect(url_for('register', ref=referral_code))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register', ref=referral_code))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('register', ref=referral_code))

        # Generate unique referral code for new user
        user_referral_code = generate_referral_code(username)
        while User.query.filter_by(referral_code=user_referral_code).first():
            user_referral_code = generate_referral_code(username)

        hashed_password = generate_password_hash(password)

        # Use referral code from URL or form input
        used_referral = referral_input or referral_code

        # Get registration bonus from configuration
        registration_bonus_config = CoinConfiguration.query.filter_by(config_name='registration_bonus', is_active=True).first()
        registration_bonus = registration_bonus_config.coin_value if registration_bonus_config else 5

        new_user = User(
            username=username, 
            email=email, 
            password=hashed_password,
            coins=registration_bonus,  # Give registration bonus instead of default 10
            referral_code=user_referral_code,
            referred_by=used_referral if used_referral else None
        )
        sync_user_data_to_supabase(new_user.id)
        db.session.add(new_user)
        db.session.commit()

        # Record registration bonus transaction
        reg_transaction = CoinTransaction(
            user_id=new_user.id,
            transaction_type='registration_bonus',
            amount=registration_bonus,
            description=f'Welcome bonus for new registration'
        )
        db.session.add(reg_transaction)

        # Register device
        device_id = request.form.get('device_id', '')
        if not device_id:
            # Generate browser fingerprint as fallback
            import hashlib
            user_agent = request.headers.get('User-Agent', '')
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            device_id = hashlib.md5(f"{user_agent}{ip_address}".encode()).hexdigest()

        # Check if device is already used by another user
        existing_device = DeviceRegistration.query.filter_by(device_id=device_id).first()
        device_already_used = existing_device is not None

        # Register device for new user
        device_registration = DeviceRegistration(
            user_id=new_user.id,
            device_id=device_id,
            browser_fingerprint=device_id,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR')),
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(device_registration)

        # If user was referred, create referral record (only if new device)
        if used_referral and not device_already_used:
            referrer = User.query.filter_by(referral_code=used_referral).first()
            if referrer:
                referral_record = UserReferral(
                    referrer_id=referrer.id,
                    referred_id=new_user.id,
                    referral_code=used_referral,
                    domain_used=get_current_domain(request),
                    is_qualified=False
                )
                db.session.add(referral_record)

        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', referral=referral_code)
sync_user_data_to_supabase(new_user.id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.is_banned:
                flash('Your account has been banned. Please contact support.')
                return render_template('login.html')

            today = datetime.now().strftime("%Y-%m-%d")
            if user.last_login_date != today:
                # Get daily login bonus from configuration
                login_bonus_config = CoinConfiguration.query.filter_by(config_name='daily_login_bonus', is_active=True).first()
                login_bonus = login_bonus_config.coin_value if login_bonus_config else 5

                user.coins += login_bonus
                user.last_login_date = today

                # Record transaction
                transaction = CoinTransaction(
                    user_id=user.id,
                    transaction_type='login_bonus',
                    amount=login_bonus,
                    description=f'Daily login bonus'
                )
                db.session.add(transaction)
                db.session.commit()

            session['user_id'] = user.id
            # Do not set is_admin flag in regular login
            flash(f'Welcome back, {user.username}!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate secure reset token
            reset_token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

            # Get user's IP and user agent for security tracking
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            user_agent = request.headers.get('User-Agent', '')[:500]

            # Create reset token record
            reset_record = PasswordResetToken(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )

            db.session.add(reset_record)
            db.session.commit()

            # In a real application, you would send an email here
            # For this demo, we'll show the reset link on the page
            reset_url = url_for('reset_password', token=reset_token, _external=True)
            flash(f'Password reset link generated: {reset_url}')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a password reset link has been sent.')

        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_record = PasswordResetToken.query.filter_by(token=token, is_used=False).first()

    if not reset_record or reset_record.expires_at < datetime.utcnow():
        flash('Invalid or expired reset token.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters long.')
            return render_template('reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return render_template('reset_password.html', token=token)

        # Update user password
        user = User.query.get(reset_record.user_id)
        user.password = generate_password_hash(new_password)

        # Mark token as used
        reset_record.is_used = True

        db.session.commit()

        flash('Password successfully reset! Please login with your new password.')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access dashboard.')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    # Get user level information
    user_level_info = get_user_level(user.id)

    # Get active announcements for dashboard
    announcements = Announcement.query.filter_by(is_active=True, show_on_dashboard=True).order_by(Announcement.created_at.desc()).all()

    # Get referral stats
    qualified_referrals = UserReferral.query.filter_by(referrer_id=user.id, is_qualified=True).count()
    available_spins = get_available_referral_spins(user.id)

    referral_stats = {
        'qualified': qualified_referrals,
        'remaining_for_bonus': max(0, 10 - qualified_referrals),
        'available_spins': available_spins
    }

    return render_template('dashboard.html', user=user, user_level=user_level_info, announcements=announcements, referral_stats=referral_stats)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin_logged_in', None)  # Also clear admin session
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/api/services')
def api_services():
    """API endpoint to get selected services only"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get only selected and active services from database
    selected_services = SelectedService.query.filter_by(is_active=True).all()

    services_list = []
    for service in selected_services:
        services_list.append({
            'service': service.service_id,
            'name': service.service_name,
            'category': service.category,
            'rate': service.rate,
            'min': service.min_quantity,
            'max': service.max_quantity,
            'description': service.description
        })

    return jsonify(services_list)

@app.route('/place-order', methods=['GET', 'POST'])
def place_order():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        service_id = request.form.get('service_id')
        service_name = request.form.get('service_name')
        service_rate = request.form.get('service_rate')
        link = request.form.get('link').strip()
        quantity_str = request.form.get('quantity')

        # Validate inputs
        if not service_id or not link or not quantity_str:
            flash('Please fill all fields.')
            return redirect(url_for('place_order'))

        try:
            quantity = int(quantity_str)
            service_rate_float = float(service_rate)
            if quantity <= 0:
                flash('Quantity must be a positive number.')
                return redirect(url_for('place_order'))
        except ValueError:
            flash('Invalid quantity or service rate.')
            return redirect(url_for('place_order'))

        # Get service from our database to use our custom rate
        selected_service = SelectedService.query.filter_by(service_id=int(service_id)).first()
        if not selected_service:
            flash('Service not found in our system.')
            return redirect(url_for('place_order'))

        # Use our custom rate (already in coins per 1000)
        cost = int((quantity / 1000.0) * selected_service.rate)
        if user.coins < cost:
            flash('Insufficient coins to place this order.')
            return redirect(url_for('place_order'))

        # Place order through JAP API
        jap_response = place_jap_order(service_id, link, quantity)
        if not jap_response or 'order' not in jap_response:
            flash('Failed to place order. Please try again.')
            return redirect(url_for('place_order'))

        # Save order to database and deduct coins
        new_order = Order(
            user_id=user.id,
            service_id=int(service_id),
            service_name=service_name,
            link=link,
            quantity=quantity,
            coins_required=cost,
            status='Processing',
            jap_order_id=jap_response['order']
        )
        user.coins -= cost

        # Record transaction
        transaction = CoinTransaction(
            user_id=user.id,
            transaction_type='order_payment',
            amount=-cost,
            description=f'Order payment for {service_name}'
        )

        db.session.add(new_order)
        db.session.add(transaction)
        db.session.commit()

        flash(f'Order placed successfully! JAP Order ID: {jap_response["order"]}')
        return redirect(url_for('order_history'))

    return render_template('place_order.html', user=user)

@app.route('/order-history')
def order_history():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()

    # Auto-update pending/processing orders from JAP API
    for order in orders:
        if order.status in ['Pending', 'Processing', 'Partial'] and order.jap_order_id:
            # Only update if last update was more than 5 minutes ago
            if not order.last_status_update or (datetime.utcnow() - order.last_status_update).total_seconds() > 300:
                update_order_from_jap(order)

    return render_template('order_history.html', user=user, orders=orders)

@app.route('/watch-ad')
def watch_ad():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))
    return render_template('watch_ad.html', user=user)

@app.route('/watch-direct-ad')
def watch_direct_ad():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))
    return render_template('watch_direct_ad.html', user=user)

@app.route('/start-ad-session', methods=['POST'])
def start_ad_session():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    today = datetime.now().strftime('%Y-%m-%d')

    # Get or create today's ad session
    ad_session = AdWatchSession.query.filter_by(
        user_id=user.id, 
        session_date=today
    ).first()

    if not ad_session:
        ad_session = AdWatchSession(
            user_id=user.id,
            session_date=today,
            ads_watched_count=0
        )
        db.session.add(ad_session)
        db.session.commit()

    # Check if user is in cooldown
    if ad_session.cooldown_until and datetime.utcnow() < ad_session.cooldown_until:
        remaining_time = int((ad_session.cooldown_until - datetime.utcnow()).total_seconds())
        return jsonify({
            'success': False, 
            'message': 'You are in cooldown period.',
            'cooldown_remaining': remaining_time
        })

    # Check daily limit (100 ads per day)
    if ad_session.ads_watched_count >= 100:
        return jsonify({
            'success': False, 
            'message': 'Daily ad limit reached (100 ads).'
        })

    # Check minimum time between ads (30 seconds)
    if ad_session.last_ad_time:
        time_since_last = datetime.utcnow() - ad_session.last_ad_time
        if time_since_last.total_seconds() < 30:
            return jsonify({
                'success': False, 
                'message': 'Please wait before watching another ad.',
                'wait_seconds': int(30 - time_since_last.total_seconds())
            })


# Ad code endpoints temporarily removed



    # Generate unique session token for this ad
    import secrets
    session_token = secrets.token_hex(16)
    session['current_ad_token'] = session_token
    session['ad_start_time'] = datetime.utcnow().isoformat()

    return jsonify({
        'success': True, 
        'session_token': session_token,
        'ads_remaining': 10 - ad_session.ads_watched_count
    })

@app.route('/start-direct-ad-session', methods=['POST'])
def start_direct_ad_session():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    today = datetime.now().strftime('%Y-%m-%d')

    # Get or create today's ad session
    ad_session = AdWatchSession.query.filter_by(
        user_id=user.id, 
        session_date=today
    ).first()

    if not ad_session:
        ad_session = AdWatchSession(
            user_id=user.id,
            session_date=today,
            ads_watched_count=0,
            direct_ads_watched_count=0
        )
        db.session.add(ad_session)
        db.session.commit()

    # Check if user is in direct ad cooldown
    if ad_session.direct_cooldown_until and datetime.utcnow() < ad_session.direct_cooldown_until:
        remaining_time = int((ad_session.direct_cooldown_until - datetime.utcnow()).total_seconds())
        return jsonify({
            'success': False, 
            'message': 'You are in cooldown period.',
            'cooldown_remaining': remaining_time
        })

    # Check daily limit for direct ads (100 ads per day)
    if ad_session.direct_ads_watched_count >= 100:
        return jsonify({
            'success': False, 
            'message': 'Daily direct ad limit reached (100 ads).'
        })

    # Check minimum time between direct ads (30 seconds)
    if ad_session.last_direct_ad_time:
        time_since_last = datetime.utcnow() - ad_session.last_direct_ad_time
        if time_since_last.total_seconds() < 30:
            return jsonify({
                'success': False, 
                'message': 'Please wait before watching another ad.',
                'wait_seconds': int(30 - time_since_last.total_seconds())
            })

    # Generate unique session token for this direct ad
    import secrets
    session_token = secrets.token_hex(16)
    session['current_direct_ad_token'] = session_token
    session['direct_ad_start_time'] = datetime.utcnow().isoformat()

    return jsonify({
        'success': True, 
        'session_token': session_token,
        'direct_ads_remaining': 100 - ad_session.direct_ads_watched_count
    })

@app.route('/api/get-ad-codes')
def api_get_ad_codes():
    """API endpoint to get current ad codes for frontend"""
    try:
        # Get current active ad configurations
        advanced_ad = AdConfiguration.query.filter_by(ad_type='advanced_ad', is_active=True).first()
        direct_ad = AdConfiguration.query.filter_by(ad_type='direct_ad', is_active=True).first()

        return jsonify({
            'success': True,
            'advanced_ad': advanced_ad.ad_code if advanced_ad else None,
            'direct_ad': direct_ad.ad_code if direct_ad else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching ad codes: {str(e)}'
        }), 500

@app.route('/api/get-random-ads')
def api_get_random_ads():
    """API endpoint to get random ads for both watch ad types"""
    try:
        import random
        
        # Get active ads for watch ad 1
        watch_ad_1_ads = MultipleAdConfig.query.filter_by(ad_type='watch_ad_1', is_active=True).all()
        watch_ad_2_ads = MultipleAdConfig.query.filter_by(ad_type='watch_ad_2', is_active=True).all()
        
        # Select random ads
        selected_ad_1 = random.choice(watch_ad_1_ads) if watch_ad_1_ads else None
        selected_ad_2 = random.choice(watch_ad_2_ads) if watch_ad_2_ads else None
        
        return jsonify({
            'success': True,
            'watch_ad_1': {
                'name': selected_ad_1.ad_name if selected_ad_1 else None,
                'code': selected_ad_1.ad_code if selected_ad_1 else None
            },
            'watch_ad_2': {
                'name': selected_ad_2.ad_name if selected_ad_2 else None,
                'code': selected_ad_2.ad_code if selected_ad_2 else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching random ads: {str(e)}'
        }), 500

@app.route('/api/get-ad-links')
def api_get_ad_links():
    """API endpoint to get active ad links for watch ad 2"""
    try:
        # Get active ad links
        ad_links = AdLink.query.filter_by(is_active=True).order_by(AdLink.display_order).all()
        
        links_data = []
        for link in ad_links:
            links_data.append({
                'id': link.id,
                'name': link.name,
                'url': link.ad_url
            })

        return jsonify({
            'success': True,
            'ad_links': links_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching ad links: {str(e)}'
        }), 500

@app.route('/complete-direct-ad-task', methods=['POST'])
def complete_direct_ad_task():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    # Verify session token
    data = request.get_json()
    if not data or data.get('session_token') != session.get('current_direct_ad_token'):
        return jsonify({'success': False, 'message': 'Invalid session token.'}), 400

    # Verify minimum watch time (40 seconds)
    direct_ad_start_time_str = session.get('direct_ad_start_time')
    if not direct_ad_start_time_str:
        return jsonify({'success': False, 'message': 'No active direct ad session.'}), 400

    direct_ad_start_time = datetime.fromisoformat(direct_ad_start_time_str)
    time_watched = (datetime.utcnow() - direct_ad_start_time).total_seconds()

    if time_watched < 35:  # Allow 5 seconds tolerance for network delays
        return jsonify({
            'success': False, 
            'message': f'Ad not watched completely. Watched: {int(time_watched)}s, Required: 40s'
        }), 400

    today = datetime.now().strftime('%Y-%m-%d')

    # Get today's ad session
    ad_session = AdWatchSession.query.filter_by(
        user_id=user.id, 
        session_date=today
    ).first()

    if not ad_session:
        return jsonify({'success': False, 'message': 'No ad session found.'}), 400

    # Double-check limits
    if ad_session.direct_ads_watched_count >= 100:
        return jsonify({'success': False, 'message': 'Daily direct ad limit already reached.'}), 400

    # Check if too soon after last ad
    if ad_session.last_direct_ad_time:
        time_since_last = datetime.utcnow() - ad_session.last_direct_ad_time
        if time_since_last.total_seconds() < 30:
            return jsonify({'success': False, 'message': 'Ads watched too quickly.'}), 400

    # Get ad reward from configuration
    ad_reward_config = CoinConfiguration.query.filter_by(config_name='direct_ad_watch_reward', is_active=True).first()
    ad_reward = ad_reward_config.coin_value if ad_reward_config else 0.5

    # Update ad session
    ad_session.direct_ads_watched_count += 1
    ad_session.last_direct_ad_time = datetime.utcnow()

    # Set 10-minute cooldown after every 10 direct ads
    if ad_session.direct_ads_watched_count % 10 == 0 and ad_session.direct_ads_watched_count > 0:
        ad_session.direct_cooldown_until = datetime.utcnow() + timedelta(minutes=10)

    # Award coins
    user.coins += ad_reward

    # Record transaction
    transaction = CoinTransaction(
        user_id=user.id,
        transaction_type='direct_ad_reward',
        amount=ad_reward,
        description=f'Direct ad watch reward (Session: {ad_session.direct_ads_watched_count}/100)'
    )

    db.session.add(transaction)
    db.session.commit()

    # Clear session token
    session.pop('current_direct_ad_token', None)
    session.pop('direct_ad_start_time', None)

    return jsonify({
        'success': True, 
        'message': f'✅ Task Completed! +{ad_reward} Coin(s) Earned', 
        'new_balance': user.coins,
        'direct_ads_watched': ad_session.direct_ads_watched_count,
        'direct_ads_remaining': 100 - ad_session.direct_ads_watched_count,
        'in_cooldown': ad_session.direct_ads_watched_count % 10 == 0 and ad_session.direct_ads_watched_count > 0
    })

@app.route('/complete-ad-task', methods=['POST'])
def complete_ad_task():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    # Verify session token
    data = request.get_json()
    if not data or data.get('session_token') != session.get('current_ad_token'):
        return jsonify({'success': False, 'message': 'Invalid session token.'}), 400

    # Verify minimum watch time (30 seconds) - more lenient
    ad_start_time_str = session.get('ad_start_time')
    if not ad_start_time_str:
        return jsonify({'success': False, 'message': 'No active ad session.'}), 400

    ad_start_time = datetime.fromisoformat(ad_start_time_str)
    time_watched = (datetime.utcnow() - ad_start_time).total_seconds()

    if time_watched < 35:  # Allow 5 seconds tolerance for network delays
        return jsonify({
            'success': False, 
            'message': f'Ad not watched completely. Watched: {int(time_watched)}s, Required: 40s'
        }), 400

    today = datetime.now().strftime('%Y-%m-%d')

    # Get today's ad session
    ad_session = AdWatchSession.query.filter_by(
        user_id=user.id, 
        session_date=today
    ).first()

    if not ad_session:
        return jsonify({'success': False, 'message': 'No ad session found.'}), 400

    # Double-check limits
    if ad_session.ads_watched_count >= 10:
        return jsonify({'success': False, 'message': 'Daily ad limit already reached.'}), 400

    # Check if too soon after last ad - more lenient
    if ad_session.last_ad_time:
        time_since_last = datetime.utcnow() - ad_session.last_ad_time
        if time_since_last.total_seconds() < 30:  # Allow 10 seconds tolerance for network delays
            return jsonify({'success': False, 'message': 'Ads watched too quickly.'}), 400

    # Get ad reward from configuration (0.5 coins for new multi-network ads)
        ad_reward_config = CoinConfiguration.query.filter_by(config_name='ad_watch_reward', is_active=True).first()
        ad_reward = 0.5  # Fixed reward for new ad system

    # Update ad session
    ad_session.ads_watched_count += 1
    ad_session.last_ad_time = datetime.utcnow()

    # Set 10-minute cooldown after every 10 ads
    if ad_session.ads_watched_count % 10 == 0 and ad_session.ads_watched_count > 0:
        ad_session.cooldown_until = datetime.utcnow() + timedelta(minutes=10)

    # Award coins
    user.coins += ad_reward

    # Record transaction
    transaction = CoinTransaction(
        user_id=user.id,
        transaction_type='ad_reward',
        amount=ad_reward,
        description=f'Ad watch reward (Session: {ad_session.ads_watched_count}/10)'
    )

    db.session.add(transaction)
    db.session.commit()

    # Clear session token
    session.pop('current_ad_token', None)
    session.pop('ad_start_time', None)

    return jsonify({
        'success': True, 
        'message': f'✅ Task Completed! +{ad_reward} Coin(s) Earned', 
        'new_balance': user.coins,
        'ads_watched': ad_session.ads_watched_count,
        'ads_remaining': 100 - ad_session.ads_watched_count,
        'in_cooldown': ad_session.ads_watched_count % 10 == 0 and ad_session.ads_watched_count > 0
    })

@app.route('/start-page-visit', methods=['POST'])
def start_page_visit():
    """Track when user starts visiting a page"""
    data = request.get_json()
    device_id = data.get('device_id', '')
    referral_code = data.get('referral_code', '')

    if not device_id:
        # Generate browser fingerprint as fallback
        import hashlib
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        device_id = hashlib.md5(f"{user_agent}{ip_address}".encode()).hexdigest()

    # Check if this device already has a visit record today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_visit = PageVisit.query.filter_by(
        device_id=device_id
    ).filter(PageVisit.visit_start >= today_start).first()

    if existing_visit:
        return jsonify({'success': True, 'visit_id': existing_visit.id})

    # Create new page visit record
    page_visit = PageVisit(
        user_id=session.get('user_id'),
        device_id=device_id,
        ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR')),
        user_agent=request.headers.get('User-Agent', '')[:500],
        referral_code=referral_code
    )

    db.session.add(page_visit)
    db.session.commit()

    return jsonify({'success': True, 'visit_id': page_visit.id})

@app.route('/update-page-visit', methods=['POST'])
def update_page_visit():
    """Update page visit duration and check qualification"""
    data = request.get_json()
    visit_id = data.get('visit_id')
    duration_seconds = data.get('duration_seconds', 0)

    if not visit_id:
        return jsonify({'success': False, 'message': 'No visit ID provided'}), 400

    page_visit = PageVisit.query.get(visit_id)
    if not page_visit:
        return jsonify({'success': False, 'message': 'Visit not found'}), 404

    # Update duration
    page_visit.duration_seconds = duration_seconds
    page_visit.visit_end = datetime.utcnow()

    # Check if qualifies (2+ minutes and not already qualified)
    if duration_seconds >= 120 and not page_visit.is_qualified:
        page_visit.is_qualified = True

        # If user is logged in and was referred, qualify the referral
        if page_visit.user_id and page_visit.referral_code:
            referral = UserReferral.query.filter_by(
                referred_id=page_visit.user_id, 
                referral_code=page_visit.referral_code,
                is_qualified=False
            ).first()

            if referral:
                referral.is_qualified = True
                referral.qualified_at = datetime.utcnow()

                # Check if referrer should get bonus
                check_and_award_referral_bonus(referral.referrer_id)

    db.session.commit()

    return jsonify({
        'success': True, 
        'qualified': page_visit.is_qualified,
        'duration': duration_seconds
    })

@app.route('/api/update-order-status/<int:order_id>', methods=['POST'])
def api_update_order_status(order_id):
    """API endpoint to manually update order status from JAP"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    order = Order.query.filter_by(id=order_id, user_id=user.id).first()
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    if update_order_from_jap(order):
        return jsonify({
            'success': True,
            'status': order.status,
            'start_count': order.start_count,
            'remains': order.remains,
            'completion_time': order.completion_time
        })
    else:
        return jsonify({'success': False, 'message': 'Failed to update order status.'}), 500

@app.route('/support')
def support():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    # Get user's recent tickets
    user_tickets = SupportTicket.query.filter_by(user_id=user.id).order_by(SupportTicket.created_at.desc()).limit(10).all()

    return render_template('support.html', user=user, user_tickets=user_tickets)

@app.route('/submit-support-ticket', methods=['POST'])
def submit_support_ticket():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    category = request.form.get('category', '').strip()
    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'medium')

    # Validation
    if not category or not subject or not description:
        flash('Please fill all required fields.')
        return redirect(url_for('support'))

    if len(subject) < 10:
        flash('Subject must be at least 10 characters long.')
        return redirect(url_for('support'))

    if len(description) < 20:
        flash('Description must be at least 20 characters long.')
        return redirect(url_for('support'))

    try:
        # Generate unique ticket number
        import random
        import string
        ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"

        # Ensure uniqueness
        while SupportTicket.query.filter_by(ticket_number=ticket_number).first():
            ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"

        # Create support ticket
        ticket = SupportTicket(
            user_id=user.id,
            ticket_number=ticket_number,
            category=category,
            subject=subject,
            description=description,
            priority=priority,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(ticket)
        db.session.commit()

        flash(f'✅ Support ticket submitted successfully! Ticket Number: {ticket_number}')
        return redirect(url_for('support'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting ticket: {str(e)}. Please try again.')
        return redirect(url_for('support'))

# ---------------------- ADMIN CREDENTIALS ---------------------- #
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "MechEnergy7130@"  # Change this to a strong password

# ---------------------- ADMIN ROUTES ---------------------- #
def is_admin():
    # Only allow admin access if explicitly logged in through admin login
    return session.get('is_admin_logged_in', False)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin_logged_in'] = True
            flash('Admin login successful!')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid admin credentials!')

    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin_logged_in', None)
    flash('Admin logged out successfully.')
    return redirect(url_for('home'))

@app.route('/admin')
def admin_panel():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    search_query = request.args.get('search', '')
    users = User.query.all()

    if search_query:
        users = User.query.filter(
            (User.username.contains(search_query)) | 
            (User.email.contains(search_query))
        ).all()

    # Add level information and activity stats to users
    users_with_stats = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for user in users:
        user_level = get_user_level(user.id)
        
        # Get today's ad session
        try:
            ad_session = AdWatchSession.query.filter_by(user_id=user.id, session_date=today).first()
            ads_watched_today = ad_session.ads_watched_count if ad_session else 0
            # Handle potential missing column
            try:
                direct_ads_watched_today = ad_session.direct_ads_watched_count if ad_session else 0
            except AttributeError:
                direct_ads_watched_today = 0
        except Exception as e:
            print(f"Error getting ad session: {e}")
            ads_watched_today = 0
            direct_ads_watched_today = 0
        
        # Get user's activity status
        if user.last_activity:
            time_since_active = (datetime.utcnow() - user.last_activity).total_seconds()
            if time_since_active <= 300:  # 5 minutes
                status = "Online"
                status_class = "text-green-600"
            elif time_since_active <= 3600:  # 1 hour
                status = "Recently Active"
                status_class = "text-yellow-600"
            else:
                status = "Offline"
                status_class = "text-gray-500"
        else:
            status = "Never Active"
            status_class = "text-red-500"
        
        # Get total orders and coins earned
        total_orders = Order.query.filter_by(user_id=user.id).count()
        completed_orders = Order.query.filter_by(user_id=user.id, status='Completed').count()
        
        # Get total ad rewards earned
        total_ad_rewards = db.session.query(db.func.sum(CoinTransaction.amount)).filter_by(
            user_id=user.id, 
            transaction_type='ad_reward'
        ).scalar() or 0
        
        user_stats = {
            'user': user,
            'level': user_level,
            'status': status,
            'status_class': status_class,
            'ads_watched_today': ads_watched_today,
            'direct_ads_watched_today': direct_ads_watched_today,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_ad_rewards': total_ad_rewards,
            'last_activity': user.last_activity
        }
        users_with_stats.append(user_stats)

    # Sort by last activity (most recent first)
    users_with_stats.sort(key=lambda x: x['last_activity'] or datetime.min, reverse=True)

    # Get all orders with user information
    orders = db.session.query(Order, User).join(User, Order.user_id == User.id).order_by(Order.created_at.desc()).limit(50).all()

    # Get online users count
    online_users_count = get_online_users_count()
    
    # Get system statistics
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_coins_distributed = db.session.query(db.func.sum(CoinTransaction.amount)).filter(CoinTransaction.amount > 0).scalar() or 0
    
    # Get today's activity stats
    today_users = User.query.filter(User.last_activity >= datetime.now().replace(hour=0, minute=0, second=0)).count()
    today_orders = Order.query.filter(Order.created_at >= datetime.now().replace(hour=0, minute=0, second=0)).count()
    
    system_stats = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_coins_distributed': total_coins_distributed,
        'online_users': online_users_count,
        'today_active_users': today_users,
        'today_orders': today_orders
    }

    return render_template('admin_panel.html', 
                         users_with_stats=users_with_stats, 
                         orders=orders, 
                         search_query=search_query, 
                         today=today, 
                         datetime=datetime, 
                         system_stats=system_stats)

@app.route('/admin/toggle-ban/<int:user_id>', methods=['POST'])
def toggle_ban_user(user_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if user:
        user.is_banned = not user.is_banned
        db.session.commit()
        action = "banned" if user.is_banned else "unbanned"
        flash(f'User {user.username} has been {action}.')
    else:
        flash('User not found.')

    return redirect(url_for('admin_panel'))

@app.route('/admin/update-coins/<int:user_id>', methods=['POST'])
def update_user_coins(user_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    new_coins = request.form.get('coins')

    if user and new_coins:
        try:
            user.coins = int(new_coins)
            db.session.commit()
            flash(f'Coins updated for {user.username}.')
        except ValueError:
            flash('Invalid coin amount.')
    else:
        flash('User not found or invalid data.')

    return redirect(url_for('admin_panel'))

@app.route('/admin/update-order-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    order = Order.query.get(order_id)
    new_status = request.form.get('status')

    if order and new_status:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order_id} status updated to {new_status}.')
    else:
        flash('Order not found or invalid status.')

    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash(f'Order #{order_id} deleted successfully.')
    else:
        flash('Order not found.')

    return redirect(url_for('admin_panel'))

@app.route('/admin/update-jap-status/<int:order_id>', methods=['POST'])
def update_jap_status(order_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    order = Order.query.get(order_id)
    if order and order.jap_order_id:
        jap_status = get_jap_order_status(order.jap_order_id)
        if jap_status:
            # Map JAP status to our status
            status_mapping = {
                'Pending': 'Pending',
                'In progress': 'Processing',
                'Processing': 'Processing',
                'Partial': 'Partial',
                'Completed': 'Completed',
                'Canceled': 'Cancelled'
            }

            jap_order_status = jap_status.get('status', 'Unknown')
            new_status = status_mapping.get(jap_order_status, jap_order_status)

            order.status = new_status
            db.session.commit()
            flash(f'Order #{order_id} status updated to {new_status} from JAP API.')
        else:
            flash('Failed to get status from JAP API.')
    else:
        flash('Order not found or no JAP order ID.')

    return redirect(url_for('admin_panel'))

@app.route('/admin/services')
def admin_services():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all services from JAP API
    jap_services = get_jap_services()

    # Get selected services from database
    selected_services = SelectedService.query.all()
    selected_service_ids = [s.service_id for s in selected_services]

    return render_template('admin_services.html', 
                         jap_services=jap_services, 
                         selected_services=selected_services,
                         selected_service_ids=selected_service_ids)

@app.route('/admin/add-service', methods=['POST'])
def add_selected_service():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    service_id = request.form.get('service_id')
    service_name = request.form.get('service_name')
    category = request.form.get('category')
    rate = request.form.get('rate')
    min_quantity = request.form.get('min_quantity')
    max_quantity = request.form.get('max_quantity')
    description = request.form.get('description', '')

    # Check if service already exists
    existing_service = SelectedService.query.filter_by(service_id=int(service_id)).first()
    if existing_service:
        flash('Service already added to selected services.')
        return redirect(url_for('admin_services'))

    new_service = SelectedService(
        service_id=int(service_id),
        service_name=service_name,
        category=category,
        rate=float(rate),
        min_quantity=int(min_quantity),
        max_quantity=int(max_quantity),
        description=description
    )

    db.session.add(new_service)
    db.session.commit()

    flash(f'Service "{service_name}" added successfully!')
    return redirect(url_for('admin_services'))

@app.route('/admin/remove-service/<int:service_id>', methods=['POST'])
def remove_selected_service(service_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    service = SelectedService.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
        flash(f'Service "{service.service_name}" removed successfully!')
    else:
        flash('Service not found.')

    return redirect(url_for('admin_services'))

@app.route('/admin/toggle-service/<int:service_id>', methods=['POST'])
def toggle_service_status(service_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    service = SelectedService.query.get(service_id)
    if service:
        service.is_active = not service.is_active
        db.session.commit()
        status = "activated" if service.is_active else "deactivated"
        flash(f'Service "{service.service_name}" {status} successfully!')
    else:
        flash('Service not found.')

    return redirect(url_for('admin_services'))

@app.route('/admin/edit-service/<int:service_id>', methods=['POST'])
def edit_selected_service(service_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    service = SelectedService.query.get(service_id)
    if service:
        service.service_name = request.form.get('service_name', service.service_name)
        service.rate = float(request.form.get('rate', service.rate))
        service.min_quantity = int(request.form.get('min_quantity', service.min_quantity))
        service.max_quantity = int(request.form.get('max_quantity', service.max_quantity))
        service.description = request.form.get('description', service.description)

        db.session.commit()
        flash(f'Service "{service.service_name}" updated successfully!')
    else:
        flash('Service not found.')

    return redirect(url_for('admin_services'))

@app.route('/admin/api-settings')
def admin_api_settings():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get current API settings
    api_url_config = CoinConfiguration.query.filter_by(config_name='jap_api_url', is_active=True).first()
    api_key_config = CoinConfiguration.query.filter_by(config_name='jap_api_key', is_active=True).first()

    current_api_url = api_url_config.description if api_url_config else JAP_API_URL
    current_api_key = api_key_config.description if api_key_config else JAP_API_KEY

    return render_template('admin_api_settings.html', 
                         current_api_url=current_api_url,
                         current_api_key=current_api_key)

@app.route('/admin/update-api-settings', methods=['POST'])
def update_api_settings():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    new_api_url = request.form.get('api_url', '').strip()
    new_api_key = request.form.get('api_key', '').strip()

    if new_api_url and new_api_key:
        try:
            # Update or create API URL config
            api_url_config = CoinConfiguration.query.filter_by(config_name='jap_api_url').first()
            if api_url_config:
                api_url_config.description = new_api_url
                api_url_config.updated_at = datetime.utcnow()
            else:
                api_url_config = CoinConfiguration(
                    config_name='jap_api_url',
                    coin_value=0,
                    description=new_api_url,
                    is_active=True
                )
                db.session.add(api_url_config)

            # Update or create API Key config
            api_key_config = CoinConfiguration.query.filter_by(config_name='jap_api_key').first()
            if api_key_config:
                api_key_config.description = new_api_key
                api_key_config.updated_at = datetime.utcnow()
            else:
                api_key_config = CoinConfiguration(
                    config_name='jap_api_key',
                    coin_value=0,
                    description=new_api_key,
                    is_active=True
                )
                db.session.add(api_key_config)

            db.session.commit()
            flash('API settings updated successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating API settings: {str(e)}')
    else:
        flash('Please fill all required fields.')

    return redirect(url_for('admin_api_settings'))

@app.route('/admin/test-api-connection', methods=['POST'])
def test_api_connection():
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'}), 401

    try:
        services = get_jap_services()
        if services and len(services) > 0:
            return jsonify({'success': True, 'message': f'Connection successful! Found {len(services)} services.'})
        else:
            return jsonify({'success': False, 'message': 'Connection failed or no services found.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/admin/coins')
def admin_coins():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all coin configurations
    coin_configs = CoinConfiguration.query.all()

    # Ensure ad reward configurations exist
    ensure_ad_reward_configs()

    # Get recent transactions
    recent_transactions = db.session.query(CoinTransaction, User).join(User, CoinTransaction.user_id == User.id).order_by(CoinTransaction.created_at.desc()).limit(50).all()

    # Get all users for manual coin adjustment
    users = User.query.all()

    return render_template('admin_coins.html', 
                         coin_configs=coin_configs, 
                         recent_transactions=recent_transactions,
                         users=users)

def ensure_ad_reward_configs():
    """Ensure ad reward configurations exist"""
    configs_to_add = [
        {
            'name': 'ad_watch_reward',
            'value': 0.5,
            'description': 'Reward for watching multi-network ads (Watch Ad 1)'
        },
        {
            'name': 'direct_ad_watch_reward', 
            'value': 0.5,
            'description': 'Reward for watching direct link ads (Watch Ad 2)'
        },
        {
            'name': 'daily_ad_limit',
            'value': 100,
            'description': 'Maximum ads per day per user'
        },
        {
            'name': 'ad_cooldown_after',
            'value': 10,
            'description': 'Number of ads before cooldown period'
        },
        {
            'name': 'ad_cooldown_minutes',
            'value': 10,
            'description': 'Cooldown period in minutes'
        }
    ]

    for config in configs_to_add:
        existing = CoinConfiguration.query.filter_by(config_name=config['name']).first()
        if not existing:
            new_config = CoinConfiguration(
                config_name=config['name'],
                coin_value=config['value'],
                description=config['description'],
                is_active=True
            )
            db.session.add(new_config)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/admin/add-coin-config', methods=['POST'])
def add_coin_config():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    config_name = request.form.get('config_name')
    coin_value = request.form.get('coin_value')
    description = request.form.get('description', '')

    if config_name and coin_value:
        try:
            # Check if config already exists
            existing_config = CoinConfiguration.query.filter_by(config_name=config_name).first()
            if existing_config:
                flash('Configuration with this name already exists.')
                return redirect(url_for('admin_coins'))

            new_config = CoinConfiguration(
                config_name=config_name,
                coin_value=int(coin_value),
                description=description
            )
            db.session.add(new_config)
            db.session.commit()
            flash(f'Coin configuration "{config_name}" added successfully!')
        except ValueError:
            flash('Invalid coin value.')
    else:
        flash('Please fill all required fields.')

    return redirect(url_for('admin_coins'))

@app.route('/admin/update-coin-config/<int:config_id>', methods=['POST'])
def update_coin_config(config_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    config = CoinConfiguration.query.get(config_id)
    if config:
        try:
            # For text configs (EasyPaisa details), only update description
            if config.config_name in ['easypaisa_account_name', 'easypaisa_account_number']:
                config.description = request.form.get('description', config.description)
            else:
                # For numeric configs, update both coin_value and description
                coin_value_str = request.form.get('coin_value')
                if coin_value_str:
                    config.coin_value = int(coin_value_str)
                config.description = request.form.get('description', config.description)

            config.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Configuration "{config.config_name}" updated successfully!')
        except ValueError:
            flash('Invalid coin value.')
    else:
        flash('Configuration not found.')

    return redirect(url_for('admin_coins'))

@app.route('/admin/toggle-coin-config/<int:config_id>', methods=['POST'])
def toggle_coin_config(config_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    config = CoinConfiguration.query.get(config_id)
    if config:
        config.is_active = not config.is_active
        config.updated_at = datetime.utcnow()
        db.session.commit()
        status = "activated" if config.is_active else "deactivated"
        flash(f'Configuration "{config.config_name}" {status} successfully!')
    else:
        flash('Configuration not found.')

    return redirect(url_for('admin_coins'))

@app.route('/admin/manual-coin-adjustment', methods=['POST'])
def manual_coin_adjustment():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    user_id = request.form.get('user_id')
    amount = request.form.get('amount')
    description = request.form.get('description', 'Manual admin adjustment')

    if user_id and amount:
        try:
            user = User.query.get(int(user_id))
            amount_int = int(amount)

            if user:
                user.coins += amount_int

                # Record transaction
                transaction = CoinTransaction(
                    user_id=user.id,
                    transaction_type='admin_adjustment',
                    amount=amount_int,
                    description=description
                )

                db.session.add(transaction)
                db.session.commit()

                action = "added" if amount_int > 0 else "deducted"
                flash(f'{abs(amount_int)} coins {action} for user {user.username}!')
            else:
                flash('User not found.')
        except ValueError:
            flash('Invalid amount.')
    else:
        flash('Please fill all required fields.')

    return redirect(url_for('admin_coins'))

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('admin_panel'))

    try:
        # Delete all related records first to maintain referential integrity

        # Delete coin transactions
        CoinTransaction.query.filter_by(user_id=user_id).delete()

        # Delete orders
        Order.query.filter_by(user_id=user_id).delete()

        # Delete ad watch sessions
        AdWatchSession.query.filter_by(user_id=user_id).delete()

        # Delete spin wheel records
        SpinWheel.query.filter_by(user_id=user_id).delete()

        # Delete password reset tokens
        PasswordResetToken.query.filter_by(user_id=user_id).delete()

        # Delete referrals where user is referrer
        UserReferral.query.filter_by(referrer_id=user_id).delete()

        # Delete referrals where user is referred
        UserReferral.query.filter_by(referred_id=user_id).delete()

        # Delete referral rewards
        ReferralReward.query.filter_by(user_id=user_id).delete()

        # Delete device registrations
        DeviceRegistration.query.filter_by(user_id=user_id).delete()

        # Delete admin spin grants
        AdminSpinGrant.query.filter_by(user_id=user_id).delete()

        # Delete page visits
        PageVisit.query.filter_by(user_id=user_id).delete()

        # Delete coin purchases
        CoinPurchase.query.filter_by(user_id=user_id).delete()

        # Finally delete the user
        username = user.username
        db.session.delete(user)
        db.session.commit()

        flash(f'User "{username}" and all related data have been permanently deleted.')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}')

    return redirect(url_for('admin_panel'))

@app.route('/admin/announcements')
def admin_announcements():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin_announcements.html', announcements=announcements)

@app.route('/admin/add-announcement', methods=['POST'])
def add_announcement():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    title = request.form.get('title')
    content = request.form.get('content')
    highlight_text = request.form.get('highlight_text', '')
    show_on_home = 'show_on_home' in request.form
    show_on_dashboard = 'show_on_dashboard' in request.form
    background_color = request.form.get('background_color', 'gradient-bg')

    if title and content:
        new_announcement = Announcement(
            title=title,
            content=content,
            highlight_text=highlight_text,
            show_on_home=show_on_home,
            show_on_dashboard=show_on_dashboard,
            background_color=background_color
        )
        db.session.add(new_announcement)
        db.session.commit()
        flash('Announcement added successfully!')
    else:
        flash('Please fill all required fields.')

    return redirect(url_for('admin_announcements'))

@app.route('/admin/edit-announcement/<int:announcement_id>', methods=['POST'])
def edit_announcement(announcement_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    announcement = Announcement.query.get(announcement_id)
    if announcement:
        announcement.title = request.form.get('title', announcement.title)
        announcement.content = request.form.get('content', announcement.content)
        announcement.highlight_text = request.form.get('highlight_text', announcement.highlight_text)
        announcement.show_on_home = 'show_on_home' in request.form
        announcement.show_on_dashboard = 'show_on_dashboard' in request.form
        announcement.background_color = request.form.get('background_color', announcement.background_color)
        announcement.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Announcement updated successfully!')
    else:
        flash('Announcement not found.')

    return redirect(url_for('admin_announcements'))

@app.route('/admin/toggle-announcement/<int:announcement_id>', methods=['POST'])
def toggle_announcement(announcement_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    announcement = Announcement.query.get(announcement_id)
    if announcement:
        announcement.is_active = not announcement.is_active
        announcement.updated_at = datetime.utcnow()
        db.session.commit()
        status = "activated" if announcement.is_active else "deactivated"
        flash(f'Announcement {status} successfully!')
    else:
        flash('Announcement not found.')

    return redirect(url_for('admin_announcements'))

@app.route('/admin/delete-announcement/<int:announcement_id>', methods=['POST'])
def delete_announcement(announcement_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    announcement = Announcement.query.get(announcement_id)
    if announcement:
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement deleted successfully!')
    else:
        flash('Announcement not found.')

    return redirect(url_for('admin_announcements'))

@app.route('/admin/home-page')
def admin_home_page():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all home page content organized by section
    hero_content = HomePageContent.query.filter_by(section_type='hero').order_by(HomePageContent.display_order).all()
    feature_content = HomePageContent.query.filter_by(section_type='feature').order_by(HomePageContent.display_order).all()
    offer_content = HomePageContent.query.filter_by(section_type='offer').order_by(HomePageContent.display_order).all()

    return render_template('admin_home_page.html', 
                         hero_content=hero_content,
                         feature_content=feature_content,
                         offer_content=offer_content)

@app.route('/admin/add-home-content', methods=['POST'])
def add_home_content():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    section_type = request.form.get('section_type')
    title = request.form.get('title')
    subtitle = request.form.get('subtitle', '')
    description = request.form.get('description', '')
    image_url = request.form.get('image_url', '')
    button_text = request.form.get('button_text', '')
    button_link = request.form.get('button_link', '')
    background_color = request.form.get('background_color', 'bg-white')
    text_color = request.form.get('text_color', 'text-gray-900')
    display_order = int(request.form.get('display_order', 0))

    if section_type and title:
        new_content = HomePageContent(
            section_type=section_type,
            title=title,
            subtitle=subtitle,
            description=description,
            image_url=image_url,
            button_text=button_text,
            button_link=button_link,
            background_color=background_color,
            text_color=text_color,
            display_order=display_order
        )
        db.session.add(new_content)
        db.session.commit()
        flash('Home page content added successfully!')
    else:
        flash('Please fill all required fields.')

    return redirect(url_for('admin_home_page'))

@app.route('/admin/edit-home-content/<int:content_id>', methods=['POST'])
def edit_home_content(content_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    content = HomePageContent.query.get(content_id)
    if content:
        content.title = request.form.get('title', content.title)
        content.subtitle = request.form.get('subtitle', content.subtitle)
        content.description = request.form.get('description', content.description)
        content.image_url = request.form.get('image_url', content.image_url)




@app.route('/admin/ad-management')
def admin_ad_management():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get current ad configurations
    advanced_ad = AdConfiguration.query.filter_by(ad_type='advanced_ad', is_active=True).first()
    direct_ad = AdConfiguration.query.filter_by(ad_type='direct_ad', is_active=True).first()

    # Get all ad configurations for history
    all_ads = AdConfiguration.query.order_by(AdConfiguration.created_at.desc()).all()

    # Get ad links
    ad_links = AdLink.query.order_by(AdLink.display_order).all()
    
    # Get multiple ads for both types
    watch_ad_1_ads = MultipleAdConfig.query.filter_by(ad_type='watch_ad_1').order_by(MultipleAdConfig.display_order).all()
    watch_ad_2_ads = MultipleAdConfig.query.filter_by(ad_type='watch_ad_2').order_by(MultipleAdConfig.display_order).all()

    return render_template('admin_ad_management.html', 
                         advanced_ad=advanced_ad,
                         direct_ad=direct_ad,
                         all_ads=all_ads,
                         ad_links=ad_links,
                         watch_ad_1_ads=watch_ad_1_ads,
                         watch_ad_2_ads=watch_ad_2_ads)

@app.route('/admin/add-ad-link', methods=['POST'])
def add_ad_link():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    name = request.form.get('name', '').strip()
    ad_url = request.form.get('ad_url', '').strip()

    if not name or not ad_url:
        flash('Please fill all required fields.')
        return redirect(url_for('admin_ad_management'))

    try:
        # Get next display order
        max_order = db.session.query(db.func.max(AdLink.display_order)).scalar() or 0
        
        new_link = AdLink(
            name=name,
            ad_url=ad_url,
            display_order=max_order + 1
        )

        db.session.add(new_link)
        db.session.commit()

        flash(f'Ad link "{name}" added successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding ad link: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/toggle-ad-link/<int:link_id>', methods=['POST'])
def toggle_ad_link(link_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad_link = AdLink.query.get(link_id)
    if not ad_link:
        flash('Ad link not found.')
        return redirect(url_for('admin_ad_management'))

    try:
        ad_link.is_active = not ad_link.is_active
        ad_link.updated_at = datetime.utcnow()
        db.session.commit()

        status = "activated" if ad_link.is_active else "deactivated"
        flash(f'Ad link "{ad_link.name}" {status} successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating ad link: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/delete-ad-link/<int:link_id>', methods=['POST'])
def delete_ad_link(link_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad_link = AdLink.query.get(link_id)
    if not ad_link:
        flash('Ad link not found.')
        return redirect(url_for('admin_ad_management'))

    try:
        name = ad_link.name
        db.session.delete(ad_link)
        db.session.commit()

        flash(f'Ad link "{name}" deleted successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting ad link: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/add-multiple-ad', methods=['POST'])
def add_multiple_ad():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad_type = request.form.get('ad_type')  # 'watch_ad_1' or 'watch_ad_2'
    ad_name = request.form.get('ad_name', '').strip()
    ad_code = request.form.get('ad_code', '').strip()

    if not ad_type or not ad_name or not ad_code:
        flash('Please fill all required fields.')
        return redirect(url_for('admin_ad_management'))

    try:
        # Get next display order
        max_order = db.session.query(db.func.max(MultipleAdConfig.display_order)).filter_by(ad_type=ad_type).scalar() or 0
        
        new_ad = MultipleAdConfig(
            ad_type=ad_type,
            ad_name=ad_name,
            ad_code=ad_code,
            display_order=max_order + 1
        )

        db.session.add(new_ad)
        db.session.commit()

        flash(f'Multiple ad "{ad_name}" added successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding multiple ad: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/toggle-multiple-ad/<int:ad_id>', methods=['POST'])
def toggle_multiple_ad(ad_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad = MultipleAdConfig.query.get(ad_id)
    if not ad:
        flash('Multiple ad not found.')
        return redirect(url_for('admin_ad_management'))

    try:
        ad.is_active = not ad.is_active
        ad.updated_at = datetime.utcnow()
        db.session.commit()

        status = "activated" if ad.is_active else "deactivated"
        flash(f'Multiple ad "{ad.ad_name}" {status} successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating multiple ad: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/delete-multiple-ad/<int:ad_id>', methods=['POST'])
def delete_multiple_ad(ad_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad = MultipleAdConfig.query.get(ad_id)
    if not ad:
        flash('Multiple ad not found.')
        return redirect(url_for('admin_ad_management'))

    try:
        name = ad.ad_name
        db.session.delete(ad)
        db.session.commit()

        flash(f'Multiple ad "{name}" deleted successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting multiple ad: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/update-ad-code', methods=['POST'])
def update_ad_code():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad_type = request.form.get('ad_type')
    ad_code = request.form.get('ad_code', '').strip()

    if not ad_type or not ad_code:
        flash('Please fill all required fields.')
        return redirect(url_for('admin_ad_management'))

    try:
        # Deactivate existing ad of this type
        AdConfiguration.query.filter_by(ad_type=ad_type).update({AdConfiguration.is_active: False})

        # Create new ad configuration
        new_ad = AdConfiguration(
            ad_type=ad_type,
            ad_code=ad_code,
            is_active=True
        )

        db.session.add(new_ad)
        db.session.commit()

        flash(f'{ad_type.replace("_", " ").title()} ad code updated successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating ad code: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/toggle-ad/<int:ad_id>', methods=['POST'])
def toggle_ad_status(ad_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ad = AdConfiguration.query.get(ad_id)
    if not ad:
        flash('Ad configuration not found.')
        return redirect(url_for('admin_ad_management'))

    try:
        if not ad.is_active:
            # Deactivate all other ads of same type
            AdConfiguration.query.filter_by(ad_type=ad.ad_type).update({AdConfiguration.is_active: False})
            ad.is_active = True
        else:
            ad.is_active = False

        ad.updated_at = datetime.utcnow()
        db.session.commit()

        status = "activated" if ad.is_active else "deactivated"
        flash(f'{ad.ad_type.replace("_", " ").title()} ad {status} successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating ad status: {str(e)}')

    return redirect(url_for('admin_ad_management'))

@app.route('/admin/toggle-home-content/<int:content_id>', methods=['POST'])
def toggle_home_content(content_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    content = HomePageContent.query.get(content_id)
    if content:
        content.is_active = not content.is_active
        content.updated_at = datetime.utcnow()
        db.session.commit()
        status = "activated" if content.is_active else "deactivated"
        flash(f'Content {status} successfully!')
    else:
        flash('Content not found.')

    return redirect(url_for('admin_home_page'))

@app.route('/admin/delete-home-content/<int:content_id>', methods=['POST'])
def delete_home_content(content_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    content = HomePageContent.query.get(content_id)
    if content:
        db.session.delete(content)
        db.session.commit()
        flash('Home page content deleted successfully!')
    else:
        flash('Content not found.')

    return redirect(url_for('admin_home_page'))

@app.route('/admin/password-resets')
def admin_password_resets():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all password reset requests
    reset_requests = db.session.query(PasswordResetToken, User).join(User, PasswordResetToken.user_id == User.id).order_by(PasswordResetToken.created_at.desc()).all()

    # Get statistics
    total_requests = PasswordResetToken.query.count()
    used_tokens = PasswordResetToken.query.filter_by(is_used=True).count()
    expired_tokens = PasswordResetToken.query.filter(PasswordResetToken.expires_at < datetime.utcnow(), PasswordResetToken.is_used == False).count()
    active_tokens = PasswordResetToken.query.filter(PasswordResetToken.expires_at > datetime.utcnow(), PasswordResetToken.is_used == False).count()

    stats = {
        'total_requests': total_requests,
        'used_tokens': used_tokens,
        'expired_tokens': expired_tokens,
        'active_tokens': active_tokens
    }

    return render_template('admin_password_resets.html', reset_requests=reset_requests, stats=stats, now=datetime.utcnow())

@app.route('/admin/invalidate-reset-token/<int:token_id>', methods=['POST'])
def invalidate_reset_token(token_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    token = PasswordResetToken.query.get(token_id)
    if token:
        token.is_used = True
        db.session.commit()
        flash('Reset token invalidated successfully!')
    else:
        flash('Token not found.')

    return redirect(url_for('admin_password_resets'))

@app.route('/admin/referrals')
def admin_referrals():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all users with referral statistics
    users = User.query.all()
    user_referral_stats = []

    for user in users:
        total_referrals = UserReferral.query.filter_by(referrer_id=user.id).count()
        qualified_referrals = UserReferral.query.filter_by(referrer_id=user.id, is_qualified=True).count()
        remaining_for_bonus = max(0, 10 - qualified_referrals)

        # Get today's available spins
        referral_spins = get_available_referral_spins(user.id)
        admin_spins = get_available_admin_spins(user.id)

        # Get device count
        device_count = DeviceRegistration.query.filter_by(user_id=user.id).count()

        user_referral_stats.append({
            'user': user,
            'total_referrals': total_referrals,
            'qualified_referrals': qualified_referrals,
            'remaining_for_bonus': remaining_for_bonus,
            'referral_spins': referral_spins,
            'admin_spins': admin_spins,
            'device_count': device_count
        })

    # Get recent referral activities with proper aliases
    referrer_user = aliased(User)
    referred_user = aliased(User)

    recent_referrals = db.session.query(UserReferral, referrer_user.username.label('referrer_name'), referred_user.username.label('referred_name'))\
        .join(referrer_user, UserReferral.referrer_id == referrer_user.id)\
        .join(referred_user, UserReferral.referred_id == referred_user.id)\
        .order_by(UserReferral.created_at.desc()).limit(50).all()

    return render_template('admin_referrals.html', 
                         user_referral_stats=user_referral_stats,
                         recent_referrals=recent_referrals)

@app.route('/admin/coin-purchases')
def admin_coin_purchases():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all coin purchases with user information
    purchases = db.session.query(CoinPurchase, User).join(User, CoinPurchase.user_id == User.id).order_by(CoinPurchase.created_at.desc()).all()

    # Get statistics
    total_purchases = CoinPurchase.query.count()
    pending_purchases = CoinPurchase.query.filter_by(status='pending').count()
    approved_purchases = CoinPurchase.query.filter_by(status='approved').count()
    rejected_purchases = CoinPurchase.query.filter_by(status='rejected').count()
    total_revenue = db.session.query(db.func.sum(CoinPurchase.amount_pkr)).filter_by(status='approved').scalar() or 0

    stats = {
        'total_purchases': total_purchases,
        'pending_purchases': pending_purchases,
        'approved_purchases': approved_purchases,
        'rejected_purchases': rejected_purchases,
        'total_revenue': total_revenue
    }

    # Get current coin rate
    coin_rate = get_coin_purchase_rate()

    return render_template('admin_coin_purchases.html', 
                         purchases=purchases, 
                         stats=stats,
                         coin_rate=coin_rate)

@app.route('/admin/verify-coin-purchase/<int:purchase_id>', methods=['POST'])
def verify_coin_purchase(purchase_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    purchase = CoinPurchase.query.get(purchase_id)
    if not purchase:
        flash('Purchase not found.')
        return redirect(url_for('admin_coin_purchases'))

    action = request.form.get('action')  # 'approve' or 'reject'
    admin_notes = request.form.get('admin_notes', '').strip()
    coins_to_award = request.form.get('coins_to_award')

    if action == 'approve':
        try:
            coins_to_award = int(coins_to_award) if coins_to_award else purchase.coins_requested

            # Find admin user ID properly
            admin_user = User.query.filter_by(is_admin=True).first()
            admin_id = admin_user.id if admin_user else 1

            # Update purchase
            purchase.status = 'approved'
            purchase.coins_awarded = coins_to_award
            purchase.admin_notes = admin_notes
            purchase.verified_by = admin_id
            purchase.verified_at = datetime.utcnow()
            purchase.updated_at = datetime.utcnow()

            # Award coins to user
            user = User.query.get(purchase.user_id)
            if user:
                user.coins += coins_to_award

                # Record transaction
                transaction = CoinTransaction(
                    user_id=user.id,
                    transaction_type='coin_purchase',
                    amount=coins_to_award,
                    description=f'EasyPaisa purchase approved - Transaction ID: {purchase.transaction_id}'
                )
                db.session.add(transaction)

            db.session.commit()
            flash(f'Purchase approved! {coins_to_award} coins awarded to user.')

        except (ValueError, TypeError):
            flash('Invalid coin amount.')
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing approval: {str(e)}')

    elif action == 'reject':
        try:
            # Find admin user ID properly
            admin_user = User.query.filter_by(is_admin=True).first()
            admin_id = admin_user.id if admin_user else 1

            purchase.status = 'rejected'
            purchase.admin_notes = admin_notes
            purchase.verified_by = admin_id
            purchase.verified_at = datetime.utcnow()
            purchase.updated_at = datetime.utcnow()

            db.session.commit()
            flash('Purchase rejected.')
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing rejection: {str(e)}')

    return redirect(url_for('admin_coin_purchases'))

@app.route('/admin/apk-management')
def admin_apk_management():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get current active APK
    current_apk = ApkFile.query.filter_by(is_active=True).first()

    # Get all APK files
    apk_history = ApkFile.query.order_by(ApkFile.created_at.desc()).all()

    # Calculate total downloads
    download_count = sum(apk.download_count for apk in apk_history)

    return render_template('admin_apk_management.html', 
                         current_apk=current_apk,
                         apk_history=apk_history,
                         download_count=download_count)

@app.route('/admin/upload-apk', methods=['POST'])
def admin_upload_apk():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    try:
        # Get form data
        app_name = request.form.get('app_name', '').strip()
        version = request.form.get('version', '').strip()
        description = request.form.get('description', '').strip()
        is_active = 'is_active' in request.form

        # Get uploaded file
        if 'apk_file' not in request.files:
            flash('No APK file selected.')
            return redirect(url_for('admin_apk_management'))

        apk_file = request.files['apk_file']
        if apk_file.filename == '':
            flash('No APK file selected.')
            return redirect(url_for('admin_apk_management'))

        if not apk_file.filename.lower().endswith('.apk'):
            flash('Only APK files are allowed.')
            return redirect(url_for('admin_apk_management'))

        # Create uploads directory if not exists
        import os
        uploads_dir = 'uploads/apk'
        os.makedirs(uploads_dir, exist_ok=True)

        # Generate unique filename
        import uuid
        file_extension = '.apk'
        unique_filename = f"{app_name}_{version}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)

        # Save file
        apk_file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Check file size (50MB limit)
        if file_size > 50 * 1024 * 1024:
            os.remove(file_path)
            flash('APK file is too large. Maximum size is 50MB.')
            return redirect(url_for('admin_apk_management'))

        # If this APK should be active, deactivate all others
        if is_active:
            ApkFile.query.update({ApkFile.is_active: False})

        # Get admin user ID
        admin_user = User.query.filter_by(is_admin=True).first()
        admin_id = admin_user.id if admin_user else 1

        # Create APK record
        new_apk = ApkFile(
            app_name=app_name,
            version=version,
            file_name=unique_filename,
            file_path=file_path,
            file_size=file_size,
            description=description,
            is_active=is_active,
            uploaded_by=admin_id
        )

        db.session.add(new_apk)
        db.session.commit()

        flash(f'APK "{app_name} v{version}" uploaded successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error uploading APK: {str(e)}')

    return redirect(url_for('admin_apk_management'))

@app.route('/admin/toggle-apk/<int:apk_id>', methods=['POST'])
def admin_toggle_apk(apk_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    apk = ApkFile.query.get(apk_id)
    if not apk:
        flash('APK not found.')
        return redirect(url_for('admin_apk_management'))

    if not apk.is_active:
        # Deactivate all other APKs first
        ApkFile.query.update({ApkFile.is_active: False})
        apk.is_active = True
        flash(f'APK "{apk.app_name} v{apk.version}" activated.')
    else:
        apk.is_active = False
        flash(f'APK "{apk.app_name} v{apk.version}" deactivated.')

    apk.updated_at = datetime.utcnow()
    db.session.commit()

    return redirect(url_for('admin_apk_management'))

@app.route('/admin/delete-apk/<int:apk_id>', methods=['POST'])
def admin_delete_apk(apk_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    apk = ApkFile.query.get(apk_id)
    if not apk:
        flash('APK not found.')
        return redirect(url_for('admin_apk_management'))

    try:
        # Delete file from filesystem
        import os
        if os.path.exists(apk.file_path):
            os.remove(apk.file_path)

        # Delete from database
        db.session.delete(apk)
        db.session.commit()

        flash(f'APK "{apk.app_name} v{apk.version}" deleted successfully.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting APK: {str(e)}')

    return redirect(url_for('admin_apk_management'))

@app.route('/admin/support-tickets')
def admin_support_tickets():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    priority_filter = request.args.get('priority', 'all')

    # Build query
    query = db.session.query(SupportTicket, User).join(User, SupportTicket.user_id == User.id)

    if status_filter != 'all':
        query = query.filter(SupportTicket.status == status_filter)
    if category_filter != 'all':
        query = query.filter(SupportTicket.category == category_filter)
    if priority_filter != 'all':
        query = query.filter(SupportTicket.priority == priority_filter)

    tickets = query.order_by(SupportTicket.created_at.desc()).all()

    # Get statistics
    total_tickets = SupportTicket.query.count()
    open_tickets = SupportTicket.query.filter_by(status='open').count()
    in_progress_tickets = SupportTicket.query.filter_by(status='in_progress').count()
    resolved_tickets = SupportTicket.query.filter_by(status='resolved').count()

    stats = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets
    }

    return render_template('admin_support_tickets.html', 
                         tickets=tickets, 
                         stats=stats,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         priority_filter=priority_filter)

@app.route('/admin/update-support-ticket/<int:ticket_id>', methods=['POST'])
def update_support_ticket(ticket_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        flash('Ticket not found.')
        return redirect(url_for('admin_support_tickets'))

    try:
        new_status = request.form.get('status')
        new_priority = request.form.get('priority')
        admin_notes = request.form.get('admin_notes', '').strip()

        if new_status:
            ticket.status = new_status
            if new_status == 'resolved':
                ticket.resolved_at = datetime.utcnow()

        if new_priority:
            ticket.priority = new_priority

        if admin_notes:
            ticket.admin_notes = admin_notes

        # Get admin user ID
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            ticket.assigned_to = admin_user.id

        ticket.updated_at = datetime.utcnow()
        db.session.commit()

        flash(f'Ticket #{ticket.ticket_number} updated successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating ticket: {str(e)}')

    return redirect(url_for('admin_support_tickets'))

@app.route('/admin/api-management')
def admin_api_management():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    # Get all configurations
    api_configs = CoinConfiguration.query.order_by(CoinConfiguration.config_name).all()

    return render_template('admin_api_management.html', api_configs=api_configs)

@app.route('/admin/add-api-config', methods=['POST'])
def add_api_config():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    config_name = request.form.get('config_name', '').strip()
    config_type = request.form.get('config_type', 'text')
    coin_value = request.form.get('coin_value', '0')
    description = request.form.get('description', '').strip()
    is_active = 'is_active' in request.form

    if not config_name or not description:
        flash('Please fill all required fields.')
        return redirect(url_for('admin_api_management'))

    # Check if config already exists
    existing_config = CoinConfiguration.query.filter_by(config_name=config_name).first()
    if existing_config:
        flash('Configuration with this name already exists.')
        return redirect(url_for('admin_api_management'))

    try:
        # Validate numeric value
        coin_value_int = int(coin_value) if coin_value else 0

        new_config = CoinConfiguration(
            config_name=config_name,
            coin_value=coin_value_int,
            description=description,
            is_active=is_active
        )

        db.session.add(new_config)
        db.session.commit()

        flash(f'API configuration "{config_name}" added successfully!')

    except ValueError:
        flash('Invalid numeric value.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding configuration: {str(e)}')

    return redirect(url_for('admin_api_management'))

@app.route('/admin/toggle-api-config-status/<int:config_id>', methods=['POST'])
def toggle_api_config_status(config_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    config = CoinConfiguration.query.get(config_id)
    if not config:
        flash('Configuration not found.')
        return redirect(url_for('admin_api_management'))

    try:
        config.is_active = not config.is_active
        config.updated_at = datetime.utcnow()
        db.session.commit()

        status = "activated" if config.is_active else "deactivated"
        flash(f'Configuration "{config.config_name}" {status} successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating configuration: {str(e)}')

    return redirect(url_for('admin_api_management'))

@app.route('/admin/delete-api-config/<int:config_id>', methods=['POST'])
def delete_api_config(config_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    config = CoinConfiguration.query.get(config_id)
    if not config:
        flash('Configuration not found.')
        return redirect(url_for('admin_api_management'))

    try:
        config_name = config.config_name
        db.session.delete(config)
        db.session.commit()

        flash(f'API configuration "{config_name}" deleted successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting configuration: {str(e)}')

    return redirect(url_for('admin_api_management'))

@app.route('/download-apk')
def download_apk():
    # Get active APK
    active_apk = ApkFile.query.filter_by(is_active=True).first()

    if not active_apk:
        flash('No APK file available for download.')
        return redirect(url_for('dashboard'))

    try:
        # Increment download count
        active_apk.download_count += 1
        db.session.commit()

        # Send file
        from flask import send_file
        return send_file(active_apk.file_path, 
                        as_attachment=True, 
                        download_name=f"{active_apk.app_name}_v{active_apk.version}.apk")
    except Exception as e:
        flash(f'Error downloading APK: {str(e)}')
        return redirect(url_for('dashboard'))

@app.route('/api/online-users-count')
def api_online_users_count():
    """API endpoint to get current online users count"""
    if not is_admin():
        return jsonify({'error': 'Access denied'}), 401
    
    online_count = get_online_users_count()
    return jsonify({'online_users': online_count})

@app.route('/api/admin/live-stats')
def api_admin_live_stats():
    """API endpoint for real-time admin dashboard stats"""
    if not is_admin():
        return jsonify({'error': 'Access denied'}), 401
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get current activity stats
        online_users = get_online_users_count()
        total_users = User.query.count()
        
        # Get today's ad watching activity
        today_ad_sessions = AdWatchSession.query.filter_by(session_date=today).all()
        total_ads_watched_today = sum(session.ads_watched_count for session in today_ad_sessions)
        total_direct_ads_watched_today = sum(session.direct_ads_watched_count for session in today_ad_sessions)
        active_ad_watchers = len([s for s in today_ad_sessions if s.ads_watched_count > 0 or s.direct_ads_watched_count > 0])
        
        # Get recent orders
        recent_orders = Order.query.filter(Order.created_at >= datetime.now().replace(hour=0, minute=0, second=0)).count()
        
        # Get top active users today
        top_users = []
        for session in sorted(today_ad_sessions, key=lambda x: x.ads_watched_count + x.direct_ads_watched_count, reverse=True)[:5]:
            user = User.query.get(session.user_id)
            if user:
                top_users.append({
                    'username': user.username,
                    'ads_watched': session.ads_watched_count,
                    'direct_ads_watched': session.direct_ads_watched_count,
                    'total_ads': session.ads_watched_count + session.direct_ads_watched_count
                })
        
        stats = {
            'online_users': online_users,
            'total_users': total_users,
            'total_ads_watched_today': total_ads_watched_today,
            'total_direct_ads_watched_today': total_direct_ads_watched_today,
            'active_ad_watchers': active_ad_watchers,
            'recent_orders_today': recent_orders,
            'top_active_users': top_users,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/user-activity/<int:user_id>')
def api_user_activity(user_id):
    """API endpoint to get detailed user activity"""
    if not is_admin():
        return jsonify({'error': 'Access denied'}), 401
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            ad_session = AdWatchSession.query.filter_by(user_id=user_id, session_date=today).first()
        except Exception:
            ad_session = None
        
        # Get recent transactions
        recent_transactions = CoinTransaction.query.filter_by(user_id=user_id).order_by(CoinTransaction.created_at.desc()).limit(10).all()
        
        # Get recent orders
        recent_orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).limit(5).all()
        
        activity_data = {
            'user_id': user.id,
            'username': user.username,
            'coins': user.coins,
            'last_activity': user.last_activity.isoformat() if user.last_activity else None,
            'ads_watched_today': ad_session.ads_watched_count if ad_session else 0,
            'direct_ads_watched_today': getattr(ad_session, 'direct_ads_watched_count', 0) if ad_session else 0,
            'recent_transactions': [
                {
                    'type': t.transaction_type,
                    'amount': t.amount,
                    'description': t.description,
                    'created_at': t.created_at.isoformat()
                } for t in recent_transactions
            ],
            'recent_orders': [
                {
                    'id': o.id,
                    'service_name': o.service_name,
                    'status': o.status,
                    'coins_required': o.coins_required,
                    'created_at': o.created_at.isoformat()
                } for o in recent_orders
            ]
        }
        
        # Sync to Supabase
        sync_user_data_to_supabase(user_id)
        
        return jsonify(activity_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-apk-availability')
def api_check_apk_availability():
    """API endpoint to check if APK is available"""
    active_apk = ApkFile.query.filter_by(is_active=True).first()

    if active_apk:
        return jsonify({
            'available': True,
            'app_name': active_apk.app_name,
            'version': active_apk.version,
            'size': round(active_apk.file_size / 1024 / 1024, 2),  # Size in MB
            'description': active_apk.description,
            'download_url': url_for('download_apk')
        })
    else:
        return jsonify({'available': False})

@app.route('/admin/grant-spin/<int:user_id>', methods=['POST'])
def admin_grant_spin(user_id):
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('admin_referrals'))

    reason = request.form.get('reason', 'Loyal User Reward')
    spins = int(request.form.get('spins', 1))

    # Get current admin user ID (for now, using session admin)
    admin_user = User.query.filter_by(is_admin=True).first()
    admin_id = admin_user.id if admin_user else 1

    if grant_admin_spin(user_id, admin_id, spins, reason):
        flash(f'Granted {spins} spin(s) to {user.username} for: {reason}')
    else:
        flash('Failed to grant spins.')

    return redirect(url_for('admin_referrals'))

@app.route('/spin-wheel')
def spin_wheel():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    # Check if user has already spun today
    today = datetime.now().strftime('%Y-%m-%d')
    today_spin = SpinWheel.query.filter_by(user_id=user.id, spin_date=today).first()

    # Check referral spins and admin spins available
    referral_spins = get_available_referral_spins(user.id)
    admin_spins = get_available_admin_spins(user.id)

    # User can spin if they haven't spun today OR have referral spins OR have admin spins
    can_spin = today_spin is None or referral_spins > 0 or admin_spins > 0

    # Get referral stats
    qualified_referrals = UserReferral.query.filter_by(referrer_id=user.id, is_qualified=True).count()
    total_referrals = UserReferral.query.filter_by(referrer_id=user.id).count()

    referral_stats = {
        'qualified': qualified_referrals,
        'total': total_referrals,
        'remaining_for_bonus': max(0, 10 - qualified_referrals),
        'available_spins': referral_spins
    }

    return render_template('spin_wheel.html', 
                         user=user, 
                         can_spin=can_spin, 
                         today_spin=today_spin, 
                         referral_stats=referral_stats)

@app.route('/start-spin-session', methods=['POST'])
def start_spin_session():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    today = datetime.now().strftime('%Y-%m-%d')
    today_spin = SpinWheel.query.filter_by(user_id=user.id, spin_date=today).first()
    referral_spins = get_available_referral_spins(user.id)
    admin_spins = get_available_admin_spins(user.id)

    # Check if user can spin (daily spin, referral spins, or admin spins)
    if today_spin and referral_spins == 0 and admin_spins == 0:
        return jsonify({'success': False, 'message': 'You have already spun today and have no bonus spins left!'}), 400

    # Generate unique session token for this spin
    import secrets
    session_token = secrets.token_hex(16)
    session['current_spin_token'] = session_token
    session['spin_start_time'] = datetime.utcnow().isoformat()
    session['using_referral_spin'] = today_spin is not None  # True if using referral spin

    return jsonify({'success': True, 'session_token': session_token})

@app.route('/complete-spin', methods=['POST'])
def complete_spin():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User session invalid.'}), 401

    # Verify session token
    data = request.get_json()
    if not data or data.get('session_token') != session.get('current_spin_token'):
        return jsonify({'success': False, 'message': 'Invalid session token.'}), 400

    today = datetime.now().strftime('%Y-%m-%d')
    today_spin = SpinWheel.query.filter_by(user_id=user.id, spin_date=today).first()
    using_referral_spin = session.get('using_referral_spin', False)

    # Determine spin type and use appropriate spin
    if using_referral_spin:
        # Try referral spin first, then admin spin
        if not use_referral_spin(user.id):
            if not use_admin_spin(user.id):
                return jsonify({'success': False, 'message': 'No bonus spins available.'}), 400
    elif today_spin:
        # Must use admin spin if available
        if not use_admin_spin(user.id):
            return jsonify({'success': False, 'message': 'You have already spun today.'}), 400

    # Spin wheel logic with weighted probabilities
    import random

    # Define actual rewards (only Try Again, 1, and 5 coins can be won)
    rewards = [
        {'type': 'extra_spin', 'amount': 0, 'message': 'Try Again! 🔄', 'weight': 40},
        {'type': 'coins', 'amount': 1, 'message': '1 Coin Won! 🪙', 'weight': 35},
        {'type': 'coins', 'amount': 5, 'message': '5 Coins Won! 🪙', 'weight': 25}
    ]

    # Create weighted list
    weighted_rewards = []
    for reward in rewards:
        weighted_rewards.extend([reward] * int(reward['weight'] * 10))

    # Select random reward
    selected_reward = random.choice(weighted_rewards)

    # Record spin (only if not using referral spin)
    if not using_referral_spin:
        spin_record = SpinWheel(
            user_id=user.id,
            spin_date=today,
            reward_type=selected_reward['type'],
            reward_amount=selected_reward['amount']
        )
        db.session.add(spin_record)

    # Handle rewards
    if selected_reward['type'] == 'coins' and selected_reward['amount'] > 0:
        user.coins += selected_reward['amount']

        # Record transaction
        transaction = CoinTransaction(
            user_id=user.id,
            transaction_type='spin_wheel',
            amount=selected_reward['amount'],
            description=f'Daily spin wheel reward: {selected_reward["amount"]} coins'
        )
        db.session.add(transaction)



    db.session.commit()

    # Clear session token
    session.pop('current_spin_token', None)
    session.pop('spin_start_time', None)
    session.pop('using_referral_spin', None)

    return jsonify({
        'success': True,
        'reward_type': selected_reward['type'],
        'reward_amount': selected_reward['amount'],
        'message': selected_reward['message'],
        'new_balance': user.coins,
        'can_spin_again': selected_reward['type'] == 'extra_spin'
    })

@app.route('/referrals')
def referrals():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    # Get referral statistics
    all_referrals = UserReferral.query.filter_by(referrer_id=user.id).all()
    qualified_referrals = [r for r in all_referrals if r.is_qualified]

    # Get referred users with details
    referred_users = []
    for referral in all_referrals:
        referred_user = User.query.get(referral.referred_id)
        if referred_user:
            referred_users.append({
                'username': referred_user.username,
                'joined_date': referral.created_at.strftime('%Y-%m-%d'),
                'qualified': referral.is_qualified,
                'qualified_date': referral.qualified_at.strftime('%Y-%m-%d') if referral.qualified_at else None,
                'domain': referral.domain_used
            })

    # Get current domain for referral link
    current_domain = get_current_domain(request)
    referral_link = f"http://{current_domain}/register?ref={user.referral_code}"

    # Get available referral spins
    available_spins = get_available_referral_spins(user.id)

    # Check if user should get bonus
    should_check_bonus = check_and_award_referral_bonus(user.id)
    if should_check_bonus:
        flash('🎉 Congratulations! You earned 3 free spins for reaching 10 qualified referrals!')

    stats = {
        'total_referrals': len(all_referrals),
        'qualified_referrals': len(qualified_referrals),
        'remaining_for_bonus': max(0, 10 - len(qualified_referrals)),
        'available_spins': available_spins,
        'referral_link': referral_link
    }

    return render_template('referrals.html', user=user, stats=stats, referred_users=referred_users)

@app.route('/test-db')
def test_db():
    """Test database connectivity and show data"""
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))
    
    try:
        # Test SQLite database
        total_users = User.query.count()
        recent_users = User.query.order_by(User.id.desc()).limit(5).all()
        
        # Test Supabase connection
        supabase_connected, supabase_message = test_supabase_connection()
        
        # Get some statistics
        total_orders = Order.query.count()
        total_coins_distributed = db.session.query(db.func.sum(CoinTransaction.amount)).filter(CoinTransaction.amount > 0).scalar() or 0
        
        db_info = {
            'sqlite_status': 'Connected',
            'total_users': total_users,
            'total_orders': total_orders,
            'total_coins_distributed': total_coins_distributed,
            'recent_users': [{'id': u.id, 'username': u.username, 'email': u.email, 'coins': u.coins} for u in recent_users],
            'supabase_connected': supabase_connected,
            'supabase_message': supabase_message
        }
        
        return f"""
        <h1>Database Test Results</h1>
        <h2>SQLite Database</h2>
        <p>Status: {db_info['sqlite_status']}</p>
        <p>Total Users: {db_info['total_users']}</p>
        <p>Total Orders: {db_info['total_orders']}</p>
        <p>Total Coins Distributed: {db_info['total_coins_distributed']}</p>
        
        <h3>Recent Users:</h3>
        <ul>
        {''.join([f"<li>ID: {u['id']}, Username: {u['username']}, Email: {u['email']}, Coins: {u['coins']}</li>" for u in db_info['recent_users']])}
        </ul>
        
        <h2>Supabase Database</h2>
        <p>Status: {'Connected' if db_info['supabase_connected'] else 'Failed'}</p>
        <p>Message: {db_info['supabase_message']}</p>
        
        <p><a href="/admin">Back to Admin Panel</a></p>
        """
        
    except Exception as e:
        return f"<h1>Database Test Error</h1><p>{str(e)}</p><p><a href='/admin'>Back to Admin Panel</a></p>"

@app.route('/buy-coins')
def buy_coins():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    # Get coin purchase rate and EasyPaisa details
    coin_rate = get_coin_purchase_rate()
    easypaisa_name = get_easypaisa_account_name()
    easypaisa_number = get_easypaisa_account_number()

    # Get user's recent purchases
    recent_purchases = CoinPurchase.query.filter_by(user_id=user.id).order_by(CoinPurchase.created_at.desc()).limit(10).all()

    return render_template('buy_coins.html', 
                         user=user, 
                         coin_rate=coin_rate, 
                         easypaisa_name=easypaisa_name,
                         easypaisa_number=easypaisa_number,
                         recent_purchases=recent_purchases)

@app.route('/submit-coin-purchase', methods=['POST'])
def submit_coin_purchase():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User session invalid. Please log in again.')
        return redirect(url_for('login'))

    transaction_id = request.form.get('transaction_id', '').strip()
    amount_pkr = request.form.get('amount_pkr')
    sender_name = request.form.get('sender_name', '').strip()
    sender_phone = request.form.get('sender_phone', '').strip()
    notes = request.form.get('notes', '').strip()

    # Validation
    if not transaction_id or not amount_pkr or not sender_name or not sender_phone:
        flash('Please fill all required fields.')
        return redirect(url_for('buy_coins'))

    # Validate transaction ID format
    if len(transaction_id) < 5:
        flash('Transaction ID seems too short. Please enter a valid EasyPaisa transaction ID.')
        return redirect(url_for('buy_coins'))

    try:
        amount_pkr = float(amount_pkr)

        # Validate amount
        if amount_pkr <= 0:
            flash('Amount must be greater than 0.')
            return redirect(url_for('buy_coins'))

        coin_rate = get_coin_purchase_rate()

        # Calculate coins
        coins_requested = int(amount_pkr / coin_rate)

        # Check minimum
        if coins_requested < 100:
            flash(f'Minimum purchase is 100 coins ({100 * coin_rate} PKR).')
            return redirect(url_for('buy_coins'))

        # Check maximum (optional safety limit)
        if coins_requested > 100000:
            flash('Maximum purchase limit is 100,000 coins per transaction.')
            return redirect(url_for('buy_coins'))

        # Check if transaction ID already exists
        existing = CoinPurchase.query.filter_by(transaction_id=transaction_id).first()
        if existing:
            flash('This transaction ID has already been submitted.')
            return redirect(url_for('buy_coins'))

        # Create purchase record
        purchase = CoinPurchase(
            user_id=user.id,
            transaction_id=transaction_id,
            amount_pkr=amount_pkr,
            coins_requested=coins_requested,
            sender_name=sender_name,
            sender_phone=sender_phone,
            notes=notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(purchase)
        db.session.commit()

        flash(f'✅ Transaction submitted successfully! You will receive {coins_requested} coins within 30 minutes after admin verification.')
        return redirect(url_for('buy_coins'))

    except ValueError:
        flash('Invalid amount entered. Please enter a valid number.')
        return redirect(url_for('buy_coins'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing transaction: {str(e)}. Please try again.')
        return redirect(url_for('buy_coins'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
