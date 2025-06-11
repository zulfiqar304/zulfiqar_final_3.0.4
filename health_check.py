
from main import app, db, User, Order, CoinConfiguration, get_user_level
import requests

def health_check():
    """Perform comprehensive health check of the application"""
    with app.app_context():
        print("🏥 Starting application health check...\n")
        
        # 1. Database connectivity
        try:
            user_count = User.query.count()
            order_count = Order.query.count()
            config_count = CoinConfiguration.query.count()
            print(f"✅ Database: {user_count} users, {order_count} orders, {config_count} configs")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        
        # 2. User level calculation
        try:
            if user_count > 0:
                first_user = User.query.first()
                level_info = get_user_level(first_user.id)
                print(f"✅ User level calculation: {level_info['level']}")
            else:
                print("✅ User level calculation: No users to test")
        except Exception as e:
            print(f"❌ User level calculation error: {e}")
            return False
        
        # 3. JAP API connectivity (external)
        try:
            jap_url = "https://justanotherpanel.com/api/v2"
            jap_key = "c88871268f8d5276927ff8c09fceb422"
            response = requests.post(jap_url, data={
                'key': jap_key,
                'action': 'services'
            }, timeout=10)
            
            if response.status_code == 200:
                services = response.json()
                print(f"✅ JAP API: Connected, {len(services)} services available")
            else:
                print(f"⚠️  JAP API: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  JAP API: Connection issue - {e}")
        
        # 4. Essential coin configurations
        try:
            essential_configs = ['daily_login_bonus', 'ad_watch_reward', 'usd_to_coins_rate']
            missing_configs = []
            
            for config_name in essential_configs:
                config = CoinConfiguration.query.filter_by(config_name=config_name, is_active=True).first()
                if not config:
                    missing_configs.append(config_name)
            
            if missing_configs:
                print(f"⚠️  Missing coin configs: {missing_configs}")
            else:
                print("✅ Coin configurations: All essential configs present")
        except Exception as e:
            print(f"❌ Coin configuration error: {e}")
        
        # 5. Template files
        import os
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
            print(f"⚠️  Missing templates: {missing_templates}")
        else:
            print("✅ Templates: All required templates present")
        
        print("\n🎉 Health check completed!")
        return True

if __name__ == "__main__":
    health_check()
