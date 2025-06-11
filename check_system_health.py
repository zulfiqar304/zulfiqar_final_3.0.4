
from main import app, db, User, Order, SelectedService, CoinConfiguration
import requests
import os

def check_system_health():
    """Comprehensive system health check"""
    print("🔍 ZMWORLD System Health Check")
    print("=" * 50)
    
    issues = []
    
    with app.app_context():
        # 1. Database connectivity
        try:
            db.create_all()
            user_count = User.query.count()
            order_count = Order.query.count()
            print(f"✅ Database: Connected ({user_count} users, {order_count} orders)")
        except Exception as e:
            issues.append(f"Database connectivity: {e}")
            print(f"❌ Database: {e}")
        
        # 2. Essential tables
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'user', 'order', 'coin_configuration', 'selected_service',
                'spin_wheel', 'user_referral', 'device_registration'
            ]
            
            missing = [t for t in required_tables if t not in tables]
            if missing:
                issues.append(f"Missing tables: {missing}")
                print(f"⚠️  Missing tables: {missing}")
            else:
                print(f"✅ Tables: All required tables exist ({len(tables)} total)")
        except Exception as e:
            issues.append(f"Table check: {e}")
            print(f"❌ Table check: {e}")
        
        # 3. Coin configurations
        try:
            essential_configs = ['daily_login_bonus', 'ad_watch_reward', 'usd_to_coins_rate']
            missing_configs = []
            
            for config in essential_configs:
                if not CoinConfiguration.query.filter_by(config_name=config, is_active=True).first():
                    missing_configs.append(config)
            
            if missing_configs:
                issues.append(f"Missing coin configs: {missing_configs}")
                print(f"⚠️  Missing coin configs: {missing_configs}")
            else:
                print("✅ Coin configs: All essential configurations present")
        except Exception as e:
            issues.append(f"Coin config check: {e}")
            print(f"❌ Coin config check: {e}")
        
        # 4. JAP API connectivity
        try:
            JAP_API_URL = "https://justanotherpanel.com/api/v2"
            JAP_API_KEY = "c88871268f8d5276927ff8c09fceb422"
            
            response = requests.post(JAP_API_URL, data={
                'key': JAP_API_KEY,
                'action': 'services'
            }, timeout=10)
            
            if response.status_code == 200:
                services = response.json()
                if isinstance(services, list) and len(services) > 0:
                    print(f"✅ JAP API: Connected ({len(services)} services)")
                else:
                    issues.append("JAP API returned invalid data")
                    print("⚠️  JAP API: Invalid response")
            else:
                issues.append(f"JAP API HTTP {response.status_code}")
                print(f"⚠️  JAP API: HTTP {response.status_code}")
        except Exception as e:
            issues.append(f"JAP API: {e}")
            print(f"❌ JAP API: {e}")
        
        # 5. Template files
        template_dir = 'templates'
        required_templates = [
            'layout.html', 'home.html', 'login.html', 'register.html',
            'dashboard.html', 'place_order.html', 'order_history.html',
            'watch_ad.html', 'spin_wheel.html', 'referrals.html'
        ]
        
        missing_templates = []
        for template in required_templates:
            if not os.path.exists(os.path.join(template_dir, template)):
                missing_templates.append(template)
        
        if missing_templates:
            issues.append(f"Missing templates: {missing_templates}")
            print(f"⚠️  Missing templates: {missing_templates}")
        else:
            print("✅ Templates: All required templates present")
        
        # 6. Selected services
        try:
            service_count = SelectedService.query.filter_by(is_active=True).count()
            if service_count == 0:
                issues.append("No active services configured")
                print("⚠️  No active services configured")
            else:
                print(f"✅ Services: {service_count} active services configured")
        except Exception as e:
            issues.append(f"Service check: {e}")
            print(f"❌ Service check: {e}")
        
        # 7. Admin user check
        try:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count == 0:
                issues.append("No admin users found")
                print("⚠️  No admin users found")
            else:
                print(f"✅ Admin: {admin_count} admin user(s) configured")
        except Exception as e:
            issues.append(f"Admin check: {e}")
            print(f"❌ Admin check: {e}")
    
    print("\n" + "=" * 50)
    if issues:
        print("🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
        print(f"\n❌ System Status: {len(issues)} issue(s) need attention")
        return False
    else:
        print("🎉 System Status: All checks passed!")
        return True

def fix_common_issues():
    """Fix common system issues automatically"""
    print("\n🔧 Attempting to fix common issues...")
    
    with app.app_context():
        # Fix missing coin configurations
        configs = [
            ('daily_login_bonus', 5, 'Daily login reward'),
            ('ad_watch_reward', 1, 'Ad watching reward'),
            ('usd_to_coins_rate', 100, 'USD to coins conversion rate')
        ]
        
        for config_name, value, desc in configs:
            existing = CoinConfiguration.query.filter_by(config_name=config_name).first()
            if not existing:
                new_config = CoinConfiguration(
                    config_name=config_name,
                    coin_value=value,
                    description=desc,
                    is_active=True
                )
                db.session.add(new_config)
                print(f"✅ Added coin config: {config_name}")
        
        try:
            db.session.commit()
            print("✅ Fixed coin configurations")
        except Exception as e:
            print(f"❌ Failed to fix coin configs: {e}")
            db.session.rollback()

if __name__ == "__main__":
    healthy = check_system_health()
    if not healthy:
        fix_common_issues()
        print("\n" + "=" * 50)
        print("🔄 Re-running health check...")
        check_system_health()
