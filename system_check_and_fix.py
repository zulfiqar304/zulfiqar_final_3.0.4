
from main import app, db, User, Order, CoinConfiguration, SelectedService, CoinPurchase
from datetime import datetime
import requests
import os

def check_and_fix_system():
    """Comprehensive system check and auto-fix"""
    print("🔍 ZMWORLD Application Verification")
    print("=" * 50)
    
    issues_found = []
    fixes_applied = []
    
    with app.app_context():
        # 1. Database Tables Check
        try:
            db.create_all()
            print("✅ Database: All tables created/verified")
        except Exception as e:
            issues_found.append(f"Database error: {e}")
            print(f"❌ Database error: {e}")
        
        # 2. Essential Coin Configurations
        essential_configs = [
            ('daily_login_bonus', 5, 'Daily login reward'),
            ('ad_watch_reward', 1, 'Ad watching reward'),
            ('pkr_to_coins_rate', 2, 'Pakistani Rupees to coins conversion rate (PKR per coin)'),
            ('easypaisa_account_name', 0, 'Zulfiqar Ali'),
            ('easypaisa_account_number', 0, '+92-343-3662304')
        ]
        
        for config_name, value, desc in essential_configs:
            existing = CoinConfiguration.query.filter_by(config_name=config_name).first()
            if not existing:
                new_config = CoinConfiguration(
                    config_name=config_name,
                    coin_value=value,
                    description=desc,
                    is_active=True
                )
                db.session.add(new_config)
                fixes_applied.append(f"Added coin config: {config_name}")
                print(f"🔧 Fixed: Added {config_name} configuration")
            else:
                print(f"✅ Config exists: {config_name}")
        
        # 3. Admin User Check
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            # Create admin user if doesn't exist
            admin = User(
                username='admin',
                email='admin@zmworld.com',
                password='scrypt:32768:8:1$YourHashedPassword',  # Change this
                is_admin=True,
                coins=1000,
                referral_code='ADMIN001'
            )
            db.session.add(admin)
            fixes_applied.append("Created admin user")
            print("🔧 Fixed: Created admin user (admin@zmworld.com)")
        else:
            print("✅ Admin user exists")
        
        # 4. JAP API Check
        try:
            response = requests.post("https://justanotherpanel.com/api/v2", 
                                   data={'key': 'c88871268f8d5276927ff8c09fceb422', 'action': 'services'}, 
                                   timeout=10)
            if response.status_code == 200:
                services = response.json()
                print(f"✅ JAP API: Connected, {len(services)} services available")
            else:
                issues_found.append(f"JAP API: HTTP {response.status_code}")
                print(f"⚠️ JAP API: HTTP {response.status_code}")
        except Exception as e:
            issues_found.append(f"JAP API: {str(e)}")
            print(f"⚠️ JAP API: {str(e)}")
        
        # 5. Template Files Check
        template_dir = 'templates'
        required_templates = [
            'home.html', 'login.html', 'register.html', 'dashboard.html',
            'place_order.html', 'order_history.html', 'watch_ad.html',
            'spin_wheel.html', 'referrals.html', 'buy_coins.html',
            'admin_panel.html', 'admin_coins.html', 'admin_coin_purchases.html'
        ]
        
        missing_templates = []
        for template in required_templates:
            if not os.path.exists(os.path.join(template_dir, template)):
                missing_templates.append(template)
        
        if missing_templates:
            issues_found.append(f"Missing templates: {missing_templates}")
            print(f"⚠️ Missing templates: {missing_templates}")
        else:
            print("✅ All required templates present")
        
        # 6. Selected Services Check
        service_count = SelectedService.query.filter_by(is_active=True).count()
        if service_count == 0:
            issues_found.append("No active services configured")
            print("⚠️ No active services configured in admin panel")
        else:
            print(f"✅ Services: {service_count} active services")
        
        # 7. Recent Activity Check
        user_count = User.query.count()
        order_count = Order.query.count()
        purchase_count = CoinPurchase.query.count()
        
        print(f"📊 Statistics:")
        print(f"   • Users: {user_count}")
        print(f"   • Orders: {order_count}")
        print(f"   • Coin Purchases: {purchase_count}")
        
        # Commit all fixes
        if fixes_applied:
            try:
                db.session.commit()
                print(f"\n🎉 Applied {len(fixes_applied)} fixes successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error applying fixes: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        if issues_found:
            print("🚨 ISSUES FOUND:")
            for issue in issues_found:
                print(f"  • {issue}")
        
        if fixes_applied:
            print("🔧 FIXES APPLIED:")
            for fix in fixes_applied:
                print(f"  • {fix}")
        
        if not issues_found and not fixes_applied:
            print("🎉 PERFECT! Application is fully configured and ready!")
        elif fixes_applied and not issues_found:
            print("✅ All issues have been automatically fixed!")
        
        return len(issues_found) == 0

if __name__ == "__main__":
    check_and_fix_system()
