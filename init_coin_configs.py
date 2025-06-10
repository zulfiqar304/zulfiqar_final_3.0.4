
from main import app, db, CoinConfiguration

def init_default_configs():
    """Initialize default coin configurations"""
    
    default_configs = [
        {
            'config_name': 'daily_login_bonus',
            'coin_value': 5,
            'description': 'Coins awarded for daily login'
        },
        {
            'config_name': 'ad_watch_reward',
            'coin_value': 1,
            'description': 'Coins awarded for watching an ad'
        },
        {
            'config_name': 'usd_to_coins_rate',
            'coin_value': 100,
            'description': 'Conversion rate: 1 USD = X coins'
        },
        {
            'config_name': 'registration_bonus',
            'coin_value': 10,
            'description': 'Welcome bonus for new users'
        },
        {
            'config_name': 'referral_bonus',
            'coin_value': 20,
            'description': 'Bonus for successful referrals'
        }
    ]
    
    with app.app_context():
        for config_data in default_configs:
            # Check if config already exists
            existing = CoinConfiguration.query.filter_by(config_name=config_data['config_name']).first()
            if not existing:
                config = CoinConfiguration(**config_data)
                db.session.add(config)
                print(f"Added configuration: {config_data['config_name']}")
            else:
                print(f"Configuration already exists: {config_data['config_name']}")
        
        db.session.commit()
        print("Default coin configurations initialized successfully!")

if __name__ == "__main__":
    init_default_configs()
