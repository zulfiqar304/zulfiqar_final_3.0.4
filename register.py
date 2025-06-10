from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db, User  # make sure these are correctly imported
from supabase_config import supabase  # Supabase client
from your_project.sync import sync_user_data_to_supabase  # If you moved sync logic to another file

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        referral = request.form.get('referral')
        device_id = request.form.get('device_id')

        if not username or not email or not password:
            flash("Please fill all fields", "danger")
            return redirect(url_for('register.register'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for('register.register'))

        # Create and save the user
        new_user = User(
            username=username,
            email=email,
            password=password,  # You should hash the password in production!
            referral_code=referral,
            coins=0,
            device_id=device_id,
            last_activity=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()

        # Sync to Supabase
        sync_user_data_to_supabase(new_user.id)

        # Login user and redirect
        session['user_id'] = new_user.id
        flash("Registration successful!", "success")
        return redirect(url_for('dashboard'))

    # GET method (show form)
    referral = request.args.get('ref')
    return render_template('register.html', referral=referral)
