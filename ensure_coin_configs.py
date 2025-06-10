
from main import app, db, CoinConfiguration
from datetime import datetime

def ensure_coin_configs():
    """Ensure essential coin configurations exist"""
    with app.app_context():
        try:
            # Define essential configurations
            essential_configs = [
                {
                    'config_name': 'daily_login_bonus',
                    'coin_value': 5,
                    'description': 'Daily login bonus coins'
                },
                {
                    'config_name': 'ad_watch_reward',
                    'coin_value': 1,
                    'description': 'Coins earned per ad watched'
                },
                {
                    'config_name': 'usd_to_coins_rate',
                    'coin_value': 100,
                    'description': 'Conversion rate: 1 USD = X coins'
                }
            ]
            
            for config_data in essential_configs:
                existing = CoinConfiguration.query.filter_by(
                    config_name=config_data['config_name']
                ).first()
                
                if not existing:
                    new_config = CoinConfiguration(
                        config_name=config_data['config_name'],
                        coin_value=config_data['coin_value'],
                        description=config_data['description'],
                        is_active=True,
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(new_config)
                    print(f"✅ Added coin configuration: {config_data['config_name']}")
                else:
                    print(f"✅ Coin configuration exists: {config_data['config_name']}")
            
            db.session.commit()
            print("🎉 Coin configurations check completed!")
            
        except Exception as e:
            print(f"❌ Error ensuring coin configurations: {e}")
            db.session.rollback()

if __name__ == "__main__":
    ensure_coin_configs()
